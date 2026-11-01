from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.diagnostic import DiagnosticSession
from app.models.vehicle import Vehicle
from app.engine.dtc_engine import KnowledgeBaseLoader, decode_dtc
from app.engine.diagnostic_rules import run_diagnostic_engine
from app.engine.repair_validator import validate_multimeter_measurement

router = APIRouter(prefix="/api/diagnosis", tags=["Diagnostics & AI Engine"])


class DiagnosisRequest(BaseModel):
    vehicle_id: Optional[str] = None
    dtc_codes: List[str] = []
    symptoms: List[str] = []
    live_telemetry: Optional[Dict[str, Any]] = None
    qa_responses: Optional[Dict[str, str]] = None


class MultimeterCheckRequest(BaseModel):
    circuit_id: str
    ref_voltage_v: Optional[float] = None
    signal_voltage_v: Optional[float] = None
    resistance_ohms: Optional[float] = None
    mode: str = "idle"


@router.post("/analyze")
def analyze_vehicle_faults(payload: DiagnosisRequest, db: Session = Depends(get_db)):
    vehicle_id = payload.vehicle_id
    if not vehicle_id:
        first_vehicle = db.query(Vehicle).first()
        if first_vehicle:
            vehicle_id = first_vehicle.id

    result = run_diagnostic_engine(
        dtc_codes=payload.dtc_codes,
        symptoms=payload.symptoms,
        live_telemetry=payload.live_telemetry,
        qa_responses=payload.qa_responses,
    )

    session_record = DiagnosticSession(
        vehicle_id=vehicle_id or "default-alto-800",
        symptoms=payload.symptoms,
        dtc_codes=result["evaluated_dtc_codes"],
        live_telemetry=payload.live_telemetry or {},
        qa_responses=payload.qa_responses or {},
        diagnosis=result,
    )
    db.add(session_record)
    db.commit()
    db.refresh(session_record)

    return {
        "session_id": session_record.id,
        "vehicle_id": session_record.vehicle_id,
        "created_at": session_record.created_at.isoformat() if session_record.created_at else None,
        "diagnosis": result,
    }


@router.get("/sessions")
def list_diagnostic_sessions(vehicle_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(DiagnosticSession)
    if vehicle_id:
        query = query.filter(DiagnosticSession.vehicle_id == vehicle_id)
    sessions = query.order_by(DiagnosticSession.created_at.desc()).limit(30).all()
    return [
        {
            "id": s.id,
            "vehicle_id": s.vehicle_id,
            "symptoms": s.symptoms,
            "dtc_codes": s.dtc_codes,
            "live_telemetry": s.live_telemetry,
            "qa_responses": s.qa_responses,
            "diagnosis": s.diagnosis,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in sessions
    ]


@router.get("/dtc/{code}")
def lookup_dtc_code(code: str):
    return decode_dtc(code)


@router.get("/knowledge-base")
def get_full_knowledge_base():
    kb = KnowledgeBaseLoader.get()
    return {
        "vehicle_spec": kb.vehicle_spec,
        "dtc_catalog": kb.dtc_catalog,
        "wiring_data": kb.wiring_data,
        "procedures": kb.procedures,
    }


@router.post("/multimeter-check")
def check_multimeter_values(payload: MultimeterCheckRequest):
    result = validate_multimeter_measurement(
        circuit_id=payload.circuit_id,
        ref_voltage_v=payload.ref_voltage_v,
        signal_voltage_v=payload.signal_voltage_v,
        resistance_ohms=payload.resistance_ohms,
        mode=payload.mode,
    )
    if not result.get("valid", True) and "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
