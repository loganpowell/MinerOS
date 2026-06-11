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

## Project Introduction

MinerOS is a document parsing tool that converts `PDF`, image, and `DOCX` inputs into machine-readable formats such as Markdown and JSON for downstream retrieval, extraction, and processing.
MinerOS was born during the pre-training process of [InternLM](https://github.com/InternLM/InternLM). We focus on solving symbol conversion issues in scientific literature and hope to contribute to technological development in the era of large models.
Compared to well-known commercial products domestically and internationally, MinerOS is still young. If you encounter any issues or if the results are not as expected, please submit an issue on [GitHub Issues](https://github.com/opendatalab/MinerU/issues) and **attach the relevant document or sample file**.

![type:video](https://github.com/user-attachments/assets/4bea02c9-6d54-4cd6-97ed-dff14340982c)

## Key Features

- Support `PDF`, image, and `DOCX` inputs
- Remove headers, footers, footnotes, page numbers and other elements to ensure semantic coherence
- Output text in human reading order, suitable for single-column, multi-column and complex layouts
- Retain the original document structure, including titles, paragraphs, lists, etc.
- Extract images, image descriptions, tables, table titles and footnotes
- Automatically identify and convert formulas in documents to LaTeX format
- Automatically identify and convert tables in documents to HTML format
- Automatically detect scanned PDFs and garbled PDFs, and enable OCR functionality
- OCR supports detection and recognition of 109 languages
- Support multiple output formats, such as multimodal and NLP Markdown, reading-order-sorted JSON, and information-rich intermediate formats
- Support multiple visualization results, including layout visualization, span visualization, etc., for efficient confirmation of output effects and quality inspection
- Built-in CLI, FastAPI, Gradio WebUI, for local orchestration and multi-service deployment
- Support pure CPU environment operation, and support GPU(CUDA)/NPU(CANN)/MPS acceleration
- Compatible with Windows, Linux and Mac platforms

## User Guide

- [Quick Start Guide](./quick_start/index.md)
- [Detailed Usage Instructions](./usage/index.md)
