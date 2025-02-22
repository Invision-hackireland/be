from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db import client

router = APIRouter()

class UserCreate(BaseModel):
    email: str
    firstname: str
    camera_ids: list[str] = []  # List of Camera UUIDs
    rules_ids: list[str] = []   # List of Rule UUIDs
    rooms_ids: list[str] = []   # List of Room UUIDs

@router.post("/users")
async def create_user(user: UserCreate):
    try:
        user_obj = await client.query_single(
            '''
            INSERT User {
                email := <str>$email,
                firstname := <str>$firstname,
                camera := (SELECT Camera FILTER .id IN <array<uuid>>$camera_ids),
                rules := (SELECT Rule FILTER .id IN <array<uuid>>$rules_ids),
                rooms := (SELECT Room FILTER .id IN <array<uuid>>$rooms_ids)
            }
            RETURNING { id, email, firstname }
            ''',
            email=user.email,
            firstname=user.firstname,
            camera_ids=user.camera_ids,
            rules_ids=user.rules_ids,
            rooms_ids=user.rooms_ids
        )
        return user_obj
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
