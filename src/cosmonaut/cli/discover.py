# src/cosmonaut/cli/discover.py
import typer

app = typer.Typer(help="🔍 Discover and explore systems")


@app.command("host")
def discover_host(
    target: str = typer.Argument(..., help="user@host"),
    port: int = typer.Option(22, "--port", "-p"),
    key: str = typer.Option(None, "--key", "-k"),
    password: bool = typer.Option(False, "--password", "-P"),
):
    """Connect to a host and gather specs."""
    # Reuse existing ssh specs logic
    from cosmonaut.cli.ssh import specs

    specs(target=target, port=port, key=key, password=password)
