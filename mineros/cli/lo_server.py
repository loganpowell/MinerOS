import subprocess
import sys

import click


@click.command()
@click.option("--host", default="0.0.0.0", show_default=True, help="Server host")
@click.option("--port", default=2003, show_default=True, help="Server port")
def lo_server(host: str, port: int) -> None:
    """Start a LibreOffice HTTP conversion server (unoserver).

    Accepts POST / with a multipart file and convert_to=pdf, returns PDF bytes.
    Set MINEROS_LO_SERVER=http://<host>:<port> so mineros can use this server
    to convert PPTX and XLSX files.

    Requires LibreOffice and the unoserver package:
        apt-get install libreoffice && pip install unoserver
    """
    try:
        subprocess.run(
            ["unoserver", "--host", host, "--port", str(port), "--http-server"],
            check=True,
        )
    except FileNotFoundError:
        click.echo(
            "Error: unoserver not found.\n"
            "Install LibreOffice, then: pip install 'mineros[lo]'",
            err=True,
        )
        sys.exit(1)
