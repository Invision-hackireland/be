from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db import client

router = APIRouter()

class RoomCreate(BaseModel):
    name: str
    user_id: str  # The user's UUID to which this room should be added


# Example curl command to create a room:
#
# curl -X POST "http://localhost:8000/rooms" \
#   -H "Content-Type: application/json" \
#   -d '{
#         "name": "Conference Room",
#         "user_id": "YOUR_USER_UUID"
#       }'

@router.post("/rooms")
async def create_room(room: RoomCreate):
    try:
        # Create the room.
        room_obj = await client.query_single(
            '''
            INSERT Room {
                name := <str>$name
            }
            RETURNING { id, name }
            ''',
            name=room.name
        )
        
        # Update the User record to add this room to the user's rooms multi-link.
        await client.query(
            '''
            UPDATE User FILTER .id = <uuid>$user_id SET {
                rooms += (SELECT Room FILTER .id = <uuid>$room_id)
            }
            ''',
            user_id=room.user_id,
            room_id=room_obj["id"]
        )
        return room_obj
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/rooms/{room_id}")
async def delete_room(room_id: str):
    try:
        await client.query(
            '''
            DELETE Room FILTER .id = <uuid>$room_id
            ''',
            room_id=room_id
        )
        return {"status": "room deleted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/rooms")
async def get_rooms():
    try:
        rooms = await client.query(
            '''
            SELECT Room { id, name }
            '''
        )
        return rooms
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
