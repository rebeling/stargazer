import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

explain_app = typer.Typer(
    help="Provides explanations for common Cosmonaut CLI workflows."
)


@explain_app.command(name="domain-discovery")
def explain_domain_discovery():
    """
    Explains the workflow for domain discovery.
    """
    console = Console()

    console.print(
        Panel(
            Text(
                "🚀 Cosmonaut Domain Discovery Workflow 🚀",
                justify="center",
                style="bold magenta",
            ),
            border_style="magenta",
        )
    )

    console.print(
        "\nThis workflow guides you through discovering and analyzing domains associated with your network."
    )

    # Step 1: Map Typology
    console.print(
        Panel(
            Text.assemble(
                Text("Step 1: Map Typology", style="bold blue"),
                Text(
                    "\n[b]What it does:[/b] This command helps you understand the network topology by scanning a specified IP range. It identifies active hosts and their basic network information, such as IP addresses and hostnames. This initial mapping is crucial for pinpointing potential entry points and key assets within your digital universe.",
                    style="italic",
                ),
                Text(
                    "\n[b]Command:[/b] `cosmonaut map typology --target <network_range>`",
                    style="green",
                ),
                Text(
                    "\n[b]Example:[/b] `cosmonaut map typology --target 192.168.1.0/24`",
                    style="dim",
                ),
                Text(
                    "\n[b]Data Handling:[/b] Discovered host information (IP, hostname) is stored locally in Cosmonaut's inventory for later use by other commands.",
                    style="dim",
                ),
            ),
            border_style="blue",
        )
    )

    # Step 2: SSH Specs
    console.print(
        Panel(
            Text.assemble(
                Text("Step 2: SSH Specifications", style="bold cyan"),
                Text(
                    "\n[b]What it does:[/b] After identifying hosts, this step focuses on gathering detailed SSH configuration information from a target server. Cosmonaut attempts to connect to the specified host via SSH (without executing arbitrary commands) to retrieve details like supported ciphers, key exchange algorithms, and authentication methods. This helps in identifying potential vulnerabilities or misconfigurations in the SSH service.",
                    style="italic",
                ),
                Text(
                    "\n[b]Command:[/b] `cosmonaut ssh specs --host <hostname_or_ip>`",
                    style="green",
                ),
                Text(
                    "\n[b]Example:[/b] `cosmonaut ssh specs --host my-server.local`",
                    style="dim",
                ),
                Text(
                    "\n[b]Data Handling:[/b] The collected SSH specification data is displayed in the console and can be stored as part of the host's detailed profile in Cosmonaut's inventory.",
                    style="dim",
                ),
            ),
            border_style="cyan",
        )
    )

    # Step 3: Web Domains
    console.print(
        Panel(
            Text.assemble(
                Text("Step 3: Web Domains Discovery", style="bold yellow"),
                Text(
                    "\n[b]What it does:[/b] This command expands your attack surface view by discovering web domains and subdomains associated with a given host. It leverages various techniques (e.g., DNS lookups, common subdomain enumeration) to find all related web presences. This is vital for comprehensive reconnaissance.",
                    style="italic",
                ),
                Text(
                    "\n[b]Command:[/b] `cosmonaut web domains --host <hostname_or_ip>`",
                    style="green",
                ),
                Text(
                    "\n[b]Example:[/b] `cosmonaut web domains --host my-web-server.com`",
                    style="dim",
                ),
                Text(
                    "\n[b]Data Handling:[/b] Discovered web domains are listed in the console and added to the host's record in Cosmonaut's inventory, linking them to the original host.",
                    style="dim",
                ),
            ),
            border_style="yellow",
        )
    )

    # Step 4: Web Check
    console.print(
        Panel(
            Text.assemble(
                Text("Step 4: Web Check and Analysis", style="bold red"),
                Text(
                    "\n[b]What it does:[/b] The final step involves performing detailed checks on discovered web services. For a given URL, Cosmonaut will analyze the web server to identify technologies used (e.g., web server software, frameworks), open ports, and potential security headers or misconfigurations. This provides actionable insights for further investigation.",
                    style="italic",
                ),
                Text(
                    "\n[b]Command:[/b] `cosmonaut web check --url <url>`", style="green"
                ),
                Text(
                    "\n[b]Example:[/b] `cosmonaut web check --url https://www.example.com`",
                    style="dim",
                ),
                Text(
                    "\n[b]Data Handling:[/b] The results of the web check, including identified technologies and potential issues, are displayed in the console and stored as part of the web service's profile within Cosmonaut's data.",
                    style="dim",
                ),
            ),
            border_style="red",
        )
    )

    console.print(
        "\nFor more detailed information on any command, use `cosmonaut [command] --help` (e.g., `cosmonaut map --help`)."
    )


