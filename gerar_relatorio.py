#!/usr/bin/env python3
"""Gera o RELATORIO.docx sem dependencias externas (apenas stdlib)."""

import datetime
import zipfile
from xml.sax.saxutils import escape

CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>
"""

ROOT_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>
"""

DOC_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>
"""

STYLES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults>
    <w:rPrDefault>
      <w:rPr>
        <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:cs="Calibri"/>
        <w:sz w:val="24"/>
        <w:szCs w:val="24"/>
      </w:rPr>
    </w:rPrDefault>
    <w:pPrDefault>
      <w:pPr><w:spacing w:after="120" w:line="276" w:lineRule="auto"/></w:pPr>
    </w:pPrDefault>
  </w:docDefaults>
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:qFormat/>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Title">
    <w:name w:val="Title"/>
    <w:basedOn w:val="Normal"/>
    <w:next w:val="Normal"/>
    <w:qFormat/>
    <w:pPr><w:spacing w:before="240" w:after="240"/><w:jc w:val="center"/></w:pPr>
    <w:rPr><w:rFonts w:ascii="Calibri Light" w:hAnsi="Calibri Light"/><w:b/><w:color w:val="1F3864"/><w:sz w:val="52"/><w:szCs w:val="52"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="heading 1"/>
    <w:basedOn w:val="Normal"/>
    <w:next w:val="Normal"/>
    <w:qFormat/>
    <w:pPr><w:keepNext/><w:spacing w:before="320" w:after="120"/><w:outlineLvl w:val="0"/></w:pPr>
    <w:rPr><w:rFonts w:ascii="Calibri Light" w:hAnsi="Calibri Light"/><w:b/><w:color w:val="2E74B5"/><w:sz w:val="32"/><w:szCs w:val="32"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading2">
    <w:name w:val="heading 2"/>
    <w:basedOn w:val="Normal"/>
    <w:next w:val="Normal"/>
    <w:qFormat/>
    <w:pPr><w:keepNext/><w:spacing w:before="240" w:after="80"/><w:outlineLvl w:val="1"/></w:pPr>
    <w:rPr><w:rFonts w:ascii="Calibri Light" w:hAnsi="Calibri Light"/><w:b/><w:color w:val="2E74B5"/><w:sz w:val="26"/><w:szCs w:val="26"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Code">
    <w:name w:val="Code"/>
    <w:basedOn w:val="Normal"/>
    <w:qFormat/>
    <w:pPr><w:spacing w:after="0" w:line="240" w:lineRule="auto"/><w:ind w:left="360"/><w:shd w:val="clear" w:color="auto" w:fill="F2F2F2"/></w:pPr>
    <w:rPr><w:rFonts w:ascii="Consolas" w:hAnsi="Consolas" w:cs="Consolas"/><w:sz w:val="20"/><w:szCs w:val="20"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Bullet">
    <w:name w:val="Bullet"/>
    <w:basedOn w:val="Normal"/>
    <w:pPr><w:ind w:left="360" w:hanging="360"/></w:pPr>
  </w:style>
</w:styles>
"""

