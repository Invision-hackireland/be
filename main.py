import asyncio
import threading

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from tasks.process_feed import background_loop_manager
from routers import room_router, camera_router, user_router, rule_router, logs_router, dashboard_router

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Start the background task when FastAPI starts."""
    thread = threading.Thread(target=background_loop_manager, daemon=True)
    thread.start()


# Include routers
app.include_router(room_router)
app.include_router(camera_router)
app.include_router(user_router)
app.include_router(rule_router)
app.include_router(logs_router)
app.include_router(dashboard_router)