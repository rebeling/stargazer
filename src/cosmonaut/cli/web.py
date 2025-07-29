# src/cosmonaut/cli/web.py
import typer
from rich.console import Console
from rich.table import Table

from cosmonaut.storage import record_server

# Create the Typer app for web commands
app = typer.Typer(help="🌐 Discover websites hosted on a server")

# Create a console for rich output
console = Console()


def get_websites(client) -> list:
    """Collect websites from config files, processes, and certs."""

    def run(cmd):
        try:
            _, stdout, _ = client.exec_command(cmd)
            return stdout.read().decode().strip()
        except Exception:
            return ""

    websites = []

    # 1. Check for Nginx virtual hosts
    nginx_sites = run("ls /etc/nginx/sites-enabled/ 2>/dev/null || echo")
    if nginx_sites.strip():
        for site in nginx_sites.strip().splitlines():
            if site.strip():
                domains = run(
                    f"grep -E 'server_name|listen' '/etc/nginx/sites-enabled/{site}' "
                    "| grep -v '#' | tr ';' ' ' | tr '{{}}' ' '"
                )
                websites.append(
                    {
                        "service": "nginx",
                        "config": site.strip(),
                        "details": domains.strip() or "configured",
                    }
                )

    # 2. Check for Apache virtual hosts
    apache_sites = run("ls /etc/apache2/sites-enabled/ 2>/dev/null || echo")
    if apache_sites.strip():
        for site in apache_sites.strip().splitlines():
            if site.strip():
                # Inside the Apache block
                domains = run(
                    f"grep -E 'ServerName|ServerAlias' '/etc/apache2/sites-enabled/{site}' "
                    "| grep -v '#'"
                )
                for line in domains.splitlines():
                    for part in line.split():
                        if part.startswith("ServerName") or part.startswith(
                            "ServerAlias"
                        ):
                            continue
                        if "." in part:  # looks like a domain
                            websites.append(
                                {
                                    "service": "website",
                                    "config": "apache",
                                    "details": part.strip(),
                                }
                            )

    # 3. Check running web server processes
    processes = run(
        "ps aux | grep -E 'nginx|apache|httpd|lighttpd|node' | grep -v grep"
    )
    if "nginx" in processes:
        websites.append({"service": "process", "config": "nginx", "details": "running"})
    if any(s in processes for s in ("apache", "httpd")):
        websites.append(
            {"service": "process", "config": "apache", "details": "running"}
        )
    if "node" in processes and ("80" in processes or "443" in processes):
        websites.append(
            {"service": "process", "config": "node.js", "details": "possible web app"}
        )

    # 4. Check open ports (80, 443, 8080)
    ports = run("ss -tuln | grep -E ':80 |:443 |:8080'")
    if ports.strip():
        first_line = ports.strip().splitlines()[0]
        websites.append({"service": "port", "config": "open", "details": first_line})

    # 5. Check SSL certificates for domains
    cert_domains = run(
        "find /etc/ssl -name '*.pem' -o -name '*.crt' 2>/dev/null | "
        "head -3 | xargs -I {} openssl x509 -noout -subject -in {} 2>/dev/null | "
        "grep -o 'CN=[^,]*'"
    )
    for line in cert_domains.splitlines():
        if "CN=" in line:
            domain = line.split("=", 1)[1]
            websites.append(
                {"service": "ssl", "config": "certificate", "details": domain}
            )

    return websites


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
    from cosmonaut.ssh.client import connect_ssh

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

    table = Table("Service", "Config", "Details", title="🌐 Websites & Services")
    for site in sites:
        table.add_row(site["service"], site["config"], site["details"])

    console.print(table)


@app.command("check")
def check_websites(
    target: str = typer.Argument(..., help="user@host"),
    port: int = typer.Option(22, "--port", "-p"),
    key: str = typer.Option(None, "--key", "-k"),
    password: bool = typer.Option(False, "--password", "-P"),
):
    """
    Check if hosted websites are reachable via HTTP/HTTPS.
    Uses curl to test each domain.
    """
    from cosmonaut.ssh.client import connect_ssh
    from rich.console import Console
    from rich.table import Table

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

    table = Table("Domain", "HTTP", "HTTPS", "Status", title="📡 Website Reachability")
    for domain in sorted(domains):
        http = run(f"curl -sk -m 5 http://{domain} -H 'Host: {domain}' && echo '200'")
        https = run(f"curl -sk -m 5 https://{domain} -H 'Host: {domain}' && echo '200'")

        http_ok = "✅" if "200" in http or len(http) > 10 else "❌"
        https_ok = "✅" if "200" in https or len(https) > 10 else "❌"

        status = (
            "Mixed"
            if http_ok == "✅" and https_ok == "❌"
            else "HTTPS-only"
            if https_ok == "✅"
            else "Down"
        )
        status = "✅ Up" if https_ok == "✅" and http_ok == "✅" else status

        table.add_row(domain, http_ok, https_ok, status)

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
    from cosmonaut.ssh.client import connect_ssh
    from rich.console import Console

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
        for site in apache_sites.strip().splitlines():
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
        for site in nginx_sites.strip().splitlines():
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
