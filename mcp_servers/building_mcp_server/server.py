import os
import mcp
from typing import Any, Dict, List
from mcp.server import Server
import logging
from typing import Annotated
from mcp.shared.exceptions import McpError
from mcp.server import Server
import json
from mcp.server import Server
from mcp.types import (
    ErrorData,
    TextContent,
    Tool,
    Prompt,
    PromptArgument,
    INVALID_PARAMS
)
from pydantic import BaseModel, Field
from .building import *
import traceback
logger = logging.getLogger(__name__)

server = Server("building_mcp_server")

def get_building_dir():
    """Get the building directory from environment variable."""
    building_dir = os.getenv("BUILDING_DIR")
    if building_dir is None:
        raise ValueError("BUILDING_DIR environment variable is not set")
    return building_dir

class Read_Building_data(BaseModel):
    """Parameters for loading building data."""
    building_name: Annotated[str, Field(description="Building name")]

class Add_Floor(BaseModel):
    """Parameters for adding a floor to the building."""
    building_name: Annotated[str, Field(description="Building name")]
    floor_number: Annotated[int, Field(description="Floor number")]
    floor_data: Annotated[dict, Field(description="Floor data in a dictionary format as {rooms: list[dict]}]")]

class Add_Room(BaseModel):
    """Parameters for adding a room to the building."""
    building_name: Annotated[str, Field(description="Building name")]
    floor_number: Annotated[int, Field(description="Floor number")]
    room: Annotated[dict, Field(description="Room data in a dictionary format as {name: str, doors: list[str], windows: int, lights: int, adjacent_rooms: list[str]}")]
    
class Remove_Room(BaseModel):
    """Parameters for removing a room from the building."""
    building_name: Annotated[str, Field(description="Building name")]
    floor_number: Annotated[int, Field(description="Floor number")]
    room_name: Annotated[str, Field(description="Room name")]

class Add_Door(BaseModel):
    """Parameters for adding a door to the building."""
    building_name: Annotated[str, Field(description="Building name")]
    floor_number: Annotated[int, Field(description="Floor number")]
    room_name: Annotated[str, Field(description="Room name")]
    adjacent_room_name: Annotated[str, Field(description="Adjacent room name")]

class Remove_Door(BaseModel):
    """Parameters for removing a door from the building."""
    building_name: Annotated[str, Field(description="Building name")]
    floor_number: Annotated[int, Field(description="Floor number")]
    room_name: Annotated[str, Field(description="Room name")]
    adjacent_room_name: Annotated[str, Field(description="Adjacent room name")]

class Update_Lights(BaseModel):
    """Parameters for updating the number of lights in a room."""
    building_name: Annotated[str, Field(description="Building name")]
    floor_number: Annotated[int, Field(description="Floor number")]
    room_name: Annotated[str, Field(description="Room name")]
    new_lights: Annotated[int, Field(description="New number of lights")]   
    
class Update_Windows(BaseModel):
    """Parameters for updating the number of windows in a room."""
    building_name: Annotated[str, Field(description="Building name")]
    floor_number: Annotated[int, Field(description="Floor number")]
    room_name: Annotated[str, Field(description="Room name")]
    new_windows: Annotated[int, Field(description="New number of windows")]

class Find_Path(BaseModel):
    """Parameters for finding a path between two rooms."""
    building_name: Annotated[str, Field(description="Building name")]
    start_room_name: Annotated[str, Field(description="Start room name")]
    end_room_name: Annotated[str, Field(description="End room name")]   
    

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="Read_Building_data",
            description="Load building data",
            inputSchema=Read_Building_data.model_json_schema(),
        ),
        Tool(
            name="Add_Floor",
            description="Add a floor to the building",
            inputSchema=Add_Floor.model_json_schema(),
        ),
        Tool(
            name="Add_Room",
            description="Add a room to the building and also update the adjacent rooms, doors, windows, lights",
            inputSchema=Add_Room.model_json_schema(),
        ),
        Tool(
            name="Remove_Room",
            description="Remove a room from the building",
            inputSchema=Remove_Room.model_json_schema(),
        ),
        Tool(
            name="Add_Door",
            description="Add a door to the building",
            inputSchema=Add_Door.model_json_schema(),
        ),
        Tool(
            name="Remove_Door",
            description="Remove a door from the building",
            inputSchema=Remove_Door.model_json_schema(),
        ),
        Tool(
            name="Update_Lights",
            description="Update the number of lights in a room",
            inputSchema=Update_Lights.model_json_schema(),
        ),
        Tool(
            name="Update_Windows",
            description="Update the number of windows in a room",
            inputSchema=Update_Windows.model_json_schema(),
        ),
        Tool(
            name="Find_Path",
            description="Find a path between two rooms",
            inputSchema=Find_Path.model_json_schema(),
        ),
        
    ]

