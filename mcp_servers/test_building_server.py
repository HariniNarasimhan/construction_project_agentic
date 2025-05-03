import os
import json
import pytest
from unittest.mock import patch, MagicMock
from building.server import (
    Read_Building_data,
    Add_Floor,
    Add_Room,
    Remove_Room,
    Add_Door,
    Remove_Door,
    Update_Lights,
    Update_Windows,
    call_tool
)

# Test data
TEST_BUILDING_NAME = "test_building"
TEST_FLOOR_NUMBER = 1
TEST_ROOM_NAME = "test_room"
TEST_ADJACENT_ROOM = "room2"
TEST_FLOOR_DATA = {
    "rooms": {
        "room1": {
            "doors": ["room2"],
            "windows": 2,
            "lights": 3,
            "adjacent_rooms": ["room2"]
        },
        "room2": {
            "doors": ["room1"],
            "windows": 1,
            "lights": 2,
            "adjacent_rooms": ["room1"]
        }
    }
}
TEST_ROOM_DATA = {
    "name": "test_room",
    "doors": ["room2"],
    "windows": 2,
    "lights": 3,
    "adjacent_rooms": ["room2", "room1"]
}

@pytest.fixture
def mock_building_dir(tmp_path):
    """Create a temporary building directory with test data"""
    building_path = tmp_path / TEST_BUILDING_NAME
    building_path.mkdir()
    
    # Create a floor file
    floor_file = building_path / f"floor_{TEST_FLOOR_NUMBER}.json"
    with open(floor_file, "w") as f:
        json.dump(TEST_FLOOR_DATA, f)
    
    # Set the BUILDING_DIR environment variable
    os.environ["BUILDING_DIR"] = str(tmp_path)
    return str(building_path)

@pytest.fixture(autouse=True)
def setup_teardown():
    """Setup and teardown for each test"""
    # Store original environment
    original_env = os.environ.get("BUILDING_DIR")
    
    yield
    
    # Restore original environment
    if original_env is not None:
        os.environ["BUILDING_DIR"] = original_env
    else:
        os.environ.pop("BUILDING_DIR", None)

@pytest.mark.asyncio
async def test_read_building_data_success(mock_building_dir):
    """Test successful reading of building data"""
    result = await call_tool("Read_Building_data", {"building_name": TEST_BUILDING_NAME})
    assert len(result) == 1
    assert "Building data" in result[0].text
    assert str(TEST_FLOOR_NUMBER) in result[0].text
    assert "room1" in result[0].text

@pytest.mark.asyncio
async def test_read_building_data_nonexistent(mock_building_dir):
    """Test reading non-existent building data"""
    result = await call_tool("Read_Building_data", {"building_name": "nonexistent_building"})
    assert "Error" in result[0].text

@pytest.mark.asyncio
async def test_add_floor_success(mock_building_dir):
    """Test successful addition of a floor"""
    result = await call_tool("Add_Floor", {
        "building_name": TEST_BUILDING_NAME,
        "floor_number": 2,
        "floor_data": TEST_FLOOR_DATA
    })
    assert "Floor added successfully" in result[0].text

@pytest.mark.asyncio
async def test_add_floor_invalid_data(mock_building_dir):
    """Test adding floor with invalid data"""
    result = await call_tool("Add_Floor", {
        "building_name": TEST_BUILDING_NAME,
        "floor_number": 2,
        "floor_data": {"invalid": "data"}
    })
    assert "Error" in result[0].text

@pytest.mark.asyncio
async def test_add_room_success(mock_building_dir):
    """Test successful addition of a room"""
    result = await call_tool("Add_Room", {
        "building_name": TEST_BUILDING_NAME,
        "floor_number": TEST_FLOOR_NUMBER,
        "room": TEST_ROOM_DATA
    })
    assert "Room added successfully" in result[0].text

@pytest.mark.asyncio
async def test_add_room_invalid_floor(mock_building_dir):
    """Test adding room to non-existent floor"""
    result = await call_tool("Add_Room", {
        "building_name": TEST_BUILDING_NAME,
        "floor_number": 999,
        "room": TEST_ROOM_DATA
    })
    assert "Error" in result[0].text

@pytest.mark.asyncio
async def test_remove_room_success(mock_building_dir):
    """Test successful removal of a room"""
    result = await call_tool("Remove_Room", {
        "building_name": TEST_BUILDING_NAME,
        "floor_number": TEST_FLOOR_NUMBER,
        "room_name": "room1"
    })
    assert "Room removed successfully" in result[0].text

@pytest.mark.asyncio
async def test_remove_nonexistent_room(mock_building_dir):
    """Test removing non-existent room"""
    result = await call_tool("Remove_Room", {
        "building_name": TEST_BUILDING_NAME,
        "floor_number": TEST_FLOOR_NUMBER,
        "room_name": "nonexistent_room"
    })
    assert "Error" in result[0].text

@pytest.mark.asyncio
async def test_add_door_success(mock_building_dir):
    """Test successful addition of a door"""
    # add  TEST_ROOM using add_room
    result = await call_tool("Add_Room", {
        "building_name": TEST_BUILDING_NAME,
        "floor_number": TEST_FLOOR_NUMBER,
        "room": TEST_ROOM_DATA
    })
    assert "Room added successfully" in result[0].text
    result = await call_tool("Add_Door", {
        "building_name": TEST_BUILDING_NAME,
        "floor_number": TEST_FLOOR_NUMBER,
        "room_name": "room1",
        "adjacent_room_name": TEST_ROOM_NAME
    })
    assert "Door added successfully" in result[0].text

