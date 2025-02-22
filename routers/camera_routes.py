from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from db import client

router = APIRouter()

# Note: We added a "user_id" field here so that the camera can be added to the user's camera list.
class CameraCreate(BaseModel):
    ip_address: str
    room_id: str  # UUID of the Room
    user_id: str  # UUID of the User

@router.post("/cameras")
async def create_camera(camera: CameraCreate):
    """
    Create a new camera and add it to the user's camera multi-link.

    Example curl:
    curl -X POST "http://localhost:8000/cameras" \
      -H "Content-Type: application/json" \
      -d '{
            "ip_address": "192.168.1.10",
            "room_id": "ROOM_UUID",
            "user_id": "USER_UUID"
          }'
    """
    try:
        camera_obj = await client.query_single(
            '''
            INSERT Camera {
                ip_address := <str>$ip_address,
                room := (SELECT Room FILTER .id = <uuid>$room_id)
            }
            RETURNING { id, ip_address }
            ''',
            ip_address=camera.ip_address,
            room_id=camera.room_id
        )
        await client.query(
            '''
            UPDATE User FILTER .id = <uuid>$user_id SET {
                camera += (SELECT Camera FILTER .id = <uuid>$camera_id)
            }
            ''',
            user_id=camera.user_id,
            camera_id=camera_obj["id"]
        )
        
        return camera_obj
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/cameras/{camera_id}")
async def delete_camera(camera_id: str):
    """
    Delete a camera by its ID.

    Example curl:
    curl -X DELETE "http://localhost:8000/cameras/CAMERA_UUID"
    """
    try:
        await client.query(
            '''
            DELETE Camera FILTER .id = <uuid>$camera_id
            ''',
            camera_id=camera_id
        )
        return {"status": "camera deleted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/cameras")
async def get_cameras(user_id: str = Query(None), room_id: str = Query(None)):
    """
    Retrieve cameras with optional filtering by user_id and/or room_id.

    Example curl (filter by both user and room):
    curl -X GET "http://localhost:8000/cameras?user_id=YOUR_USER_UUID&room_id=YOUR_ROOM_UUID"
    
    Example curl (all cameras):
    curl -X GET "http://localhost:8000/cameras"
    """
    filters = []
    params = {}
    
    if room_id:
        filters.append(".room.id = <uuid>$room_id")
        params["room_id"] = room_id
    if user_id:
        filters.append(
            ".id IN (SELECT cam FROM User UNNEST .camera AS cam FILTER .id = <uuid>$user_id)"
        )
        params["user_id"] = user_id
        
    # If no filters, set filter clause to always true.
    filter_clause = " AND ".join(filters) if filters else "true"
    
    query = f"""
    SELECT Camera {{
        id,
        ip_address,
        room: {{ id, name }}
    }}
    FILTER {filter_clause}
    """
    
    try:
        cameras = await client.query(query, **params)
        return cameras
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/cameras/{camera_id}/rules")
async def get_camera_rules(camera_id: str, user_id: str = Query(...)):
    """
    Returns rule texts for the specified user and camera.
    - For rules where `shared` is true, the rule is always returned.
    - For rules where `shared` is false, the rule is returned only if one of its linked rooms
      matches the room of the specified camera.

    Example curl:
    curl -X GET "http://localhost:8000/cameras/CAMERA_UUID/rules?user_id=YOUR_USER_UUID"
    """
    try:
        query = '''
        WITH 
            user_rules := (SELECT User.rules FILTER .id = <uuid>$user_id),
            camera_room := (SELECT Camera.room.id FILTER .id = <uuid>$camera_id)
        SELECT user_rules.text
        FILTER
            user_rules.shared = true OR 
            (
                user_rules.shared = false AND 
                EXISTS(
                    SELECT r 
                    FROM user_rules.rooms AS r 
                    FILTER r.id = camera_room
                )
            )
        '''
        rule_texts = await client.query(query, camera_id=camera_id, user_id=user_id)
        return rule_texts
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
