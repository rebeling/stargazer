# src/cosmonaut/cli/map.py
import typer
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table

from cosmonaut.discovery.hostname import get_hostname_via_ssh
from cosmonaut.discovery.network import scan_network
from cosmonaut.discovery.dependencies import detect_dependencies
from cosmonaut.rendering.graph import generate_dot, generate_json
from cosmonaut.storage import record_server, load_servers


app = typer.Typer(help="🌌 Map your digital universe")

console = Console()


@app.command("topology")
def map_topology(
    network: str = typer.Argument(..., help="CIDR, e.g. 192.168.1.0/24"),
    user: str = typer.Option(None, "--user", "-u", help="SSH user for enrichment"),
    key: str = typer.Option(None, "--key", "-k", help="SSH key file"),
    password: bool = typer.Option(False, "--password", "-P", help="Use password auth"),
):
    """Discover live hosts. Optionally enrich with SSH data."""
    hosts = scan_network(network)
    if not hosts:
        console.print("📭 No hosts found.")
        return

    table = Table("IP", "Hostname", "Status")
    for h in hosts:
        table.add_row(h["ip"], h["hostname"], h["status"])

    console.print(table)

    # Enrich via SSH if requested
    if user:
        console.print("\n[bold]🔐 Connecting via SSH to enrich data...[/bold]")
        for h in hosts:
            name = get_hostname_via_ssh(h["ip"], user, key, password)
            if name:
                h["hostname"] = name
                record_server(ip=h["ip"], hostname=name, source="ssh-enriched")
                console.print(f"✅ {h['ip']} → {name}")
            else:
                # Keep DNS name
                record_server(ip=h["ip"], hostname=h["hostname"], source="network-scan")
                console.print(f"✅ {h['ip']} → {h['hostname']}")

    console.print(f"\n💾 Recorded {len(hosts)} servers in inventory")


@app.command("dependencies")
def map_dependencies():
    """Show likely service dependencies."""
    servers = list(load_servers().values())
    if not servers:
        console.print("📭 No servers in inventory. Run `cosmonaut map topology` first.")
        return

    console.print("\n[bold magenta]🔗 Service Dependencies[/bold magenta]\n")

    deps = detect_dependencies(servers)

    table = Table("Source", "Depends On")
    for src, dst in deps:
        table.add_row(src, dst)
    console.print(table)


@app.command("graph")
def graph(
    output: Path = typer.Option(None, "--output", "-o", help="Save to .dot or .json"),
    format: str = typer.Option("dot", "--format", "-f", help="dot or json"),
):
    """Generate a graph of your infrastructure."""
    servers = list(load_servers().values())
    if not servers:
        console.print("📭 No data. Discover servers first.")
        return

    deps = detect_dependencies(servers)

    if format == "json" or (output and output.suffix == ".json"):
        data = generate_json(servers, deps)
        content = json.dumps(data, indent=2)
        ext = ".json"
    else:
        content = generate_dot(servers, deps)
        ext = ".dot"

    if output:
        output = output.with_suffix(ext)
        output.write_text(content)
        console.print(f"📊 Graph saved to [bold]{output}[/bold]")
    else:
        print(content)
