# src/cosmonaut/storage.py
import json
from pathlib import Path
from datetime import datetime

# Define paths
DATA_DIR = Path("data")
SERVERS_FILE = DATA_DIR / "servers.json"


def ensure_data_dir():
    """Create data/ directory if it doesn't exist."""
    DATA_DIR.mkdir(exist_ok=True)


def load_servers():
    """Load servers dict from JSON. Create default if missing."""
    ensure_data_dir()

    if not SERVERS_FILE.exists():
        SERVERS_FILE.write_text("{}")  # Create empty JSON object
        return {}

    try:
        text = SERVERS_FILE.read_text(encoding="utf-8")
        if not text.strip():
            SERVERS_FILE.write_text("{}")
            return {}
        return json.loads(text)
    except (json.JSONDecodeError, OSError) as e:
        print(f"⚠️ Failed to read {SERVERS_FILE}: {e}")
        print("🔁 Creating a fresh servers.json")
        SERVERS_FILE.write_text("{}")
        return {}


def save_servers(servers):
    """Save servers dict to JSON. Ensures dir and file exist."""
    ensure_data_dir()
    try:
        SERVERS_FILE.write_text(
            json.dumps(servers, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    except Exception as e:
        print(f"❌ Failed to write {SERVERS_FILE}: {e}")


def record_server(
    ip: str,
    hostname: str = None,
    specs: dict = None,
    websites: list = None,
    source: str = "unknown",
):
    """Record or update a server with discovery metadata."""
    servers = load_servers()

    if ip not in servers:
        servers[ip] = {
            "ip": ip,
            "first_seen": datetime.now().isoformat(),
            "last_seen": None,
            "hostname": "unknown",
            "specs": {},
            "websites": [],
            "sources": [],
            "tags": [],
        }

    # Update fields
    if hostname:
        servers[ip]["hostname"] = hostname

    if specs is not None:
        # Ensure lists are flat
        if isinstance(specs.get("outbound_dbs"), list):
            specs["outbound_dbs"] = [
                str(ip) for ip in specs["outbound_dbs"] if isinstance(ip, (str, int))
            ]

        if isinstance(specs.get("outbound_webs"), list):
            specs["outbound_webs"] = [
                str(ip) for ip in specs["outbound_webs"] if isinstance(ip, (str, int))
            ]

        servers[ip]["specs"] = specs

    if websites is not None:
        servers[ip]["websites"] = sorted(set(websites))

    # Always update last_seen
    servers[ip]["last_seen"] = datetime.now().isoformat()

    # Track discovery sources
    sources = servers[ip].get("sources", [])
    if source not in sources:
        sources.append(source)
    servers[ip]["sources"] = sources

    save_servers(servers)
    return servers[ip]
