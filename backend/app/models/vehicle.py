import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from app.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(255), default="Alto 800 DIY Owner")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    brand = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    engine = Column(String(150), default="F8D 796cc 3-Cyl 12V MPFI")
    variant = Column(String(100), default="LXi (Manual)")
    fuel_type = Column(String(50), default="Petrol")
    vin = Column(String(64), default="MA3EUA61S00201308")
    registration_number = Column(String(32), default="AP-09-CA-2013")
    odometer_km = Column(Integer, default=68400)
    obd_protocol = Column(
        String(120),
        default="ISO 14230-4 KWP2000 (Fast Init) / ISO 15765-4 CAN (16-Pin DLC)",
    )
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
