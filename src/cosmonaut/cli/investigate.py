# src/cosmonaut/cli/investigate.py
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

app = typer.Typer(
    help="🔍 Deep investigation of server state", rich_markup_mode="markdown"
)

console = Console()


@app.command("processes")
def investigate_processes(
    target: str = typer.Argument(..., help="user@host"),
    top: int = typer.Option(10, "--top", "-n", help="Show top N processes"),
    user_filter: str = typer.Option(None, "--user", "-u", help="Filter by user"),
):
    """List top running processes by memory usage."""
    from cosmonaut.ssh.client import connect_ssh

    if "@" not in target:
        typer.secho("❌ Format: user@host", fg=typer.colors.RED)
        raise typer.Exit(1)

    user, host = target.split("@", 1)
    client = connect_ssh(host=host, user=user)
    if not client:
        raise typer.Exit(1)

    console.print(Panel(f"🧩 Top {top} Processes on {host}", border_style="blue"))

    # Build ps command
    ps_cmd = "ps aux --sort=-%mem"
    if user_filter:
        ps_cmd += f" | grep {user_filter}"
    ps_cmd += f" | head -{top + 1}"

    _, stdout, _ = client.exec_command(ps_cmd)
    output = stdout.read().decode().strip()

    if not output:
        console.print("📭 No processes found.")
        client.close()
        return

    lines = output.splitlines()
    if len(lines) == 1:
        console.print("📭 No processes match criteria.")
        client.close()
        return

    # Parse header and rows
    headers = lines[0].split()
    data_rows = [line.split(None, 10) for line in lines[1:]]

    table = Table(*headers[:10], title=f"Top {len(data_rows)} Processes")
    for row in data_rows:
        table.add_row(*[cell[:40] + "..." if len(cell) > 40 else cell for cell in row])

    console.print(table)
    client.close()


@app.command("services")
def investigate_services(
    target: str = typer.Argument(..., help="user@host"),
):
    """List active systemd services."""
    from cosmonaut.ssh.client import connect_ssh

    user, host = target.split("@", 1) if "@" in target else (None, target)
    if not user:
        user = typer.prompt("Username")

    client = connect_ssh(host=host, user=user)
    if not client:
        raise typer.Exit(1)

    console.print(Panel(f"⚙️ Active Services on {host}", border_style="green"))

    _, stdout, _ = client.exec_command(
        "systemctl list-units --type=service --state=active --no-pager | head -20"
    )
    services = stdout.read().decode().strip()

    if not services:
        console.print("📭 No active services found.")
    else:
        console.print(services)
    client.close()


@app.command("cron")
def investigate_cron(
    target: str = typer.Argument(..., help="user@host"),
    show_commands: bool = typer.Option(
        False, "--show-commands", "-c", help="Show full command details"
    ),
):
    """List all cron jobs in a clean table."""
    from cosmonaut.ssh.client import connect_ssh

    if "@" not in target:
        typer.secho("❌ Format: user@host", fg=typer.colors.RED)
        raise typer.Exit(1)

    user, host = target.split("@", 1)
    client = connect_ssh(host=host, user=user)
    if not client:
        raise typer.Exit(1)

    console.print(Panel("⏰ Cron Jobs", border_style="yellow"))

    table = Table("User", "Schedule", "Command", "Type", title="Scheduled Tasks")

    def run(cmd):
        return client.exec_command(cmd)[1].read().decode().strip()

    # Helper: parse crontab lines
    def add_jobs(jobs: str, user: str, job_type: str):
        for line in jobs.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line == "no crontab":
                continue
            if line.startswith("SHELL=") or line.startswith("PATH="):
                continue

            # Try to split into time + command
            parts = line.split(None, 5)
            if len(parts) >= 6:
                timing = " ".join(parts[:5])
                command = parts[5].strip()
                if not show_commands:
                    command = (command[:50] + "...") if len(command) > 50 else command
                table.add_row(user, timing, command, job_type)
            else:
                table.add_row(user, "???", line, job_type)

    # 1. Root/system cron (via sudo)
    system_cron = run("sudo crontab -l 2>/dev/null || echo 'no system cron'")
    if "no system cron" not in system_cron:
        add_jobs(system_cron, "root", "system")

    # 2. Current user cron
    user_cron = run("crontab -l 2>/dev/null || echo 'no user cron'")
    if "no user cron" not in user_cron:
        add_jobs(user_cron, user, "user")

    # 3. /etc/cron.d/ jobs
    cron_d_files = run("ls /etc/cron.d/ 2>/dev/null || echo")
    if cron_d_files.strip():
        for fname in cron_d_files.strip().splitlines():
            content = run(f"cat /etc/cron.d/{fname} 2>/dev/null || true")
            for line in content.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split(None, 5)
                if len(parts) >= 6:
                    timing = " ".join(parts[:5])
                    command = parts[5].strip()
                    if not show_commands:
                        command = (
                            (command[:50] + "...") if len(command) > 50 else command
                        )
                    table.add_row("root", timing, command, f"/etc/cron.d/{fname}")

    client.close()

    if not table.rows:
        console.print("📭 No cron jobs found.")
    else:
        console.print(table)


