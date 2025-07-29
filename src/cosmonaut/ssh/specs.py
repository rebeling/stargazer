# src/cosmonaut/ssh/specs.py
import ipaddress


def get_remote_specs(client):
    """Run remote commands and return system specs."""

    def run(cmd):
        try:
            _, stdout, _ = client.exec_command(cmd)
            return stdout.read().decode().strip()
        except Exception:
            return "N/A"

    # Detect language and get memory free (available)
    def get_memory_free():
        try:
            # Run `free -h` and read first line (header)
            _, stdout, _ = client.exec_command("free -h")
            lines = stdout.read().decode().strip().splitlines()
            if not lines:
                return "N/A"

            header = lines[0].lower()
            mem_line = None
            for line in lines[1:]:
                if line.startswith("Speicher:") or line.startswith("Mem:"):
                    mem_line = line
                    break

            if not mem_line:
                return "N/A"

            # Split header and find "verfügbar" or "available"
            header_parts = header.split()
            mem_parts = mem_line.split()

            # Look for "verfügbar" or "available" in headers
            available_idx = -1
            for i, col in enumerate(header_parts):
                if "verf" in col or "available" in col:
                    available_idx = i
                    break

            if available_idx == -1 or available_idx >= len(mem_parts):
                return "N/A"

            return mem_parts[available_idx]
        except Exception:
            return "N/A"

    def extract_remote_ips(info, output: str) -> list[str]:
        ips = []

        for line in output.splitlines():
            line = line.strip()
            # print(line)

            if "State" in line or "Netid" in line or "ESTAB" not in line:
                continue

            parts = line.split()
            # print(parts, len(parts))
            if len(parts) < 6:  # Need at least 6 columns
                continue

            # 6th column = remote address:port
            remote = parts[5]

            # Remove port
            if ":" in remote:
                addr = remote.rsplit(":", 1)[0]
            else:
                addr = remote

            # Remove brackets
            if addr.startswith("[") and addr.endswith("]"):
                addr = addr[1:-1]

            # Handle ::ffff:
            if addr.lower().startswith("::ffff:"):
                addr = addr.split("::ffff:", 1)[1]

            if addr == "::1":
                addr = "127.0.0.1"

            # Validate
            try:
                ipaddress.ip_address(addr)
                ips.append(addr)
            except Exception:
                # this fails silently
                print(f"Failed to parse IP address: {addr}")
                continue

        return list(set(ips))

    return {
        "Hostname": run("hostname"),
        "OS": run("grep PRETTY_NAME /etc/os-release | cut -d= -f2 | tr -d '\"'"),
        "Kernel": run("uname -r"),
        "Architecture": run("uname -m"),
        # "OS": run("uname -srm"),
        "Uptime": run("uptime -p"),
        "CPU Cores": run("nproc"),
        "Memory Free": get_memory_free(),
        "Disk Root Free": run('df -h / | awk \'NR==2{print $4 " (" $5 ")"}\''),
        "Public IP": run("curl -s ifconfig.me || echo 'Unknown'"),
        "Users Logged In": run("who | wc -l | xargs echo -n"),
        "outbound_dbs": extract_remote_ips(
            "dbs",
            run(
                "/usr/bin/ss -tun | /usr/bin/grep ESTAB | /usr/bin/grep -E ':3306|:5432|:6379'"
            ),
        ),
        "outbound_webs": extract_remote_ips(
            "webs", run("/usr/bin/ss -tun | /usr/bin/grep ESTAB")
        ),
    }