@explain_app.command(name="host-investigation")
def explain_host_investigation():
    """
    Explains the workflow for deep host investigation.
    """
    console = Console()

    console.print(
        Panel(
            Text(
                "🕵️‍♂️ Cosmonaut Host Investigation Workflow 🕵️‍♀️",
                justify="center",
                style="bold blue",
            ),
            border_style="blue",
        )
    )

    console.print(
        "\nThis workflow guides you through a comprehensive investigation of a target host after initial discovery."
    )

    # Step 1: Initial Host Discovery (Prerequisite)
    console.print(
        Panel(
            Text.assemble(
                Text(
                    "Step 1: Initial Host Discovery (Prerequisite)", style="bold green"
                ),
                Text(
                    "\n[b]What it does:[/b] Before deep investigation, you need to identify a target host. This can be done through network scanning or by directly specifying a known host. This step ensures you have a valid target for subsequent investigative commands.",
                    style="italic",
                ),
                Text(
                    "\n[b]Command (Option A - Network Scan):[/b] `cosmonaut map typology --target <network_range>`",
                    style="green",
                ),
                Text(
                    "\n[b]Example:[/b] `cosmonaut map typology --target 192.168.1.0/24`",
                    style="dim",
                ),
                Text(
                    "\n[b]Command (Option B - Direct Host):[/b] `cosmonaut discover host <user@host>`",
                    style="green",
                ),
                Text(
                    "\n[b]Example:[/b] `cosmonaut discover host user@my-server.local`",
                    style="dim",
                ),
                Text(
                    "\n[b]Data Handling:[/b] Discovered hosts are added to Cosmonaut's inventory, making them available for further investigation.",
                    style="dim",
                ),
            ),
            border_style="green",
        )
    )

    # Step 2: Investigate Processes
    console.print(
        Panel(
            Text.assemble(
                Text("Step 2: Investigate Processes", style="bold cyan"),
                Text(
                    "\n[b]What it does:[/b] Connects to the target host via SSH and lists the top running processes, typically ordered by memory or CPU usage. This helps in identifying resource-intensive applications or suspicious processes.",
                    style="italic",
                ),
                Text(
                    "\n[b]Command:[/b] `cosmonaut investigate processes <user@host> --top 10`",
                    style="green",
                ),
                Text(
                    "\n[b]Example:[/b] `cosmonaut investigate processes admin@192.168.1.100 --top 5`",
                    style="dim",
                ),
                Text(
                    "\n[b]Data Handling:[/b] Process information is displayed in the console. No persistent storage for individual process lists.",
                    style="dim",
                ),
            ),
            border_style="cyan",
        )
    )

    # Step 3: Investigate Services
    console.print(
        Panel(
            Text.assemble(
                Text("Step 3: Investigate Services", style="bold yellow"),
                Text(
                    "\n[b]What it does:[/b] Connects to the target host via SSH and lists active systemd services. This provides an overview of the services running on the server, which can indicate its primary functions and potential attack vectors.",
                    style="italic",
                ),
                Text(
                    "\n[b]Command:[/b] `cosmonaut investigate services <user@host>`",
                    style="green",
                ),
                Text(
                    "\n[b]Example:[/b] `cosmonaut investigate services root@my-server.com`",
                    style="dim",
                ),
                Text(
                    "\n[b]Data Handling:[/b] Service information is displayed in the console. No persistent storage for individual service lists.",
                    style="dim",
                ),
            ),
            border_style="yellow",
        )
    )

    # Step 4: Investigate Cron Jobs
    console.print(
        Panel(
            Text.assemble(
                Text("Step 4: Investigate Cron Jobs", style="bold magenta"),
                Text(
                    "\n[b]What it does:[/b] Connects to the target host via SSH and lists scheduled cron jobs for various users (root, current user, and from /etc/cron.d/). This is crucial for identifying automated tasks, which could be legitimate system operations or malicious persistence mechanisms.",
                    style="italic",
                ),
                Text(
                    "\n[b]Command:[/b] `cosmonaut investigate cron <user@host> --show-commands`",
                    style="green",
                ),
                Text(
                    "\n[b]Example:[/b] `cosmonaut investigate cron user@10.0.0.5 --show-commands`",
                    style="dim",
                ),
                Text(
                    "\n[b]Data Handling:[/b] Cron job details are displayed in the console. No persistent storage for individual cron job lists.",
                    style="dim",
                ),
            ),
            border_style="magenta",
        )
    )

    # Step 5: Investigate Databases
    console.print(
        Panel(
            Text.assemble(
                Text("Step 5: Investigate Databases", style="bold red"),
                Text(
                    "\n[b]What it does:[/b] Connects to the target host via SSH and checks for the presence and status of common database systems (SQL and NoSQL). It identifies if databases are running, their versions, and typical data directories. This helps in mapping data storage and potential data exfiltration points.",
                    style="italic",
                ),
                Text(
                    "\n[b]Command:[/b] `cosmonaut investigate databases <user@host>`",
                    style="green",
                ),
                Text(
                    "\n[b]Example:[/b] `cosmonaut investigate databases admin@db-server`",
                    style="dim",
                ),
                Text(
                    "\n[b]Data Handling:[/b] Database information is displayed in the console. No persistent storage for individual database lists.",
                    style="dim",
                ),
            ),
            border_style="red",
        )
    )

    # Step 6: Investigate Runtimes
    console.print(
        Panel(
            Text.assemble(
                Text("Step 6: Investigate Runtimes", style="bold blue"),
                Text(
                    "\n[b]What it does:[/b] Connects to the target host via SSH and identifies installed programming language runtimes (e.g., Python, Node.js, Java), frameworks, and container technologies (e.g., Docker, Kubernetes). This provides insights into the software stack and potential vulnerabilities related to specific versions or configurations.",
                    style="italic",
                ),
                Text(
                    "\n[b]Command:[/b] `cosmonaut investigate runtimes <user@host>`",
                    style="green",
                ),
                Text(
                    "\n[b]Example:[/b] `cosmonaut investigate runtimes dev@app-server`",
                    style="dim",
                ),
                Text(
                    "\n[b]Data Handling:[/b] Runtime and framework information is displayed in the console. No persistent storage for individual runtime lists.",
                    style="dim",
                ),
            ),
            border_style="blue",
        )
    )

    # Step 7: Investigate Security
    console.print(
        Panel(
            Text.assemble(
                Text("Step 7: Investigate Security", style="bold green"),
                Text(
                    "\n[b]What it does:[/b] Connects to the target host via SSH and performs basic security checks, such as listing SSH authorized keys, checking sudo access for the current user, and verifying `PermitRootLogin` status in `sshd_config`. This helps in assessing the host's security posture and identifying potential misconfigurations.",
                    style="italic",
                ),
                Text(
                    "\n[b]Command:[/b] `cosmonaut investigate security <user@host>`",
                    style="green",
                ),
                Text(
                    "\n[b]Example:[/b] `cosmonaut investigate security auditor@jump-box`",
                    style="dim",
                ),
                Text(
                    "\n[b]Data Handling:[/b] Security findings are displayed in the console. No persistent storage for individual security check results.",
                    style="dim",
                ),
            ),
            border_style="green",
        )
    )

    # Step 8: Investigate Traffic
    console.print(
        Panel(
            Text.assemble(
                Text("Step 8: Investigate Traffic", style="bold cyan"),
                Text(
                    "\n[b]What it does:[/b] Connects to the target host via SSH and shows recent outbound network connections, including DNS queries and established TCP/UDP connections. This helps in understanding the server's communication patterns and identifying connections to external services or suspicious destinations.",
                    style="italic",
                ),
                Text(
                    "\n[b]Command:[/b] `cosmonaut investigate traffic <user@host>`",
                    style="green",
                ),
                Text(
                    "\n[b]Example:[/b] `cosmonaut investigate traffic monitor@web-server`",
                    style="dim",
                ),
                Text(
                    "\n[b]Data Handling:[/b] Traffic information is displayed in the console. No persistent storage for individual traffic logs.",
                    style="dim",
                ),
            ),
            border_style="cyan",
        )
    )

    # Step 9: Investigate Connections
    console.print(
        Panel(
            Text.assemble(
                Text("Step 9: Investigate Connections", style="bold yellow"),
                Text(
                    "\n[b]What it does:[/b] Connects to the target host via SSH and lists all current active network connections (inbound and outbound). This provides a real-time snapshot of network activity, including local and remote addresses, connection states, and associated processes.",
                    style="italic",
                ),
                Text(
                    "\n[b]Command:[/b] `cosmonaut investigate connections <user@host>`",
                    style="green",
                ),
                Text(
                    "\n[b]Example:[/b] `cosmonaut investigate connections sysadmin@db-server`",
                    style="dim",
                ),
                Text(
                    "\n[b]Data Handling:[/b] Connection details are displayed in the console. No persistent storage for individual connection lists.",
                    style="dim",
                ),
            ),
            border_style="yellow",
        )
    )

    # Step 10: Investigate Firewall
    console.print(
        Panel(
            Text.assemble(
                Text("Step 10: Investigate Firewall", style="bold magenta"),
                Text(
                    "\n[b]What it does:[/b] Connects to the target host via SSH and displays the active firewall rules (iptables or nftables). This is critical for understanding network access controls, identifying open ports, and verifying security policies.",
                    style="italic",
                ),
                Text(
                    "\n[b]Command:[/b] `cosmonaut investigate firewall <user@host>`",
                    style="green",
                ),
                Text(
                    "\n[b]Example:[/b] `cosmonaut investigate firewall security@router`",
                    style="dim",
                ),
                Text(
                    "\n[b]Data Handling:[/b] Firewall rules are displayed in the console. No persistent storage for individual firewall configurations.",
                    style="dim",
                ),
            ),
            border_style="magenta",
        )
    )

    console.print(
        "\nFor more detailed information on any command, use `cosmonaut [command] --help` (e.g., `cosmonaut investigate --help`)."
    )


