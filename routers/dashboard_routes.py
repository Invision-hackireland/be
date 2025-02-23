from fastapi import APIRouter, HTTPException, Header
import datetime
import random
from db import client  # Your EdgeDB client

router = APIRouter()

@router.get("/dashboardstats")
async def dashboard_stats(
    x_user_id: str = Header(..., alias="X-User-ID"),
    authorization: str = Header(...)
):
    try:
        now = datetime.datetime.now(datetime.timezone.utc)
        start_of_day = datetime.datetime(now.year, now.month, now.day, tzinfo=datetime.timezone.utc)
        
        # Fetch the user's associated cameras, rules, and rooms.
        user = await client.query_single(
            """
            SELECT User {
                id,
                camera: { id },
                rules: { id },
                rooms: { id }
            }
            FILTER .id = <uuid>$user_id
            """,
            user_id=x_user_id
        )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        total_cameras = len(user.camera)
        active_cameras = total_cameras - random.randint(0, total_cameras // 4)
        total_rooms = len(user.rooms)
        locations = len({room.id for room in user.rooms})
        total_rules = len(user.rules)
        pending_review = random.randint(0, total_rules // 2)
        
        # Query for today's alerts count (using nested subselect for user camera IDs).
        todays_alerts_count = await client.query_single(
            """
            SELECT count(
                LogEntry FILTER (
                    .camera IN (
                        SELECT Camera
                        FILTER .id IN (
                            SELECT (SELECT User FILTER .id = <uuid>$user_id).camera.id
                        )
                    )
                    AND .time >= <datetime>$start_of_day
                )
            )
            """,
            user_id=x_user_id,
            start_of_day=start_of_day
        )
        requires_attention = random.randint(0, todays_alerts_count)
        
        overview = {
            "totalCameras": {"count": total_cameras, "active": active_cameras},
            "monitoredRooms": {"count": total_rooms, "locations": locations},
            "activeRules": {"count": total_rules, "pendingReview": pending_review},
            "todaysAlerts": {"count": todays_alerts_count, "requiresAttention": requires_attention}
        }
        
        # Simulate active monitors data.
        active_monitors = [
            {
                "id": "monitor_1",
                "name": "Main Entrance",
                "status": "online",
                "stats": {
                    "violations": 0,
                    "warnings": 2,
                    "lastCheck": (now - datetime.timedelta(minutes=2)).isoformat()
                }
            },
            {
                "id": "monitor_2",
                "name": "Production Line A",
                "status": "online",
                "stats": {
                    "violations": 1,
                    "warnings": 0,
                    "lastCheck": (now - datetime.timedelta(minutes=1)).isoformat()
                }
            }
        ]
        
        # Query recent alerts (latest 2 LogEntry items) for the user's cameras (using nested subselect).
        recent_alerts_raw = await client.query(
            """
            SELECT LogEntry {
                id,
                time,
                description,
                rule: { text },
                camera: { room: { name } }
            }
            FILTER .camera IN (
                SELECT Camera
                FILTER .id IN (
                    SELECT (SELECT User FILTER .id = <uuid>$user_id).camera.id
                )
            )
            ORDER BY .time DESC
            LIMIT 2
            """,
            user_id=x_user_id
        )
        
        recent_alerts = []
        for alert in recent_alerts_raw:
            recent_alerts.append({
                "id": alert.id,
                "type": alert.rule.text,
                "location": {
                    "room": alert.camera.room.name if alert.camera and alert.camera.room else "Unknown",
                    "camera": "Camera " + alert.id[:4]  # Dummy label
                },
                "timestamp": alert.time.isoformat(),
                "status": "pending"  # Adjust based on your business logic
            })
        
        metadata = {
            "lastUpdated": now.isoformat(),
            "timeZone": "UTC"
        }
        
        return {
            "overview": overview,
            "activeMonitors": active_monitors,
            "recentAlerts": recent_alerts,
            "metadata": metadata
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
