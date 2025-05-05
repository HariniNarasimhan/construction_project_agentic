---
title: "Problem 1: Abstract Optimization of a Building Floor Plan"
layout: default
---

## The Challenge
Designing a simplified floor plan of a construction site — no geometry, no 3D CAD complexity. Just a logical structure made up of Rooms, Doors, and Connections. The challenge was to:
- Model a building with rooms, doors, windows, and lights.
- Navigate from one room to another via doors.
- Build an MCP server interface that understands natural language instructions like: “Add a door between room 3 and room 7” or “Set the number of lights in room 5 to 3”

## Design

Using Python, I implemented an abstract object model consisting of:
* ```Room``` with attributes like name, windows, lights, doors, and adjacent_rooms.
* ```Floor``` a container for multiple rooms.
* ```Building``` an abstraction over one or more floors.

## Prerequisites

- Python 3.8 or higher
- UV package manager
- Git
- Claude Desktop

## Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/HariniNarasimhan/construction_agent.git
cd construction_agent/mcp_servers
```

2. Install UV if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. Create and activate a virtual environment:
```bash
uv sync
source .venv/bin/activate
```
4. Download and install Claude Desktop from [here](http://claude.ai/download)

5. We'll need to configure Claude for Desktop for whichever MCP servers you want to use. To do this, open your Claude for Desktop App configuration.

    ```bash
    nano ~/Library/Application Support/Claude/claude_desktop_config.json
    ```

   Make sure to create the file if it doesn't exist. If you have VS code installed

    <details>
    <summary>MacOS/Linux</summary>
    
    ```bash
    code ~/Library/Application\ Support/Claude/claude_desktop_config.json
    ```
    </details>

    <details>
    <summary>Windows</summary>

    ```bash 
    code $env:AppData\Claude\claude_desktop_config.json
    ```
    </details>

7. Add the mcp server in the ```mcpServers``` key
    ```json
    {"mcpServers": {
    "building": {
            "command": "uv",
            "env": {
                "BUILDING_DIR":"<path to github repo>/construction_agent/building_data"
            },
            "args": [
                "--directory",
                "<path to github repo>/construction_agent/mcp_servers",
                "run",
                "main.py"
            ]
        }
    }
    }
    ```

8. Save the file, and restart Claude for Desktop.

9. You can now see totally of 9 "building" mcp tools in the Claude desktop

![Claude MCP Integration](/assets/calude_mcp.png)

You will find the following tools in the app. Make sure all of them are selected

![Tools List](/assets/tools_list.png)

To know more about the Building MCP server - [Click here](https://harininarasimhan.github.io/construction_project_agentic/mcp_servers/)
