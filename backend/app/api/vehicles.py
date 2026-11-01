from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.vehicle import Vehicle
from app.engine.dtc_engine import KnowledgeBaseLoader

router = APIRouter(prefix="/api/vehicles", tags=["Vehicles"])


class VehicleCreate(BaseModel):
    brand: str = "Maruti Suzuki"
    model: str = "Alto 800"
    year: int = 2013
    engine: Optional[str] = "F8D 796cc 3-Cyl 12V MPFI"
    variant: Optional[str] = "LXi (Manual)"
    fuel_type: Optional[str] = "Petrol"
    vin: Optional[str] = "MA3EUA61S00201308"
    registration_number: Optional[str] = "AP-09-CA-2013"
    odometer_km: Optional[int] = 68400
    obd_protocol: Optional[str] = "ISO 14230-4 KWP2000 (Fast Init) / ISO 15765-4 CAN"


@router.get("")
def list_vehicles(db: Session = Depends(get_db)):
    vehicles = db.query(Vehicle).order_by(Vehicle.created_at.desc()).all()
    return [
        {
            "id": v.id,
            "brand": v.brand,
            "model": v.model,
            "year": v.year,
            "engine": v.engine,
            "variant": v.variant,
            "fuel_type": v.fuel_type,
            "vin": v.vin,
            "registration_number": v.registration_number,
            "odometer_km": v.odometer_km,
            "obd_protocol": v.obd_protocol,
            "created_at": v.created_at.isoformat() if v.created_at else None,
        }
        for v in vehicles
    ]


@router.post("")
def create_vehicle(payload: VehicleCreate, db: Session = Depends(get_db)):
    vehicle = Vehicle(
        brand=payload.brand,
        model=payload.model,
        year=payload.year,
        engine=payload.engine,
        variant=payload.variant,
        fuel_type=payload.fuel_type,
        vin=payload.vin,
        registration_number=payload.registration_number,
        odometer_km=payload.odometer_km,
        obd_protocol=payload.obd_protocol,
    )
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return {
        "id": vehicle.id,
        "brand": vehicle.brand,
        "model": vehicle.model,
        "year": vehicle.year,
        "engine": vehicle.engine,
        "variant": vehicle.variant,
        "fuel_type": vehicle.fuel_type,
        "vin": vehicle.vin,
        "registration_number": vehicle.registration_number,
        "odometer_km": vehicle.odometer_km,
        "obd_protocol": vehicle.obd_protocol,
    }


@router.get("/spec/alto-800-2013")
def get_alto_800_engineering_spec():
    kb = KnowledgeBaseLoader.get()
    return kb.vehicle_spec


@router.get("/{vehicle_id}")
def get_vehicle(vehicle_id: str, db: Session = Depends(get_db)):
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    kb = KnowledgeBaseLoader.get()
    return {
        "id": v.id,
        "brand": v.brand,
        "model": v.model,
        "year": v.year,
        "engine": v.engine,
        "variant": v.variant,
        "fuel_type": v.fuel_type,
        "vin": v.vin,
        "registration_number": v.registration_number,
        "odometer_km": v.odometer_km,
        "obd_protocol": v.obd_protocol,
        "engineering_spec": kb.vehicle_spec,
    }
