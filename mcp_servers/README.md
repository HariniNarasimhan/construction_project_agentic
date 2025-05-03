# Building MCP Server Documentation

This document provides detailed information about the Building MCP Server and its available tools and functionalities.

## Overview

The Building MCP Server provides a set of tools for managing and interacting with building data structures. It allows for operations such as adding/removing floors and rooms, managing doors between rooms, updating room properties, and finding paths between rooms.

## Available Tools

### 1. Read Building Data
- **Description**: Load and read building data from a specified building name
- **Parameters**:
  - `building_name` (str): Name of the building to read data from
- **Returns**: Building data structure containing floors and rooms

### 2. Add Floor
- **Description**: Add a new floor to the building
- **Parameters**:
  - `building_name` (str): Name of the building
  - `floor_number` (int): Number of the floor to add
  - `floor_data` (dict): Floor data in format `{rooms: list[dict]}`

### 3. Add Room
- **Description**: Add a new room to a specific floor
- **Parameters**:
  - `building_name` (str): Name of the building
  - `floor_number` (int): Floor number where the room will be added
  - `room` (dict): Room data in format:
    ```json
    {
      "name": str,
      "doors": list[str],
      "windows": int,
      "lights": int,
      "adjacent_rooms": list[str]
    }
    ```

### 4. Remove Room
- **Description**: Remove a room from a specific floor
- **Parameters**:
  - `building_name` (str): Name of the building
  - `floor_number` (int): Floor number containing the room
  - `room_name` (str): Name of the room to remove

### 5. Add Door
- **Description**: Add a door connection between two rooms
- **Parameters**:
  - `building_name` (str): Name of the building
  - `floor_number` (int): Floor number containing the rooms
  - `room_name` (str): Name of the first room
  - `adjacent_room_name` (str): Name of the adjacent room

### 6. Remove Door
- **Description**: Remove a door connection between two rooms
- **Parameters**:
  - `building_name` (str): Name of the building
  - `floor_number` (int): Floor number containing the rooms
  - `room_name` (str): Name of the first room
  - `adjacent_room_name` (str): Name of the adjacent room

### 7. Update Lights
- **Description**: Update the number of lights in a room
- **Parameters**:
  - `building_name` (str): Name of the building
  - `floor_number` (int): Floor number containing the room
  - `room_name` (str): Name of the room
  - `new_lights` (int): New number of lights (must be non-negative)

### 8. Update Windows
- **Description**: Update the number of windows in a room
- **Parameters**:
  - `building_name` (str): Name of the building
  - `floor_number` (int): Floor number containing the room
  - `room_name` (str): Name of the room
  - `new_windows` (int): New number of windows (must be non-negative)

### 9. Find Path
- **Description**: Find a path between two rooms in the building
- **Parameters**:
  - `building_name` (str): Name of the building
  - `start_room_name` (str): Name of the starting room
  - `end_room_name` (str): Name of the destination room
- **Returns**: List of rooms representing the path, or None if no path exists

## Data Storage

The building data is stored in JSON format with the following structure:
- Each building has its own directory
- Each floor is stored in a separate file named `floor_N.json` where N is the floor number range(1,N)
- Building metadata is stored in `building_metadata.json`

## Error Handling

The server implements comprehensive error handling for:
- Invalid room connections
- Non-existent rooms or floors
- Invalid parameter values (e.g., negative number of lights or windows)
- Missing building data
- Invalid door connections


## Environment Variables

- `BUILDING_DIR`: Directory where building data is stored
  - Must be set before running the server
  - Default location for storing building JSON files

## Testing the MCP Server

The project uses pytest for testing. You can run tests using the following commands:

```bash
poe test
```

The test configuration is set up in `pyproject.toml` and will automatically:
- Look for tests in the `construction_agent/mcp_servers/test_building_server.py` directory
- Run all files matching `test_*.py`
- Execute functions starting with `test_*`
- Run classes starting with `Test*`

## Notes

- All room names must be unique within a building
- Door connections are bidirectional (automatically added to both rooms)
- Path finding uses BFS algorithm for optimal path discovery
- Building data is automatically saved to JSON files after modifications


## Additional Notes

- Make sure all dependencies are properly installed before running tests
- The test suite uses verbose output by default for detailed test results
- For development, it's recommended to run tests frequently to ensure changes don't break existing functionality
