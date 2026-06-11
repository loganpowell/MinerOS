# 快速入门

如果遇到任何安装问题，请先查询 [FAQ](../faq/index.md)

## 在线体验

### 官网在线应用

官网在线版功能与客户端一致，界面美观，功能丰富，需要登录使用

### 基于Gradio的在线demo

基于gradio开发的webui，界面简洁，仅包含核心解析功能，免登录

## 本地部署

> [!WARNING]
> **安装前必看——软硬件环境支持说明**
>
> 为了确保项目的稳定性和可靠性，我们在开发过程中仅对特定的软硬件环境进行优化和测试。这样当用户在推荐的系统配置上部署和运行项目时，能够获得最佳的性能表现和最少的兼容性问题。
>
> 通过集中资源和精力于主线环境，我们团队能够更高效地解决潜在的BUG，及时开发新功能。
>
> 在非主线环境中，由于硬件、软件配置的多样性，以及第三方依赖项的兼容性问题，我们无法100%保证项目的完全可用性。因此，对于希望在非推荐环境中使用本项目的用户，我们建议先仔细阅读文档以及FAQ，大多数问题已经在FAQ中有对应的解决方案，除此之外我们鼓励社区反馈问题，以便我们能够逐步扩大支持范围。

<table border="1">
  <thead>
    <tr>
      <th rowspan="2" style="text-align:center; vertical-align:middle;">解析后端</th>
      <th rowspan="2" style="text-align:center; vertical-align:middle;">pipeline</th>
      <th colspan="2" style="text-align:center;">*-auto-engine</th>
      <th colspan="2" style="text-align:center;">*-http-client</th>
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
      <td style="text-align:center;">兼容性好</td>
      <td colspan="2" style="text-align:center;">硬件配置要求较高</td>
      <td colspan="2" style="text-align:center;">适用于OpenAI兼容服务器<sup>2</sup></td>
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
      <td rowspan="2" style="text-align:center; vertical-align:middle;">不需要</td>
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
      <td colspan="2" style="text-align:center;">16GB</td>
    </tr>
    <tr>
      <th>磁盘空间要求</th>
      <td colspan="3" style="text-align:center;">20GB以上,推荐使用SSD</td>
      <td colspan="2" style="text-align:center;">2GB</td>
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
> 如果您有意将自己的环境适配经验分享给社区，欢迎通过提交或提交PR至[其他加速卡适配](https://github.com/loganpowell/MinerU/tree/master/docs/zh/usage/acceleration_cards)文档。

### 安装 MinerOS

#### 使用pip或uv安装MinerOS

```bash
pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple
pip install uv -i https://mirrors.aliyun.com/pypi/simple
uv pip install -U "mineros[all]" -i https://mirrors.aliyun.com/pypi/simple
```

#### 通过源码安装MinerOS

```bash
git clone https://github.com/loganpowell/MinerU.git
cd MinerOS
uv pip install -e .[all] -i https://mirrors.aliyun.com/pypi/simple
```

> [!TIP]
> `mineros[all]`包含所有核心功能，兼容Windows / Linux / macOS系统，适合绝大多数用户。
> 如果您需要指定vlm模型的推理框架，或是仅准备在边缘设备安装轻量版client端，可以参考文档[扩展模块安装指南](https://loganpowell.github.io/MinerOS/zh/quick_start/extension_modules/)。

---

#### 使用docker部署Mineru

MinerOS提供了便捷的docker部署方式，这有助于快速搭建环境并解决一些棘手的环境兼容问题。
您可以在文档中获取[Docker部署说明](./docker_deployment.md)。

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

当前 `mineros` 支持本地 `PDF / 图片 / DOCX` 文件或目录输入。

您可以通过命令行、API、WebUI 等多种方式使用 MinerOS 进行文档解析，具体使用方法请参考[使用指南](../usage/index.md)。
