# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Stargazer is a digital universe explorer - a CLI tool called `cosmonaut` for discovering, mapping, and investigating servers, networks, and services. It's designed for DevOps engineers, SREs, and security audits.

## Development Commands

### Installation and Setup
```bash
# Install in development mode
uv pip install -e .

# Run the CLI
cosmonaut --help
```

### Running Commands
```bash
# Main entry point
cosmonaut <subcommand>

# Run scripts on all discovered servers
./scripts/run_on_all.py '<command template with {} placeholder>'
```

## Architecture Overview

### CLI Structure
- **Entry Point**: `src/main.py` → `cosmonaut/cli/base.py` → `cosmonaut/__init__.py`
- **Main App**: `cosmonaut.cli.base.app` (Typer application)
- **Command Groups**: Each major feature has its own CLI module:
  - `cosmonaut.cli.ssh` - SSH connection and specs gathering
  - `cosmonaut.cli.web` - Website discovery and checking
  - `cosmonaut.cli.map` - Network topology and dependency mapping
  - `cosmonaut.cli.investigate` - Deep server investigation
  - `cosmonaut.cli.discover` - Host discovery
  - `cosmonaut.explain.explain` - Workflow explanations

### Core Components

#### Data Storage (`storage.py`)
- **Central Storage**: `data/servers.json` - JSON file containing discovered server inventory
- **Functions**: `load_servers()`, `save_servers()`, `record_server()` for persistent state
- **Server Schema**: Each server has IP, hostname, specs, websites, discovery sources, timestamps

#### Discovery System
- `discovery/network.py` - Network scanning and host discovery
- `discovery/hostname.py` - Hostname resolution
- `discovery/dependencies.py` - Service dependency mapping

#### SSH Operations
- `ssh/client.py` - SSH connection management using paramiko
- `ssh/specs.py` - System specification gathering via SSH

#### Rendering and Output
- `rendering/console.py` - Rich console output formatting
- `rendering/graph.py` - Graph visualization
- `rendering/json.py` - JSON output formatting

### Key Dependencies
- **Typer**: CLI framework with rich formatting
- **Paramiko**: SSH client functionality
- **Rich**: Terminal formatting and tables
- **TQDM**: Progress bars

### Data Flow
1. Discovery commands populate `data/servers.json` with server metadata
2. Investigation commands enrich server data with detailed specs
3. Map commands analyze relationships between discovered servers
4. All data persists in the central JSON storage for future reference

### Helper Scripts
- `scripts/run_on_all.py` - Execute commands across all discovered servers
- Uses `{}` placeholder for IP substitution in command templates