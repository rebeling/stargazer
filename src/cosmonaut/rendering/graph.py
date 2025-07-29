# src/cosmonaut/rendering/graph.py
def generate_dot(servers: list, dependencies: list) -> str:
    """Generate DOT file for Graphviz."""
    lines = [
        "digraph Infrastructure {",
        "  rankdir=TB;",
        "  node [shape=box, style=rounded];",
        "",
    ]

    # Nodes
    for server in servers:
        label = f"{server['ip']}\\n{server.get('hostname', '')}"
        lines.append(f'  "{server["ip"]}" [label="{label}"];')

    # Edges
    lines.append("")
    for src, dst in dependencies:
        lines.append(f'  "{src}" -> "{dst}";')

    lines.append("}")
    return "\n".join(lines)


def generate_json(servers: list, dependencies: list) -> str:
    """Generate JSON for web UI."""
    return {
        "nodes": [
            {"id": s["ip"], "label": f"{s['ip']}\\n{s.get('hostname', '')}"}
            for s in servers
        ],
        "edges": [{"from": src, "to": dst} for src, dst in dependencies],
    }
