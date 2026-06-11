# MinerOS

[![open issues](https://img.shields.io/github/issues-raw/loganpowell/MinerOS)](https://github.com/loganpowell/MinerOS/issues)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE.md)
[![Python Version](https://img.shields.io/badge/python-3.10--3.13-blue)](https://github.com/loganpowell/MinerOS)

**MinerOS** 是 [MinerU](https://github.com/opendatalab/MinerU) 的 Apache 2.0 授权分支 —— 一款高精度文档解析引擎，可将 PDF、Word、PPT 及图片转换为结构化的 Markdown/JSON，适用于 LLM · RAG · Agent 工作流。

## 为什么叫 "OS"？

MinerU 上游的许可证历史较为复杂：该项目曾短暂采用 AGPLv3，后又恢复原状。MinerOS 固定在最后一个干净的 **Apache 2.0** 提交（`e148afa9`），并在此后持续保持 Apache 2.0 授权 —— 使其可以安全地嵌入商业和政府应用，无需担忧 AGPL 传染性问题。

**OS** 后缀代表：

- **开源（Open Source）** —— 完全 Apache 2.0，无 AGPL，无 CC-BY-NC
- **开放标准（Open Standard）** —— 适用于政府采购、受监管行业及开放数据流程
- **操作系统级可靠性（OS-level reliability）** —— 设计为基础设施运行，而非仅作脚本使用

### MinerOS 相较上游 MinerU 的新增功能

| 功能                         | MinerU 上游             | MinerOS                                 |
| ---------------------------- | ----------------------- | --------------------------------------- |
| 许可证                       | 曾短暂为 AGPLv3，后恢复 | 全程 Apache 2.0                         |
| 修订记录 / 删除线检测        | ❌                      | ✅（在 Markdown 中输出 `~~删除文本~~`） |
| 通过 `.env` 自动配置远程 VLM | 手动配置                | 自动加载 `.env`                         |
| 包名                         | `mineru`                | `mineros`                               |

## 项目简介

MinerOS 是一款文档解析工具，可将 `PDF`、图片和 `DOCX` 转化为机器可读格式（如 Markdown、JSON），便于后续检索、抽取与二次处理。
MinerOS诞生于[书生-浦语](https://github.com/InternLM/InternLM)的预训练过程中，我们将会集中精力解决科技文献中的符号转化问题，希望在大模型时代为科技发展做出贡献。
相比国内外知名商用产品MinerOS还很年轻，如果遇到问题或者结果不及预期请到[issue](https://github.com/opendatalab/MinerU/issues)提交问题，同时**附上相关文档或样例文件**。

![type:video](https://github.com/user-attachments/assets/4bea02c9-6d54-4cd6-97ed-dff14340982c)

## 主要功能

- 支持 `PDF`、图片与 `DOCX` 输入
- 删除页眉、页脚、脚注、页码等元素，确保语义连贯
- 输出符合人类阅读顺序的文本，适用于单栏、多栏及复杂排版
- 保留原文档的结构，包括标题、段落、列表等
- 提取图像、图片描述、表格、表格标题及脚注
- 自动识别并转换文档中的公式为LaTeX格式
- 自动识别并转换文档中的表格为HTML格式
- 自动检测扫描版PDF和乱码PDF，并启用OCR功能
- OCR支持109种语言的检测与识别
- 支持多种输出格式，如多模态与NLP的Markdown、按阅读顺序排序的JSON、含有丰富信息的中间格式等
- 支持多种可视化结果，包括layout可视化、span可视化等，便于高效确认输出效果与质检
- 内置命令行、FastAPI、Gradio WebUI，支持本地编排和多服务部署
- 支持纯CPU环境运行，并支持 GPU(CUDA)/NPU(CANN)/MPS 加速
- 兼容Windows、Linux和Mac平台

## 使用指南

- [快速上手指南](./quick_start/index.md)
- [详细使用说明](./usage/index.md)
