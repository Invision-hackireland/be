from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db import client

router = APIRouter()

class RuleCreate(BaseModel):
    text: str
    shared: bool
    rooms_ids: list[str] = []  # Optional list of Room UUIDs
    user_id: str             # The User's UUID to which this rule should be added

# Example curl command to create a rule:
#
# curl -X POST "http://localhost:8000/rules" \
#   -H "Content-Type: application/json" \
#   -d '{
#         "text": "Some rule text",
#         "shared": true,
#         "rooms_ids": ["ROOM_UUID1", "ROOM_UUID2"],
#         "user_id": "USER_UUID"
#       }'

@router.post("/rules")
async def create_rule(rule: RuleCreate):
    try:
        # Insert the Rule record with an optional link to rooms.
        rule_obj = await client.query_single(
            '''
            WITH
                new_rule := (
                    INSERT Rule {
                        text := <str>$text,
                        shared := <bool>$shared,
                        rooms := (SELECT Room FILTER .id IN array_unpack(<array<uuid>>$rooms_ids))
                    }
                )
            SELECT new_rule { id, text, shared }
            ''',
            text=rule.text,
            shared=rule.shared,
            rooms_ids=rule.rooms_ids
        )
        
        await client.query(
            '''
            UPDATE User FILTER .id = <uuid>$user_id SET {
                rules += (SELECT Rule FILTER .id = <uuid>$rule_id)
            }
            ''',
            user_id=rule.user_id,
            rule_id= rule_obj.id
        )
        
        return rule_obj
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
