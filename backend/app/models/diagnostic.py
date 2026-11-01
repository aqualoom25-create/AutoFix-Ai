import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from app.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class DiagnosticSession(Base):
    __tablename__ = "diagnostic_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    vehicle_id = Column(String(36), ForeignKey("vehicles.id"), nullable=False)
    symptoms = Column(JSON, default=list)
    dtc_codes = Column(JSON, default=list)
    live_telemetry = Column(JSON, default=dict)
    qa_responses = Column(JSON, default=dict)
    diagnosis = Column(JSON, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
