FROM python:3.12-slim

# LibreOffice for document conversion + unoserver for the HTTP API
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libreoffice \
        libreoffice-java-common \
        default-jre-headless \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir unoserver

EXPOSE 2003

# unoserver --http-server exposes a REST API:
#   POST / (multipart: file=<bytes>, convert_to=pdf) → PDF bytes
CMD ["unoserver", "--host", "0.0.0.0", "--port", "2003", "--http-server"]