@app.command("databases")
def investigate_databases(
    target: str = typer.Argument(..., help="user@host"),
):
    """Check for all common databases (running or configured)."""
    from cosmonaut.ssh.client import connect_ssh

    if "@" not in target:
        typer.secho("❌ Format: user@host", fg=typer.colors.RED)
        raise typer.Exit(1)

    user, host = target.split("@", 1)
    client = connect_ssh(host=host, user=user)
    if not client:
        raise typer.Exit(1)

    console.print(Panel("🧮 Databases", border_style="red"))

    table = Table("Database", "Status", "Port", "Version", "Data Dir")

    def run(cmd):
        try:
            _, stdout, _ = client.exec_command(cmd)
            return stdout.read().decode().strip()
        except:
            return ""

    def is_listening(port):
        return "LISTEN" in run(f"ss -tuln | grep ':{port} '")

    def get_version(cmd, grep_str=None):
        out = run(cmd)
        if grep_str:
            out = run(f"echo '{out}' | grep -i '{grep_str}'")
        return (out or "unknown")[:30]

    # Define checks
    db_checks = [
        # SQL
        ("MySQL", 3306, "mysql --version", "/var/lib/mysql"),
        ("MariaDB", 3306, "mariadb --version", "/var/lib/mysql"),
        ("PostgreSQL", 5432, "psql --version", "/var/lib/postgresql"),
        ("SQLite", None, "", "/var/lib/sqlite"),
        # NoSQL
        ("Redis", 6379, "redis-server --version", "/var/lib/redis"),
        ("MongoDB", 27017, "mongod --version", "/var/lib/mongodb"),
        ("CouchDB", 5984, "couchdb -V", "/var/lib/couchdb"),
        ("Elasticsearch", 9200, "elasticsearch --version", "/var/lib/elasticsearch"),
        ("etcd", 2379, "etcd --version", "/var/lib/etcd"),
        # In-memory / config
        ("Memcached", 11211, "memcached -h | head -1", "N/A"),
    ]

    for name, port, version_cmd, data_dir in db_checks:
        if port:
            status = "✅ Running" if is_listening(port) else "🔸 Not listening"
        else:
            # SQLite: check for .db files
            has_dbs = "found" in run(
                "find / -name '*.sqlite' -o -name '*.db' 2>/dev/null | head -1"
            )
            status = "✅ In use" if has_dbs else "🔸 No DBs found"

        version = get_version(version_cmd) if version_cmd else "N/A"
        dir_status = "✅" if run(f"test -d {data_dir} && echo yes") == "yes" else "❌"

        table.add_row(name, status, str(port) if port else "file", version, dir_status)

    console.print(table)
    client.close()


