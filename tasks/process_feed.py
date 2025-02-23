import json
import multiprocessing
import os
import edgedb
from video_processor import VideoProcessor
from video_recorder import VideoSnippetRecorder

from ai.invision_ai.video_analyzer import VideoAnalyzer
from ai.invision_ai.video_annotator import VideoAnnotator

processor = VideoProcessor()

def fetch_video_task():
    recorder = VideoSnippetRecorder()
    client = edgedb.create_client()
    print("Starting to sync camera")
    while True:
        if len(client.query('select Camera')) == 0:
            continue

        video_path = recorder.record_snippet()
        current_chunks = json.loads(client.query_json('''
            SELECT Camera {
                chunks,
                id
            };
        '''))[0]['chunks']
        current_chunks.append(video_path)
        client.query_json('''
            UPDATE Camera 
            SET {
                chunks := <array<str>>%s,
            }
        ''' % json.dumps(current_chunks))
            
def process_video(video_path, user_id, camera_id):
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

    print("\nBreach Reports:")
    if breach_reports:
        for report in breach_reports:
            client.query_json('''
                with cam := (SELECT Camera FILTER .id = <uuid>$camera_id)
                UPDATE Camera
                FILTER .id = <uuid>$camera_id
                SET {
                    logs += (select (INSERT LogEntry {
                        description := <str>$description,
                        camera := cam,
                        time := <datetime>datetime_current(),
                        rule := (SELECT Rule FILTER .id = <uuid>$rule_id),
                    }))
                }
            ''', description=report.description, camera_id=camera_id, rule_id=report.rule_id)
    else:
        print("No breaches detected.")
    

def process_video_task():
    client = edgedb.create_client()
    while True:
        if len(client.query('select Camera')) == 0:
            continue

        result = json.loads(client.query_json('''
            SELECT Camera {
                id,
                chunks
            };
        '''))
        chunks = result[0]['chunks']
        camera_id = result[0]['id']
        user_id = json.loads(client.query_json('''
            SELECT User {
                id,
                camera: {
                    id
                }
            } FILTER .camera.id = <uuid>$camera_id;
        ''', camera_id=camera_id))[0]['id']

        if len(chunks) > 0:
            print("Processing video")
            process_video(chunks.pop(0), user_id, camera_id)
            client.query_json('''
                UPDATE Camera 
                SET {
                    chunks := <array<str>>%s,
                }
            ''' % json.dumps(chunks))

def spawn_processes():
    init_loop()
    
    # Spawn two separate processes
    p1 = multiprocessing.Process(target=fetch_video_task, daemon=True)
    p2 = multiprocessing.Process(target=process_video_task, daemon=True)
    
    p1.start()
    p2.start()

    # Keep the background loop alive (not necessary if main thread stays active)
    p1.join()
    p2.join()

def init_loop():
    client = edgedb.create_client()
    # Clear all chunks
    os.system('rm -rf ./tmp/*')
    client.query_json('''
        UPDATE Camera 
        SET {
            chunks := <array<str>>[],
        }
    ''')

def background_loop_manager():
    return
    init_loop()
    spawn_processes()