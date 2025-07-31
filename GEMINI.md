# Stargazer Project

This document provides an overview of the Stargazer project, its command-line interface `cosmonaut`, and common workflows.

## Project Description

Stargazer is a digital exploration tool designed for system administrators, DevOps engineers, and security professionals. It provides a command-line interface (`cosmonaut`) to discover, analyze, and map servers, networks, and services.

The core philosophy of Stargazer is to build a dynamic inventory of your digital infrastructure, allowing you to understand its components, their connections, and how they change over time.

## `cosmonaut` CLI

The main entry point to Stargazer is the `cosmonaut` CLI. It is built using the Typer library and is organized into a series of commands and subcommands.

### Installation

To use the `cosmonaut` CLI, you need to have Python and `uv` installed. Then, you can install it in development mode:

```bash
git clone https://github.com/rebeling/stargazer.git
cd stargazer
uv pip install -e .
```

### Commands

The `cosmonaut` CLI provides the following main commands:

-   `inventory`: Shows all discovered servers.
-   `discover`: Discovers and explores systems.
-   `ssh`: Provides SSH-related commands.
-   `web`: Discovers and checks websites hosted on a server.
-   `map`: Maps the digital universe by discovering hosts and their dependencies.
-   `investigate`: Performs a deep investigation of a server's state.
-   `explain`: Explains common `cosmonaut` workflows. You can use `cosmonaut explain --help` to see all available topics. The `workflow-discovery` and `workflow-investigation` commands provide ASCII diagrams of the data flow.

You can get more information about each command by running `cosmonaut <command> --help`.

## Workflows

### Domain Discovery

The `explain domain-discovery` command provides a detailed explanation of the domain discovery workflow. In summary, the workflow is as follows:

1.  **Map Topology**: Use `cosmonaut map topology` to discover live hosts on a network.
2.  **SSH Specs**: Use `cosmonaut ssh specs` to gather SSH configuration details from a host.
3.  **Web Domains**: Use `cosmonaut web domains` to discover web domains and subdomains associated with a host.
4.  **Web Check**: Use `cosmonaut web check` to analyze the discovered web services.

### Host Investigation

The `explain host-investigation` command provides a detailed explanation of the host investigation workflow. This workflow allows you to perform a deep dive into a specific host to understand its configuration and running services. The `investigate` command provides several subcommands to inspect various aspects of a host, such as:

-   Running processes (`processes`)
-   Active services (`services`)
-   Cron jobs (`cron`)
-   Databases (`databases`)
-   Runtimes and frameworks (`runtimes`)
-   Security settings (`security`)
-   Network traffic (`traffic`)
-   Active connections (`connections`)
-   Firewall rules (`firewall`)

### Data Storage

Stargazer stores the discovered information in a JSON file located at `data/servers.json`. This file serves as the inventory of all discovered servers and their associated information.

## Workflow Pipelines

Here are a couple of ASCII diagrams illustrating the data flow in common Stargazer workflows.

### Discovery Pipeline

This pipeline shows how to go from a network range to a populated inventory of servers and their websites.

```
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
```

### Investigation Pipeline

This pipeline shows how to use the inventory to investigate a specific server.

```
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
```
