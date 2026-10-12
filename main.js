import vertShaderSrc from './pipa.vert.js';
import fragShaderSrc from './pipa.frag.js';
import WebGPU from './lib/webgpu.js';
import {
    createIdentityMat4,
    createLookAtMat4,
    createOrthographicMat4,
    createRotationZMat4,
    createScaleMat4,
    createTranslationMat4,
    multiplyMat4,
} from './lib/utils.js';

const SKY_COLOR = { r: 0.53, g: 0.81, b: 0.92, a: 1.0 };

const KITE_TOP = [0.0, 0.4];
const KITE_LEFT = [-0.4, 0.0];
const KITE_RIGHT = [0.4, 0.0];
const KITE_BOTTOM = [0.0, -0.6];

const KITE_LEFT_COLOR = [0.9, 0.16, 0.22, 1.0];
const KITE_RIGHT_COLOR = [1.0, 0.78, 0.12, 1.0];
const TAIL_COLOR = [1.0, 0.5, 0.0, 1.0];

const TAIL_ATTACH_YS = [KITE_BOTTOM[1] - 0.05, KITE_BOTTOM[1] - 0.27];

const BOB_FREQUENCY = 2.2;
const BOB_AMPLITUDE = 0.55;
const SWAY_AMPLITUDE = 0.06;
const TILT_AMPLITUDE = 0.18;
const CAMERA_FOLLOW = 0.4;

const ORTHO_HALF_HEIGHT = 1.5;
const ORTHO_NEAR = 0.1;
const ORTHO_FAR = 10.0;

class Scene {
    constructor(gpu) {
        this.gpu = gpu;
        this.program = gpu.createProgram(vertShaderSrc, fragShaderSrc);

        this.kiteShape = gpu.createShape(this.createKite(), 6);
        this.tailAShape = gpu.createShape(this.createLoop(TAIL_COLOR), 3);
        this.tailBShape = gpu.createShape(this.createLoop(TAIL_COLOR), 3);

        this.kiteUniform = gpu.createUniform(this.program, createIdentityMat4());
        this.tailAUniform = gpu.createUniform(this.program, createIdentityMat4());
        this.tailBUniform = gpu.createUniform(this.program, createIdentityMat4());
    }

    /**
     * A pipa é um losango cortado pela diagonal vertical: dois triângulos,
     * a metade esquerda (vermelho vivo) e a metade direita (amarelo brilhante).
     */
    createKite() {
        const positions = [
            ...KITE_TOP, 0.0, 1.0,
            ...KITE_BOTTOM, 0.0, 1.0,
            ...KITE_LEFT, 0.0, 1.0,

            ...KITE_TOP, 0.0, 1.0,
            ...KITE_RIGHT, 0.0, 1.0,
            ...KITE_BOTTOM, 0.0, 1.0,
        ];

        const colors = [
            ...KITE_LEFT_COLOR,
            ...KITE_LEFT_COLOR,
            ...KITE_LEFT_COLOR,
            ...KITE_RIGHT_COLOR,
            ...KITE_RIGHT_COLOR,
            ...KITE_RIGHT_COLOR,
        ];

        return [positions, colors];
    }

    /**
     * Um laço da rabiola é um único triângulo com o pivô no topo (0,0),
     * de modo que a rotação em Z o faz balançar como um pêndulo.
     */
    createLoop(color) {
        const positions = [
            0.0, 0.0, 0.0, 1.0,
            0.08, -0.18, 0.0, 1.0,
            -0.08, -0.18, 0.0, 1.0,
        ];

        const colors = [
            ...color,
            ...color,
            ...color,
        ];

        return [positions, colors];
    }

