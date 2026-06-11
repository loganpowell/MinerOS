# 模型源说明

MinerOS使用 `HuggingFace` 和 `ModelScope` 作为模型仓库，用户可以根据需要切换模型源或使用本地模型。

- `HuggingFace` 是默认的模型源，在全球范围内提供了优异的加载速度和极高稳定性。
- `ModelScope` 是中国大陆地区用户的最佳选择，提供了无缝兼容的SDK模块，适用于无法访问`HuggingFace`的用户。

## 模型源的切换方法

### 通过环境变量切换

MinerOS 通过 `MINEROS_MODEL_SOURCE` 环境变量配置模型源，这适用于所有命令行工具和 API 调用。

```bash
export MINEROS_MODEL_SOURCE=modelscope
mineros -p <input_path> -o <output_path>
```

或在代码中设置：

```python
import os
os.environ["MINEROS_MODEL_SOURCE"] = "modelscope"
```

> [!TIP]
> MinerOS 已不再提供用于切换模型源的命令行参数。通过环境变量设置的模型源会在当前终端会话中生效，直到终端关闭或环境变量被修改。

## 使用本地模型

### 1. 下载模型到本地

```bash
mineros-models-download --help
```

或使用交互式命令行工具选择模型下载：

```bash
mineros-models-download
```

> [!NOTE]
>
> - 下载完成后，模型路径会在当前终端窗口输出，并自动写入用户目录下的 `mineros.json`。
> - 您也可以通过将[配置模板文件](https://github.com/loganpowell/MinerOS/blob/main/mineros.template.json)复制到用户目录下并重命名为 `mineros.json` 来创建配置文件。
> - 模型下载到本地后，您可以自由移动模型文件夹到其他位置，同时需要在 `mineros.json` 中更新模型路径。
> - 如您将模型文件夹部署到其他服务器上，请确保将 `mineros.json`文件一同移动到新设备的用户目录中并正确配置模型路径。
> - 如您需要更新模型文件，可以再次运行 `mineros-models-download` 命令，模型更新暂不支持自定义路径，如您没有移动本地模型文件夹，模型文件会增量更新；如您移动了模型文件夹，模型文件会重新下载到默认位置并更新`mineros.json`。
> - `mineros-models-download` 必须使用远端模型源执行真实下载；如果当前终端已设置 `MINEROS_MODEL_SOURCE=local`，该命令会仅在本次执行中临时忽略该值，并改用您选择的 `huggingface` 或 `modelscope` 下载模型。

### 2. 使用本地模型进行解析

通过环境变量启用本地模型：

```bash
export MINEROS_MODEL_SOURCE=local
mineros -p <input_path> -o <output_path>
```