@app.command("runtimes")
def investigate_runtimes(
    target: str = typer.Argument(..., help="user@host"),
):
    """Check all installed runtimes, frameworks, and containers."""
    from cosmonaut.ssh.client import connect_ssh

    if "@" not in target:
        typer.secho("❌ Format: user@host", fg=typer.colors.RED)
        raise typer.Exit(1)

    user, host = target.split("@", 1)
    client = connect_ssh(host=host, user=user)
    if not client:
        raise typer.Exit(1)

    console.print(Panel("🧩 Runtimes & Frameworks", border_style="magenta"))

    table = Table("Runtime", "Status", "Version", "Processes", "Config Files")

    def run(cmd):
        try:
            _, stdout, _ = client.exec_command(cmd)
            return stdout.read().decode().strip()
        except:
            return ""

    def count_proc(pattern):
        return run(f"ps aux | grep -v grep | grep -c '{pattern}'") or "0"

    def find_conf(pattern):
        files = run(
            f"find /etc /opt /home -name '{pattern}' -type f 2>/dev/null | head -3 | wc -l"
        )
        return "✅" if int(files) > 0 else "❌"

    # Language Runtimes
    for name, which, version_cmd, proc_pattern, conf in [
        ("Python", "python3", "python3 --version", "python", "*.py"),
        ("PHP", "php", "php --version | head -n1", "php", "*.php"),
        ("Java", "java", "java -version 2>&1 | head -n1", "java", "*.jar"),
        ("Node.js", "node", "node --version", "node", "package.json"),
        ("Ruby", "ruby", "ruby --version", "ruby", "Gemfile"),
        ("Go", "go", "go version", "go", "go.mod"),
        ("Deno", "deno", "deno --version", "deno", "deno.json"),
        ("Bun", "bun", "bun --version", "bun", "bun.lockb"),
        (".NET", "dotnet", "dotnet --version", "dotnet", "*.csproj"),
    ]:
        bin_path = run(f"which {which}")
        version = run(version_cmd) if bin_path else "N/A"
        procs = count_proc(proc_pattern)
        confs = find_conf(conf)
        status = "✅" if bin_path else "❌"
        table.add_row(name, status, version[:30], procs, confs)

    # Container Runtimes
    for name, which, version_cmd, proc_pattern, conf in [
        ("Docker", "docker", "docker --version", "dockerd", "docker-compose.yml"),
        ("Podman", "podman", "podman --version", "podman", "Containerfile"),
        ("rkt", "rkt", "rkt version", "rkt", "aci"),
    ]:
        bin_path = run(f"which {which}")
        version = run(version_cmd) if bin_path else "N/A"
        procs = count_proc(proc_pattern)
        confs = find_conf(conf)
        status = "✅" if bin_path else "❌"
        table.add_row(name, status, version[:30], procs, confs)

    # Kubernetes (lightweight)
    k3s = run("which k3s || which k3s-server")
    k3s_ver = run("k3s --version") if k3s else "N/A"
    k3s_procs = count_proc("k3s")
    table.add_row("K3s", "✅" if k3s else "❌", k3s_ver[:30], k3s_procs, "k3s.yaml")

    microk8s = run("which microk8s.status")
    table.add_row(
        "microk8s", "✅" if microk8s else "❌", "N/A", count_proc("kubelet"), "microk8s"
    )

    console.print(table)
    client.close()


@app.command("security")
def investigate_security(
    target: str = typer.Argument(..., help="user@host"),
):
    """Check SSH authorized keys and sudo access."""
    from cosmonaut.ssh.client import connect_ssh

    user, host = target.split("@", 1)
    client = connect_ssh(host=host, user=user)
    if not client:
        raise typer.Exit(1)

    console.print(Panel("🔐 Security Audit", border_style="red"))

    def run(cmd):
        return client.exec_command(cmd)[1].read().decode().strip()

    # Authorized keys
    keys = run("cat ~/.ssh/authorized_keys 2>/dev/null | wc -l")
    console.print(f"🔑 {keys} SSH public keys installed")

    # Sudoers
    sudo = run("sudo -l")
    if "not allowed" in sudo:
        console.print("🚨 User has NO sudo access")
    else:
        console.print("✅ User has sudo access:")
        console.print(sudo)

    # Root login enabled?
    sshd = run("grep 'PermitRootLogin' /etc/ssh/sshd_config || echo 'not set'")
    console.print(f"🔧 PermitRootLogin: {sshd}")

    client.close()


