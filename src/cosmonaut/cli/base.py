# src/cosmonaut/cli/base.py
import typer
from typing import Optional

# Import the ssh command group
from cosmonaut.cli.ssh import app as ssh_app
from cosmonaut.cli.web import app as web_app
from cosmonaut.cli.map import app as map_app
from cosmonaut.cli.investigate import app as investigate_app
from cosmonaut.cli.discover import app as discover_app
from cosmonaut.explain.explain import explain_app
from cosmonaut.meta import __version__, __app_name__

from rich.table import Table
from rich.console import Console
from cosmonaut.storage import load_servers

# Main app
app = typer.Typer(help="🚀 Cosmonaut - Digital Universe Explorer")

# Register ssh as a subcommand group
app.add_typer(ssh_app, name="ssh")
app.add_typer(web_app, name="web")
app.add_typer(investigate_app, name="investigate")
app.add_typer(map_app, name="map")
app.add_typer(discover_app, name="discover")
app.add_typer(explain_app, name="explain")


@app.command("inventory")
def inventory():
    """Show all discovered servers."""

    console = Console()
    servers = load_servers()

    if not servers:
        console.print("📭 No servers discovered yet.")
        return

    table = Table("IP", "Hostname", "Last Seen", "Sources", "Websites")
    for server in servers.values():
        sources = ", ".join(server["sources"]) if server.get("sources") else "unknown"
        websites = len(server.get("websites", []))
        last_seen = (
            server["last_seen"][:16].replace("T", " ")
            if server.get("last_seen")
            else "?"
        )

        table.add_row(
            server["ip"], server["hostname"], last_seen, sources, str(websites)
        )

    console.print(table)


def version_callback(value: bool):
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        help="Show the application's version and exit.",
        callback=version_callback,
        is_eager=True,
    )
):
    """Application description and docs."""
    pass