@server.list_prompts()
async def list_prompts() -> list[Prompt]:
    return [
        Prompt(
            name="Read_Building_data",
            description="Read building data from building name",
            arguments=[
                PromptArgument(
                    name="building_name", description="Building name", required=True
                )
            ]
        ),
        Prompt(
            name="Add_Floor",
            description="Add a floor to the building",
            arguments=[
                PromptArgument(
                    name="building_name", description="Building name", required=True
                ),
                PromptArgument(
                    name="floor_number", description="Floor number", required=True
                ),
                PromptArgument(
                    name="floor_data", description="Floor data", required=True
                )
            ]   
        ),
        Prompt(
            name="Add_Room",
            description="Add a room to the building",
            arguments=[
                PromptArgument(
                    name="building_name", description="Building name", required=True
                ),
                PromptArgument(
                    name="floor_number", description="Floor number", required=True
                ),
                PromptArgument(
                    name="room", description="Room data", required=True
                )
            ]       
        ),
        Prompt(
            name="Remove_Room",
            description="Remove a room from the building",
            arguments=[
                PromptArgument(
                    name="building_name", description="Building name", required=True
                ),
                PromptArgument(
                    name="floor_number", description="Floor number", required=True
                ),
                PromptArgument(
                    name="room_name", description="Room name", required=True
                )
            ]   
        ),
        Prompt(
            name="Add_Door",
            description="Add a door to the building",
            arguments=[
                PromptArgument(
                    name="building_name", description="Building name", required=True
                ),
                PromptArgument(
                    name="floor_number", description="Floor number", required=True
                ),
                PromptArgument(
                    name="room_name", description="Room name", required=True
                ),
                PromptArgument(
                    name="adjacent_room_name", description="Adjacent room name", required=True
                )
            ]   
        ),
        Prompt(
            name="Remove_Door",
            description="Remove a door from the building",
            arguments=[
                PromptArgument(
                    name="building_name", description="Building name", required=True
                ),
                PromptArgument(
                    name="floor_number", description="Floor number", required=True
                ),
                PromptArgument(
                    name="room_name", description="Room name", required=True
                ),
                PromptArgument(
                    name="adjacent_room_name", description="Adjacent room name", required=True
                )
            ]   
        ),
        Prompt(
            name="Update_Lights",
            description="Update the number of lights in a room",
            arguments=[
                PromptArgument(
                    name="building_name", description="Building name", required=True
                ),
                PromptArgument(
                    name="floor_number", description="Floor number", required=True
                ),
                PromptArgument(
                    name="room_name", description="Room name", required=True
                ),
                PromptArgument(
                    name="new_lights", description="New number of lights", required=True
                )
            ]   
        ),
        Prompt(
            name="Update_Windows",
            description="Update the number of windows in a room",
            arguments=[
                PromptArgument(
                    name="building_name", description="Building name", required=True
                ),
                PromptArgument(
                    name="floor_number", description="Floor number", required=True
                ),
                PromptArgument(
                    name="room_name", description="Room name", required=True
                ),
                PromptArgument(
                    name="new_windows", description="New number of windows", required=True
                )
            ] 
            ),
        Prompt(
            name="Find_Path",
            description="Find a path between two rooms",
            arguments=[
                PromptArgument(
                    name="building_name", description="Building name", required=True
                ),
                PromptArgument(
                    name="start_room_name", description="Start room name", required=True
                ),
                PromptArgument(
                    name="end_room_name", description="End room name", required=True
                )
            ]   
        )
    ]

