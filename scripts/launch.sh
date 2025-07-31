#!/bin/bash

# IMPORTANT: this script must be sourced!
# Usage: source ./cosmonaut-launch.sh

set -e

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  echo "❌ This script must be sourced: use 'source ./scripts/launch.sh'"
  exit 1
fi

if [ ! -d ".venv" ]; then
    echo "📦 Creating .venv..."
    uv venv
fi

echo "📡 Syncing dependencies..."
source .venv/bin/activate
uv sync

echo "🚀 Virtual environment activated: $(which python)"

cosmonaut --help
