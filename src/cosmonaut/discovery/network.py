# src/cosmonaut/discovery/network.py
import subprocess
import ipaddress
from typing import List, Dict


def scan_network(cidr: str) -> List[Dict[str, str]]:
    """Ping-scan a network and return live hosts."""
    try:
        network = ipaddress.ip_network(cidr, strict=False)
    except ValueError as e:
        raise ValueError(f"Invalid CIDR: {cidr}") from e

    alive = []

    for ip in network.hosts():
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "1", str(ip)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if result.returncode == 0:
            # Reverse DNS
            hostname = "unknown"
            try:
                r = subprocess.run(
                    ["dig", "+short", "-x", str(ip)],
                    capture_output=True,
                    text=True,
                    timeout=2,
                )
                hostname = r.stdout.strip() or "unknown"
            except Exception:
                pass

            alive.append({"ip": str(ip), "hostname": hostname, "status": "alive"})
            print(f"🟢 {ip} ({hostname})")

    return alive
