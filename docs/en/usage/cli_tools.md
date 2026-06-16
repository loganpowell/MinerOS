# Command Line Tools Usage Instructions

## View Help Information

To view help information for MinerOS command line tools, you can use the `--help` parameter. Here are help information examples for various command line tools:

```bash
mineros --help
Usage: mineros [OPTIONS]

Options:
  -v, --version                   Show version and exit
  -p, --path PATH                 Input file path or directory (required)
  -o, --output PATH               Output directory (required)
  --api-url TEXT                  MinerOS FastAPI base URL; if omitted, `mineros` starts a temporary local `mineros-api`
  -m, --method [auto|txt|ocr]     Parsing method: auto (default), txt, ocr (pipeline and hybrid* backend only)
  -b, --backend [pipeline|hybrid-auto-engine|hybrid-http-client|vlm-auto-engine|vlm-http-client]
                                  Parsing backend (default: hybrid-auto-engine)
  -l, --lang [ch|ch_server|ch_lite|en|korean|japan|chinese_cht|ta|te|ka|th|el|latin|arabic|east_slavic|cyrillic|devanagari]
                                  Specify document language (improves OCR accuracy, pipeline and hybrid* backend only)
  -u, --url TEXT                  OpenAI-compatible backend URL passed through to the server when using http-client
  -s, --start INTEGER             Starting page number for parsing (0-based)
  -e, --end INTEGER               Ending page number for parsing (0-based)
  -f, --formula BOOLEAN           Enable formula parsing (default: enabled)
  -t, --table BOOLEAN             Enable table parsing (default: enabled)
  --help                          Show help information
```

> [!TIP]
> `mineros` currently supports local `PDF`, image, and `DOCX` file or directory inputs.

```bash
mineros-api --help
Usage: mineros-api [OPTIONS]

Options:
  --host TEXT     Server host (default: 127.0.0.1)
  --port INTEGER  Server port (default: 8000)
  --reload        Enable auto-reload (development mode)
  --enable-vlm-preload BOOLEAN
                  Preload the local VLM model during mineros-api startup.
  --help          Show this message and exit.
```

```bash
mineros-gradio --help
Usage: mineros-gradio [OPTIONS]

Options:
  --enable-example BOOLEAN        Enable example files for input. The example
                                  files to be input need to be placed in the
                                  `example` folder within the directory where
                                  the command is currently executed.
  --enable-http-client BOOLEAN    Enable http-client backend to link openai-
                                  compatible servers.
  --enable-api BOOLEAN            Enable gradio API for serving the
                                  application.
  --max-convert-pages INTEGER     Set the maximum number of pages to convert
                                  from PDF to Markdown.
  --server-name TEXT              Set the server name for the Gradio app.
  --server-port INTEGER           Set the server port for the Gradio app.
  --api-url TEXT                  MinerOS FastAPI base URL. If omitted, gradio
                                  starts a reusable local mineros-api service.
  --enable-vlm-preload BOOLEAN    Preload the local VLM model when gradio
                                  starts a local mineros-api service.
  --latex-delimiters-type [a|b|all]
                                  Set the type of LaTeX delimiters to use in
                                  Markdown rendering: 'a' for type '$', 'b' for
                                  type '()[]', 'all' for both types.
  --help                          Show this message and exit.
```

```bash
mineros-router --help
Usage: mineros-router [OPTIONS]

Options:
  --host TEXT             Server host (default: 127.0.0.1)
  --port INTEGER          Server port (default: 8002)
  --reload                Enable auto-reload (development mode)
  --upstream-url TEXT     Existing MinerOS FastAPI base URL; repeat to add more
  --local-gpus TEXT       Local GPU workers to launch: auto, none, or CSV such
                          as 0,1,2
  --worker-host TEXT      Host for router-managed workers (default: 127.0.0.1)
  --enable-vlm-preload BOOLEAN
                          Preload the local VLM model in router-managed
                          mineros-api workers.
  --help                  Show this message and exit.
```

## Environment Variables Description

> [!NOTE]
> Starting from this version, `mineros` is an orchestration client built on top of `mineros-api`:
>
> - Without `--api-url`, the CLI launches a temporary local `mineros-api`
> - With `--api-url`, the CLI connects to that FastAPI service directly
> - `--url` is no longer the MinerOS API address; it is the OpenAI-compatible backend URL used by server-side `vlm/hybrid-http-client`

Some parameters of MinerOS command line tools have equivalent environment variable configurations. Generally, environment variable configurations have higher priority than command line parameters and take effect across all command line tools.
Here are the environment variables and their descriptions:

- `MINEROS_TOOLS_CONFIG_JSON`:
  - Used to specify configuration file path
  - defaults to `mineros.json` in user directory, can specify other configuration file paths through environment variables.
- `MINEROS_FORMULA_ENABLE`:
  - Used to enable formula parsing
  - defaults to `true`, can be set to `false` through environment variables to disable formula parsing.
