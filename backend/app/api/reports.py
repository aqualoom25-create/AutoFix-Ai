from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.repair import RepairRecord
from app.models.vehicle import Vehicle
from app.engine.repair_validator import validate_repair_execution

router = APIRouter(prefix="/api/reports", tags=["Repair Records & Verification"])


class RepairCreateRequest(BaseModel):
    vehicle_id: Optional[str] = None
    diagnosis_id: Optional[str] = None
    repair_description: str
    replaced_parts: List[Dict[str, Any]] = []
    before_test: Dict[str, Any] = {}
    after_test: Dict[str, Any] = {}


@router.post("")
def create_and_verify_repair_report(payload: RepairCreateRequest, db: Session = Depends(get_db)):
    vehicle_id = payload.vehicle_id
    if not vehicle_id:
        first_v = db.query(Vehicle).first()
        vehicle_id = first_v.id if first_v else "default-alto-800"

    validation = validate_repair_execution(
        before_test=payload.before_test,
        after_test=payload.after_test,
    )

    record = RepairRecord(
        vehicle_id=vehicle_id,
        diagnosis_id=payload.diagnosis_id,
        repair_description=payload.repair_description,
        replaced_parts=payload.replaced_parts,
        before_test=payload.before_test,
        after_test=payload.after_test,
        verified=validation["verified"],
        verification_report=validation,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "id": record.id,
        "vehicle_id": record.vehicle_id,
        "diagnosis_id": record.diagnosis_id,
        "repair_description": record.repair_description,
        "replaced_parts": record.replaced_parts,
        "before_test": record.before_test,
        "after_test": record.after_test,
        "verified": record.verified,
        "verification_report": record.verification_report,
        "created_at": record.created_at.isoformat() if record.created_at else None,
    }


@router.get("")
def list_repair_reports(vehicle_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(RepairRecord)
    if vehicle_id:
        query = query.filter(RepairRecord.vehicle_id == vehicle_id)
    records = query.order_by(RepairRecord.created_at.desc()).limit(30).all()
    return [
        {
            "id": r.id,
            "vehicle_id": r.vehicle_id,
            "diagnosis_id": r.diagnosis_id,
            "repair_description": r.repair_description,
            "replaced_parts": r.replaced_parts,
            "before_test": r.before_test,
            "after_test": r.after_test,
            "verified": r.verified,
            "verification_report": r.verification_report,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in records
    ]
