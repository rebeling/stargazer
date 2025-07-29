# src/cosmonaut/discovery/dependencies.py
def detect_dependencies(servers: list) -> list[tuple]:
    deps = []
    ip_to_hostname = {s["ip"]: s["hostname"] or s["ip"] for s in servers}

    for server in servers:
        ip = server["ip"]
        specs = server.get("specs", {})

        # Handle DB connections
        for db_ip in specs.get("outbound_dbs", []):
            db_ip = db_ip.strip()
            if db_ip in ("127.0.0.1", "::1", "0.0.0.0"):
                deps.append((ip, f"{ip}-db"))
            elif db_ip in ip_to_hostname:
                deps.append((ip, db_ip))
            else:
                deps.append((ip, db_ip))  # unknown IP

        # Handle web connections
        for web_ip in specs.get("outbound_webs", []):
            web_ip = web_ip.strip()
            if web_ip == ip:
                deps.append((ip, ip))  # self-call
            elif web_ip in ip_to_hostname:
                deps.append((ip, web_ip))

    return list(set(deps))
