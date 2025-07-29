#!/usr/bin/env python
import json
import subprocess
import sys
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print("Usage: ./scripts/run_on_all.py <command>")
        print("Example: ./scripts/run_on_all.py 'echo {}'")
        sys.exit(1)

    command_template = " ".join(sys.argv[1:])

    # Construct the path to servers.json relative to the script's location
    script_dir = Path(__file__).parent.absolute()
    servers_json_path = script_dir.parent / "data" / "servers.json"

    if not servers_json_path.exists():
        print(f"Error: {servers_json_path} not found.")
        sys.exit(1)

    with open(servers_json_path, "r") as f:
        servers_data = json.load(f)

    if not servers_data:
        print("No servers found in data/servers.json.")
        return

    for ip in servers_data.keys():
        # Replace {} with the IP address
        command_to_run = command_template.replace("{}", ip)
        print(f"🚀 Running on {ip}: {command_to_run}")
        try:
            # Using shell=True for simplicity, but be cautious with untrusted input
            result = subprocess.run(
                command_to_run, shell=True, check=True, text=True, capture_output=True
            )
            print(result.stdout)
            if result.stderr:
                print(f"Stderr: {result.stderr}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error running command on {ip}: {e}")
            print(f"Stderr: {e.stderr}")


if __name__ == "__main__":
    main()
