# stargazer 🌌

> _Observe your digital universe._

`stargazer` is a **digital universe explorer** — a command-line observatory for your servers, networks, and services.

Use `cosmonaut` (its CLI) to:
- 🔍 Discover servers and networks
- 🖥️ Connect via SSH and gather specs
- 📦 Build an inventory of your infrastructure
- 🗺️ Map the hidden landscape of your systems

Perfect for:
- DevOps engineers
- SREs
- Security audits
- Network discovery
- Learning Python automation

---

## 🎯 Vision

Most tools ask: *"What’s running where?"*

**stargazer** asks:
> *"What have we discovered? What’s changed? What’s connected?"*

It’s not just a scanner — it’s a **living map of your digital cosmos**.

---

## 🚀 Quick Start

### 1. Clone and install
```bash
git clone https://github.com/rebeling/stargazer.git
cd stargazer

# Install in development mode
uv pip install -e .
```

### 2. See Commands
```bash
cosmonaut --help
```

---


## Helper

Run for all hosts in data/servers.json.

```bash
./scripts/run_on_all.py 'echo "Pinging {}..." && ping -c 3 {}'
```
