from typing import List, Set, Dict, Optional
from dataclasses import dataclass
from collections import deque
import json
import os

def get_building_dir():
    """Get the building directory from environment variable."""
    building_dir = os.getenv("BUILDING_DIR")
    if building_dir is None:
        raise ValueError("BUILDING_DIR environment variable is not set")
    return building_dir

@dataclass
class Room:
    name: str
    doors: List[str]  # List of room names connected by doors
    windows: int
    lights: int
    adjacent_rooms: List[str]  # Names of adjacent rooms

    def add_door(self, adjacent_room: 'Room') -> None:
        """Add a door connecting to an adjacent room"""
        if adjacent_room.name in self.doors:
            raise ValueError(f"Door already exists to {adjacent_room.name} from {self.name}")
        if adjacent_room.name not in self.adjacent_rooms:
            raise ValueError(f"Room {adjacent_room.name} is not an adjacent room of {self.name}")
        self.doors.append(adjacent_room.name)
        # Add reciprocal door connection
        if self.name not in adjacent_room.doors:
            adjacent_room.doors.append(self.name)

    def remove_door(self, adjacent_room: 'Room') -> None:
        """Remove a door connection"""
        if adjacent_room.name not in self.doors:
            raise ValueError(f"Door to {adjacent_room.name} does not exist")
        self.doors.remove(adjacent_room.name)
        # Remove reciprocal door connection
        if self.name in adjacent_room.doors:
            adjacent_room.doors.remove(self.name)

    def update_lights(self, new_count: int) -> None:
        """Update the number of lights in the room"""
        if new_count < 0:
            raise ValueError("Number of lights cannot be negative")
        self.lights = new_count

    def update_windows(self, new_count: int) -> None:
        """Update the number of windows in the room"""
        if new_count < 0:
            raise ValueError("Number of windows cannot be negative")
        self.windows = new_count

class Floor:
    def __init__(self, rooms: List[Room]):
        self.rooms = rooms

    def add_room(self, room: Room) -> None:
        """Add a new room to the floor"""
        if room in self.rooms:
            raise ValueError(f"Room {room.name} already exists on this floor")
        self.rooms.append(room)
        # if the room has doors to other rooms, add the information to the other rooms
        for door in room.doors:
            other_room = self.get_room_by_name(door)
            if other_room:
                other_room.add_door(room)
        
    def get_room_by_name(self, name: str) -> Optional[Room]:
        """Get a room by name"""
        for room in self.rooms:
            if room.name == name:
                return room
        return None
    
    def remove_room(self, room: Room) -> None:
        """Remove a room from the floor"""
        if room not in self.rooms:
            raise ValueError(f"Room {room.name} does not exist on this floor")
        
        # Remove all door connections to this room
        for other_room in self.rooms:
            if room.name in other_room.doors:
                other_room.doors.remove(room.name)
        
        self.rooms.remove(room)