@pytest.mark.asyncio
async def test_add_door_existing_door(mock_building_dir):
    """Test adding a door to an existing door"""
    result = await call_tool("Add_Door", {
        "building_name": TEST_BUILDING_NAME,
        "floor_number": TEST_FLOOR_NUMBER,
        "room_name": "room1",
        "adjacent_room_name": "room2"
    })
    assert "Error" in result[0].text

@pytest.mark.asyncio
async def test_add_door_invalid_room(mock_building_dir):
    """Test adding door to non-existent room"""
    result = await call_tool("Add_Door", {
        "building_name": TEST_BUILDING_NAME,
        "floor_number": TEST_FLOOR_NUMBER,
        "room_name": "nonexistent_room",
        "adjacent_room_name": TEST_ADJACENT_ROOM
    })
    assert "Error" in result[0].text

@pytest.mark.asyncio
async def test_remove_door_success(mock_building_dir):
    """Test successful removal of a door"""
    result = await call_tool("Remove_Door", {
        "building_name": TEST_BUILDING_NAME,
        "floor_number": TEST_FLOOR_NUMBER,
        "room_name": "room1",
        "adjacent_room_name": "room2"
    })
    assert "Door removed successfully" in result[0].text


@pytest.mark.asyncio
async def test_remove_nonexistent_door(mock_building_dir):
    """Test removing non-existent door"""
    result = await call_tool("Remove_Door", {
        "building_name": TEST_BUILDING_NAME,
        "floor_number": TEST_FLOOR_NUMBER,
        "room_name": "room1",
        "adjacent_room_name": "nonexistent_room"
    })
    assert "Error" in result[0].text

@pytest.mark.asyncio
async def test_update_lights_success(mock_building_dir):
    """Test successful update of lights"""
    result = await call_tool("Update_Lights", {
        "building_name": TEST_BUILDING_NAME,
        "floor_number": TEST_FLOOR_NUMBER,
        "room_name": "room1",
        "new_lights": 5
    })
    assert "Lights updated successfully" in result[0].text

@pytest.mark.asyncio
async def test_update_lights_invalid_room(mock_building_dir):
    """Test updating lights in non-existent room"""
    result = await call_tool("Update_Lights", {
        "building_name": TEST_BUILDING_NAME,
        "floor_number": TEST_FLOOR_NUMBER,
        "room_name": "nonexistent_room",
        "new_lights": 5
    })
    assert "Error" in result[0].text

@pytest.mark.asyncio
async def test_update_windows_success(mock_building_dir):
    """Test successful update of windows"""
    result = await call_tool("Update_Windows", {
        "building_name": TEST_BUILDING_NAME,
        "floor_number": TEST_FLOOR_NUMBER,
        "room_name": "room1",
        "new_windows": 4
    })
    assert "Windows updated successfully" in result[0].text

@pytest.mark.asyncio
async def test_update_windows_invalid_room(mock_building_dir):
    """Test updating windows in non-existent room"""
    result = await call_tool("Update_Windows", {
        "building_name": TEST_BUILDING_NAME,
        "floor_number": TEST_FLOOR_NUMBER,
        "room_name": "nonexistent_room",
        "new_windows": 4
    })
    assert "Error" in result[0].text

@pytest.mark.asyncio
async def test_find_path_success(mock_building_dir):
    """Test successful finding of a path between rooms"""
    # First add a room and connect it to room1
    result = await call_tool("Add_Room", {
        "building_name": TEST_BUILDING_NAME,
        "floor_number": TEST_FLOOR_NUMBER,
        "room": TEST_ROOM_DATA
    })
    assert "Room added successfully" in result[0].text

    # Add a door between room1 and test_room
    result = await call_tool("Add_Door", {
        "building_name": TEST_BUILDING_NAME,
        "floor_number": TEST_FLOOR_NUMBER,
        "room_name": "room1",
        "adjacent_room_name": TEST_ROOM_NAME
    })
    assert "Door added successfully" in result[0].text

    # Remove the door between room2 and test_room
    result = await call_tool("Remove_Door", {
        "building_name": TEST_BUILDING_NAME,
        "floor_number": TEST_FLOOR_NUMBER,
        "room_name": "room2",
        "adjacent_room_name": TEST_ROOM_NAME
    })
    assert "Door removed successfully" in result[0].text
    # Now find path from room2 to test_room (should go through room1)
    result = await call_tool("Find_Path", {
        "building_name": TEST_BUILDING_NAME,
        "start_room_name": "room2",
        "end_room_name": TEST_ROOM_NAME
    })
    
    assert "Path found" in result[0].text
    assert "room2" in result[0].text
    assert "room1" in result[0].text
    assert TEST_ROOM_NAME in result[0].text

@pytest.mark.asyncio
async def test_find_path_no_path(mock_building_dir):
    """Test finding path when no path exists"""
    # Try to find path from room2 to a non-existent room
    result = await call_tool("Find_Path", {
        "building_name": TEST_BUILDING_NAME,
        "start_room_name": "room2",
        "end_room_name": "nonexistent_room"
    })
    assert "Error" in result[0].text