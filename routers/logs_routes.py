import uuid
from fastapi import APIRouter, HTTPException
from datetime import datetime
from ai.invision_ai.video_analyzer import VideoAnalyzer
from ai.invision_ai.video_annotator import VideoAnnotator
from db import client
import edgedb

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
    
@router.get("/simulate")
async def simulate_log_entry(camera_id: str, video_id: str):

    video_path = "./videos/" + video_id
    user_id = "ba3197a8-f182-11ef-80e2-77fbe9534181"

    try:
        client = edgedb.create_client()
        print("Processing video: ", video_path, user_id, camera_id)

        annotator = VideoAnnotator()
        # Run the analysis for a given camera and video file path
        annotations = annotator.run(camera_id=camera_id, video_file_path=video_path)
        print("Video Annotations done")
        
        # Now, initialize the VideoAnalyzer (OPENAI_API_KEY is loaded from .env if not passed)
        analyzer = VideoAnalyzer()
        # Analyze the annotations for potential code-of-conduct breaches
        breach_reports = analyzer.analyze(annotations, camera_id=camera_id, user_id=user_id)

        response = {
            "simulation_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "breaches": []
        }

        print("\nBreach Reports:")
        for report in breach_reports:
            breach = {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "description": report.description,
                "rule_id": str(report.rule_id),
                "severity": report.severity if hasattr(report, 'severity') else "medium",
                "location": report.location if hasattr(report, 'location') else None,
                "confidence": report.confidence if hasattr(report, 'confidence') else 0.85,
                "metadata": {
                    "frame_number": report.frame_number if hasattr(report, 'frame_number') else None,
                    "zone": report.zone if hasattr(report, 'zone') else None,
                    "additional_info": report.additional_info if hasattr(report, 'additional_info') else None
                }
            }
            response["breaches"].append(breach)

        # Add summary statistics
        response["summary"] = {
            "total_breaches": len(breach_reports),
            "timestamp": datetime.now().isoformat(),
            "camera_id": str(camera_id)
        }

        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