class Building:
    def __init__(self, floors: List[Floor], name: str = "Main Complex"):
        self.floors = floors
        self.name = name
        self._room_dict = {}  # name -> Room mapping
        self._build_room_dict()

    def _build_room_dict(self):
        """Build a dictionary mapping room names to Room objects"""
        self._room_dict = {}
        for floor in self.floors:
            for room in floor.rooms:
                self._room_dict[room.name] = room

    def add_floor(self, floor: Floor) -> None:
        """Add a new floor to the building"""
        self.floors.append(floor)

    def remove_floor(self, floor: Floor) -> None:
        """Remove a floor from the building"""
        if floor not in self.floors:
            raise ValueError("Floor does not exist in the building")
        self.floors.remove(floor)

    def find_path(self, start_room: Room, end_room: Room) -> Optional[List[Room]]:
        """
        Find a path from start_room to end_room using BFS algorithm.
        Returns a list of rooms representing the path, or None if no path exists.
        """
        if start_room == end_room:
            return [start_room]

        visited = set()
        queue = deque()
        queue.append((start_room, [start_room]))

        while queue:
            current_room, path = queue.popleft()
            visited.add(current_room.name)

            for door_name in current_room.doors:
                adjacent_room = self._room_dict[door_name]
                if adjacent_room == end_room:
                    return path + [adjacent_room]
                
                if adjacent_room.name not in visited:
                    queue.append((adjacent_room, path + [adjacent_room]))
                    visited.add(adjacent_room.name)

        return None  # No path found

    def find_path_by_name(self, start_room_name: str, end_room_name: str) -> Optional[List[Room]]:
        """
        Find a path between two rooms using their names.
        Returns a list of rooms representing the path, or None if no path exists.
        """
        if start_room_name not in self._room_dict:
            raise ValueError(f"Start room '{start_room_name}' not found")
        if end_room_name not in self._room_dict:
            raise ValueError(f"End room '{end_room_name}' not found")
        
        return self.find_path(self._room_dict[start_room_name], self._room_dict[end_room_name])

    def to_json(self, building_name: str = "Main Complex") -> None:
        """
        Save the building data to JSON files in the specified directory.
        Each floor will be saved in a separate file named 'floor_N.json'.
        """
        building_dir = get_building_dir()
        # Create directory if it doesn't exist
        directory_path = os.path.join(building_dir, building_name)  
        os.makedirs(directory_path, exist_ok=True)
        
        # Save each floor to a separate file
        for floor_num, floor in enumerate(self.floors, 1):
            floor_dict = {"rooms": {}}
            for room in floor.rooms:
                floor_dict["rooms"][room.name] = {
                    "windows": room.windows,
                    "lights": room.lights,
                    "adjacent_rooms": room.adjacent_rooms,
                    "doors": room.doors
                }
            
            # Save floor data to file
            floor_path = os.path.join(directory_path, f"floor_{floor_num}.json")
            with open(floor_path, 'w') as f:
                json.dump(floor_dict, f, indent=2)
        
        # Save building metadata
        metadata = {
            "building_name": self.name,
            "num_floors": len(self.floors)
        }
        metadata_path = os.path.join(directory_path, "building_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)


def load_building_from_directory(building_name: str = "Main Complex") -> Building:
    """
    Load building data from a directory containing floor JSON files.
    Each floor should be in a separate JSON file named 'floor_N.json' where N is the floor number.
    """
    building_dir = get_building_dir()
    directory_path = os.path.join(building_dir, building_name)
    floors = []
    room_instances = {}  # name -> Room instance
    
    # First pass: create all rooms from all floor files
    for filename in sorted(os.listdir(directory_path)):
        if filename.startswith('floor_') and filename.endswith('.json'):
            floor_path = os.path.join(directory_path, filename)
            with open(floor_path, 'r') as f:
                floor_data = json.load(f)
                
                # Create rooms for this floor
                for room_name, room_data in floor_data["rooms"].items():
                    if room_name not in room_instances:
                        room = Room(
                            name=room_name,
                            doors=[],
                            windows=room_data["windows"],
                            lights=room_data["lights"],
                            adjacent_rooms=room_data["adjacent_rooms"]
                        )
                        room_instances[room_name] = room
    
    # Second pass: create floors and connect rooms
    for filename in sorted(os.listdir(directory_path)):
        if filename.startswith('floor_') and filename.endswith('.json'):
            floor_path = os.path.join(directory_path, filename)
            with open(floor_path, 'r') as f:
                floor_data = json.load(f)
                rooms = []
                
                # Add rooms to this floor
                for room_name, room_data in floor_data["rooms"].items():
                    room = room_instances[room_name]
                    rooms.append(room)
                    
                    # Connect doors
                    for adj_room_name in room_data["doors"]:
                        if adj_room_name not in room.doors:
                            room.doors.append(adj_room_name)
                
                floor = Floor(rooms)
                floors.append(floor)
    
    return Building(floors, building_name)


# if __name__ == "__main__":
#     # Load building from directory
#     building = load_building_from_directory("Main")
    
#     # Example: find path from Room1 to Room17 using room names
#     try:
#         path = building.find_path_by_name("Office_Room_2", "Auditorium_3")
#         if path:
#             print("Path found:", " -> ".join(room.name for room in path))
#         else:
#             print("No path found")
#     except ValueError as e:
#         print(f"Error: {e}")
    
#     # Save the building back to the directory
#     building.to_json(building_name)