import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, JSON
from app.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class RepairRecord(Base):
    __tablename__ = "repair_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    vehicle_id = Column(String(36), ForeignKey("vehicles.id"), nullable=False)
    diagnosis_id = Column(String(36), ForeignKey("diagnostic_sessions.id"), nullable=True)
    repair_description = Column(String(1000), nullable=False)
    replaced_parts = Column(JSON, default=list)
    before_test = Column(JSON, default=dict)
    after_test = Column(JSON, default=dict)
    verified = Column(Boolean, default=False)
    verification_report = Column(JSON, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
