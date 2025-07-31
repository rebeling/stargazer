# src/cosmonaut/cli/web.py
import typer
from rich.console import Console
from rich.table import Table
import json
import csv
from rich.progress import track
from concurrent.futures import ThreadPoolExecutor

from cosmonaut.ssh.client import connect_ssh
from cosmonaut.storage import record_server
from cosmonaut.web.utils import get_websites, check_domain

# Create the Typer app for web commands
app = typer.Typer(help="🌐 Discover websites hosted on a server")

# Create a console for rich output
console = Console()


@app.command("list")
def list_websites(
    target: str = typer.Argument(..., help="user@host"),
    port: int = typer.Option(22, "--port", "-p"),
    key: str = typer.Option(None, "--key", "-k"),
    password: bool = typer.Option(False, "--password", "-P"),
):
    """
    List websites registered on the server.
    Tries to find:
    - Nginx/Apache virtual hosts
    - Running web processes
    - Open ports (80, 443)
    - SSL certificate domains
    """
    if "@" not in target:
        typer.secho("❌ Format: user@host", fg=typer.colors.RED)
        raise typer.Exit(1)

    user, host = target.split("@", 1)

    pwd = None
    if password:
        pwd = typer.prompt("Password", hide_input=True)

    client = connect_ssh(
        host=host,
        user=user,
        port=port,
        key_file=key,
        password=pwd,
    )
    if not client:
        raise typer.Exit(1)

    console.print(f"🔍 Finding websites on [bold]{host}[/bold]...\n")

    sites = get_websites(client)
    client.close()

    if not sites:
        console.print("📭 No websites found or no access to config files.")
        return

    table = Table(
        "Service", "Config", "Details", "Document Root", title="🌐 Websites & Services"
    )
    for site in sites:
        table.add_row(
            site["service"], site["config"], site["details"], site.get("root", "N/A")
        )

    console.print(table)


@app.command("check-from-server")
def check_websites_from_server(
    target: str = typer.Argument(..., help="user@host"),
    port: int = typer.Option(22, "--port", "-p"),
    key: str = typer.Option(None, "--key", "-k"),
    password: bool = typer.Option(False, "--password", "-P"),
):
    """
    Check if hosted websites are reachable via HTTP/HTTPS.
    Uses curl to test each domain.
    """
    console = Console()

    if "@" not in target:
        typer.secho("❌ Format: user@host", fg=typer.colors.RED)
        raise typer.Exit(1)

    user, host = target.split("@", 1)

    pwd = typer.prompt("Password", hide_input=True) if password else None

    client = connect_ssh(host=host, user=user, port=port, key_file=key, password=pwd)
    if not client:
        raise typer.Exit(1)

    console.print(f"📡 Testing website reachability on [bold]{host}[/bold]...\n")

    def run(cmd):
        try:
            _, stdout, _ = client.exec_command(cmd)
            return stdout.read().decode().strip()
        except Exception:
            return ""

    # Reuse domain extraction
    domains = set()

    # Apache
    apache_sites = run("ls /etc/apache2/sites-enabled/ 2>/dev/null || echo")
    if apache_sites.strip():
        for site in apache_sites.strip().splitlines():
            config = run(
                f"grep -E 'ServerName|ServerAlias' '/etc/apache2/sites-enabled/{site}' | grep -v '#'"
            )
            for line in config.splitlines():
                for word in line.split():
                    if word not in ("ServerName", "ServerAlias") and "." in word:
                        domains.add(word.strip().rstrip(";"))

    # Nginx
    nginx_sites = run("ls /etc/nginx/sites-enabled/ 2>/dev/null || echo")
    if nginx_sites.strip():
        for site in nginx_sites.strip().splitlines():
            config = run(
                f"grep 'server_name' '/etc/nginx/sites-enabled/{site}' | grep -v '#'"
            )
            for line in config.splitlines():
                for word in line.replace("server_name", "").replace(";", "").split():
                    if "." in word:
                        domains.add(word)

    if not domains:
        console.print("📭 No domains to check.")
        client.close()
        return

    table = Table(
        "Domain",
        "HTTP",
        "HTTPS",
        "Status",
        "Redirect To",
        title="📡 Website Reachability",
    )
    for domain in track(sorted(domains), description="Checking domains on server..."):
        http_redirect_to = "N/A"
        https_redirect_to = "N/A"

        # Check HTTP
        http_code_raw = run(
            f"curl -s -o /dev/null -w '%{{http_code}}' -m 5 http://{domain} -H 'Host: {domain}'"
        )
        http_code = int(http_code_raw) if http_code_raw.isdigit() else 0
        http_details = f"❌ {http_code}"
        http_status = "Down"
        if 200 <= http_code < 300:
            http_details = f"✅ {http_code}"
            http_status = "Up"
        elif 300 <= http_code < 400:
            location = run(
                f"curl -s -I -L -m 5 http://{domain} -H 'Host: {domain}' | grep -i Location | cut -d' ' -f2-"
            ).strip()
            http_details = f"↪ {http_code}"
            http_status = "Redirect"
            http_redirect_to = location

        # Check HTTPS
        https_code_raw = run(
            f"curl -s -o /dev/null -w '%{{http_code}}' -m 5 https://{domain} -H 'Host: {domain}'"
        )
        https_code = int(https_code_raw) if https_code_raw.isdigit() else 0
        https_details = f"❌ {https_code}"
        https_status = "Down"
        if 200 <= https_code < 300:
            https_details = f"✅ {https_code}"
            https_status = "Up"
        elif 300 <= https_code < 400:
            location = run(
                f"curl -s -I -L -m 5 https://{domain} -H 'Host: {domain}' | grep -i Location | cut -d' ' -f2-"
            ).strip()
            https_details = f"↪ {https_code}"
            https_status = "Redirect"
            https_redirect_to = location

        status = "Down"
        redirect_info = "N/A"

        if https_status in ["Up", "Redirect"]:
            status = "✅ HTTPS"
            if https_redirect_to != "N/A":
                redirect_info = https_redirect_to
            if http_status in ["Up", "Redirect"]:
                status += " & HTTP"
                if http_redirect_to != "N/A" and redirect_info == "N/A":
                    redirect_info = http_redirect_to
        elif http_status in ["Up", "Redirect"]:
            status = "✅ HTTP-only"
            if http_redirect_to != "N/A":
                redirect_info = http_redirect_to

        table.add_row(domain, http_details, https_details, status, redirect_info)

    console.print(table)

    if domains:
        record_server(
            ip=host,
            # hostname=run("hostname") or "unknown",
            websites=list(domains),
            source="web-discovery",
        )
        console.print(f"💾 {len(domains)} domains saved to inventory")

    client.close()


