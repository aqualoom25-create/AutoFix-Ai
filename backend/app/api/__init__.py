from app.api.vehicles import router as vehicles_router
from app.api.diagnosis import router as diagnosis_router
from app.api.reports import router as reports_router
from app.api.hardware import router as hardware_router
from app.api.manuals import router as manuals_router
from app.api.vision import router as vision_router

__all__ = [
    "vehicles_router",
    "diagnosis_router",
    "reports_router",
    "hardware_router",
    "manuals_router",
    "vision_router",
]
