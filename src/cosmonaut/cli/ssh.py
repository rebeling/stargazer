# src/cosmonaut/cli/ssh.py
import typer
from pathlib import Path
import ipaddress

from cosmonaut.storage import record_server

app = typer.Typer(help="🔐 SSH commands")


@app.command("connect")
def connect(
    target: str = typer.Argument(..., help="User@Host"),
):
    print(f"✅ SSH: Connecting to {target}")


@app.command("specs")
def specs(
    target: str = typer.Argument(..., help="user@host"),
    port: int = typer.Option(22, "--port", "-p"),
    key: Path = typer.Option(None, "--key", "-k", exists=True, dir_okay=False),
    password: bool = typer.Option(False, "--password", "-P"),
):
    """
    Connect to a server and show real system specifications.
    """
    from rich.console import Console
    from cosmonaut.ssh.client import connect_ssh
    from cosmonaut.ssh.specs import get_remote_specs
    from cosmonaut.rendering.console import render_specs

    console = Console()

    if "@" not in target:
        typer.secho("❌ Usage: user@host", fg=typer.colors.RED)
        raise typer.Exit(1)

    user, host = target.split("@", 1)

    # Handle auth
    pwd = None
    if password:
        pwd = typer.prompt("Password", hide_input=True)

    console.print(f"🔐 Connecting to [bold]{user}@{host}[/bold]...")

    client = connect_ssh(
        host=host,
        user=user,
        port=port,
        key_file=str(key) if key else None,
        password=pwd,
    )

    if not client:
        typer.secho("❌ Failed to connect", fg=typer.colors.RED)
        raise typer.Exit(1)

    console.print("✅ Connected. Gathering specs...")

    specs_data = get_remote_specs(client)

    # ----------------------------------------------------------------------------------
    # ✅ RIGHT HERE: After getting specs_data, before closing client
    # ----------------------------------------------------------------------------------
    try:
        # Only record if 'host' is an IP address
        ipaddress.ip_address(host)
        # Record to data/servers.json
        record_server(
            ip=host, hostname=specs_data.get("Hostname", "unknown"), specs=specs_data
        )
        console.print(f"💾 Server [cyan]{host}[/cyan] recorded in data/servers.json")
    except ipaddress.AddressValueError:
        # host is a domain name (e.g., myserver.com), not an IP
        console.print(
            f"💡 Host [yellow]{host}[/yellow] is not an IP — not storing in inventory"
        )
    # ----------------------------------------------------------------------------------
    # End of recording
    # ----------------------------------------------------------------------------------

    client.close()

    render_specs(target=target, specs=specs_data)


# Test: python -m cosmonaut.cli.ssh
if __name__ == "__main__":
    app()