@explain_app.command(name="workflow-discovery")
def explain_workflow_discovery():
    """
    Explains the discovery workflow with a pipeline diagram.
    """
    console = Console()
    console.print(
        Panel(
            Text(
                "Discovery Pipeline",
                justify="center",
                style="bold blue",
            ),
            border_style="blue",
        )
    )
    console.print(
        """
This pipeline shows how to go from a network range to a populated inventory of servers and their websites.

[Network Range]
      |
      v
+---------------------+      +-------------------+
| cosmonaut map       |----->| data/servers.json |
|     topology        |      +-------------------+
+---------------------+             ^
      |                             |
      v                             |
[List of IPs]                       |
      |                             |
      v                             |
+---------------------+             |
| cosmonaut discover  |             |
|     host            |-------------+
+---------------------+
      |
      v
+---------------------+      +-------------------+
| cosmonaut web       |----->| data/servers.json |
|     domains         |      | (updated)         |
+---------------------+      +-------------------+
"""
    )


@explain_app.command(name="workflow-investigation")
def explain_workflow_investigation():
    """
    Explains the investigation workflow with a pipeline diagram.
    """
    console = Console()
    console.print(
        Panel(
            Text(
                "Investigation Pipeline",
                justify="center",
                style="bold blue",
            ),
            border_style="blue",
        )
    )
    console.print(
        """
This pipeline shows how to use the inventory to investigate a specific server.

+-------------------+
| data/servers.json |
+-------------------+
      |
      v
+---------------------+
| cosmonaut inventory |
+---------------------+
      |
      v
[Select a server]
      |
      v
+-----------------------+      +-----------------+
| cosmonaut investigate |----->| SSH to Server   |
|     [subcommand]      |      +-----------------+
+-----------------------+             |
      |                             |
      v                             v
[Detailed Information]        [Live System Data]
(Processes, Services, etc.)
"""
    )


if __name__ == "__main__":
    explain_app()