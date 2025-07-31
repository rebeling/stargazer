from typing import Tuple
from typing import List, Dict
import subprocess

# src/cosmonaut/cli/web.py
from rich.console import Console
from rich.progress import track


# Create a console for rich output
console = Console()


def run(client, cmd: str) -> str:
    try:
        _, stdout, _ = client.exec_command(cmd)
        return stdout.read().decode().strip()
    except Exception:
        return ""


def parse_nginx_sites(client) -> List[Dict]:
    results = []
    sites = run(client, "ls /etc/nginx/sites-enabled/ 2>/dev/null || echo").splitlines()

    for site in track(sites, description="Checking Nginx sites..."):
        site = site.strip()
        if not site:
            continue
        config = run(client, f"cat /etc/nginx/sites-enabled/{site}")
        domains = [
            line.split()[1].rstrip(";")
            for line in config.splitlines()
            if "server_name" in line and "#" not in line
        ]
        roots = [
            line.split()[1].rstrip(";")
            for line in config.splitlines()
            if "root" in line and "#" not in line
        ]
        results.append({
            "service": "nginx",
            "config": site,
            "details": ", ".join(domains) or "configured",
            "root": roots[0] if roots else "N/A",
        })
    return results


def parse_apache_sites(client) -> List[Dict]:
    results = []
    sites = run(client, "ls /etc/apache2/sites-enabled/ 2>/dev/null || echo").splitlines()

    for site in track(sites, description="Checking Apache sites..."):
        site = site.strip()
        if not site:
            continue
        config = run(client, f"cat /etc/apache2/sites-enabled/{site}")
        domains = [
            word
            for line in config.splitlines()
            if "ServerName" in line or "ServerAlias" in line
            for word in line.split()
            if word not in ("ServerName", "ServerAlias") and "." in word
        ]
        roots = [
            line.split()[1]
            for line in config.splitlines()
            if "DocumentRoot" in line and "#" not in line
        ]
        for domain in domains:
            results.append({
                "service": "apache",
                "config": site,
                "details": domain,
                "root": roots[0] if roots else "N/A",
            })
    return results


def detect_web_processes(client) -> List[Dict]:
    results = []
    processes = run(client, "ps aux | grep -E 'nginx|apache|httpd|lighttpd|node' | grep -v grep")

    if "nginx" in processes:
        results.append({"service": "process", "config": "nginx", "details": "running", "root": "N/A"})
    if any(p in processes for p in ("apache", "httpd")):
        results.append({"service": "process", "config": "apache", "details": "running", "root": "N/A"})
    if "node" in processes and ("80" in processes or "443" in processes):
        results.append({"service": "process", "config": "node.js", "details": "possible web app", "root": "N/A"})
    return results


def detect_open_ports(client) -> List[Dict]:
    ports = run(client, "ss -tuln | grep -E ':80 |:443 |:8080'")
    if ports:
        return [{"service": "port", "config": "open", "details": ports.splitlines()[0], "root": "N/A"}]
    return []


def parse_ssl_certs(client) -> List[Dict]:
    results = []
    certs = run(
        client,
        "find /etc/ssl -name '*.pem' -o -name '*.crt' 2>/dev/null | "
        "head -3 | xargs -I {} openssl x509 -noout -subject -in {} 2>/dev/null | "
        "grep -o 'CN=[^,]*'"
    )
    for line in certs.splitlines():
        if "CN=" in line:
            results.append({
                "service": "ssl",
                "config": "certificate",
                "details": line.split("=", 1)[1],
                "root": "N/A",
            })
    return results


def get_status_and_redirect(domain: str, protocol: str) -> Tuple[str, str]:
    base_url = f"{protocol}://{domain}"
    status = "❌ Down"
    redirect_to = "N/A"

    try:
        result = subprocess.run(
            f"curl -s -o /dev/null -w '%{{http_code}}' -m 5 {base_url}",
            shell=True, capture_output=True, text=True
        )
        code = int(result.stdout) if result.stdout.isdigit() else 0

        if 200 <= code < 300:
            status = f"✅ {code}"
        elif 300 <= code < 400:
            status = f"↪ {code}"
            location_result = subprocess.run(
                f"curl -s -I -L -m 5 {base_url} | grep -i '^location:' | tail -1",
                shell=True, capture_output=True, text=True
            )
            if location_result.stdout:
                redirect_to = location_result.stdout.strip().split(": ", 1)[-1]
    except Exception as e:
        console.print(f"[red]{protocol.upper()} check failed for {domain}: {e}[/red]")

    return status, redirect_to


def get_websites(client):
    """Collect websites from config files, processes, and certs."""
    websites = []
    websites.extend(parse_nginx_sites(client))
    websites.extend(parse_apache_sites(client))
    websites.extend(detect_web_processes(client))
    websites.extend(detect_open_ports(client))
    websites.extend(parse_ssl_certs(client))
    return websites


def check_domain(domain: str):
    domain = domain[2:] if domain.startswith("*.") else domain

    http_status, http_redirect_to = get_status_and_redirect(domain, "http")
    https_status, https_redirect_to = get_status_and_redirect(domain, "https")

    overall_status = "❌ Down"
    redirect_info = "N/A"

    has_https = https_status.startswith(("✅", "↪"))
    has_http = http_status.startswith(("✅", "↪"))

    if has_https:
        overall_status = "✅ HTTPS"
        redirect_info = https_redirect_to or "N/A"
        if has_http:
            overall_status += " & HTTP"
            if http_redirect_to != "N/A" and redirect_info == "N/A":
                redirect_info = http_redirect_to
    elif has_http:
        overall_status = "✅ HTTP-only"
        redirect_info = http_redirect_to

    return domain, http_status, https_status, overall_status, redirect_info