APP_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Python stdlib docx generator</Application>
</Properties>
"""


def core_xml():
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<cp:coreProperties '
        'xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/" '
        'xmlns:dcterms="http://purl.org/dc/terms/" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        '<dc:title>Relatório - Pipa WebGPU</dc:title>'
        '<dc:subject>Computação Gráfica - WebGPU</dc:subject>'
        '<dc:creator>Aluno</dc:creator>'
        '<cp:lastModifiedBy>Aluno</cp:lastModifiedBy>'
        f'<dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>'
        f'<dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>'
        '</cp:coreProperties>'
    )


def paragraph(style, text):
    ppr = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ''
    runs = []
    for line in text.split('\n'):
        runs.append(f'<w:r><w:t xml:space="preserve">{escape(line)}</w:t></w:r>')
        runs.append('<w:r><w:br/></w:r>')
    if runs:
        runs.pop()
    return f'<w:p>{ppr}{"".join(runs)}</w:p>'


CONTENT = [
    ("Title", "Relatório: Cena 2D animada de uma pipa em WebGPU"),
    ("Normal", "Disciplina: Computação Gráfica — Prof. Marcos Lage (UFF)"),
    ("Normal", "Base: códigos produzidos em sala, repositório github.com/mlage/curso-cg"),

    ("Heading1", "1. Objetivo"),
    ("Normal", "Este trabalho implementa, em WebGPU, uma cena 2D animada de uma pipa voando sobre um fundo de céu de cor sólida. A cena é composta exclusivamente por quatro triângulos (dois para o corpo da pipa e dois para os laços da rabiola), sem texturas, imagens externas ou bibliotecas de renderização. Toda a animação é contínua, via requestAnimationFrame, e utiliza matrizes de modelagem, câmera (view) e projeção ortográfica, além de shaders WGSL, vertex buffers e uniform buffers."),

    ("Heading1", "2. Fundamentação e reuso do código de sala"),
    ("Normal", "A implementação parte dos exemplos das aulas de Transformações (05), Câmera (06) e Projeções (07) do repositório da disciplina. Em particular, a biblioteca compartilhada lib/webgpu.js (wrapper GPUCanvas, que encapsula dispositivo, contexto, uniforms e desenho) e lib/utils.js (matemática de matrizes 4x4 em ordem column-major) foram reaproveitadas. A estrutura de cada cena (arquivo main.js com as classes Scene e Main, shaders em arquivos .vert.js/.frag.js, e um par main.html/main.css) foi mantida idêntica à das aulas, mudando apenas a geometria, as transformações e a animação."),

    ("Heading1", "3. Estrutura do projeto"),
    ("Code", "pipa/\n  main.html          -> canvas #glcanvas e carregamento do módulo main.js\n  main.css           -> estilo do canvas (1024 x 768)\n  main.js            -> classes Scene e Main (geometria, matrizes, animação)\n  pipa.vert.js       -> shader WGSL de vértice\n  pipa.frag.js       -> shader WGSL de fragmento\n  lib/utils.js       -> matrizes (translação, escala, rotação, lookAt, ortho)\n  lib/webgpu.js      -> wrapper do WebGPU (program, shape, uniform, draw)"),
    ("Normal", "Nenhuma primitiva diferente de triângulos é utilizada e não há dependências externas."),

    ("Heading1", "4. Modelagem da cena"),
    ("Heading2", "4.1 Fundo (céu)"),
    ("Normal", "Como a cena admite apenas quatro triângulos, o céu não é uma geometria: ele é a cor de limpeza (clearValue) do render pass, definida em SKY_COLOR como um azul-céu (r=0,53; g=0,81; b=0,92; a=1). Dessa forma, o fundo sólido é desenhado sem consumir nenhum dos quatro triângulos disponíveis."),

    ("Heading2", "4.2 Corpo da pipa (2 triângulos)"),
    ("Normal", "A pipa é um losango cortado pela diagonal vertical (topo–base), gerando duas metades com cores sólidas: vermelho vivo à esquerda e amarelo brilhante à direita. Em coordenadas locais (plano XY, z = 0):"),
    ("Bullet", "• topo = (0,00; 0,50)"),
    ("Bullet", "• esquerda = (-0,30; 0,00)"),
    ("Bullet", "• direita = (0,30; 0,00)"),
    ("Bullet", "• base = (0,00; -0,45)"),
    ("Normal", "Triângulo esquerdo: (topo, base, esquerda), cor vermelha (0,90; 0,16; 0,22; 1). Triângulo direito: (topo, direita, base), cor amarelo-dourada (1,00; 0,78; 0,12; 1). Como os dois triângulos formam um único corpo rígido, eles são agrupados em um mesmo shape e compartilham a mesma transformação de modelagem, sendo desenhados em uma única chamada."),

    ("Heading2", "4.3 Rabiola (2 triângulos)"),
    ("Normal", "A rabiola é composta por dois laços triangulares cor-de-laranja, dispostos ao longo de uma linha fina implícita que desce da ponta inferior da pipa. Cada laço é um único triângulo com o pivô no topo (0,0) e corpo em (±0,08; -0,18), ambos na cor laranja (1,00; 0,50; 0,00; 1). Os laços são empilhados verticalmente, com pivôs em (0; -0,50) e (0; -0,72), o que sugere a linha sem precisar desenhar uma primitiva de reta. Cada laço é um shape separado, pois possui transformação própria."),

    ("Heading1", "5. Pipeline de renderização"),
    ("Normal", "O pipeline usa um único programa (mesmo par de shaders) para os quatro triângulos, com topology 'triangle-list' e cullMode 'none'. Como a cena é plana e coplanar (z = 0), o teste de profundidade é desabilitado (depth: false), e a sobreposição é definida apenas pela ordem de desenho (pipa primeiro, laços da rabiola depois). Cada triângulo recebe sua cor por vértice (atributo de cor no vertex buffer), conforme o padrão das aulas."),
    ("Normal", "O shader de vértice recebe position (location 0) e color (location 1), multiplica a posição pela matriz modelViewProjection contida no uniform buffer e repassa a cor. O shader de fragmento simplesmente retorna a cor interpolada. Não há uso de texturas."),
    ("Code", "@group(0) @binding(0) var<uniform> uniforms : Uniforms;\n...\noutput.position = uniforms.modelViewProjection * position;\noutput.color = color;"),
    ("Normal", "São usados três uniform buffers distintos (pipa, laço A, laço B), um por objeto, cada um com sua própria bind group, atendendo ao requisito de uniform buffers e permitindo transformações independentes."),

    ("Heading1", "6. Transformações geométricas"),
    ("Normal", "As matrizes são montadas com a biblioteca da disciplina, em ordem column-major, e combinadas no CPU como P · V · M, no mesmo estilo da aula de Projeções."),
    ("Heading2", "6.1 Matriz de modelagem da pipa"),
    ("Normal", "A pipa translada no plano e gira levemente em torno de Z:"),
    ("Code", "M_pipa = T(x(t), y(t), 0) · Rz(tilt(t)) · S(1, 1, 1)\nx(t)   = 0,06 · sin(0,5 · w · t)        (deriva lateral suave)\ny(t)   = 0,55 · sin(w · t)              (subida e descida), w = 2,2 rad/s\ntilt(t)= 0,18 · sin(w · t + 0,6)        (leve rotação)"),
    ("Heading2", "6.2 Matriz de modelagem dos laços da rabiola (parentesco)"),
    ("Normal", "Cada laço herda a transformação da pipa e acrescenta um pivô sobre a linha e a oscilação própria, o que garante um movimento diferente, porém coerente, em relação à pipa:"),
    ("Code", "M_laco_i = M_pipa · T(0, attachY_i, 0) · Rz(swing_i)\nattachY_i = {-0,50 ; -0,72}\nswing_A  = 0,45·sin(1,4·w·t)        + 0,12·sin(2,7·w·t + 1,0)\nswing_B  = 0,40·sin(1,4·w·t + 1,8)  + 0,15·sin(2,5·w·t + 0,5)"),
    ("Normal", "As fases e frequências diferentes fazem os dois laços se moverem de maneira distinta; o fato de ambos serem multiplicados por M_pipa garante que acompanhem a pipa, mantendo a coerência do conjunto."),

    ("Heading1", "7. Câmera e acompanhamento parcial"),
    ("Normal", "A câmera é montada com createLookAtMat4, olhando para o plano da cena a partir de z = 1 (convenção right-handed, compatível com a projeção ortográfica da biblioteca). Para acompanhar parcialmente a pipa, a posição vertical da câmera é proporcional (fator 0,4) ao deslocamento vertical da pipa:"),
    ("Code", "eye = [0, 0,4 · y(t), 1]\nat  = [0, 0,4 · y(t), 0]\nup  = [0, 1, 0]"),
    ("Normal", "Como o fator é menor que 1, a câmera segue apenas parte do movimento. Assim, a pipa ainda percorre a tela verticalmente, preservando a percepção de movimento, em vez de permanecer fixa no centro."),

    ("Heading1", "8. Projeção ortográfica"),
    ("Normal", "A projeção é ortográfica, com o aspecto calculado a partir das dimensões do canvas (1024 x 768). A meia-altura do volume de visão é 1,5 e a faixa de profundidade segue o intervalo [0,1] do WebGPU:"),
    ("Code", "aspecto = largura / altura            = 1024 / 768 = 1,333\nP = Ortho(-1,5·aspecto, +1,5·aspecto, -1,5, +1,5, 0,1, 10)"),
    ("Normal", "Com essa projeção, verifica-se que os vértices da pipa e dos laços da rabiola mapeiam para coordenadas normalizadas dentro de [-1,1] em X e Y e com profundidade z ≈ 0,09, dentro de [0,1], ou seja, sem recorte."),

    ("Heading1", "9. Animação e laço principal"),
    ("Normal", "O laço de animação segue o padrão da disciplina: a cada quadro, Main.draw() inicia o pass (gpu.start()), a cena recalcula as matrizes, atualiza os uniform buffers e emite três desenhos (pipa, laço A, laço B), finaliza o pass (gpu.finish()) e reagenda a si mesmo com requestAnimationFrame. O tempo é lido de performance.now() em segundos, de modo que as funções senoidais produzam o voo contínuo e independente da taxa de quadros."),
    ("Code", "draw() {\n  this.gpu.start();\n  this.scene.draw(this.gpu);\n  this.gpu.finish();\n  requestAnimationFrame(this.draw.bind(this));\n}"),

    ("Heading1", "10. Como executar"),
    ("Normal", "O WebGPU exige que a página seja servida por HTTP (não funciona via file://). Duas opções:"),
    ("Bullet", "• VS Code com a extensão Live Server (recomendação da disciplina), abrindo main.html;"),
    ("Bullet", "• ou, no diretório do projeto: python3 -m http.server 8000, e acessar http://localhost:8000/main.html em um navegador com suporte a WebGPU (Chrome/Edge recentes)."),

    ("Heading1", "11. Conclusão"),
    ("Normal", "A cena atende a todos os requisitos: é composta por exatamente quatro triângulos (dois no corpo da pipa e dois nos laços da rabiola), sem texturas ou bibliotecas externas; usa modelagem, câmera e projeção ortográfica por matrizes; anima a subida/descida com leve rotação, faz os laços da rabiola se moverem de forma diferente porém coerente (parentesco) e mantém uma câmera que acompanha parcialmente o movimento vertical. A implementação reutiliza diretamente a infraestrutura de WebGPU, WGSL e matemática produzida em sala."),
]


def build_document():
    body = [paragraph(style, text) for style, text in CONTENT]
    body.append(
        '<w:sectPr>'
        '<w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134" '
        'w:header="720" w:footer="720" w:gutter="0"/>'
        '</w:sectPr>'
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:body>' + "".join(body) + '</w:body>'
        '</w:document>'
    )


def main():
    with zipfile.ZipFile("RELATORIO.docx", "w", zipfile.ZIP_DEFLATED) as docx:
        docx.writestr("[Content_Types].xml", CONTENT_TYPES)
        docx.writestr("_rels/.rels", ROOT_RELS)
        docx.writestr("docProps/core.xml", core_xml())
        docx.writestr("docProps/app.xml", APP_XML)
        docx.writestr("word/_rels/document.xml.rels", DOC_RELS)
        docx.writestr("word/styles.xml", STYLES)
        docx.writestr("word/document.xml", build_document())
    print("RELATORIO.docx gerado com sucesso.")


if __name__ == "__main__":
    main()