@app.command("check")
def check_websites_from_file(
    target: str = typer.Argument(
        None, help="The IP or user@host to check websites for."
    ),
    csv_output: bool = typer.Option(False, "--csv", help="Save output to a CSV file."),
):
    """
    Check if hosted websites are reachable via HTTP/HTTPS using the local servers.json file.
    Uses curl to test each domain.
    """
    console = Console()

    try:
        with open("data/servers.json", "r") as f:
            servers = json.load(f)
    except FileNotFoundError:
        console.print("❌ [bold]data/servers.json[/bold] not found.")
        raise typer.Exit(1)

    websites_to_check = []
    ip_to_check = None
    if target:
        if "@" in target:
            _, ip_to_check = target.split("@", 1)
        else:
            ip_to_check = target

    if ip_to_check:
        if ip_to_check in servers:
            websites_to_check.extend(servers[ip_to_check].get("websites", []))
        else:
            console.print(
                f"❌ IP [bold]{ip_to_check}[/bold] not found in [bold]data/servers.json[/bold]."
            )
            raise typer.Exit(1)
    else:
        for server_ip, data in servers.items():
            websites_to_check.extend(data.get("websites", []))

    if not websites_to_check:
        console.print("📭 No websites to check.")
        return

    unique_websites = sorted(list(set(websites_to_check)))

    results = []
    # for x in unique_websites:
    #     results.append(check_domain(x))

    with ThreadPoolExecutor() as executor:
        results = list(
            track(
                executor.map(check_domain, unique_websites),
                total=len(unique_websites),
                description="Checking websites",
            )
        )

    if csv_output:
        with open("websites_check.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Domain", "HTTP", "HTTPS", "Status", "Redirect To"])
            writer.writerows(results)
        console.print("✅ Results saved to [bold]websites_check.csv[/bold]")
    else:
        table = Table(
            "Domain",
            "HTTP",
            "HTTPS",
            "Status",
            "Redirect To",
            title="📡 Website Reachability",
        )
        for result in results:
            table.add_row(*result)
        console.print(table)


@app.command("domains")
def list_domains(
    target: str = typer.Argument(..., help="user@host"),
    port: int = typer.Option(22, "--port", "-p"),
    key: str = typer.Option(None, "--key", "-k"),
    password: bool = typer.Option(False, "--password", "-P"),
):
    """
    List only the domain names hosted on the server.
    Extracts ServerName and ServerAlias from Apache/Nginx configs.
    """
    console = Console()

    if "@" not in target:
        typer.secho("❌ Format: user@host", fg=typer.colors.RED)
        raise typer.Exit(1)

    user, host = target.split("@", 1)

    pwd = typer.prompt("Password", hide_input=True) if password else None

    client = connect_ssh(host=host, user=user, port=port, key_file=key, password=pwd)
    if not client:
        raise typer.Exit(1)

    console.print(f"🔍 Extracting domains from [bold]{host}[/bold]...\n")

    def run(cmd):
        try:
            _, stdout, _ = client.exec_command(cmd)
            return stdout.read().decode().strip()
        except Exception:
            return ""

    domains = set()

    # Apache
    apache_sites = run("ls /etc/apache2/sites-enabled/ 2>/dev/null || echo")
    if apache_sites.strip():
        for site in track(
            apache_sites.strip().splitlines(), description="Checking Apache sites..."
        ):
            if not site.strip():
                continue
            config = run(
                f"grep -E 'ServerName|ServerAlias' '/etc/apache2/sites-enabled/{site}' | grep -v '#'"
            )
            for line in config.splitlines():
                for word in line.split():
                    if word not in ("ServerName", "ServerAlias") and "." in word:
                        domains.add(word.strip().rstrip(";"))

    # Nginx
    nginx_sites = run("ls /etc/nginx/sites-enabled/ 2>/dev/null || echo")
    if nginx_sites.strip():
        for site in track(
            nginx_sites.strip().splitlines(), description="Checking Nginx sites..."
        ):
            if not site.strip():
                continue
            config = run(
                f"grep 'server_name' '/etc/nginx/sites-enabled/{site}' | grep -v '#'"
            )
            for line in config.splitlines():
                for word in line.replace("server_name", "").replace(";", "").split():
                    if "." in word:
                        domains.add(word)

    client.close()

    if not domains:
        console.print("📭 No domains found.")
        return

    console.print("🌐 Domains hosted on this server:")
    for domain in sorted(domains):
        console.print(f"  - [bold]{domain}[/bold]")

    console.print(f"\n✅ Total: {len(domains)} domains")

    if domains:
        record_server(
            ip=host,
            # hostname=run("hostname") or "unknown",
            websites=list(domains),
            source="web-discovery",
        )
        console.print(f"💾 {len(domains)} domains saved to inventory")
