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

'''
 Example curl command:
 curl -X POST "http://localhost:8000/users" \
   -H "Content-Type: application/json" \
   -d '{
         "email": "example@example.com",
         "firstname": "John",
         "camera_ids": [],
         "rules_ids": [],
         "rooms_ids": []
       }
'''

'''
Sample Response
{
    "id": "5d1f051c-f17a-11ef-a29a-1be31c412e2d",
    "email": "example@example.com",
    "firstname": "John"
}
'''

@router.post("/users")
async def create_user(user: UserCreate):
    try:
        user_obj = await client.query_single(
            '''
            WITH inserted := (
                INSERT User {
                    email := <str>$email,
                    firstname := <str>$firstname,
                    camera := (SELECT Camera FILTER .id IN array_unpack(<array<uuid>>$camera_ids)),
                    rules := (SELECT Rule FILTER .id IN array_unpack(<array<uuid>>$rules_ids)),
                    rooms := (SELECT Room FILTER .id IN array_unpack(<array<uuid>>$rooms_ids))
                }
            )
            SELECT inserted { id, email, firstname };
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

# curl -X GET "http://localhost:8000/users/by_email?email=example@example.com"

'''
Sample Response :  
{
    "id": "5d1f051c-f17a-11ef-a29a-1be31c412e2d",
    "email": "example@example.com",
    "firstname": "John",
    "rules": [],
    "camera": [],
    "rooms": []
}
'''

@router.get("/users/by_email")
async def get_user_by_email(email: str):
    try:
        print (email)
        user_obj = await client.query_single(
            '''
            SELECT User {
                id,
                email,
                firstname,
                rules,
                camera,
                rooms
            }
            FILTER .email = <str>$email;
            ''',
            email=email
        )
        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")
        return user_obj
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