@server.call_tool()
async def call_tool(name:str , arguments: Dict) -> list[TextContent]:
    """Call the MCP tool

    Args:
        name (str): name of the tool to be called
        arguments (Dict): Arguments with type Dict 

    Returns:
        list[TextContent]: response of the tool in text content format
    """
    logger.info(f"call_tool triggered with Arguments are: {arguments} with type {type(arguments)} and name :{name} ")
    try:
        building_dir = get_building_dir()
        if name == "Read_Building_data":
            args = Read_Building_data(**arguments)
            message = ""
            for floor in os.listdir(os.path.join(building_dir, args.building_name)):
                with open(os.path.join(building_dir, args.building_name, floor), "r") as f:
                    floor_data = json.load(f)
                message += f"Floor {floor}: {floor_data}\n"
            
            return [TextContent(type="text", text=f"Building data: {message}")]
        elif name == "Add_Floor":
            args = Add_Floor(**arguments)
            building = load_building_from_directory(args.building_name)
            floor_data = args.floor_data
            rooms = []
            for room_name, room_data in floor_data["rooms"].items():
                room = Room(
                    name=room_name,
                    doors=room_data["doors"],
                    windows=room_data["windows"],
                    lights=room_data["lights"],     
                    adjacent_rooms=room_data["adjacent_rooms"]
                )
                rooms.append(room)
            floor = Floor(rooms)
            building.add_floor(floor)
            building.to_json(args.building_name)
            return [TextContent(type="text", text=f"Floor added successfully")]
        elif name == "Add_Room":
            args = Add_Room(**arguments)
            building = load_building_from_directory(args.building_name)
            room_data = args.room
            floor_number = args.floor_number
            floor = building.floors[floor_number - 1]
            # check the adjacent rooms and add new room to the adjacent room's adjacent_rooms list
            for adjacent_room in room_data["adjacent_rooms"]:
                adj_room = floor.get_room_by_name(adjacent_room)
                if adj_room is not None:
                    adj_room.adjacent_rooms.append(room_data["name"])
            
            room = Room(**room_data)
            floor.add_room(room)
            
            building.to_json(args.building_name)
            return [TextContent(type="text", text=f"Room added successfully")]
        elif name == "Remove_Room":
            args = Remove_Room(**arguments)
            building = load_building_from_directory(args.building_name)
            floor_number = args.floor_number
            room_name = args.room_name
            floor = building.floors[floor_number - 1]
            room = floor.get_room_by_name(room_name)
            if room is None:
                raise ValueError(f"Room {room_name} not found")
            floor.remove_room(room)
            building.to_json(args.building_name)
            return [TextContent(type="text", text=f"Room removed successfully")]
        elif name == "Add_Door":
            args = Add_Door(**arguments)
            building = load_building_from_directory(args.building_name)
            room_name = args.room_name
            adjacent_room_name = args.adjacent_room_name
            floor_number = args.floor_number
            floor = building.floors[floor_number - 1]
            room = floor.get_room_by_name(room_name)
            adjacent_room = floor.get_room_by_name(adjacent_room_name)
            if room is None:
                raise ValueError(f"Room {room_name} not found")
            if adjacent_room is None:
                raise ValueError(f"Room {adjacent_room_name} not found")
            room.add_door(adjacent_room)
            building.to_json(args.building_name)
            return [TextContent(type="text", text=f"Door added successfully")]
        elif name == "Remove_Door":
            args = Remove_Door(**arguments)
            building = load_building_from_directory(args.building_name)
            floor_number = args.floor_number
            room_name = args.room_name
            adjacent_room_name = args.adjacent_room_name
            floor = building.floors[floor_number - 1]
            room = floor.get_room_by_name(room_name)
            adjacent_room = floor.get_room_by_name(adjacent_room_name)
            if room is None:
                raise ValueError(f"Room {room_name} not found")
            if adjacent_room is None:
                raise ValueError(f"Room {adjacent_room_name} not found")
            room.remove_door(adjacent_room)
            building.to_json(args.building_name)
            return [TextContent(type="text", text=f"Door removed successfully")]
        elif name == "Update_Lights":
            args = Update_Lights(**arguments)
            building = load_building_from_directory(args.building_name)
            floor_number = args.floor_number
            room_name = args.room_name
            new_lights = args.new_lights
            floor = building.floors[floor_number - 1]
            room = floor.get_room_by_name(room_name)
            room.update_lights(new_lights)
            building.to_json(args.building_name)
            return [TextContent(type="text", text=f"Lights updated successfully")]
        elif name == "Update_Windows":
            args = Update_Windows(**arguments)
            building = load_building_from_directory(args.building_name)
            floor_number = args.floor_number
            room_name = args.room_name
            new_windows = args.new_windows
            floor = building.floors[floor_number - 1]
            room = floor.get_room_by_name(room_name)
            room.update_windows(new_windows)
            building.to_json(args.building_name)
            return [TextContent(type="text", text=f"Windows updated successfully")]
        elif name == "Find_Path":
            args = Find_Path(**arguments)
            building = load_building_from_directory(args.building_name)
            start_room_name = args.start_room_name
            end_room_name = args.end_room_name
            path = building.find_path_by_name(start_room_name, end_room_name)
            if path is None:
                return [TextContent(type="text", text=f"No path found")]
            else:
                message =  "Path found:" + " -> ".join(room.name for room in path)
                return [TextContent(type="text", text=message)]
    except Exception as e:
        error_details = traceback.format_exc()
        return [TextContent(type="text", text=f"Error occured : {str(error_details)}")] 

async def serve():
    options = server.create_initialization_options()
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)