    /**
     * Matriz de modelagem da pipa: translação (subida/descida + deriva lateral)
     * composta com a leve rotação e a escala do objeto.
     */
    createKiteModel(time) {
        const y = BOB_AMPLITUDE * Math.sin(BOB_FREQUENCY * time);
        const x = SWAY_AMPLITUDE * Math.sin(0.5 * BOB_FREQUENCY * time);
        const tilt = TILT_AMPLITUDE * Math.sin(BOB_FREQUENCY * time + 0.6);

        const scale = createScaleMat4(1.0, 1.0, 1.0);
        const rotate = createRotationZMat4(tilt);
        const translate = createTranslationMat4(x, y, 0.0);

        return {
            y,
            model: multiplyMat4(translate, multiplyMat4(rotate, scale)),
        };
    }

    /**
     * Matriz de modelagem de cada laço da rabiola. O laço herda a transformação
     * da pipa (parentesco) e acrescenta um pivô sobre a linha e uma oscilação
     * própria, garantindo um movimento diferente, porém coerente, em relação à pipa.
     */
    createTailModel(kiteModel, attachY, swing) {
        const pivot = createTranslationMat4(0.0, attachY, 0.0);
        const rotate = createRotationZMat4(swing);
        return multiplyMat4(kiteModel, multiplyMat4(pivot, rotate));
    }

    /**
     * Matriz de câmera. A posição vertical acompanha apenas parcialmente a
     * pipa, preservando a percepção do movimento vertical na tela.
     */
    createViewMatrix(kiteY) {
        const camY = CAMERA_FOLLOW * kiteY;
        const eye = [0.0, camY, 1.0];
        const at = [0.0, camY, 0.0];
        const up = [0.0, 1.0, 0.0];

        return createLookAtMat4(eye, at, up, true);
    }

    /**
     * Projeção ortográfica com o aspecto calculado a partir do canvas.
     */
    createProjectionMatrix() {
        const aspect = this.gpu.canvas.width / this.gpu.canvas.height;
        const halfWidth = ORTHO_HALF_HEIGHT * aspect;

        return createOrthographicMat4(
            -halfWidth, halfWidth,
            -ORTHO_HALF_HEIGHT, ORTHO_HALF_HEIGHT,
            ORTHO_NEAR, ORTHO_FAR,
        );
    }

    drawObject(shape, uniform, projection, view, model) {
        const modelView = multiplyMat4(view, model);
        uniform.data.set(multiplyMat4(projection, modelView));
        this.gpu.writeBuffer(uniform.buffer, uniform.data);
        this.gpu.draw(this.program, shape, [uniform.bindGroup]);
    }

    draw() {
        const time = performance.now() / 1000;

        const { y, model: kiteModel } = this.createKiteModel(time);

        const swingA = 0.45 * Math.sin(1.4 * BOB_FREQUENCY * time)
            + 0.12 * Math.sin(2.7 * BOB_FREQUENCY * time + 1.0);
        const swingB = 0.40 * Math.sin(1.4 * BOB_FREQUENCY * time + 1.8)
            + 0.15 * Math.sin(2.5 * BOB_FREQUENCY * time + 0.5);

        const tailAModel = this.createTailModel(kiteModel, TAIL_ATTACH_YS[0], swingA);
        const tailBModel = this.createTailModel(kiteModel, TAIL_ATTACH_YS[1], swingB);

        const view = this.createViewMatrix(y);
        const projection = this.createProjectionMatrix();

        this.drawObject(this.kiteShape, this.kiteUniform, projection, view, kiteModel);
        this.drawObject(this.tailAShape, this.tailAUniform, projection, view, tailAModel);
        this.drawObject(this.tailBShape, this.tailBUniform, projection, view, tailBModel);
    }
}

class Main {
    async init() {
        this.gpu = await WebGPU.createCanvas('#glcanvas', 1024, 768, {
            clearColor: SKY_COLOR,
            depth: false,
        });
        this.scene = new Scene(this.gpu);
    }

    draw() {
        this.gpu.start();
        this.scene.draw(this.gpu);
        this.gpu.finish();
        requestAnimationFrame(this.draw.bind(this));
    }
}

try {
    const app = new Main();
    await app.init();
    app.draw();
} catch (error) {
    console.error(error);
    document.body.insertAdjacentHTML('beforeend', `<p>${error.message}</p>`);
}
