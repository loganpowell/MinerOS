# Quick Start

If you encounter any installation issues, please check the [FAQ](../faq/index.md) first.

## Local Deployment

> [!WARNING]
> **Prerequisites - Hardware and Software Environment Support**
>
> To ensure the stability and reliability of the project, we have optimized and tested only specific hardware and software environments during development. This ensures that users can achieve optimal performance and encounter the fewest compatibility issues when deploying and running the project on recommended system configurations.
>
> By concentrating our resources and efforts on mainstream environments, our team can more efficiently resolve potential bugs and timely develop new features.
>
> In non-mainstream environments, due to the diversity of hardware and software configurations, as well as compatibility issues with third-party dependencies, we cannot guarantee 100% usability of the project. Therefore, for users who wish to use this project in non-recommended environments, we suggest carefully reading the documentation and FAQ first, as most issues have corresponding solutions in the FAQ. Additionally, we encourage community feedback on issues so that we can gradually expand our support range.

<table border="1">
  <thead>
    <tr>
      <th rowspan="2" style="text-align:center; vertical-align:middle;">Parsing Backend</th>
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
      <th>Backend Features</th>
      <td >Good Compatibility</td>
      <td colspan="2">High Hardware Requirements</td>
      <td colspan="2">For OpenAI Compatible Servers<sup>2</sup></td>
    </tr> 
    <tr>
      <th>Accuracy<sup>1</sup></th>
      <td style="text-align:center;">86+</td>
      <td colspan="4" style="text-align:center;">90+</td>
    </tr>
    <tr>
      <th>Operating System</th>
      <td colspan="5" style="text-align:center;">Linux<sup>3</sup> / Windows<sup>4</sup> / macOS<sup>5</sup></td>
    </tr>
    <tr>
      <th>Pure CPU Support</th>
      <td style="text-align:center;">✅</td>
      <td colspan="2" style="text-align:center;">❌</td>
      <td colspan="2" style="text-align:center;">✅</td>
    </tr>
        <tr>
      <th>GPU Acceleration</th>
      <td colspan="4" style="text-align:center;">Volta and later architecture GPUs or Apple Silicon</td>
      <td rowspan="2" style="text-align:center; vertical-align:middle;">Not Required</td>
    </tr>
    <tr>
      <th>Min VRAM</th>
      <td style="text-align:center;">4GB</td>
      <td style="text-align:center;">8GB</td>
      <td style="text-align:center;">8GB</td>
      <td style="text-align:center;">2GB</td>
    </tr>
    <tr>
      <th>RAM</th>
      <td colspan="3" style="text-align:center;">Min 16GB+, Recommended 32GB+</td>
      <td colspan="2" style="text-align:center;">16GB</td>
    </tr>
    <tr>
      <th>Disk Space</th>
      <td colspan="3" style="text-align:center;">20GB+, SSD Recommended</td>
      <td colspan="2" style="text-align:center;">2GB</td>
    </tr>
    <tr>
      <th>Python Version</th>
      <td colspan="5" style="text-align:center;">3.10-3.13</td>
    </tr>
  </tbody>
</table>

<sup>1</sup> Accuracy metrics are the End-to-End Evaluation Overall scores from OmniDocBench (v1.5), based on the latest version of `MinerOS`.  
<sup>2</sup> Servers compatible with OpenAI API, such as local model servers or remote model services deployed via inference frameworks like `vLLM`/`SGLang`/`LMDeploy`.  
<sup>3</sup> Linux only supports distributions from 2019 and later.  
<sup>4</sup> Since the key dependency `ray` does not support Python 3.13 on Windows, only versions 3.10~3.12 are supported.  
<sup>5</sup> macOS requires version 14.0 or later.

### Install MinerOS

#### Install MinerOS using pip or uv

```bash
pip install --upgrade pip
pip install uv
uv pip install -U "mineros[all]"
```

#### Install MinerOS from source code

```bash
git clone https://github.com/loganpowell/MinerOS.git
cd MinerOS
uv pip install -e .[all]
```

> [!TIP]
> `mineros[all]` includes all core features, compatible with Windows / Linux / macOS systems, suitable for most users.
> If you need to specify the inference framework for the VLM model, or only intend to install a lightweight client on an edge device, please refer to the documentation [Extension Modules Installation Guide](https://loganpowell.github.io/MinerOS/quick_start/extension_modules/).

---

#### Deploy MinerOS using Docker

MinerOS provides a convenient Docker deployment method, which helps quickly set up the environment and solve some tricky environment compatibility issues.
You can get the [Docker Deployment Instructions](./docker_deployment.md) in the documentation.

---

### Using MinerOS

If your device meets the GPU acceleration requirements in the table above, you can use a simple command line for document parsing:

```bash
mineros -p <input_path> -o <output_path>
```

If your device does not meet the GPU acceleration requirements, you can specify the backend as `pipeline` to run in a pure CPU environment:

```bash
mineros -p <input_path> -o <output_path> -b pipeline
```

`mineros` currently supports local `PDF`, image, and `DOCX` file or directory inputs.

You can use MinerOS for document parsing through the CLI, API, WebUI. For detailed instructions, please refer to the [Usage Guide](../usage/index.md).
