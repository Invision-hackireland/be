from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db import client

router = APIRouter()

class RoomCreate(BaseModel):
    name: str
    user_id: str  # The user's UUID to which this room should be added



'''
Example Curl

curl -X POST "http://localhost:8000/rooms" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "Conference Room",
        "user_id": "YOUR_USER_UUID"
      }'
'''

# Sample Response 

'''
{
    "id": "5db9b4c2-f17f-11ef-9519-cb96c6699c26",
    "name": "Conference Room"
}
'''

@router.post("/rooms")
async def create_room(room: RoomCreate):
    try:
        # Create the room using a CTE to return the inserted record.
        room_obj = await client.query_single(
            '''
            WITH inserted := (
                INSERT Room {
                    name := <str>$name
                }
            )
            SELECT inserted { id, name };
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
            room_id=room_obj.id
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


# sample ":curl -X GET "http://localhost:8000/rooms?user_id=YOUR_USER_UUID"
@router.get("/rooms")
async def get_rooms(user_id: str):
    try:
        rooms = await client.query(
            '''
            WITH u := (
                SELECT User FILTER .id = <uuid>$user_id
            )
            SELECT u.rooms {
                id,
                name,
                num_cameras := count(.cameras),
                num_rules := count(.rules)
            };
            ''',
            user_id=user_id
        )
        return rooms
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

