# MinerOS

[![open issues](https://img.shields.io/github/issues-raw/loganpowell/MinerOS)](https://github.com/loganpowell/MinerOS/issues)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE.md)
[![Python Version](https://img.shields.io/badge/python-3.10--3.13-blue)](https://github.com/loganpowell/MinerOS)

**MinerOS** is an Apache 2.0-licensed fork of [MinerU](https://github.com/opendatalab/MinerU) — a high-accuracy document parsing engine that converts PDF, Word, PPT, and images into structured Markdown/JSON for LLM · RAG · Agent workflows.

## Why "OS"?

MinerU's upstream license history is complicated: the project briefly adopted AGPLv3 before reverting. MinerOS is pinned to the last clean **Apache 2.0** commit (`e148afa9`) and kept Apache 2.0 going forward — making it safe to embed in commercial and government applications without AGPL copyleft concerns.

The **OS** suffix signals:

- **Open Source** — fully Apache 2.0, no AGPL, no CC-BY-NC
- **Open Standard** — suitable for government procurement, regulated industries, and open-data pipelines
- **OS-level reliability** — designed to run as infrastructure, not just a script

### What MinerOS adds over upstream MinerU

| Feature                                   | MinerU upstream          | MinerOS                            |
| ----------------------------------------- | ------------------------ | ---------------------------------- |
| License                                   | Briefly AGPLv3, reverted | Apache 2.0 throughout              |
| Tracked-changes / strikethrough detection | ❌                       | ✅ (`~~struck text~~` in Markdown) |
| Remote VLM via `.env` auto-config         | manual                   | `.env` loaded automatically        |
| Package name                              | `mineru`                 | `mineros`                          |

## Core Parsing Capabilities

- **PDF · DOCX · PPTX · Images** → Markdown + JSON
- **Tracked-changes detection** — renders struck-through text as `~~...~~` in Markdown output (critical for government contracts, legislative drafts, redlined legal documents)
- Formulas → LaTeX · Tables → HTML · accurate layout reconstruction
- Scanned docs, handwriting, multi-column layouts, cross-page table merging
- Output follows human reading order with automatic header/footer removal
- VLM + OCR dual engine, 109-language OCR recognition

## Deployment Backends

| Backend              | Best For                                                                      |
| -------------------- | ----------------------------------------------------------------------------- |
| `pipeline`           | Fast & stable, no hallucination, runs on CPU or GPU                           |
| `vlm-http-client`    | High accuracy via remote OpenAI-compatible VLM server (e.g., Azure llama.cpp) |
| `hybrid-http-client` | High accuracy + local OCR, minimal local VRAM                                 |
| `vlm-auto-engine`    | High accuracy via local vLLM / LMDeploy / mlx                                 |
| `hybrid-auto-engine` | Best accuracy, native text extraction, low hallucination                      |

## Quick Start

### Install

```bash
pip install uv
uv pip install -e ".[core]"
```

Or from PyPI (once published):

```bash
uv pip install "mineros[core]"
```

### Run

```bash
# Basic parsing (auto-selects best available backend)
mineros -p <input.pdf> -o <output_dir>

# CPU-only (pipeline backend)
mineros -p <input.pdf> -o <output_dir> -b pipeline

# Remote VLM server (reads MINERU_VL_SERVER / MINERU_VL_API_KEY / MINERU_VL_MODEL_NAME from .env)
mineros -p <input.pdf> -o <output_dir> -b vlm-http-client

# Specific page range
mineros -p <input.pdf> -o <output_dir> -b vlm-http-client -s 0 -e 3
```

### Environment Variables (`.env`)

```dotenv
# Remote VLM server (OpenAI-compatible)
MINERU_VL_SERVER=https://your-llm-server.example.com
MINERU_VL_API_KEY=your-api-key
MINERU_VL_MODEL_NAME=your-model-name

# Required when server n_ctx is small (e.g., llama.cpp with 8192 context)
MINERU_PROCESSING_WINDOW_SIZE=1
```

The `.env` file is loaded automatically via `python-dotenv` — no manual export needed.

## Hardware Requirements

<table>
  <thead>
    <tr>
      <th rowspan="2">Backend</th>
      <th rowspan="2">pipeline</th>
      <th colspan="2">*-auto-engine</th>
      <th colspan="2">*-http-client</th>
    </tr>
    <tr>
      <th>hybrid</th>
      <th>vlm</th>
      <th>hybrid</th>
      <th>vlm</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>Pure CPU</th>
      <td style="text-align:center;">✅</td>
      <td colspan="2" style="text-align:center;">❌</td>
      <td colspan="2" style="text-align:center;">✅</td>
    </tr>
    <tr>
      <th>Min VRAM</th>
      <td style="text-align:center;">4 GB</td>
      <td style="text-align:center;">8 GB</td>
      <td style="text-align:center;">8 GB</td>
      <td style="text-align:center;">2 GB</td>
      <td style="text-align:center;">None</td>
    </tr>
    <tr>
      <th>Min RAM</th>
      <td colspan="3" style="text-align:center;">16 GB (32 GB recommended)</td>
      <td colspan="2" style="text-align:center;">16 GB</td>
    </tr>
    <tr>
      <th>Python</th>
      <td colspan="5" style="text-align:center;">3.10 – 3.13</td>
    </tr>
    <tr>
      <th>OS</th>
      <td colspan="5" style="text-align:center;">Linux (2019+) · Windows · macOS 14+</td>
    </tr>
  </tbody>
</table>

## Docker

```bash
# Build
docker build -f docker/global/Dockerfile -t mineros:latest .

# Run via Compose
docker compose -f docker/compose.yaml up
```

## Known Issues

- Reading order may be out of sequence in extremely complex multi-column layouts.
- Strikethrough detection relies on the VLM visually identifying struck text — accuracy depends on model capability and image resolution.
- Tables of contents and lists are recognized via rules; uncommon formats may be missed.
- Comic books, art albums, and heavily stylized documents parse poorly.
- OCR may produce inaccurate characters for lesser-known languages.

## License

[Apache 2.0](LICENSE.md)

MinerOS is a derivative of [MinerU](https://github.com/opendatalab/MinerU) (opendatalab), used and redistributed under the terms of the Apache 2.0 license as it existed at commit `e148afa9`. All modifications are also released under Apache 2.0.

## Acknowledgments

MinerOS stands on the shoulders of MinerU and its dependencies:

- [MinerU](https://github.com/opendatalab/MinerU) — opendatalab
- [UniMERNet](https://github.com/opendatalab/UniMERNet)
- [TableStructureRec](https://github.com/RapidAI/TableStructureRec)
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
- [fast-langdetect](https://github.com/LlmKira/fast-langdetect)
- [pypdfium2](https://github.com/pypdfium2-team/pypdfium2)
- [pdfminer.six](https://github.com/pdfminer/pdfminer.six)
- [pypdf](https://github.com/py-pdf/pypdf)
- [magika](https://github.com/google/magika)
- [vLLM](https://github.com/vllm-project/vllm)
- [LMDeploy](https://github.com/InternLM/lmdeploy)
