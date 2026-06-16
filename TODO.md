# MinerOS Task List

## Office Format Support

- [ ] **PPTX support via LibreOffice → PDF**
  - `libreoffice --headless --convert-to pdf` on PPTX bytes in a temp dir
  - Replace the `logger.warning` + `need_remove_index.append` in `_process_office_doc()` with a conversion that pushes the resulting PDF bytes back into the normal VLM pipeline
  - Graceful `shutil.which("libreoffice")` check with an actionable error if not installed
  - Integration point: `mineros/cli/common.py`, `_process_office_doc()`

- [ ] **XLSX support via LibreOffice → PDF**
  - Same LibreOffice headless path as PPTX (`--convert-to pdf`)
  - Each sheet becomes a page in the output PDF, which then flows through the VLM pipeline
  - Same availability check and error message as PPTX
  - Integration point: `mineros/cli/common.py`, `_process_office_doc()`

- [ ] **DOCX inline image-tables extraction via VLM**
  - Currently `_handle_pictures()` in `docx_converter.py` emits opaque `IMAGE` blocks for any embedded image — including tables pasted as screenshots
  - Route DOCX image blocks through the VLM (same `vlm-http-client` call used for PDF pages) to attempt table extraction
  - Replace the `IMAGE` block with a `TABLE` block (HTML content) when the VLM returns structured table output; fall back to the original image if it doesn't
  - Integration point: `mineros/model/docx/docx_converter.py`, `_handle_pictures()` / `model_output_to_middle_json.py`

## CI / Release

- [ ] **PyPI publish workflow: set version from git tag**
  - Add a step before `uv build` in `.github/workflows/publish.yml` that writes `mineros/version.py` from `$GITHUB_REF_NAME` (strips leading `v`)
  - Eliminates the need to manually bump `version.py` before tagging
  - Integration point: `.github/workflows/publish.yml`
