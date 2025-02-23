from .room_routes import router as room_router
from .camera_routes import router as camera_router
from .user_routes import router as user_router
from .rule_routes import router as rule_router
from .logs_routes import router as logs_router
from .dashboard_routes import router as dashboard_router

__all__ = [
    "room_router",
    "camera_router",
    "user_router",
    "rule_router",
    "logs_router"
    "dashboard_router"
]
