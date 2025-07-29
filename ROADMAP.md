# Stargazer Roadmap

This document outlines the planned features for the `stargazer` project.

## Feature: Interactive HTML Network Map from Inventory

**Goal:** Create a self-contained, interactive HTML file that visualizes the servers and their interconnections as recorded in `data/servers.json`. This provides a rich, explorable "map of the digital cosmos" from the known inventory without needing a live network scan.

### 1. New Command: `map inventory`

-   **Action:** Introduce a new subcommand: `cosmonaut map inventory`.
-   **Rationale:** This command's name clearly communicates that it generates a map from the existing, stored inventory, distinguishing it from the `map topology` command which implies an active scan.
-   **Options:**
    -   `--format <FORMAT>`: Specifies the output format.
        -   `dot`: The existing format (default).
        -   `html`: The new interactive format.
-   **Example Usage:**
    ```bash
    cosmonaut map inventory --format html > inventory_map.html
    ```

### 2. Data Processing from `servers.json`

-   **Action:** Implement the logic to load and parse `data/servers.json`.
-   **Details:**
    -   **Nodes:** Each server entry in the JSON file will become a "node" in the graph. Key information like `ip`, `hostname`, and `os` will be included as node attributes.
    -   **Edges:** The connections between nodes will be determined by parsing the `outbound_webs` and `outbound_dbs` arrays within each server's `specs`. An edge will be created from the server to each IP address listed in these arrays.

### 3. HTML Generation (`render_html_graph`)

-   **Action:** Create a new function, likely `render_html_graph`, in `src/cosmonaut/rendering/graph.py`.
-   **Implementation:**
    -   **Data Conversion:** The function will receive the lists of nodes and edges and convert them into a JSON format suitable for a JavaScript graphing library.
    -   **Templating:** It will use a self-contained HTML template that includes:
        -   A CDN link to a JavaScript library, preferably **vis.js (vis-network)**, for its excellent interactivity and ease of use.
        -   A `<div>` container for the graph visualization.
        -   A `<script>` block to initialize the graph with the generated node/edge data.
-   **Output:** The function will return a single HTML string, ready to be printed to standard output. This allows for easy redirection to a file.

This feature will provide a powerful and intuitive way for users to visualize and explore their discovered infrastructure.