@app.command("traffic")
def investigate_traffic(
    target: str = typer.Argument(..., help="user@host"),
):
    """Show recent outbound connections (DNS & IPs)."""
    from cosmonaut.ssh.client import connect_ssh

    user, host = target.split("@", 1)
    client = connect_ssh(host=host, user=user)
    if not client:
        raise typer.Exit(1)

    console.print("\n[bold blue]📡 Recent Outbound Traffic[/bold blue]")
    console.print("[dim]Top remote hosts this server connects to[/dim]\n")

    table = Table(
        "Protocol", "Remote Host", "Port", "Purpose", title="Outbound Connections"
    )

    def run(cmd):
        return client.exec_command(cmd)[1].read().decode().strip()

    # Extract recent outbound connections
    # Parse /proc/net/{tcp,udp} or use ss
    dns_queries = run("""
        grep -iE 'A |AAAA|query' /var/log/syslog /var/log/messages 2>/dev/null |
        grep -oE '[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}' |
        sort | uniq -c | sort -nr | head -10 || echo
    """)

    # Use ss to find established outbound connections
    connections = run(
        "ss -tuln state established | grep -v '127.0.0.1' | grep -E ':80 |:443 |:22 |:53 '"
    )

    seen = set()

    for line in connections.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            dest = parts[4]
            if ":" in dest:
                ip, port = dest.rsplit(":", 1)
                if (
                    ip in ("127.0.0.1", "::1")
                    or ip.startswith("192.168.")
                    or ip.startswith("10.")
                ):
                    continue  # skip private
                key = (ip, port)
                if key not in seen:
                    seen.add(key)
                    table.add_row("TCP", ip, port, "active session")

    # Add DNS-based guesses
    for line in dns_queries.splitlines():
        if " " in line and len(line.split()) >= 2:
            count, domain = line.strip().split(None, 1)
            domain = domain.strip("`'\"")
            if "google" in domain:
                purpose = "Google API"
            elif "aws" in domain or "amazonaws" in domain:
                purpose = "AWS"
            elif "github" in domain:
                purpose = "GitHub"
            else:
                purpose = "external service"
            table.add_row("DNS", domain, "53", purpose)

    if not table.rows:
        console.print("📭 No recent outbound traffic found.")

    console.print(table)
    client.close()


@app.command("connections")
def investigate_connections(
    target: str = typer.Argument(..., help="user@host"),
):
    """Show current network connections (inbound & outbound)."""
    from cosmonaut.ssh.client import connect_ssh

    user, host = target.split("@", 1)
    client = connect_ssh(host=host, user=user)
    if not client:
        raise typer.Exit(1)

    console.print("\n[bold green]🔁 Active Network Connections[/bold green]\n")

    table = Table("Proto", "Local", "Remote", "State", "Process")

    def run(cmd):
        return client.exec_command(cmd)[1].read().decode().strip()

    # ss -tup state established
    output = run("ss -tup state established 2>/dev/null || echo")
    for line in output.splitlines():
        if "Netid" in line or not line.strip():
            continue
        parts = line.split()
        if len(parts) < 5:
            continue
        proto = parts[0]
        local = parts[4]
        remote = parts[5] if len(parts) > 5 else "?"
        pid = "?"

        # Try to get process
        if len(parts) > 6 and "pid=" in parts[6]:
            pid = parts[6].split("pid=")[1].split(",")[0]

        table.add_row(proto, local, remote, "ESTABLISHED", pid)

    if not table.rows:
        console.print("📭 No active connections.")

    console.print(table)
    client.close()


@app.command("firewall")
def investigate_firewall(
    target: str = typer.Argument(..., help="user@host"),
):
    """Show firewall rules (iptables or nftables)."""
    from cosmonaut.ssh.client import connect_ssh
    from rich.panel import Panel

    user, host = target.split("@", 1)
    client = connect_ssh(host=host, user=user)
    if not client:
        raise typer.Exit(1)

    console.print("\n[bold yellow]🛡️ Firewall Configuration[/bold yellow]\n")

    def run(cmd):
        return client.exec_command(cmd)[1].read().decode().strip()

    # Check for iptables
    iptables = run("sudo iptables -L -n -v 2>/dev/null | head -20 || echo 'not found'")
    if "not found" not in iptables:
        console.print(Panel(iptables, title="iptables", border_style="yellow"))
    else:
        # Check nftables
        nft = run("sudo nft list ruleset 2>/dev/null || echo 'none'")
        if "none" not in nft:
            console.print(Panel(nft, title="nftables", border_style="yellow"))
        else:
            console.print("🟢 No firewall rules detected (or no sudo access)")

    client.close()