- `MINEROS_FORMULA_CH_SUPPORT`:
  - Used to enable Chinese formula parsing optimization (experimental feature)
  - Default is `false`, can be set to `true` via environment variable to enable Chinese formula parsing optimization.
  - Only effective for `pipeline` backend.
- `MINEROS_TABLE_ENABLE`:
  - Used to enable table parsing
  - Default is `true`, can be set to `false` via environment variable to disable table parsing.

- `MINEROS_TABLE_MERGE_ENABLE`:
  - Used to enable table merging functionality
  - Default is `true`, can be set to `false` via environment variable to disable table merging functionality.

- `MINEROS_PDF_RENDER_TIMEOUT`:
  - Used to set the timeout (in seconds) for rendering PDFs to images.
  - Default is `300` seconds; you can set a different value via an environment variable to adjust the rendering timeout.
  - Only effective on Linux and macOS systems.

- `MINEROS_PDF_RENDER_THREADS`:
  - Used to set the number of threads used when rendering PDFs to images.
  - Default is `4`; you can set a different value via an environment variable to adjust the number of threads for image rendering.
  - Only effective on Linux and macOS systems.

- `MINEROS_PROCESSING_WINDOW_SIZE`:
  - Used to control the processing window size, which affects memory use and throughput on large-document workloads.
  - Default is `64`; set it to another positive integer when needed.

- `MINEROS_API_MAX_CONCURRENT_REQUESTS`:
  - Used to control the maximum concurrent requests handled by `mineros-api` or router-managed workers.
  - Default is `3`, and it must be a positive integer.

- `MINEROS_API_ENABLE_FASTAPI_DOCS`:
  - Used to control whether FastAPI documentation endpoints such as `/docs`, `/openapi.json`, and `/redoc` are enabled.
  - Default is `true`.

- `MINEROS_API_OUTPUT_ROOT`:
  - Used to configure the root output directory for `mineros-api`.
  - Default is `./output` under the current working directory.

- `MINEROS_LOCAL_API_STARTUP_TIMEOUT_SECONDS`:
  - Used to control how long CLI tools wait for a locally started `mineros-api` to become healthy.
  - Default is `300` seconds.
  - Applies to temporary local API startup in `mineros`, preload startup in `mineros-gradio`, and router-managed local workers.

- `MINEROS_API_TASK_RETENTION_SECONDS`:
  - Used to set how long completed or failed tasks are retained, in seconds.
  - Default is `86400` seconds (24 hours).

- `MINEROS_API_TASK_CLEANUP_INTERVAL_SECONDS`:
  - Used to set the cleanup polling interval for expired tasks, in seconds.
  - Default is `300` seconds (5 minutes).

- `MINEROS_INTRA_OP_NUM_THREADS`:
  - Used to set the intra_op thread count for ONNX models, affects the computation speed of individual operators
  - Default is `-1` (auto-select), can be set to other values via environment variable to adjust the thread count.

- `MINEROS_INTER_OP_NUM_THREADS`:
  - Used to set the inter_op thread count for ONNX models, affects the parallel execution of multiple operators
  - Default is `-1` (auto-select), can be set to other values via environment variable to adjust the thread count.

- `MINEROS_HYBRID_BATCH_RATIO`:
  - Used to set the batch ratio for small model processing in `hybrid-*` backends.
  - Commonly used in `hybrid-http-client`, it allows adjusting the VRAM usage of a single client by controlling the batch ratio of small models.
  - | Single Client VRAM Size | MINEROS_HYBRID_BATCH_RATIO |
    | ----------------------- | -------------------------- |
    | <= 6 GB                 | 8                          |
    | <= 4 GB                 | 4                          |
    | <= 3 GB                 | 2                          |
    | <= 2 GB                 | 1                          |

- `MINEROS_HYBRID_FORCE_PIPELINE_ENABLE`:
  - Used to force the text extraction part in `hybrid-*` backends to be processed using small models.
  - Defaults to `false`. Can be set to `true` via environment variable to enable this feature, thereby reducing hallucinations in certain extreme cases.

- `MINERU_VL_MODEL_NAME`:
  - Used to specify the model name for the vlm/hybrid backend, allowing you to designate the model required for MinerOS to run when multiple models exist on a remote openai-server.

- `MINERU_VL_API_KEY`:
  - Used to specify the API Key for the vlm/hybrid backend, enabling authentication on the remote openai-server.

- `MINEROS_LO_SERVER`:
  - Base URL of a running [unoserver](https://github.com/unoserver/unoserver) HTTP instance used to convert PPTX and XLSX files to PDF before VLM processing.
  - Example: `http://127.0.0.1:2003`
  - When set, MinerOS POSTs the source file to `{MINEROS_LO_SERVER}/` and receives PDF bytes back, which then flow through the normal VLM pipeline.
  - When not set, MinerOS falls back to a locally installed `libreoffice` / `soffice` binary.
  - Start a local server with `mineros-lo-server` (requires `pip install 'mineros[lo]'` and LibreOffice installed).
