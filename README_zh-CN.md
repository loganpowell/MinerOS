# MinerOS

[![open issues](https://img.shields.io/github/issues-raw/loganpowell/MinerOS)](https://github.com/loganpowell/MinerOS/issues)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE.md)
[![Python Version](https://img.shields.io/badge/python-3.10--3.13-blue)](https://github.com/loganpowell/MinerOS)

**MinerOS** 是 [MinerOS](https://github.com/loganpowell/MinerOS) 的 Apache 2.0 授权分支 —— 一款高精度文档解析引擎，可将 PDF、Word、PPT 及图片转换为结构化的 Markdown/JSON，适用于 LLM · RAG · Agent 工作流。

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

<details>
<summary>MinerU — 专为 LLM · RAG · Agent 场景构建的高精度文档解析引擎 </summary>
将 PDF · Word · PPT · 图片 · 网页转为结构化 Markdown / JSON · VLM+OCR 双引擎 · 109 种语言 <br>
MCP Server · LangChain / Dify / FastGPT 原生集成 · 10+ 国产算力适配 <br>

**🔍 核心解析能力**

- 公式 → LaTeX · 表格 → HTML，精准还原复杂版面
- 支持扫描件、手写体、多栏布局、跨页表格合并
- 输出符合人类阅读顺序，自动去除页眉页脚
- VLM + OCR 双引擎，支持 109 种语言识别

**🔌 接入方式**

| 场景        | 方案                                                                       |
| ----------- | -------------------------------------------------------------------------- |
| AI 编程工具 | MCP Server — Cursor · Claude Desktop · Windsurf                            |
| RAG 框架    | LangChain · LlamaIndex · RAGFlow · RAG-Anything · Flowise · Dify · FastGPT |
| 开发集成    | Python / Go / TypeScript SDK · CLI · REST API · Docker                     |

**🖥️ 部署生态（支持私有化 · 完全离线）**

| 推理后端      | 适用场景                                |
| ------------- | --------------------------------------- |
| pipeline      | 快速稳定，无幻觉，CPU / GPU 均可运行    |
| vlm-engine    | 高精度，支持 vLLM / LMdeploy / mlx 生态 |
| hybrid-engine | 高精度，原生文本提取，低幻觉            |

国产算力：昇腾 · 寒武纪 · 燧原 · 沐曦 · 摩尔线程 · 昆仑芯 · 天数智芯 · 瀚博 · 太初元碁 · 海光 · 平头哥

</details>

# 更新记录

- 2026/03/29 3.0.0 发布

  本次版本更新围绕**解析能力、系统架构与工程可用性**进行了系统升级。主要更新内容包括：
  - `DOCX` 原生解析
    - 正式支持 `DOCX` 原生解析，在无幻觉前提下实现高精度解析。
    - 相较于“先将 `DOCX` 转为 `PDF` 再解析”的传统流程，端到端速度提升数十倍以上，更适合对精度与吞吐均有要求的场景。
  - `pipeline` 后端升级
    - `pipeline` 后端在 OmniDocBench (v1.5) 上取得 `86.2` 分，精度超过上一代主流 VLM `MinerU2.0-2505-0.9B`。
    - 新增表格内图片/公式解析、印章文字识别、竖排文本支持、行间公式序号识别等能力，持续提升复杂文档场景下的解析效果。
    - 在保持高精度的同时，资源占用极低，并继续支持纯 CPU 环境推理。
  - `API / CLI / Router` 编排升级
    - `mineros` 现作为基于 `mineros-api` 的编排客户端运行；在未传入 `--api-url` 时，会自动拉起本地临时服务。
    - `mineros-api` 新增异步任务接口 `POST /tasks`，支持任务提交、状态查询与结果获取；同时保留同步解析接口 `POST /file_parse`，以兼容老版本插件。
    - 新增 `mineros-router`，适用于多服务、多 GPU 的统一入口部署与任务路由；其接口与 `mineros-api` 完全兼容，并支持任务自动负载均衡。
  - 部署与使用体验优化
    - 解决了 `torch >= 2.8` 的兼容问题，基础镜像升级为 `vllm0.11.2 + torch2.9.0`，统一了不同 Compute Capability 的安装路径。
    - 通过滑动窗口优化解析链路，显著降低长文档场景下的内存峰值占用，上万页文档解析不再需要手动拆分。
    - `pipeline` 的 batch 推理支持流式落盘，已完成的解析结果可及时写出，进一步提升长任务处理体验。
    - 完成线程安全优化，全面支持多线程并发推理；配合 `mineros-router`，可一键实现多卡部署，轻松构建高并发、高吞吐解析系统。
    - 完全移除了两个 AGPLv3 模型（`doclayoutyolo` 和 `mfd_yolov8`）以及一个 CC-BY-NC-SA 4.0 模型（`layoutreader`）的使用。

  本次更新不仅是若干功能点的补强，更是 MinerOS 在系统能力上的一次关键跃迁。我们重点解决了长文档解析过程中的内存峰值占用问题，通过滑动窗口、流式落盘等链路优化，让超长文档解析从“需要手动拆分、谨慎处理”走向“稳定可跑、规模可扩展”。同时，我们完成了线程安全优化，全面支持多线程并发推理，进一步提升了单机资源利用率与高并发场景下的运行稳定性。在此基础上，基于 mineros-router 与全新的 API / CLI 编排体系，MinerOS 已具备一键多卡部署、多服务统一接入、任务自动负载均衡的能力，显著降低了大规模部署难度。至此，MinerOS 正在从单一的数据生产工具，进一步演进为面向高并发、高吞吐场景的大规模文档解析基座，为企业级文档数据处理提供更稳定、更高效、更易扩展的基础设施能力。

> 📝 查看完整的 [更新日志](https://loganpowell.github.io/MinerOS/zh/reference/changelog/) 了解更多历史版本信息

# MinerOS

## 项目简介

MinerOS 是一款文档解析工具，可将 `PDF`、图片和 `DOCX` 转化为机器可读格式（如 Markdown、JSON），便于后续检索、抽取与二次处理。
MinerOS诞生于[书生-浦语](https://github.com/InternLM/InternLM)的预训练过程中，我们将会集中精力解决科技文献中的符号转化问题，希望在大模型时代为科技发展做出贡献。
相比国内外知名商用产品MinerOS还很年轻，如果遇到问题或者结果不及预期请到[issue](https://github.com/loganpowell/MinerOS/issues)提交问题，同时**附上相关文档或样例文件**。

https://github.com/user-attachments/assets/4bea02c9-6d54-4cd6-97ed-dff14340982c

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

# 快速开始

如果安装或使用中遇到任何问题，请先查询 <a href="#faq">FAQ</a> </br>
如果遇到解析效果不及预期，参考 <a href="#known-issues">Known Issues</a></br>

## 本地部署

> [!WARNING]
> **安装前必看——软硬件环境支持说明**
>
> 为了确保项目的稳定性和可靠性，我们在开发过程中仅对特定的软硬件环境进行优化和测试。这样当用户在推荐的系统配置上部署和运行项目时，能够获得最佳的性能表现和最少的兼容性问题。
>
> 通过集中资源和精力于主线环境，我们团队能够更高效地解决潜在的BUG，及时开发新功能。
>
> 在非主线环境中，由于硬件、软件配置的多样性，以及第三方依赖项的兼容性问题，我们无法100%保证项目的完全可用性。因此，对于希望在非推荐环境中使用本项目的用户，我们建议先仔细阅读文档以及FAQ，大多数问题已经在FAQ中有对应的解决方案，除此之外我们鼓励社区反馈问题，以便我们能够逐步扩大支持范围。

<table>
  <thead>
    <tr>
      <th rowspan="2">解析后端</th>
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
      <th>后端特性</th>
      <td >兼容性好</td>
      <td colspan="2">硬件配置要求较高</td>
      <td colspan="2">适用于OpenAI兼容服务器<sup>2</sup></td>
    </tr> 
    <tr>
      <th>精度指标<sup>1</sup></th>
      <td style="text-align:center;">86+</td>
      <td colspan="4" style="text-align:center;">90+</td>
    </tr>
    <tr>
      <th>操作系统</th>
      <td colspan="5" style="text-align:center;">Linux<sup>3</sup> / Windows<sup>4</sup> / macOS<sup>5</sup></td>
    </tr>
    <tr>
      <th>纯CPU平台支持</th>
      <td style="text-align:center;">✅</td>
      <td colspan="2" style="text-align:center;">❌</td>
      <td colspan="2" style="text-align:center;">✅</td>
    </tr>
        <tr>
      <th>GPU加速支持</th>
      <td colspan="4" style="text-align:center;">Volta及以后架构GPU或Apple Silicon</td>
      <td rowspan="2">不需要</td>
    </tr>
    <tr>
      <th>显存最低要求</th>
      <td style="text-align:center;">4GB</td>
      <td style="text-align:center;">8GB</td>
      <td style="text-align:center;">8GB</td>
      <td style="text-align:center;">2GB</td>
    </tr>
    <tr>
      <th>内存要求</th>
      <td colspan="3" style="text-align:center;">最低16GB以上,推荐32GB以上</td>
      <td colspan="2" style="text-align:center;">最低16GB</td>
    </tr>
    <tr>
      <th>磁盘空间要求</th>
      <td colspan="3" style="text-align:center;">20GB以上,推荐使用SSD</td>
      <td colspan="2" style="text-align:center;">至少2GB</td>
    </tr>
    <tr>
      <th>python版本</th>
      <td colspan="5" style="text-align:center;">3.10-3.13</td>
    </tr>
  </tbody>
</table>

<sup>1</sup> 精度指标为OmniDocBench (v1.5)的End-to-End Evaluation Overall分数，基于`MinerOS`最新版本测试  
<sup>2</sup> 兼容OpenAI API的服务器，如通过`vLLM`/`SGLang`/`LMDeploy`等推理框架部署的本地模型服务器或远程模型服务  
<sup>3</sup> Linux仅支持2019年及以后发行版  
<sup>4</sup> 由于关键依赖`ray`未能在windows平台支持Python 3.13，故仅支持至3.10~3.12版本  
<sup>5</sup> macOS 需使用14.0以上版本

> [!TIP]
> 除以上主流环境与平台外，我们也收录了一些社区用户反馈的其他平台支持情况，详情请参考[其他加速卡适配](https://loganpowell.github.io/MinerOS/zh/usage/)。  
> 如果您有意将自己的环境适配经验分享给社区，欢迎通过[show-and-tell](https://github.com/loganpowell/MinerOS/discussions/categories/show-and-tell)提交或提交PR至[其他加速卡适配](https://github.com/loganpowell/MinerOS/tree/main/docs/zh/usage/acceleration_cards)文档。

### 安装 MinerOS

#### 使用pip或uv安装MinerOS

```bash
pip install --upgrade pip
pip install uv -i
uv pip install -U "mineros[all]"
```

#### 通过源码安装MinerU

```bash
git clone https://github.com/loganpowell/MinerOS.git
cd MinerOS
uv pip install -e .[all]
```

> [!TIP]
> `mineros[all]`包含所有核心功能，兼容Windows / Linux / macOS系统，适合绝大多数用户。
> 如果您需要指定vlm模型的推理框架，或是仅准备在边缘设备安装轻量版client端，可以参考文档[扩展模块安装指南](https://loganpowell.github.io/MinerOS/zh/quick_start/extension_modules/)。

---

#### 使用docker部署MinerOS

MinerOS提供了便捷的docker部署方式，这有助于快速搭建环境并解决一些棘手的环境兼容问题。
您可以在文档中获取[Docker部署说明](https://loganpowell.github.io/MinerOS/zh/quick_start/docker_deployment/)。

---

### 使用 MinerOS

> [!TIP]
> 默认使用托管在`huggingface`的模型进行解析，首次使用时会自动下载所需模型文件，后续使用将直接加载本地缓存的模型。如果您无法访问`huggingface`，可以通过以下命令切换至国内镜像源:
>
> ```bash
> export MINEROS_MODEL_SOURCE=modelscope
> ```

如果您的设备满足上表中GPU加速的条件，可以使用简单的命令行进行文档解析:

```bash
mineros -p <input_path> -o <output_path>
```

如果您的设备不满足GPU加速条件，可以指定后端为`pipeline`，以在纯CPU环境下运行:

```bash
mineros -p <input_path> -o <output_path> -b pipeline
```

当前 `mineros` 支持本地 `PDF / 图片 / DOCX` 文件或目录输入，并可通过命令行、API、WebUI、`mineros-router` 等多种方式进行文档解析，具体使用方法请参考[使用指南](https://loganpowell.github.io/MinerOS/zh/usage/)。

# TODO

- [x] 基于模型的阅读顺序
- [x] 正文中目录、列表识别
- [x] 表格识别
- [x] 标题分级
- [x] 手写文本识别
- [x] 竖排文本识别
- [x] 拉丁字母重音符号识别
- [x] 正文中代码块识别
- [x] [化学式识别](docs/chemical_knowledge_introduction/introduction.pdf)
- [ ] 图表内容识别

# Known Issues

- 阅读顺序基于模型对可阅读内容在空间中的分布进行排序，在极端复杂的排版下可能会部分区域乱序
- 对竖排文字的支持较为有限
- 目录和列表通过规则进行识别，少部分不常见的列表形式可能无法识别
- 代码块在layout模型里还没有支持
- 漫画书、艺术图册、小学教材、习题尚不能很好解析
- 表格识别在复杂表格上可能会出现行/列识别错误
- 在小语种PDF上，OCR识别可能会出现字符不准确的情况（如阿拉伯文易混淆字符等）
- 部分公式可能会无法在markdown中渲染

# FAQ

- 如果您在使用过程中遇到问题，可以先查看[常见问题](https://loganpowell.github.io/MinerOS/zh/faq/)是否有解答。

# All Thanks To Our Contributors

<a href="https://github.com/loganpowell/MinerOS/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=loganpowell/MinerOS" />
</a>

# License Information

[LICENSE.md](LICENSE.md)

本仓库源码采用 AGPLv3 许可。

# Acknowledgments

- [UniMERNet](https://github.com/opendatalab/UniMERNet)
- [TableStructureRec](https://github.com/RapidAI/TableStructureRec)
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
- [PaddleOCR2Pytorch](https://github.com/frotms/PaddleOCR2Pytorch)
- [fast-langdetect](https://github.com/LlmKira/fast-langdetect)
- [pypdfium2](https://github.com/pypdfium2-team/pypdfium2)
- [pdftext](https://github.com/datalab-to/pdftext)
- [pdfminer.six](https://github.com/pdfminer/pdfminer.six)
- [pypdf](https://github.com/py-pdf/pypdf)
- [magika](https://github.com/google/magika)
- [vLLM](https://github.com/vllm-project/vllm)
- [LMDeploy](https://github.com/InternLM/lmdeploy)

# Citation

```bibtex
@article{niu2025mineru2,
  title={Mineru2. 5: A decoupled vision-language model for efficient high-resolution document parsing},
  author={Niu, Junbo and Liu, Zheng and Gu, Zhuangcheng and Wang, Bin and Ouyang, Linke and Zhao, Zhiyuan and Chu, Tao and He, Tianyao and Wu, Fan and Zhang, Qintong and others},
  journal={arXiv preprint arXiv:2509.22186},
  year={2025}
}

@article{wang2024mineru,
  title={Mineru: An open-source solution for precise document content extraction},
  author={Wang, Bin and Xu, Chao and Zhao, Xiaomeng and Ouyang, Linke and Wu, Fan and Zhao, Zhiyuan and Xu, Rui and Liu, Kaiwen and Qu, Yuan and Shang, Fukai and others},
  journal={arXiv preprint arXiv:2409.18839},
  year={2024}
}

@article{he2024opendatalab,
  title={Opendatalab: Empowering general artificial intelligence with open datasets},
  author={He, Conghui and Li, Wei and Jin, Zhenjiang and Xu, Chao and Wang, Bin and Lin, Dahua},
  journal={arXiv preprint arXiv:2407.13773},
  year={2024}
}
```

# Star History

<a>
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=loganpowell/MinerOS&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=loganpowell/MinerOS&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=loganpowell/MinerOS&type=Date" />
 </picture>
</a>

# Links

- [Easy Data Preparation with latest LLMs-based Operators and Pipelines](https://github.com/OpenDCAI/DataFlow)
- [Vis3 (OSS browser based on s3)](https://github.com/opendatalab/Vis3)
- [LabelU (A Lightweight Multi-modal Data Annotation Tool)](https://github.com/opendatalab/labelU)
- [LabelLLM (An Open-source LLM Dialogue Annotation Platform)](https://github.com/opendatalab/LabelLLM)
- [PDF-Extract-Kit (A Comprehensive Toolkit for High-Quality PDF Content Extraction)](https://github.com/opendatalab/PDF-Extract-Kit)
- [OmniDocBench (A Comprehensive Benchmark for Document Parsing and Evaluation)](https://github.com/opendatalab/OmniDocBench)
- [Magic-HTML (Mixed web page extraction tool)](https://github.com/opendatalab/magic-html)
- [Magic-Doc (Fast speed ppt/pptx/doc/docx/pdf extraction tool)](https://github.com/InternLM/magic-doc)
- [Dingo: A Comprehensive AI Data Quality Evaluation Tool](https://github.com/MigoXLab/dingo)
