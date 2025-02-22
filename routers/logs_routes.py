from fastapi import APIRouter, HTTPException
from datetime import datetime
from db import client

router = APIRouter()

@router.get("/rooms/{room_id}/logs")
async def get_logs_for_room(room_id: str, start_time: str, end_time: str):
    try:
        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS).")
    
    try:
        logs = await client.query(
            '''
            SELECT LogEntry {
                id,
                time,
                description,
                rule: { id, text },
                camera: { id, ip_address }
            }
            FILTER .camera.room.id = <uuid>$room_id AND .time >= <datetime>$start AND .time <= <datetime>$end
            ''',
            room_id=room_id,
            start=start,
            end=end
        )
        return logs
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
