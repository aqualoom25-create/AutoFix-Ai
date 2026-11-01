# AutoFix AI — Complete Automotive Engineering & DIY Diagnostic SaaS + Hardware Suite
### Flagship Target Vehicle: **2013 Maruti Suzuki Alto 800 (0.8L F8D 12-Valve MPFI Petrol • BS-IV • Manual)**

AutoFix AI is an end-to-end automotive diagnostic SaaS platform, wiring & multimeter verification laboratory, guided DIY repair system (with Maruti Genuine Parts `MGP` numbers & torque specifications), and dual-protocol hardware scanner bridge (`ISO 14230-4 KWP2000` on DLC Pin 7 & `ISO 15765-4 CAN` on DLC Pins 6 & 14).

---

## Project Structure
```text
autofix-ai/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI SaaS Server + Interactive Web UI + Auto-Seeding
│   │   ├── database.py              # PostgreSQL & SQLite Zero-Config ORM Engine
│   │   ├── models/
│   │   │   ├── vehicle.py           # User & Vehicle Models
│   │   │   ├── diagnostic.py        # DiagnosticSession Model
│   │   │   └── repair.py            # RepairRecord & Verification Certificate Model
│   │   ├── api/
│   │   │   ├── vehicles.py          # Vehicle Registration & F8D Engineering Specs API
│   │   │   ├── diagnosis.py         # AI Fault Analysis, Knowledge Base & Multimeter API
│   │   │   ├── reports.py           # Before/After Repair Verification & Reports API
│   │   │   └── hardware.py          # OBD-II / KWP2000 Serial Bridge & F8D ECU Simulator API
│   │   ├── engine/
│   │   │   ├── dtc_engine.py        # Alto 800 DTC Decoder & Multi-Code Correlation Engine
│   │   │   ├── diagnostic_rules.py  # Bayesian Symptom + Telemetry + Owner Q&A Rule Engine
│   │   │   └── repair_validator.py  # Post-Repair Telemetry & Multimeter Pinout Validator
│   │   └── static/
│   │       └── index.html           # Complete Interactive 6-Tab AutoFix AI SaaS Web App
│   ├── tests/
│   │   └── test_alto800_saas.py     # End-to-End Pytest Suite
│   ├── schema.sql                   # PostgreSQL / SQLite Database Schema
│   ├── Dockerfile                   # Backend Container Build
│   └── requirements.txt             # Python Dependencies
├── frontend/
│   ├── app/
│   │   ├── page.tsx                 # Next.js My Garage Dashboard
│   │   ├── garage/page.tsx          # F8D Vehicle Specs View
│   │   ├── diagnostics/page.tsx     # AI Diagnostic Console
│   │   └── reports/page.tsx         # Verified Repair Certificates
│   └── package.json
├── android/
│   └── AutoFixAI/                   # Android Companion App + Bluetooth Classic SPP OBD-II Service
├── knowledge_base/
│   ├── vehicles/
│   │   └── maruti_alto_800_2013_petrol.json
│   ├── dtc_codes/
│   │   └── alto_800_dtc_catalog.json
│   ├── wiring_diagrams/
│   │   └── alto_800_f8d_ecm_wiring.json
│   └── repair_procedures/
│       └── alto_800_service_procedures.json
├── hardware/
│   ├── obd_adapter/
│   │   └── elm327_alto800_scanner.py                # Live Python USB/Bluetooth ELM327/KWP2000 Scanner
│   └── can_interface/
│       ├── esp32_alto800_kline_can_firmware.ino     # Custom ESP32 + L9637D + SN65HVD230 Firmware
│       └── HARDWARE_BOM_AND_SCHEMATIC.md            # Complete Hardware BOM & 16-Pin DLC Schematic
├── docker-compose.yml               # Full Docker Compose Stack (PostgreSQL + Backend)
├── start_autofix.bat                # 1-Click Windows Local Launcher (No Docker Required)
└── README.md
```

---

## How to Launch the SaaS Application

### Option 1 — Instant Local Launch on Windows (No Docker Required)
```powershell
# 1. Install Python dependencies (one-time)
pip install -r backend/requirements.txt

# 2. Launch AutoFix AI on port 8080
.\start_autofix.bat
```
- **AutoFix AI SaaS Dashboard**: http://localhost:8080
- **Interactive OpenAPI Console**: http://localhost:8080/docs

### Option 2 — Docker Compose (PostgreSQL + Backend Service)
```bash
docker compose up --build -d
```

---

## Hardware Strategy for 2013 Maruti Suzuki Alto 800 (Petrol)
1. **16-Pin DLC Connector Location**: Under driver-side dashboard, lower right near steering column and fuse box.
2. **Protocols**:
   - **Pin 7 (Purple/Yellow)**: `ISO 14230-4 KWP2000 (Fast Init, 10.4 kbps)` — ECM physical address `0x10`, header `81 10 F1`.
   - **Pins 6 & 14 (White/Red & White)**: `ISO 15765-4 CAN (11-bit, 500 kbps)` — ECM request `0x7E0`, response `0x7E8`.
3. **Live Hardware Scanner Script**:
   ```bash
   python hardware/obd_adapter/elm327_alto800_scanner.py --port COM3 --baud 38400 --api http://localhost:8080
   ```
