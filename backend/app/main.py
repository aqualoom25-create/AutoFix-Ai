import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from app.database import Base, engine, SessionLocal
from app.models.vehicle import User, Vehicle
from app.models.diagnostic import DiagnosticSession
from app.models.repair import RepairRecord
from app.api import vehicles_router, diagnosis_router, reports_router, hardware_router
from app.engine.diagnostic_rules import run_diagnostic_engine
from app.engine.repair_validator import validate_repair_execution


def seed_initial_data():
    db = SessionLocal()
    try:
        if db.query(Vehicle).count() == 0:
            user = User(email="owner@autofix-ai.local", full_name="Alto 800 Owner")
            db.add(user)
            db.flush()

            alto800 = Vehicle(
                user_id=user.id,
                brand="Maruti Suzuki",
                model="Alto 800",
                year=2013,
                engine="F8D 796cc 3-Cylinder 12-Valve SOHC MPFI",
                variant="LXi • Manual (5MT) • BS-IV",
                fuel_type="Petrol",
                vin="MA3EUA61S00201308",
                registration_number="AP-09-CA-2013",
                odometer_km=68450,
                obd_protocol="ISO 14230-4 KWP2000 (Fast Init Pin 7) / ISO 15765-4 CAN (Pins 6 & 14)",
            )
            db.add(alto800)
            db.flush()

            sample_telemetry = {
                "rpm": 1120,
                "coolant_temp_c": 91,
                "map_kpa": 64,
                "iat_c": 41,
                "tps_percent": 0.5,
                "stft_bank1_percent": 18.6,
                "ltft_bank1_percent": 26.2,
                "o2_b1s1_voltage_v": 0.14,
                "battery_voltage_v": 13.9,
            }
            initial_diag = run_diagnostic_engine(
                dtc_codes=["P0105", "P0171"],
                symptoms=["Rough or surging idle", "Poor fuel mileage"],
                live_telemetry=sample_telemetry,
                qa_responses={"q_map_idle": "yes"},
            )
            diag_session = DiagnosticSession(
                vehicle_id=alto800.id,
                symptoms=["Rough or surging idle", "Poor fuel mileage"],
                dtc_codes=["P0105", "P0171"],
                live_telemetry=sample_telemetry,
                qa_responses={"q_map_idle": "yes"},
                diagnosis=initial_diag,
            )
            db.add(diag_session)
            db.flush()

            before_data = {
                "dtc_codes": ["P0105", "P0171"],
                "rpm": 1120,
                "map_kpa": 64,
                "coolant_temp_c": 91,
                "stft_bank1_percent": 18.6,
                "ltft_bank1_percent": 26.2,
                "battery_voltage_v": 13.9,
            }
            after_data = {
                "dtc_codes": [],
                "rpm": 805,
                "map_kpa": 32,
                "coolant_temp_c": 90,
                "stft_bank1_percent": 1.4,
                "ltft_bank1_percent": 2.1,
                "battery_voltage_v": 14.1,
            }
            verification = validate_repair_execution(before_data, after_data)
            sample_repair = RepairRecord(
                vehicle_id=alto800.id,
                diagnosis_id=diag_session.id,
                repair_description=(
                    "Cleaned oil blow-by from F8D intake plenum port, replaced cracked MAP sensor O-ring "
                    "(MGP 09280-10016) & split PCV hose, verified Pin 3 5.02V reference and Pin 4 1.32V idle signal."
                ),
                replaced_parts=[
                    {"name": "O-Ring, MAP Sensor Seal", "mgp_part_number": "09280-10016", "cost_inr": 45},
                    {"name": "Valve & Hose, PCV", "mgp_part_number": "18118-78G50", "cost_inr": 240},
                ],
                before_test=before_data,
                after_test=after_data,
                verified=verification["verified"],
                verification_report=verification,
            )
            db.add(sample_repair)
            db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_initial_data()
    yield


app = FastAPI(
    title="AutoFix AI — Automotive Engineering & DIY Diagnostic SaaS",
    description=(
        "Full-stack AI diagnostic engine, F8D wiring pinout analyzer, OBD-II/KWP2000 hardware bridge, "
        "guided DIY repair procedures, and post-repair verification for the 2013 Maruti Suzuki Alto 800 (0.8L Petrol)."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(vehicles_router)
app.include_router(diagnosis_router)
app.include_router(reports_router)
app.include_router(hardware_router)


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "service": "AutoFix AI SaaS Backend",
        "version": "1.0.0",
        "target_vehicle": "2013 Maruti Suzuki Alto 800 (0.8L F8D 12V MPFI Petrol)",
    }


@app.get("/", response_class=HTMLResponse)
def serve_saas_dashboard():
    static_html = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "index.html")
    if os.path.exists(static_html):
        with open(static_html, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return JSONResponse({"message": "AutoFix AI API is running. Visit /docs for OpenAPI documentation."})
