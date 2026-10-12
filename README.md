# Pipa em WebGPU

Cena 2D animada de uma pipa voando sobre um céu de cor sólida, renderizada em
**WebGPU** com shaders **WGSL**. Trabalho da disciplina de Computação Gráfica.

## Descrição

- A pipa é o losango do corpo (dividido ao meio na vertical: metade vermelha à
  esquerda, metade amarela à direita) mais a **rabiola**, com dois laços
  triangulares laranja empilhados sob a ponta inferior.
- A cena usa **exatamente 4 triângulos**, sem texturas, imagens externas ou
  bibliotecas de renderização.
- A animação é contínua (`requestAnimationFrame`): a pipa sobe e desce, inclina
  levemente e a rabiola balança com um movimento próprio, porém coerente
  (transformação "parente" da pipa). A câmera acompanha parcialmente o
  movimento vertical.
- Usa matrizes de **modelagem**, **câmera (view)** e **projeção ortográfica**,
  além de vertex buffers e uniform buffers.

## Requisitos

- Um navegador com suporte a **WebGPU** (Chrome/Edge recentes; Firefox ainda
  não habilita WebGPU por padrão).
- Python 3 (apenas para subir um servidor HTTP local) ou qualquer outro
  servidor estático.

> WebGPU só funciona via `http://` (ou `https://`), não abrindo o arquivo
> diretamente com `file://`.

## Como executar

Na raiz do projeto:

```bash
python3 -m http.server 8000
```

Depois abra no navegador:

```
http://localhost:8000/main.html
```

### Dica no Linux (Chrome/Chromium)

Se o canvas aparecer preto e o console mostrar "No available adapters", o
WebGPU provavelmente está sem suporte a Vulkan. Rode o Chrome com flags
semelhantes a:

```bash
google-chrome --enable-unsafe-webgpu --ignore-gpu-blocklist --use-angle=vulkan \
  --enable-features=Vulkan,VulkanFromANGLE http://localhost:8000/main.html
```

## Estrutura

```
pipa/
├── main.html            # página com o canvas
├── main.css             # estilos básicos do canvas
├── main.js              # cena: geometria, matrizes, animação e desenho
├── pipa.vert.js         # shader de vértices (WGSL)
├── pipa.frag.js         # shader de fragmentos (WGSL)
├── lib/
│   ├── utils.js         # matemática de matrizes e utilidades
│   └── webgpu.js        # inicialização do WebGPU e helpers de desenho
├── gerar_relatorio.py   # gera o RELATORIO.docx (sem dependências externas)
└── RELATORIO.docx       # relatório do trabalho
```

## Como contribuir

- Trabalhe em uma branch própria: `git checkout -b feature/minha-mudanca`.
- Abra um **Pull Request** para `main`.
- Evite reescrever histórico de branches já compartilhadas.
