import json
import os
import sqlite3
from typing import Dict, Any, List, Optional, Tuple

ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(os.path.dirname(ENGINE_DIR))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
KB_DIR = os.path.join(PROJECT_ROOT, "knowledge_base")
MASTER_DB_PATH = os.path.join(BACKEND_DIR, "autofix_master_20k.db")

# 125 Authentic 2013 Maruti Suzuki Alto 800 (FB308 / F8D 796cc 12V MPFI Petrol) Components & Subsystems
ALTO800_COMPONENTS: List[Dict[str, Any]] = [
    # --- SECTION 1F / 1C / 1D: ECM SENSORS, ACTUATORS & OBD-II CIRCUITS (1..35) ---
    {"comp_id": "CMP-001", "name": "MAP Sensor Pressure Element", "section": "SEC-1F", "category": "OBD-II Real-Time DTC", "base_dtc": "P0105", "mgp": "18590-68K00", "cost": 1480, "torque": 6, "pin": "ECM C44 (Pin 4)", "wire": "Lg/R (Light Green/Red)", "gnd": "G3", "fuse": "F-01 (15A FI)", "zone": (380, 145), "spec": "1.15-1.55V @ Idle (30-35 kPa)"},
    {"comp_id": "CMP-002", "name": "MAP Sensor 5V Reference Line", "section": "SEC-1F", "category": "Electrical & Wiring Routing", "base_dtc": "P0107", "mgp": "18590-68K00", "cost": 1480, "torque": 6, "pin": "ECM C32 (Pin 3)", "wire": "R/Bl (Red/Blue)", "gnd": "G3", "fuse": "F-01 (15A FI)", "zone": (382, 148), "spec": "4.85-5.15V Regulated 5V"},
    {"comp_id": "CMP-003", "name": "MAP Sensor Signal High / Boost Short", "section": "SEC-1F", "category": "OBD-II Real-Time DTC", "base_dtc": "P0108", "mgp": "09280-10016", "cost": 45, "torque": 6, "pin": "ECM C44 (Pin 4)", "wire": "Lg/R (Light Green/Red)", "gnd": "G3", "fuse": "F-01 (15A FI)", "zone": (385, 142), "spec": "< 4.30V KOEO (~101 kPa)"},
    {"comp_id": "CMP-004", "name": "Intake Air Temperature (IAT) Thermistor", "section": "SEC-1F", "category": "OBD-II Real-Time DTC", "base_dtc": "P0110", "mgp": "18590-68K00", "cost": 1480, "torque": 6, "pin": "ECM C40 (Pin 1)", "wire": "Lg/B (Light Green/Black)", "gnd": "G3", "fuse": "F-01 (15A FI)", "zone": (375, 150), "spec": "1.8-2.8V @ 25-35°C (2.2kΩ)"},
    {"comp_id": "CMP-005", "name": "IAT Sensor Circuit Low Input", "section": "SEC-1F", "category": "Electrical & Wiring Routing", "base_dtc": "P0112", "mgp": "18590-68K00", "cost": 1480, "torque": 6, "pin": "ECM C40 (Pin 1)", "wire": "Lg/B (Light Green/Black)", "gnd": "G3", "fuse": "F-01 (15A FI)", "zone": (376, 152), "spec": "0.2-4.6V Operating Range"},
    {"comp_id": "CMP-006", "name": "IAT Sensor Circuit High Input (Open)", "section": "SEC-1F", "category": "Electrical & Wiring Routing", "base_dtc": "P0113", "mgp": "18590-68K00", "cost": 1480, "torque": 6, "pin": "ECM C40 (Pin 1)", "wire": "Lg/B (Light Green/Black)", "gnd": "G3", "fuse": "F-01 (15A FI)", "zone": (378, 154), "spec": "5.0V Pull-up via ECM 3.9kΩ"},
    {"comp_id": "CMP-007", "name": "Engine Coolant Temp (ECT) Sensor", "section": "SEC-1B", "category": "OBD-II Real-Time DTC", "base_dtc": "P0115", "mgp": "13650-78G00", "cost": 395, "torque": 15, "pin": "ECM C41 (Pin 1)", "wire": "Lg/W (Light Green/White)", "gnd": "G3", "fuse": "F-01 (15A FI)", "zone": (345, 175), "spec": "290-350Ω @ 80°C (0.5-0.85V)"},
    {"comp_id": "CMP-008", "name": "ECT Sensor Signal Low (Shorted Hot)", "section": "SEC-1B", "category": "Electrical & Wiring Routing", "base_dtc": "P0117", "mgp": "13650-78G00", "cost": 395, "torque": 15, "pin": "ECM C41 (Pin 1)", "wire": "Lg/W (Light Green/White)", "gnd": "G3", "fuse": "F-01 (15A FI)", "zone": (348, 178), "spec": "> 0.15V (< 115°C)"},
    {"comp_id": "CMP-009", "name": "ECT Sensor Signal High (Open -40°C)", "section": "SEC-1B", "category": "Electrical & Wiring Routing", "base_dtc": "P0118", "mgp": "13650-78G00", "cost": 395, "torque": 15, "pin": "ECM C41 (Pin 1)", "wire": "Lg/W (Light Green/White)", "gnd": "G3", "fuse": "RLY-FAN", "zone": (342, 172), "spec": "2,200-2,700Ω @ 20°C"},
    {"comp_id": "CMP-010", "name": "Throttle Position Sensor (TPS) Potentiometer", "section": "SEC-1F", "category": "OBD-II Real-Time DTC", "base_dtc": "P0120", "mgp": "13420-79G00", "cost": 1150, "torque": 3, "pin": "ECM C43 (Pin 2)", "wire": "Y/G (Yellow/Green)", "gnd": "G3", "fuse": "F-01 (15A FI)", "zone": (360, 138), "spec": "0.45-0.65V Closed -> 4.3V WOT"},
    {"comp_id": "CMP-011", "name": "TPS Circuit Low Voltage Input", "section": "SEC-1F", "category": "Electrical & Wiring Routing", "base_dtc": "P0122", "mgp": "13420-79G00", "cost": 1150, "torque": 3, "pin": "ECM C43 (Pin 2)", "wire": "Y/G (Yellow/Green)", "gnd": "G3", "fuse": "F-01 (15A FI)", "zone": (362, 140), "spec": ">= 0.45V at Idle Stop"},
    {"comp_id": "CMP-012", "name": "TPS Circuit High Voltage Input", "section": "SEC-1F", "category": "Electrical & Wiring Routing", "base_dtc": "P0123", "mgp": "13420-79G00", "cost": 1150, "torque": 3, "pin": "ECM C43 (Pin 2)", "wire": "Y/G (Yellow/Green)", "gnd": "G3", "fuse": "F-01 (15A FI)", "zone": (364, 136), "spec": "<= 4.75V at Full Throttle"},
    {"comp_id": "CMP-013", "name": "Upstream Oxygen Sensor (HO2S-1 B1S1)", "section": "SEC-1C", "category": "OBD-II Real-Time DTC", "base_dtc": "P0130", "mgp": "18213-68K00", "cost": 2690, "torque": 45, "pin": "ECM C46 (Pin 1)", "wire": "Y/R (Yellow/Red)", "gnd": "G3", "fuse": "RLY-MAIN", "zone": (310, 150), "spec": "0.15-0.85V Cycling @ 2000 RPM"},
    {"comp_id": "CMP-014", "name": "Upstream O2 Sensor Low Voltage (Stuck Lean)", "section": "SEC-1C", "category": "OBD-II Real-Time DTC", "base_dtc": "P0131", "mgp": "18213-68K00", "cost": 2690, "torque": 45, "pin": "ECM C46 (Pin 1)", "wire": "Y/R (Yellow/Red)", "gnd": "G3", "fuse": "RLY-MAIN", "zone": (312, 152), "spec": "Crosses 0.45V >= 5 times/10s"},
    {"comp_id": "CMP-015", "name": "Upstream O2 Sensor High Voltage (Stuck Rich)", "section": "SEC-1C", "category": "OBD-II Real-Time DTC", "base_dtc": "P0132", "mgp": "18213-68K00", "cost": 2690, "torque": 45, "pin": "ECM C46 (Pin 1)", "wire": "Y/R (Yellow/Red)", "gnd": "G3", "fuse": "RLY-MAIN", "zone": (314, 148), "spec": "0.10-0.90V Zirconia Swing"},
    {"comp_id": "CMP-016", "name": "Upstream O2 Sensor Slow Response", "section": "SEC-1C", "category": "OBD-II Real-Time DTC", "base_dtc": "P0133", "mgp": "18213-68K00", "cost": 2690, "torque": 45, "pin": "ECM C46 (Pin 1)", "wire": "Y/R (Yellow/Red)", "gnd": "G3", "fuse": "RLY-MAIN", "zone": (315, 150), "spec": "< 150ms Lean-to-Rich Transition"},
    {"comp_id": "CMP-017", "name": "Upstream O2 Sensor Heater Coil Circuit", "section": "SEC-1C", "category": "Electrical & Wiring Routing", "base_dtc": "P0135", "mgp": "18213-68K00", "cost": 2690, "torque": 45, "pin": "ECM C05 (Pin 4)", "wire": "P/B (Pink/Black)", "gnd": "G3", "fuse": "F-01 (15A FI)", "zone": (310, 155), "spec": "5.0-9.5Ω Heater @ 20°C (12V)"},
    {"comp_id": "CMP-018", "name": "Downstream Oxygen Sensor (HO2S-2 Post-Cat)", "section": "SEC-1C", "category": "OBD-II Real-Time DTC", "base_dtc": "P0136", "mgp": "18213-68K10", "cost": 2750, "torque": 45, "pin": "ECM C47 (Pin 1)", "wire": "Y/Bl (Yellow/Blue)", "gnd": "G3", "fuse": "F-01 (15A FI)", "zone": (430, 155), "spec": "0.60-0.80V Steady Warm"},
    {"comp_id": "CMP-019", "name": "Downstream O2 Sensor Heater Circuit", "section": "SEC-1C", "category": "Electrical & Wiring Routing", "base_dtc": "P0141", "mgp": "18213-68K10", "cost": 2750, "torque": 45, "pin": "ECM C04 (Pin 4)", "wire": "P/G (Pink/Green)", "gnd": "G3", "fuse": "F-01 (15A FI)", "zone": (435, 155), "spec": "5.0-9.5Ω Heater Resistance"},
    {"comp_id": "CMP-020", "name": "F8D Air-Fuel Ratio System Too Lean (Bank 1)", "section": "SEC-1C", "category": "OBD-II Real-Time DTC", "base_dtc": "P0171", "mgp": "18118-78G50", "cost": 240, "torque": 12, "pin": "ECM Fuel Trim Map", "wire": "Vacuum / Fuel Rail", "gnd": "G3", "fuse": "RLY-FP", "zone": (370, 145), "spec": "LTFT + STFT within ±10%"},
    {"comp_id": "CMP-021", "name": "F8D Air-Fuel Ratio System Too Rich (Bank 1)", "section": "SEC-1C", "category": "OBD-II Real-Time DTC", "base_dtc": "P0172", "mgp": "15710-68K00", "cost": 1590, "torque": 22, "pin": "ECM Fuel Trim Map", "wire": "Fuel Rail / MAP", "gnd": "G3", "fuse": "RLY-FP", "zone": (372, 145), "spec": "LTFT > -15% @ Warm Idle"},
    {"comp_id": "CMP-022", "name": "Cylinder #1 Fuel Injector Solenoid & Harness", "section": "SEC-1C", "category": "OBD-II Real-Time DTC", "base_dtc": "P0201", "mgp": "15710-68K00", "cost": 1590, "torque": 22, "pin": "ECM C01", "wire": "Gr/R (Grey/Red)", "gnd": "G3", "fuse": "RLY-MAIN", "zone": (355, 125), "spec": "11.5-13.5Ω @ 20°C (3.4ms Pulse)"},
    {"comp_id": "CMP-023", "name": "Cylinder #2 Fuel Injector Solenoid & Harness", "section": "SEC-1C", "category": "OBD-II Real-Time DTC", "base_dtc": "P0202", "mgp": "15710-68K00", "cost": 1590, "torque": 22, "pin": "ECM C02", "wire": "Gr/Y (Grey/Yellow)", "gnd": "G3", "fuse": "RLY-MAIN", "zone": (355, 150), "spec": "11.5-13.5Ω @ 20°C (3.4ms Pulse)"},
    {"comp_id": "CMP-024", "name": "Cylinder #3 Fuel Injector Solenoid & Harness", "section": "SEC-1C", "category": "OBD-II Real-Time DTC", "base_dtc": "P0203", "mgp": "15710-68K00", "cost": 1590, "torque": 22, "pin": "ECM C03", "wire": "Gr/Bl (Grey/Blue)", "gnd": "G3", "fuse": "RLY-MAIN", "zone": (355, 175), "spec": "11.5-13.5Ω @ 20°C (3.4ms Pulse)"},
    {"comp_id": "CMP-025", "name": "Fuel Pump Primary Relay Control Circuit", "section": "SEC-1C", "category": "Electrical & Wiring Routing", "base_dtc": "P0230", "mgp": "38860-76F01", "cost": 290, "torque": 0, "pin": "ECM C49", "wire": "P/B (Pink/Black)", "gnd": "G10", "fuse": "F-01 (15A FI)", "zone": (285, 95), "spec": "12V Coil / 3.5 bar Fuel Pressure"},
    {"comp_id": "CMP-026", "name": "F8D 3-Cylinder Random/Multiple Misfire", "section": "SEC-1D", "category": "OBD-II Real-Time DTC", "base_dtc": "P0300", "mgp": "09482-00494", "cost": 420, "torque": 18, "pin": "ECM C14/C15/C16", "wire": "B/W + Coil Drivers", "gnd": "G13", "fuse": "F-12 (15A IG)", "zone": (340, 150), "spec": "NGK DCPR7E Gap 0.8-0.9mm"},
    {"comp_id": "CMP-027", "name": "Cylinder #1 Ignition / Compression Misfire", "section": "SEC-1D", "category": "OBD-II Real-Time DTC", "base_dtc": "P0301", "mgp": "33400-68K00", "cost": 1650, "torque": 18, "pin": "ECM C14", "wire": "Br/Y (Brown/Yellow)", "gnd": "G13", "fuse": "F-12 (15A IG)", "zone": (340, 125), "spec": "14.0 bar Compression / 0.85mm Gap"},
    {"comp_id": "CMP-028", "name": "Cylinder #2 Ignition / Compression Misfire", "section": "SEC-1D", "category": "OBD-II Real-Time DTC", "base_dtc": "P0302", "mgp": "33400-68K00", "cost": 1650, "torque": 18, "pin": "ECM C15", "wire": "Br/Bl (Brown/Blue)", "gnd": "G13", "fuse": "F-12 (15A IG)", "zone": (340, 150), "spec": "14.0 bar Compression / 0.85mm Gap"},
    {"comp_id": "CMP-029", "name": "Cylinder #3 Ignition / Compression Misfire", "section": "SEC-1D", "category": "OBD-II Real-Time DTC", "base_dtc": "P0303", "mgp": "33400-68K00", "cost": 1650, "torque": 18, "pin": "ECM C16", "wire": "Br/W (Brown/White)", "gnd": "G13", "fuse": "F-12 (15A IG)", "zone": (340, 175), "spec": "14.0 bar Compression / 0.85mm Gap"},
    {"comp_id": "CMP-030", "name": "Crankshaft Position Sensor (CKP) Reluctor", "section": "SEC-1F", "category": "OBD-II Real-Time DTC", "base_dtc": "P0335", "mgp": "33220-76G30", "cost": 890, "torque": 9, "pin": "ECM C27 & C28", "wire": "G & Bl (Shielded)", "gnd": "G3", "fuse": "F-12 (15A IG)", "zone": (330, 120), "spec": "480-650Ω @ 20°C (2-5V AC Idle)"},
    {"comp_id": "CMP-031", "name": "Camshaft Position Sensor (CMP) Hall Circuit", "section": "SEC-1F", "category": "OBD-II Real-Time DTC", "base_dtc": "P0340", "mgp": "33220-68K00", "cost": 960, "torque": 9, "pin": "ECM C30", "wire": "G/R (Green/Red)", "gnd": "G3", "fuse": "F-01 (15A FI)", "zone": (335, 180), "spec": "0V-5.0V Square Wave Pulse"},
    {"comp_id": "CMP-032", "name": "Three-Way Catalytic Converter (TWC Bank 1)", "section": "SEC-1C", "category": "OBD-II Real-Time DTC", "base_dtc": "P0420", "mgp": "14190-68K00", "cost": 14500, "torque": 35, "pin": "ECM O2 B1S1/B1S2 Ratio", "wire": "Exhaust Collector", "gnd": "G3", "fuse": "RLY-MAIN", "zone": (320, 150), "spec": "B1S2 Steady 0.65-0.75V @ Cruise"},
    {"comp_id": "CMP-033", "name": "EVAP Canister Purge Control Solenoid Valve", "section": "SEC-1C", "category": "OBD-II Real-Time DTC", "base_dtc": "P0443", "mgp": "18117-68K00", "cost": 680, "torque": 7, "pin": "ECM C06", "wire": "R/Y (Red/Yellow)", "gnd": "G3", "fuse": "F-01 (15A FI)", "zone": (390, 115), "spec": "26-32Ω @ 20°C (12V Supply)"},
    {"comp_id": "CMP-034", "name": "Radiator Cooling Fan Relay & Control Driver", "section": "SEC-1B", "category": "OBD-II Real-Time DTC", "base_dtc": "P0480", "mgp": "38860-76F01", "cost": 290, "torque": 8, "pin": "ECM C50", "wire": "Bl/W (Blue/White)", "gnd": "G4", "fuse": "FL-4 (30A Fan)", "zone": (275, 145), "spec": "ON @ 98°C / OFF @ 93°C (12V)"},
    {"comp_id": "CMP-035", "name": "Vehicle Speed Sensor (VSS 5MT Gearbox)", "section": "SEC-2B", "category": "OBD-II Real-Time DTC", "base_dtc": "P0500", "mgp": "34960-68K00", "cost": 780, "torque": 9, "pin": "ECM C52", "wire": "Y (Yellow)", "gnd": "G7", "fuse": "F-13 (10A Meter)", "zone": (395, 185), "spec": "0V-4.8V 4-Pulse/Rev Square Wave"},

    # --- SECTION 1F / 5A / 3A: IACV, SYSTEM VOLTAGE, IMMOBILIZER, EPS & NETWORK (36..55) ---
    {"comp_id": "CMP-036", "name": "Idle Air Control Valve (IACV) Stepper Motor", "section": "SEC-1F", "category": "OBD-II Real-Time DTC", "base_dtc": "P0505", "mgp": "18137-79G01", "cost": 2450, "torque": 4, "pin": "ECM C08-C11", "wire": "Bl/R, Bl/B, Bl/Y, Bl/G", "gnd": "G3", "fuse": "RLY-MAIN", "zone": (365, 132), "spec": "28-36Ω per Coil (15-35 Steps Idle)"},
    {"comp_id": "CMP-037", "name": "IACV Idle Speed Lower Than Target (<700 RPM)", "section": "SEC-1F", "category": "OBD-II Real-Time DTC", "base_dtc": "P0506", "mgp": "18137-79G01", "cost": 2450, "torque": 4, "pin": "ECM C08-C11", "wire": "Bl/R, Bl/B", "gnd": "G3", "fuse": "RLY-MAIN", "zone": (366, 134), "spec": "800 ± 50 RPM (A/C OFF) | 900 (A/C ON)"},
    {"comp_id": "CMP-038", "name": "IACV Idle Speed Higher Than Target (>1100 RPM)", "section": "SEC-1F", "category": "OBD-II Real-Time DTC", "base_dtc": "P0507", "mgp": "13421-68K00", "cost": 65, "torque": 10, "pin": "ECM C08-C11", "wire": "Throttle Bypass", "gnd": "G3", "fuse": "RLY-MAIN", "zone": (368, 130), "spec": "800 ± 50 RPM Warm Idle"},
    {"comp_id": "CMP-039", "name": "ECM System Battery Voltage Sense Circuit", "section": "SEC-1E", "category": "OBD-II Real-Time DTC", "base_dtc": "P0560", "mgp": "31400-68K00", "cost": 6800, "torque": 23, "pin": "ECM C59 (+B) & C60 (IG1)", "wire": "W/R & B/W", "gnd": "G1", "fuse": "FL-1 (80A Main)", "zone": (295, 115), "spec": "13.8-14.4V Charging @ 2000 RPM"},
    {"comp_id": "CMP-040", "name": "Charging System Low Voltage (<12.2V Running)", "section": "SEC-1E", "category": "OBD-II Real-Time DTC", "base_dtc": "P0562", "mgp": "31400-68K00", "cost": 6800, "torque": 23, "pin": "Alternator B+ & L Terminal", "wire": "W/B & W/R", "gnd": "G2", "fuse": "FL-1 (80A Main)", "zone": (325, 115), "spec": "13.8-14.4V Regulated Output"},
    {"comp_id": "CMP-041", "name": "Alternator Voltage Regulator Overcharging (>15.5V)", "section": "SEC-1E", "category": "OBD-II Real-Time DTC", "base_dtc": "P0563", "mgp": "32500-68K00", "cost": 1450, "torque": 8, "pin": "Alternator IC Regulator", "wire": "W/B", "gnd": "G2", "fuse": "FL-1 (80A Main)", "zone": (328, 118), "spec": "< 14.6V Max at All RPMs"},
    {"comp_id": "CMP-042", "name": "ECM Internal EEPROM / Flash Checksum Memory", "section": "SEC-1F", "category": "OBD-II Real-Time DTC", "base_dtc": "P0601", "mgp": "33920-68K10", "cost": 11200, "torque": 8, "pin": "ECM 60-Pin Connector", "wire": "Main Harness", "gnd": "G3", "fuse": "F-01 (15A FI)", "zone": (415, 105), "spec": "Clean 12V Power & <0.05V G3 Drop"},
    {"comp_id": "CMP-043", "name": "Immobilizer Ring Antenna & Transponder Key", "section": "SEC-5A", "category": "OBD-II Real-Time DTC", "base_dtc": "P1610", "mgp": "33970-68K00", "cost": 1850, "torque": 3, "pin": "ICM Pin 5 -> ECM K-Line", "wire": "P/Y (Purple/Yellow)", "gnd": "G7", "fuse": "F-11 (10A Dome)", "zone": (455, 125), "spec": "125 kHz RF Challenge-Response"},
    {"comp_id": "CMP-044", "name": "Immobilizer-to-ECM K-Line Authentication", "section": "SEC-5A", "category": "OBD-II Real-Time DTC", "base_dtc": "P1614", "mgp": "37145-68K00", "cost": 650, "torque": 3, "pin": "DLC Pin 7 / ECM C58", "wire": "P/Y (Purple/Yellow)", "gnd": "G7", "fuse": "F-11 (10A Dome)", "zone": (458, 128), "spec": "Steady Padlock Lamp -> OFF on Key ON"},
    {"comp_id": "CMP-045", "name": "Electric Power Steering (EPS) Torque Sensor", "section": "SEC-3A", "category": "OBD-II Real-Time DTC", "base_dtc": "C1111", "mgp": "48200-68K10", "cost": 8900, "torque": 28, "pin": "EPS Module Pin A1-A4", "wire": "G/W & G/B", "gnd": "G7", "fuse": "FL-2 (50A EPS)", "zone": (445, 130), "spec": "2.50V Neutral Center (1.0-4.0V Turn)"},
    {"comp_id": "CMP-046", "name": "EPS Assist DC Motor & Clutch Armature", "section": "SEC-3A", "category": "OBD-II Real-Time DTC", "base_dtc": "C1141", "mgp": "48200-68K10", "cost": 8900, "torque": 28, "pin": "EPS 2-Pin Heavy Connector", "wire": "R & B (10 AWG)", "gnd": "G7", "fuse": "FL-2 (50A EPS)", "zone": (448, 132), "spec": "0.1-0.4Ω Motor Winding (0-35A Load)"},
    {"comp_id": "CMP-047", "name": "EPS Vehicle Speed / Engine RPM Input Loss", "section": "SEC-3A", "category": "OBD-II Real-Time DTC", "base_dtc": "C1122", "mgp": "38720-68K00", "cost": 4200, "torque": 8, "pin": "EPS Pin B6 (RPM) & B7 (VSS)", "wire": "Br & Y", "gnd": "G7", "fuse": "F-13 (10A Meter)", "zone": (442, 126), "spec": "12V Tachometer & 5V VSS Square Wave"},
    {"comp_id": "CMP-048", "name": "16-Pin OBD-II DLC K-Line & CAN Bus Gateway", "section": "SEC-1F", "category": "OBD-II Real-Time DTC", "base_dtc": "U0001", "mgp": "36650-68K00", "cost": 950, "torque": 0, "pin": "DLC Pin 6, 7, 14, 16", "wire": "W/R, P/Y, W, W/B", "gnd": "G6", "fuse": "F-11 (10A OBDC)", "zone": (460, 118), "spec": "60Ω across Pin 6 & 14; 12V on Pin 7/16"},
    {"comp_id": "CMP-049", "name": "Lost Communication With ECM / PCM on Bus", "section": "SEC-1F", "category": "OBD-II Real-Time DTC", "base_dtc": "U0100", "mgp": "33920-68K10", "cost": 11200, "torque": 8, "pin": "DLC Pin 6/14 & Pin 7", "wire": "W/R, W & P/Y", "gnd": "G3", "fuse": "F-01 (15A FI)", "zone": (420, 108), "spec": "CAN-H 2.5-3.5V / CAN-L 1.5-2.5V"},
    {"comp_id": "CMP-050", "name": "Digital Instrument Cluster LCD & Gauge Driver", "section": "SEC-5A", "category": "Electrical & Wiring Routing", "base_dtc": "B1500", "mgp": "34100-68K00", "cost": 3650, "torque": 3, "pin": "Cluster 16-Pin Plug", "wire": "R/Y (+B) & B/W (IG1)", "gnd": "G7", "fuse": "F-13 (10A Meter)", "zone": (450, 122), "spec": "12V IG1 & 12V Constant Memory"},

    # --- SECTION 8A-8F: GROUND POINTS G1-G14, FUSES & RELAY ROUTING CIRCUITS (51..75) ---
    {"comp_id": "CMP-051", "name": "Ground Point G1 (Battery Negative to Fender Apron)", "section": "SEC-1E", "category": "Electrical & Wiring Routing", "base_dtc": "E-GND-G01", "mgp": "33850-68K00", "cost": 480, "torque": 12, "pin": "Chassis Apron M8 Bolt", "wire": "Black 25mm² Cable", "gnd": "G1", "fuse": "FL-1 (80A)", "zone": (290, 92), "spec": "< 0.05V Voltage Drop under 40A Load"},
    {"comp_id": "CMP-052", "name": "Ground Point G2 (5MT Gearbox to Battery Negative)", "section": "SEC-1E", "category": "Electrical & Wiring Routing", "base_dtc": "E-GND-G02", "mgp": "33850-68K00", "cost": 480, "torque": 23, "pin": "Bellhousing Top M10 Stud", "wire": "Black 25mm² Strap", "gnd": "G2", "fuse": "Starter 150A", "zone": (385, 175), "spec": "< 0.15V Drop During Starter Cranking"},
    {"comp_id": "CMP-053", "name": "Ground Point G3 (F8D Intake Manifold ECM Master Ground)", "section": "SEC-1F", "category": "Electrical & Wiring Routing", "base_dtc": "E-GND-G03", "mgp": "36610-68K00", "cost": 350, "torque": 10, "pin": "Intake Plenum Rear M6 Bolts", "wire": "Br/W & B/O eyelets", "gnd": "G3", "fuse": "F-01 (15A FI)", "zone": (375, 142), "spec": "< 0.02V Drop to Battery Negative"},
    {"comp_id": "CMP-054", "name": "Ground Point G4 (Left Headlamp & Radiator Fan Ground)", "section": "SEC-5A", "category": "Electrical & Wiring Routing", "base_dtc": "E-GND-G04", "mgp": "36620-68K00", "cost": 220, "torque": 9, "pin": "Left Radiator Support Apron", "wire": "Black (B)", "gnd": "G4", "fuse": "FL-4 (30A Fan)", "zone": (268, 105), "spec": "< 0.08V Drop with Fan & Headlamp ON"},
    {"comp_id": "CMP-055", "name": "Ground Point G5 (Right Headlamp & Washer Pump Ground)", "section": "SEC-5A", "category": "Electrical & Wiring Routing", "base_dtc": "E-GND-G05", "mgp": "36620-68K00", "cost": 220, "torque": 9, "pin": "Right Fender Apron Bolt", "wire": "Black (B)", "gnd": "G5", "fuse": "F-03 (15A HL-R)", "zone": (268, 195), "spec": "< 0.08V Drop with High Beam ON"},
    {"comp_id": "CMP-056", "name": "Ground Point G6 (Driver Kick Panel & OBD-II DLC Pin 4)", "section": "SEC-5A", "category": "Electrical & Wiring Routing", "base_dtc": "E-GND-G06", "mgp": "36650-68K00", "cost": 180, "torque": 9, "pin": "Right A-Pillar Lower Bolt", "wire": "Black (B)", "gnd": "G6", "fuse": "F-11 (10A OBDC)", "zone": (465, 110), "spec": "< 0.1Ω from DLC Pin 4 to Chassis"},
    {"comp_id": "CMP-057", "name": "Ground Point G10 (Fuel Pump & Tank Sender Sill Ground)", "section": "SEC-1C", "category": "Electrical & Wiring Routing", "base_dtc": "E-GND-G10", "mgp": "15100-68K00", "cost": 180, "torque": 9, "pin": "B-Pillar Floor Sill Bolt", "wire": "Black (B)", "gnd": "G10", "fuse": "RLY-FP", "zone": (580, 115), "spec": "< 0.05V Drop at 4.5A Fuel Pump Draw"},
    {"comp_id": "CMP-058", "name": "Ground Point G11 (Rear Tail / Stop / Turn Cluster Ground)", "section": "SEC-5A", "category": "Electrical & Wiring Routing", "base_dtc": "E-GND-G11", "mgp": "35650-68K00", "cost": 150, "torque": 8, "pin": "Rear Left Quarter Panel Bolt", "wire": "Black (B)", "gnd": "G11", "fuse": "F-17 (10A Stop)", "zone": (785, 115), "spec": "0.0V Backfeed when Brake + Turn Active"},
    {"comp_id": "CMP-059", "name": "FI Main Relay (RLY-MAIN) Contacts & Coil", "section": "SEC-1F", "category": "Electrical & Wiring Routing", "base_dtc": "E-RLY-MAIN", "mgp": "38860-76F01", "cost": 290, "torque": 0, "pin": "Engine J/B Slot R1 (Pin 30/87)", "wire": "W/R -> B/R", "gnd": "G3", "fuse": "F-01 (15A FI)", "zone": (290, 102), "spec": "75-95Ω Coil | <0.1V Contact Drop"},
    {"comp_id": "CMP-060", "name": "Fuel Pump Relay (RLY-FP) Contacts & Harness", "section": "SEC-1C", "category": "Electrical & Wiring Routing", "base_dtc": "E-RLY-FP", "mgp": "38860-76F01", "cost": 290, "torque": 0, "pin": "Engine J/B Slot R2 (Pin 30/87)", "wire": "P/B (Pink/Black)", "gnd": "G10", "fuse": "F-01 (15A FI)", "zone": (292, 105), "spec": "12V Output to Tank for 3s on Key-ON"},
    {"comp_id": "CMP-061", "name": "A/C Compressor Clutch Relay (RLY-AC) & Diode", "section": "SEC-6A", "category": "Electrical & Wiring Routing", "base_dtc": "E-RLY-AC", "mgp": "38860-76F01", "cost": 290, "torque": 0, "pin": "Engine J/B Slot R4", "wire": "B/Y (Black/Yellow)", "gnd": "G14", "fuse": "F-04 (10A A/C)", "zone": (295, 108), "spec": "12V to Magnetic Clutch (3.8Ω Coil)"},
    {"comp_id": "CMP-062", "name": "Negative-Switched Headlamp Stalk & Relay Circuit", "section": "SEC-5A", "category": "Electrical & Wiring Routing", "base_dtc": "E-LGT-HL01", "mgp": "37400-68K00", "cost": 1280, "torque": 4, "pin": "Combination Switch Connector", "wire": "R/W (Low) & R (High)", "gnd": "G6", "fuse": "F-02/F-03 (15A)", "zone": (452, 115), "spec": "+12V Common at H4; Stalk Grounds Hi/Lo"},
    {"comp_id": "CMP-063", "name": "Front Wiper Motor Park Switch & Intermittent Relay", "section": "SEC-5A", "category": "Electrical & Wiring Routing", "base_dtc": "E-WIP-001", "mgp": "38100-68K00", "cost": 2150, "torque": 10, "pin": "Wiper Motor 5-Pin Plug", "wire": "Bl/W, Bl/R, Y/G", "gnd": "G6", "fuse": "F-14 (20A Wiper)", "zone": (418, 145), "spec": "12V Park Feed Returns Blade to Cowl"},
    {"comp_id": "CMP-064", "name": "Power Window Master Switch & Regulator Motor", "section": "SEC-5A", "category": "Electrical & Wiring Routing", "base_dtc": "E-PWN-001", "mgp": "37990-68K00", "cost": 980, "torque": 6, "pin": "Door Boot Grommet C31", "wire": "G/W & R/Bl", "gnd": "G9", "fuse": "30A P/W Fuse", "zone": (510, 95), "spec": "Polarity Reversal 12V (4.5s Full Travel)"},
    {"comp_id": "CMP-065", "name": "Central Door Locking Actuator & Control Unit", "section": "SEC-5A", "category": "Electrical & Wiring Routing", "base_dtc": "E-CDL-001", "mgp": "37190-68K00", "cost": 1150, "torque": 5, "pin": "CDL 8-Pin Module Right Kick", "wire": "Br/Y & Br/W", "gnd": "G9", "fuse": "20A Door Lock", "zone": (470, 185), "spec": "0.5s 12V Lock/Unlock Pulse"},

    # --- SECTION 1A / 1B / 1C / 1E: F8D ENGINE MECHANICAL, COOLING, FUEL & STARTING (66..95) ---
    {"comp_id": "CMP-066", "name": "F8D Cylinder #1 Intake & Exhaust Valve Clearance", "section": "SEC-1A", "category": "Engine Mechanical", "base_dtc": "MECH-F8D-V01", "mgp": "12841-78G00", "cost": 320, "torque": 16, "pin": "Rocker Arm Adjusting Screw #1", "wire": "Mechanical Valvetrain", "gnd": "G3", "fuse": "N/A", "zone": (342, 128), "spec": "Cold IN: 0.13-0.17mm | EX: 0.23-0.27mm"},
    {"comp_id": "CMP-067", "name": "F8D Cylinder #2 Intake & Exhaust Valve Clearance", "section": "SEC-1A", "category": "Engine Mechanical", "base_dtc": "MECH-F8D-V02", "mgp": "12841-78G00", "cost": 320, "torque": 16, "pin": "Rocker Arm Adjusting Screw #2", "wire": "Mechanical Valvetrain", "gnd": "G3", "fuse": "N/A", "zone": (342, 150), "spec": "Cold IN: 0.13-0.17mm | EX: 0.23-0.27mm"},
    {"comp_id": "CMP-068", "name": "F8D Cylinder #3 Intake & Exhaust Valve Clearance", "section": "SEC-1A", "category": "Engine Mechanical", "base_dtc": "MECH-F8D-V03", "mgp": "12841-78G00", "cost": 320, "torque": 16, "pin": "Rocker Arm Adjusting Screw #3", "wire": "Mechanical Valvetrain", "gnd": "G3", "fuse": "N/A", "zone": (342, 172), "spec": "Cold IN: 0.13-0.17mm | EX: 0.23-0.27mm"},
    {"comp_id": "CMP-069", "name": "F8D Multi-Layer Steel (MLS) Cylinder Head Gasket", "section": "SEC-1A", "category": "Engine Mechanical", "base_dtc": "MECH-F8D-HG1", "mgp": "11141-68K00", "cost": 780, "torque": 70, "pin": "8x M10 Cylinder Head Bolts", "wire": "Block-to-Head Deck", "gnd": "G3", "fuse": "N/A", "zone": (345, 150), "spec": "14.0 bar Compression | Warpage <0.05mm"},
    {"comp_id": "CMP-070", "name": "F8D Cylinder #1 Piston Rings & Oil Control Ring", "section": "SEC-1A", "category": "Engine Mechanical", "base_dtc": "MECH-F8D-PR1", "mgp": "12140-68K00", "cost": 1650, "torque": 35, "pin": "68.5mm Bore Cylinder #1", "wire": "Rotating Assembly", "gnd": "G2", "fuse": "N/A", "zone": (340, 126), "spec": "End Gap 0.15-0.30mm | Compression >11.5 bar"},
    {"comp_id": "CMP-071", "name": "F8D Cylinder #2 Piston Rings & Skirt Clearance", "section": "SEC-1A", "category": "Engine Mechanical", "base_dtc": "MECH-F8D-PR2", "mgp": "12140-68K00", "cost": 1650, "torque": 35, "pin": "68.5mm Bore Cylinder #2", "wire": "Rotating Assembly", "gnd": "G2", "fuse": "N/A", "zone": (340, 150), "spec": "Bore Taper <0.02mm | Wet Test Delta <1 bar"},
    {"comp_id": "CMP-072", "name": "F8D Cylinder #3 Piston Rings & Cylinder Wall", "section": "SEC-1A", "category": "Engine Mechanical", "base_dtc": "MECH-F8D-PR3", "mgp": "12140-68K00", "cost": 1650, "torque": 35, "pin": "68.5mm Bore Cylinder #3", "wire": "Rotating Assembly", "gnd": "G2", "fuse": "N/A", "zone": (340, 174), "spec": "14.0 bar Standard Compression"},
    {"comp_id": "CMP-073", "name": "F8D 107-Tooth Camshaft Timing Belt & Marks", "section": "SEC-1A", "category": "Engine Mechanical", "base_dtc": "MECH-F8D-TB1", "mgp": "12761-78G00", "cost": 690, "torque": 45, "pin": "Crank & Cam Timing Sprockets", "wire": "Left Timing Cover", "gnd": "G3", "fuse": "N/A", "zone": (328, 125), "spec": "107 Teeth Aligned at Cyl #1 TDC"},
    {"comp_id": "CMP-074", "name": "Timing Belt Tensioner Pulley & Spring Assembly", "section": "SEC-1A", "category": "Engine Mechanical", "base_dtc": "MECH-F8D-TT1", "mgp": "12810-78G00", "cost": 740, "torque": 27, "pin": "Tensioner Pivot M8 Bolt", "wire": "Left Timing Cover", "gnd": "G3", "fuse": "N/A", "zone": (330, 130), "spec": "27 Nm Lock Bolt after 2 Crank Turns"},
    {"comp_id": "CMP-075", "name": "Valve Stem Oil Seals (12x Viton Seals)", "section": "SEC-1A", "category": "Engine Mechanical", "base_dtc": "MECH-F8D-VSS", "mgp": "09289-05012", "cost": 540, "torque": 16, "pin": "12V SOHC Valve Guides", "wire": "Cylinder Head Top", "gnd": "G3", "fuse": "N/A", "zone": (345, 148), "spec": "Zero Blue Smoke on Morning Cold Start"},
    {"comp_id": "CMP-076", "name": "Crankshaft Main & Connecting Rod Big-End Bearings", "section": "SEC-1A", "category": "Engine Mechanical", "base_dtc": "MECH-F8D-CRK", "mgp": "12300-68K00", "cost": 1420, "torque": 54, "pin": "4 Main Caps & 3 Con-Rod Caps", "wire": "Lower Crankcase", "gnd": "G2", "fuse": "N/A", "zone": (345, 152), "spec": "Oil Clearance 0.020-0.040mm | 3.5 bar Oil"},
    {"comp_id": "CMP-077", "name": "Engine Oil Pump Rotor & Low Oil Pressure Switch", "section": "SEC-1A", "category": "Engine Mechanical", "base_dtc": "MECH-F8D-OIL", "mgp": "16100-78G00", "cost": 1890, "torque": 14, "pin": "Block Oil Gallery Switch", "wire": "Y/B (Yellow/Black)", "gnd": "G2", "fuse": "F-13 (10A)", "zone": (332, 138), "spec": "> 0.5 bar Idle | 3.2-4.2 bar @ 3000 RPM"},
    {"comp_id": "CMP-078", "name": "Rear Engine Mount (Torque Rod) & LH/RH Engine Mounts", "section": "SEC-1A", "category": "Engine Mechanical", "base_dtc": "MECH-F8D-MNT", "mgp": "11710-68K00", "cost": 1350, "torque": 55, "pin": "Subframe & Frame Rail Brackets", "wire": "3-Point Pendulum Mount", "gnd": "G2", "fuse": "N/A", "zone": (375, 160), "spec": "Zero Rubber Tear / Cabin Clunk on Shift"},
    {"comp_id": "CMP-079", "name": "PCV (Positive Crankcase Ventilation) One-Way Valve", "section": "SEC-1C", "category": "Engine Mechanical", "base_dtc": "MECH-F8D-PCV", "mgp": "18118-78G50", "cost": 240, "torque": 12, "pin": "Rocker Cover to Plenum Hose", "wire": "Breather Hose", "gnd": "G3", "fuse": "N/A", "zone": (358, 145), "spec": "Clicks Freely; Blocks Reverse Airflow"},
    {"comp_id": "CMP-080", "name": "88°C Wax-Pellet Cooling Thermostat & Housing", "section": "SEC-1B", "category": "Engine Mechanical", "base_dtc": "MECH-COL-THM", "mgp": "17670-65G00", "cost": 420, "torque": 12, "pin": "Cylinder Head Outlet Housing", "wire": "Upper Radiator Hose", "gnd": "G3", "fuse": "N/A", "zone": (350, 178), "spec": "Opens at 88±1.5°C | >8mm Lift @ 100°C"},
    {"comp_id": "CMP-081", "name": "Centrifugal Water Pump Impeller & Mechanical Seal", "section": "SEC-1B", "category": "Engine Mechanical", "base_dtc": "MECH-COL-WMP", "mgp": "17400-78G00", "cost": 1250, "torque": 12, "pin": "Front Right Block Pocket", "wire": "4PK750 Ribbed Belt", "gnd": "G3", "fuse": "N/A", "zone": (326, 122), "spec": "Zero Weep-Hole Seepage | Belt 6-8mm"},
    {"comp_id": "CMP-082", "name": "Aluminum Core Radiator & 1.1 Bar Pressure Cap", "section": "SEC-1B", "category": "Engine Mechanical", "base_dtc": "MECH-COL-RAD", "mgp": "17700-68K00", "cost": 3150, "torque": 10, "pin": "Front Core Support Mounts", "wire": "Upper/Lower Hoses", "gnd": "G4", "fuse": "FL-4 (30A)", "zone": (272, 150), "spec": "Holds 1.1 bar (108 kPa) for 2 Minutes"},
    {"comp_id": "CMP-083", "name": "In-Tank Electric Fuel Pump & Strainer Filter", "section": "SEC-1C", "category": "Engine Mechanical", "base_dtc": "MECH-FUL-PMP", "mgp": "15100-68K00", "cost": 4450, "torque": 8, "pin": "Tank 4-Pin Flange Under Rear Seat", "wire": "P/B (+12V) & B (GND)", "gnd": "G10", "fuse": "RLY-FP", "zone": (695, 150), "spec": "3.5 bar Operating | >2.5 bar Hold Pressure"},
    {"comp_id": "CMP-084", "name": "0.8 kW Starter Motor Solenoid & Bendix Pinion", "section": "SEC-1E", "category": "Engine Mechanical", "base_dtc": "MECH-STR-001", "mgp": "31100-68K00", "cost": 4650, "torque": 42, "pin": "Terminal 30 (+B) & Terminal 50", "wire": "R/B (25mm²) & B/Y", "gnd": "G2", "fuse": "FL-3 (40A IG)", "zone": (372, 168), "spec": "Cranks F8D >= 250 RPM @ <120A Draw"},
    {"comp_id": "CMP-085", "name": "55A Alternator Drive Belt & Bearings (4PK750)", "section": "SEC-1E", "category": "Engine Mechanical", "base_dtc": "MECH-ALT-001", "mgp": "17521-68K00", "cost": 310, "torque": 23, "pin": "Alternator Tensioner Bracket", "wire": "W/B & W/R", "gnd": "G2", "fuse": "FL-1 (80A)", "zone": (322, 112), "spec": "6-8mm Deflection @ 10kgf | 14.1V Output"},

    # --- SECTION 2A / 2B: CLUTCH, 5-SPEED MANUAL TRANSAXLE & CV DRIVESHAFTS (86..102) ---
    {"comp_id": "CMP-086", "name": "160mm Clutch Friction Disc & Diaphragm Pressure Plate", "section": "SEC-2A", "category": "Drivetrain & 5MT Gearbox", "base_dtc": "MECH-CLU-001", "mgp": "22400-68K00", "cost": 2650, "torque": 23, "pin": "F8D Flywheel 6x M8 Bolts", "wire": "Bellhousing", "gnd": "G2", "fuse": "N/A", "zone": (368, 178), "spec": "Rivet Depth >0.3mm | Zero Slip in 4th Gear"},
    {"comp_id": "CMP-087", "name": "Clutch Release Throw-Out Bearing & Fork Shaft", "section": "SEC-2A", "category": "Drivetrain & 5MT Gearbox", "base_dtc": "MECH-CLU-002", "mgp": "23265-78G00", "cost": 580, "torque": 23, "pin": "Input Shaft Quill Sleeve", "wire": "Clutch Release Lever", "gnd": "G2", "fuse": "N/A", "zone": (372, 182), "spec": "Silent when Clutch Pedal Pressed"},
    {"comp_id": "CMP-088", "name": "Bowden Clutch Cable & Pedal Free-Play Adjuster", "section": "SEC-2A", "category": "Drivetrain & 5MT Gearbox", "base_dtc": "MECH-CLU-003", "mgp": "23710-68K00", "cost": 385, "torque": 10, "pin": "Release Arm 14mm Locknut", "wire": "Driver Firewall Loop", "gnd": "G2", "fuse": "N/A", "zone": (410, 175), "spec": "15-20mm Pedal Free Play (2-4mm at Fork)"},
    {"comp_id": "CMP-089", "name": "5MT 1st & 2nd Gear Brass Synchronizer Rings", "section": "SEC-2B", "category": "Drivetrain & 5MT Gearbox", "base_dtc": "MECH-5MT-S12", "mgp": "24431-68K00", "cost": 920, "torque": 23, "pin": "Mainshaft 1-2 Synchro Hub", "wire": "5MT Transaxle Case", "gnd": "G2", "fuse": "N/A", "zone": (385, 185), "spec": "Ring-to-Cone Clearance >= 0.5mm"},
    {"comp_id": "CMP-090", "name": "5MT 3rd, 4th & 5th Gear Synchronizer & Shift Fork", "section": "SEC-2B", "category": "Drivetrain & 5MT Gearbox", "base_dtc": "MECH-5MT-S35", "mgp": "24432-68K00", "cost": 950, "torque": 23, "pin": "Countershaft / Input Hub", "wire": "5MT Transaxle Case", "gnd": "G2", "fuse": "N/A", "zone": (390, 188), "spec": "Smooth Engagement with 75W-90 GL-4 Oil"},
    {"comp_id": "CMP-091", "name": "Gear Shift & Selector Dual-Cable Assembly", "section": "SEC-2B", "category": "Drivetrain & 5MT Gearbox", "base_dtc": "MECH-5MT-CBL", "mgp": "28300-68K00", "cost": 1680, "torque": 12, "pin": "Floor Shifter to Gearbox Tower", "wire": "Center Tunnel", "gnd": "G8", "fuse": "N/A", "zone": (485, 152), "spec": "Crisp Gate Return; Nylon Bush Intact"},
    {"comp_id": "CMP-092", "name": "5MT Input Shaft Bearing & Differential Oil Seals", "section": "SEC-2B", "category": "Drivetrain & 5MT Gearbox", "base_dtc": "MECH-5MT-BRG", "mgp": "09283-35047", "cost": 450, "torque": 23, "pin": "LH/RH Axle Output Ports", "wire": "5MT Transaxle Case", "gnd": "G2", "fuse": "N/A", "zone": (388, 180), "spec": "2.1L SAE 75W-90 GL-4 | Zero Whine in Neutral"},
    {"comp_id": "CMP-093", "name": "Front Left Driveshaft Outer CV Joint & Tripod Boot", "section": "SEC-2B", "category": "Drivetrain & 5MT Gearbox", "base_dtc": "MECH-AXL-FL1", "mgp": "44102-68K00", "cost": 3450, "torque": 175, "pin": "FL Wheel Hub 22-Spline Spindle", "wire": "Left Front Axle", "gnd": "G2", "fuse": "N/A", "zone": (355, 85), "spec": "Zero Clicking at Full Steering Lock | 175 Nm"},
    {"comp_id": "CMP-094", "name": "Front Right Driveshaft Outer CV Joint & Tripod Boot", "section": "SEC-2B", "category": "Drivetrain & 5MT Gearbox", "base_dtc": "MECH-AXL-FR1", "mgp": "44101-68K00", "cost": 3650, "torque": 175, "pin": "FR Wheel Hub 22-Spline Spindle", "wire": "Right Front Axle", "gnd": "G2", "fuse": "N/A", "zone": (355, 215), "spec": "Zero Clicking at Full Steering Lock | 175 Nm"},
    {"comp_id": "CMP-095", "name": "Reverse Lamp Switch on 5MT Gearbox Housing", "section": "SEC-2B", "category": "Electrical & Wiring Routing", "base_dtc": "E-5MT-REV", "mgp": "37610-76G10", "cost": 260, "torque": 20, "pin": "2-Pin Plug on Gearbox Front", "wire": "R/Y -> R", "gnd": "G11", "fuse": "F-13 (10A Meter)", "zone": (380, 188), "spec": "< 0.5Ω Closed in Reverse Gear | Infinite Neutral"},

    # --- SECTION 3A / 3B / 4A: STEERING, SUSPENSION, WHEEL BEARINGS & BRAKES (96..115) ---
    {"comp_id": "CMP-096", "name": "Steering Rack Pinion Bush, Yoke Pad & Boot", "section": "SEC-3A", "category": "Suspension, Steering & Brakes", "base_dtc": "MECH-STR-RCK", "mgp": "48500-68K00", "cost": 4250, "torque": 55, "pin": "Front Subframe Crossmember", "wire": "Steering Gear", "gnd": "G7", "fuse": "N/A", "zone": (395, 150), "spec": "Steering Wheel Free Play < 10-25 mm"},
    {"comp_id": "CMP-097", "name": "Outer Tie Rod End Ball Joints (LH & RH) & Toe-In", "section": "SEC-3A", "category": "Suspension, Steering & Brakes", "base_dtc": "MECH-STR-TIE", "mgp": "48810-68K00", "cost": 680, "torque": 43, "pin": "Steering Knuckle Arm Taper", "wire": "Tie Rod Locknut", "gnd": "G7", "fuse": "N/A", "zone": (365, 92), "spec": "Toe-In 0 ± 2 mm | Castle Nut 43 Nm + Cotter Pin"},
    {"comp_id": "CMP-098", "name": "Front Left MacPherson Strut Damper & Top Strut Mount", "section": "SEC-3B", "category": "Suspension, Steering & Brakes", "base_dtc": "MECH-SUS-FLS", "mgp": "41602-68K00", "cost": 2180, "torque": 85, "pin": "FL Strut Tower & Knuckle", "wire": "Front Left Wheel Arch", "gnd": "G1", "fuse": "N/A", "zone": (350, 82), "spec": "Zero Oil Leak | Rebound Stops in 1.5 Cycles"},
    {"comp_id": "CMP-099", "name": "Front Right MacPherson Strut Damper & Top Bearing", "section": "SEC-3B", "category": "Suspension, Steering & Brakes", "base_dtc": "MECH-SUS-FRS", "mgp": "41601-68K00", "cost": 2180, "torque": 85, "pin": "FR Strut Tower & Knuckle", "wire": "Front Right Wheel Arch", "gnd": "G5", "fuse": "N/A", "zone": (350, 218), "spec": "Knuckle Bolts 85 Nm | Top Nut 50 Nm"},
    {"comp_id": "CMP-100", "name": "Front Lower Control Arm & Ball Joint (LH / RH)", "section": "SEC-3B", "category": "Suspension, Steering & Brakes", "base_dtc": "MECH-SUS-LCA", "mgp": "45200-68K00", "cost": 1490, "torque": 55, "pin": "Knuckle Pinch Bolt & Subframe", "wire": "Lower Wishbone", "gnd": "G1", "fuse": "N/A", "zone": (360, 88), "spec": "Zero Vertical Ball Play | Pinch Bolt 55 Nm"},
    {"comp_id": "CMP-101", "name": "Front Stabilizer Anti-Roll Bar D-Bushes & End Bushes", "section": "SEC-3B", "category": "Suspension, Steering & Brakes", "base_dtc": "MECH-SUS-STB", "mgp": "42431-68K00", "cost": 260, "torque": 29, "pin": "Lower Control Arm Eyelets", "wire": "Front Sway Bar", "gnd": "G1", "fuse": "N/A", "zone": (370, 150), "spec": "Eliminates Front Thud over Speed Breakers"},
    {"comp_id": "CMP-102", "name": "Rear 3-Link Trailing Arm Bushes & Panhard Lateral Rod", "section": "SEC-3B", "category": "Suspension, Steering & Brakes", "base_dtc": "MECH-SUS-RTA", "mgp": "46200-68K00", "cost": 1350, "torque": 75, "pin": "Rear Axle Beam & Underbody", "wire": "Rear Suspension", "gnd": "G11", "fuse": "N/A", "zone": (710, 150), "spec": "Tighten at Curb Weight: 75 Nm"},
    {"comp_id": "CMP-103", "name": "Rear Telescopic Shock Absorbers & Coil Springs (LH/RH)", "section": "SEC-3B", "category": "Suspension, Steering & Brakes", "base_dtc": "MECH-SUS-RSH", "mgp": "41800-68K00", "cost": 1290, "torque": 60, "pin": "Rear Axle Lower Stud & Wheelhouse", "wire": "Rear Dampers", "gnd": "G11", "fuse": "N/A", "zone": (725, 95), "spec": "Upper/Lower Mounts 60 Nm"},
    {"comp_id": "CMP-104", "name": "Front & Rear Wheel Hub Bearings (DAC3562W / Tapered)", "section": "SEC-3B", "category": "Suspension, Steering & Brakes", "base_dtc": "MECH-WHL-BRG", "mgp": "09267-35009", "cost": 890, "torque": 175, "pin": "Steering Knuckle / Rear Spindle", "wire": "Wheel Hubs", "gnd": "G1", "fuse": "N/A", "zone": (352, 78), "spec": "Axial Play < 0.05 mm | Zero Humming @ 60 km/h"},
    {"comp_id": "CMP-105", "name": "Front Disc Brake Caliper Slide Pins, Pads & Rotor", "section": "SEC-4A", "category": "Suspension, Steering & Brakes", "base_dtc": "MECH-BRK-FRT", "mgp": "55810-68K00", "cost": 890, "torque": 26, "pin": "Front Knuckle Caliper Bracket", "wire": "Hydraulic Hose", "gnd": "G1", "fuse": "N/A", "zone": (348, 80), "spec": "Pad > 2.0mm | Rotor Runout < 0.10mm"},
    {"comp_id": "CMP-106", "name": "Rear Drum Brake Shoes, Wheel Cylinder & Self-Adjuster", "section": "SEC-4A", "category": "Suspension, Steering & Brakes", "base_dtc": "MECH-BRK-RER", "mgp": "53200-68K00", "cost": 940, "torque": 85, "pin": "Rear Backing Plate", "wire": "Steel Brake Line", "gnd": "G11", "fuse": "N/A", "zone": (720, 82), "spec": "Drum ID <= 181.5mm | Lining > 1.5mm"},
    {"comp_id": "CMP-107", "name": "Tandem Brake Master Cylinder & Vacuum Booster Check Valve", "section": "SEC-4A", "category": "Suspension, Steering & Brakes", "base_dtc": "MECH-BRK-TMC", "mgp": "51100-68K00", "cost": 2750, "torque": 13, "pin": "Driver Bulkhead Firewall", "wire": "Booster Vacuum Hose", "gnd": "G6", "fuse": "F-17 (10A Stop)", "zone": (405, 192), "spec": "Firm Pedal >65mm from Floor | DOT 3/4"},
    {"comp_id": "CMP-108", "name": "Parking Brake Equalizer & Rear Handbrake Cables", "section": "SEC-4A", "category": "Suspension, Steering & Brakes", "base_dtc": "MECH-BRK-PRK", "mgp": "54410-68K00", "cost": 720, "torque": 10, "pin": "Center Tunnel Handbrake Lever", "wire": "1-Pin Switch to Cluster", "gnd": "G8", "fuse": "F-13 (10A Meter)", "zone": (545, 150), "spec": "Locks Rear Wheels in 4-7 Clicks @ 200 N"},

    # --- SECTION 6A / 5A: HVAC, SUBROS A/C COMPRESSOR, BLOWER & BODY SYSTEMS (109..125) ---
    {"comp_id": "CMP-109", "name": "Subros A/C Compressor Magnetic Clutch & Reed Valves", "section": "SEC-6A", "category": "HVAC & Body Systems", "base_dtc": "HVAC-AC-001", "mgp": "95200-68K00", "cost": 10500, "torque": 23, "pin": "1-Pin Black/Yellow Clutch Wire", "wire": "B/Y (Black/Yellow)", "gnd": "G14", "fuse": "F-04 (10A A/C)", "zone": (315, 185), "spec": "Coil 3.4-4.2Ω | Air Gap 0.35-0.65mm"},
    {"comp_id": "CMP-110", "name": "A/C Dual High/Low Pressure Cut-Off Switch", "section": "SEC-6A", "category": "HVAC & Body Systems", "base_dtc": "HVAC-AC-002", "mgp": "95526-68K00", "cost": 780, "torque": 10, "pin": "Liquid Line Receiver-Drier Sight", "wire": "Bl/R -> ECM C55", "gnd": "G4", "fuse": "F-04 (10A A/C)", "zone": (282, 185), "spec": "Closed between 2.0 bar and 31.4 bar"},
    {"comp_id": "CMP-111", "name": "A/C Evaporator Core Fin Anti-Freeze Thermistor", "section": "SEC-6A", "category": "HVAC & Body Systems", "base_dtc": "HVAC-AC-003", "mgp": "95431-68K00", "cost": 460, "torque": 2, "pin": "HVAC Cooling Unit 2-Pin Plug", "wire": "G/Y & Br/W", "gnd": "G8", "fuse": "F-16 (25A Blower)", "zone": (445, 155), "spec": "4.5kΩ @ 0°C (Cuts OFF at 1.5°C, ON at 4°C)"},
    {"comp_id": "CMP-112", "name": "Thermal Expansion Valve (TXV) & Receiver Drier", "section": "SEC-6A", "category": "HVAC & Body Systems", "base_dtc": "HVAC-AC-004", "mgp": "95431-68K10", "cost": 1450, "torque": 12, "pin": "Firewall Evaporator Inlet", "wire": "R134a 320±20g", "gnd": "G8", "fuse": "N/A", "zone": (422, 162), "spec": "Low Side 1.8-2.4 bar | High Side 13-16 bar"},
    {"comp_id": "CMP-113", "name": "HVAC 4-Speed Blower Motor & Ceramic Resistor Pack", "section": "SEC-6A", "category": "HVAC & Body Systems", "base_dtc": "HVAC-BLW-001", "mgp": "95626-68K00", "cost": 380, "torque": 3, "pin": "4-Pin Resistor Block in Duct", "wire": "Bl/W, Bl/Y, Bl/R, Bl", "gnd": "G8", "fuse": "F-16 (25A Blower)", "zone": (448, 165), "spec": "0.8Ω / 1.6Ω / 3.2Ω Steps (Speed 4 Direct)"},
    {"comp_id": "CMP-114", "name": "Exhaust Manifold Gasket & Flexible Downpipe Flange", "section": "SEC-1C", "category": "Engine Mechanical", "base_dtc": "MECH-EXH-001", "mgp": "14140-68K00", "cost": 290, "torque": 23, "pin": "F8D Cylinder Head Front Studs", "wire": "Exhaust Collector", "gnd": "G3", "fuse": "N/A", "zone": (312, 150), "spec": "Zero Soot Leak Before B1S1 O2 Sensor"},
    {"comp_id": "CMP-115", "name": "Intake Manifold Plenum Gasket & Vacuum Nipples", "section": "SEC-1C", "category": "Engine Mechanical", "base_dtc": "MECH-INT-001", "mgp": "13119-68K00", "cost": 210, "torque": 23, "pin": "F8D Cylinder Head Rear Intake", "wire": "Intake Plenum", "gnd": "G3", "fuse": "N/A", "zone": (368, 150), "spec": "Holds 65 kPa Vacuum (32 kPa Absolute Idle)"},
    {"comp_id": "CMP-116", "name": "Throttle Cable & Accelerator Pedal Return Spring", "section": "SEC-1C", "category": "Engine Mechanical", "base_dtc": "MECH-THR-001", "mgp": "15910-68K00", "cost": 340, "torque": 10, "pin": "Throttle Body Cam Bracket", "wire": "Bulkhead Grommet", "gnd": "G3", "fuse": "N/A", "zone": (395, 138), "spec": "2-4mm Cable Slack at Closed Idle Stop"},
    {"comp_id": "CMP-117", "name": "Ignition Switch Contact Block (LOCK/ACC/ON/START)", "section": "SEC-1E", "category": "Electrical & Wiring Routing", "base_dtc": "E-IGN-SW1", "mgp": "37110-68K00", "cost": 890, "torque": 5, "pin": "6-Pin Steering Column Plug", "wire": "W/B (+B) -> B/W (IG1) & B/Y (ST)", "gnd": "G7", "fuse": "FL-3 (40A IG)", "zone": (455, 128), "spec": "< 0.05V Drop across IG1 Contacts"},
    {"comp_id": "CMP-118", "name": "Brake Light Pedal Switch (Normally Open Plunger)", "section": "SEC-4A", "category": "Electrical & Wiring Routing", "base_dtc": "E-BRK-SW1", "mgp": "37740-68K00", "cost": 195, "torque": 12, "pin": "Brake Pedal Bracket 2-Pin", "wire": "G/W -> G/R (ECM C54)", "gnd": "G11", "fuse": "F-17 (10A Stop)", "zone": (435, 188), "spec": "12V Output with 5-10mm Pedal Depression"},
    {"comp_id": "CMP-119", "name": "Horn Relay, Dual Disc Horn & Steering Pad Contact", "section": "SEC-5A", "category": "Electrical & Wiring Routing", "base_dtc": "E-HRN-001", "mgp": "38500-68K00", "cost": 460, "torque": 12, "pin": "Front Grille Bracket & Clockspring", "wire": "G/B -> G/O", "gnd": "G4", "fuse": "F-05 (15A Horn)", "zone": (262, 150), "spec": "105-115 dB @ 4.5A Draw"},
    {"comp_id": "CMP-120", "name": "Turn Signal Electronic Flasher Relay & Hazard Switch", "section": "SEC-5A", "category": "Electrical & Wiring Routing", "base_dtc": "E-TRN-001", "mgp": "38610-68K00", "cost": 340, "torque": 0, "pin": "Cabin Fuse Box 3-Pin Relay", "wire": "G/R & G/Y", "gnd": "G6", "fuse": "F-05 (15A Hazard)", "zone": (462, 114), "spec": "85 ± 10 Blinks/Minute (2x 21W + 5W)"},
    {"comp_id": "CMP-121", "name": "Windshield Washer Electric Pump & Nozzle Tubing", "section": "SEC-5A", "category": "Electrical & Wiring Routing", "base_dtc": "E-WSH-001", "mgp": "38410-68K00", "cost": 390, "torque": 0, "pin": "Washer Tank Lower Grommet", "wire": "Bl/Y & B", "gnd": "G5", "fuse": "F-14 (20A Wiper)", "zone": (298, 198), "spec": "12V Motor / 1.8 bar Spray Jet"},
    {"comp_id": "CMP-122", "name": "Fuel Tank Level Float Sender Potentiometer", "section": "SEC-5A", "category": "Electrical & Wiring Routing", "base_dtc": "E-FUL-SND", "mgp": "34810-68K00", "cost": 680, "torque": 6, "pin": "Tank Unit Pin 2 & 3", "wire": "Y/R (Signal) & B/O (GND)", "gnd": "G10", "fuse": "F-13 (10A Meter)", "zone": (700, 155), "spec": "Full: 3-7Ω | Half: 35Ω | Empty: 110Ω"},
    {"comp_id": "CMP-123", "name": "Cabin Dome Lamp & 4x Door Courtesy Plunger Switches", "section": "SEC-5A", "category": "Electrical & Wiring Routing", "base_dtc": "E-DOM-001", "mgp": "37670-68K00", "cost": 120, "torque": 3, "pin": "A/B-Pillar Single-Wire Switches", "wire": "B/R (Black/Red)", "gnd": "G6", "fuse": "F-11 (10A Dome)", "zone": (550, 150), "spec": "Grounds 12V 10W Festoon Bulb when Door Open"},
    {"comp_id": "CMP-124", "name": "Tailgate Latch Striker, Fuel Lid & Hood Release Cables", "section": "SEC-5A", "category": "HVAC & Body Systems", "base_dtc": "BODY-CBL-001", "mgp": "82180-68K00", "cost": 450, "torque": 10, "pin": "Driver Floor Lever to Rear Latch", "wire": "Left Sill Channel", "gnd": "G11", "fuse": "N/A", "zone": (795, 150), "spec": "Smooth Latch Engagement; Zero Tailgate Rattle"},
    {"comp_id": "CMP-125", "name": "Front Door Window Glass Run Channel & Regulator Scissor", "section": "SEC-5A", "category": "HVAC & Body Systems", "base_dtc": "BODY-GLS-001", "mgp": "83401-68K00", "cost": 1120, "torque": 8, "pin": "Front Door Inner Panel", "wire": "Silicone Baize Channel", "gnd": "G9", "fuse": "30A P/W", "zone": (520, 88), "spec": "Parallel Glass Lift < 3.5A Motor Current"},
]

# 16 Distinct Engineering Failure Modes
FAILURE_MODES: List[Dict[str, Any]] = [
    {"mode_idx": 1, "code_suffix": "SHORT-GND", "name": "Signal / Supply Wire Shorted to Chassis Ground", "severity": "CRITICAL", "delta_desc": "Measured signal reads 0.00-0.05V (Dead Short to Ground); blows fuse or triggers low-voltage fault."},
    {"mode_idx": 2, "code_suffix": "SHORT-12V", "name": "Signal Wire Shorted to +12V Battery / Reference Supply", "severity": "HIGH", "delta_desc": "Measured signal pegged at 4.95V / 12.4V regardless of engine operating state."},
    {"mode_idx": 3, "code_suffix": "OPEN-CKT", "name": "Open Circuit / Broken Conductor in Engine or Body Harness", "severity": "HIGH", "delta_desc": "Infinite resistance (OL Ω) between component terminal and ECM / J/B pin; open pull-up voltage."},
    {"mode_idx": 4, "code_suffix": "HIGH-RES", "name": "High Contact Resistance / Voltage Drop at Oxidized Pin", "severity": "MEDIUM", "delta_desc": "0.45-1.20V parasitic voltage drop across connector pin or ground eyelet under load."},
    {"mode_idx": 5, "code_suffix": "GND-LOSS", "name": "Corroded or Loose Ground Point Return Path", "severity": "HIGH", "delta_desc": "Ground reference floats at 0.8-2.4V instead of <0.05V, causing erratic sensor readings."},
    {"mode_idx": 6, "code_suffix": "DRIFT-HI", "name": "Sensor Calibration Drift High / Out-of-Range Upper Limit", "severity": "MEDIUM", "delta_desc": "Output skewed +25% above Maruti Suzuki F8D warm-idle OEM specification."},
    {"mode_idx": 7, "code_suffix": "DRIFT-LO", "name": "Sensor Calibration Drift Low / Sluggish Response", "severity": "MEDIUM", "delta_desc": "Output lags >300ms or reads -25% below OEM service manual baseline."},
    {"mode_idx": 8, "code_suffix": "THERM-98C", "name": "Thermal Breakdown in Heavy Traffic (Coolant >= 95°C)", "severity": "CRITICAL", "delta_desc": "Works when cold (25°C) but coil/circuit opens or binds once engine bay heat-soaks above 95°C."},
    {"mode_idx": 9, "code_suffix": "COLD-15C", "name": "Cold Morning Start Failure (Ambient 10-20°C)", "severity": "MEDIUM", "delta_desc": "Fails during cold open-loop cranking/enrichment; stabilizes only after 10 minutes of warm-up."},
    {"mode_idx": 10, "code_suffix": "AC-LOAD", "name": "Failure Under A/C Compressor & Electrical Load (Headlights + Blower)", "severity": "HIGH", "delta_desc": "RPM drops below 550 RPM or voltage sags below 12.1V when A/C clutch and headlights engage."},
    {"mode_idx": 11, "code_suffix": "INCLINE-WOT", "name": "High-Load / Uphill WOT Acceleration Breakdown (3000+ RPM)", "severity": "HIGH", "delta_desc": "Misfires, starves, or slips specifically under high manifold pressure (>85 kPa) in 2nd/3rd gear."},
    {"mode_idx": 12, "code_suffix": "MECH-WEAR", "name": "Mechanical Friction Wear / Excessive Internal Clearance", "severity": "MEDIUM", "delta_desc": "Physical clearance exceeds Maruti Suzuki service limit, producing knock, play, or pressure loss."},
    {"mode_idx": 13, "code_suffix": "SEAL-LEAK", "name": "Gasket, O-Ring, Diaphragm or Vacuum/Fluid Seal Leakage", "severity": "HIGH", "delta_desc": "Unmetered air ingress or fluid pressure drop below minimum hold specification."},
    {"mode_idx": 14, "code_suffix": "CARBON-FOUL", "name": "Carbon Soot, Oil Blow-By Sludge or Fuel Gum Contamination", "severity": "MEDIUM", "delta_desc": "Blow-by oil film or carbon deposit restricts mechanical travel or insulates sensing element."},
    {"mode_idx": 15, "code_suffix": "VIB-TORQ", "name": "Fastener Torque Loss / 3-Cylinder Harmonic Vibration Fatigue", "severity": "MEDIUM", "delta_desc": "3-cylinder F8D 1.5-order harmonic vibration has loosened mounting fastener or chafed harness loom."},
    {"mode_idx": 16, "code_suffix": "WATER-MON", "name": "Monsoon Water Ingress / Road Splash Electrochemical Corrosion", "severity": "HIGH", "delta_desc": "Green copper-oxide bridging inside weatherpack seal after deep water wading or pressure wash."},
]

# 10 Mileage & Operating Lifecycle Bands (125 * 16 * 10 = 20,000 exact issues)
MILEAGE_BANDS: List[Dict[str, Any]] = [
    {"band_idx": 1, "km_label": "10,000 km (1st Annual Service Window)", "km_num": 10000},
    {"band_idx": 2, "km_label": "20,000 km (Spark Plug & Filter Interval)", "km_num": 20000},
    {"band_idx": 3, "km_label": "30,000 km (Brake & Throttle Service Window)", "km_num": 30000},
    {"band_idx": 4, "km_label": "40,000 km (Major Coolant & Transaxle Oil Service)", "km_num": 40000},
    {"band_idx": 5, "km_label": "50,000 km (Mid-Life Sensor & Suspension Window)", "km_num": 50000},
    {"band_idx": 6, "km_label": "60,000 km (Timing Belt & Valve Clearance Inspection)", "km_num": 60000},
    {"band_idx": 7, "km_label": "70,000 km (Clutch, Mounts & Cooling Refresh)", "km_num": 70000},
    {"band_idx": 8, "km_label": "80,000 km (Timing Belt Replacement & Major Overhaul)", "km_num": 80000},
    {"band_idx": 9, "km_label": "90,000 km (High-Mileage Harness & Chassis Conditioning)", "km_num": 90000},
    {"band_idx": 10, "km_label": "100,000+ km (Master Engine & Drivetrain Restoration)", "km_num": 100000},
]


def ensure_master_20k_database() -> int:
    conn = sqlite3.connect(MASTER_DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS alto800_master_issues (
                id INTEGER PRIMARY KEY,
                issue_code TEXT UNIQUE NOT NULL,
                dtc_code TEXT NOT NULL,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                manual_section TEXT NOT NULL,
                subsystem TEXT NOT NULL,
                severity TEXT NOT NULL,
                mileage_band TEXT NOT NULL,
                symptoms TEXT NOT NULL,
                root_cause TEXT NOT NULL,
                harness_routing TEXT NOT NULL,
                connector_pin TEXT NOT NULL,
                wire_color TEXT NOT NULL,
                ground_point TEXT NOT NULL,
                fuse_relay TEXT NOT NULL,
                expected_spec TEXT NOT NULL,
                realtime_fault_reading TEXT NOT NULL,
                mgp_part_number TEXT NOT NULL,
                part_cost_inr INTEGER NOT NULL,
                torque_nm INTEGER NOT NULL,
                zone_x INTEGER NOT NULL,
                zone_y INTEGER NOT NULL,
                diy_steps_json TEXT NOT NULL,
                image_url TEXT NOT NULL
            )
            """
        )
        cur.execute("SELECT COUNT(*) FROM alto800_master_issues")
        existing_count = cur.fetchone()[0]
        if existing_count >= 20000:
            return existing_count

        cur.execute("DELETE FROM alto800_master_issues")

        rows_to_insert = []
        issue_id = 0
        for comp in ALTO800_COMPONENTS:
            for mode in FAILURE_MODES:
                for band in MILEAGE_BANDS:
                    issue_id += 1
                    issue_code = f"ALTO800-ISS-{issue_id:05d}"
                    dtc_code = comp["base_dtc"]
                    title = f"[{dtc_code}] {comp['name']} — {mode['name']} ({band['km_label']})"
                    symptoms = (
                        f"Abnormal {comp['name']} behavior at {band['km_label']}; "
                        f"{mode['delta_desc']} Active/Pending Code: {dtc_code}."
                    )
                    root_cause = (
                        f"{mode['name']} affecting {comp['name']} (MGP #{comp['mgp']}) on 2013 Alto 800 F8D "
                        f"at {comp['pin']} ({comp['wire']} wire, Ground {comp['gnd']})."
                    )
                    harness_routing = (
                        f"Manual {comp['section']} -> Terminal {comp['pin']} -> Wire {comp['wire']} "
                        f"-> Protection {comp['fuse']} -> Return Ground {comp['gnd']}"
                    )

                    diy_steps = [
                        {
                            "step": 1,
                            "title": "Safety Disconnection & DLC Scan",
                            "detail": (
                                f"Chock rear wheels, set parking brake, connect OBD-II scanner to 16-pin DLC (Pin 7 K-Line / Pins 6&14 CAN) "
                                f"to record freeze-frame for {dtc_code}, then disconnect Battery Negative (-) at {comp['gnd']}."
                            ),
                        },
                        {
                            "step": 2,
                            "title": f"Locate {comp['name']} & Inspect Harness Routing",
                            "detail": (
                                f"Refer to Manual {comp['section']}. Locate {comp['name']} and inspect {comp['wire']} wire at {comp['pin']} "
                                f"and fuse/relay {comp['fuse']} for {mode['name'].lower()}."
                            ),
                        },
                        {
                            "step": 3,
                            "title": "Multimeter Pinout & Mechanical Spec Verification",
                            "detail": (
                                f"Back-probe {comp['pin']} ({comp['wire']}) to ground {comp['gnd']}. "
                                f"OEM Spec: {comp['spec']}. Fault condition detected: {mode['delta_desc']}"
                            ),
                        },
                        {
                            "step": 4,
                            "title": f"Service / Replace with Genuine MGP #{comp['mgp']}",
                            "detail": (
                                f"Clean connector terminals with electronic contact cleaner, repair/seal harness or install genuine "
                                f"Maruti Genuine Part #{comp['mgp']} (~₹{comp['cost']}). Torque fasteners to {comp['torque']} Nm."
                            ),
                        },
                        {
                            "step": 5,
                            "title": "ECM Relearn & Post-Repair Telemetry Validation",
                            "detail": (
                                f"Reconnect battery, clear DTC {dtc_code}, warm F8D engine to 90°C (800±50 RPM idle), "
                                f"and verify live reading stays within {comp['spec']}."
                            ),
                        },
                    ]

                    rows_to_insert.append(
                        (
                            issue_id,
                            issue_code,
                            dtc_code,
                            title,
                            comp["category"],
                            comp["section"],
                            comp["name"],
                            mode["severity"],
                            band["km_label"],
                            symptoms,
                            root_cause,
                            harness_routing,
                            comp["pin"],
                            comp["wire"],
                            comp["gnd"],
                            comp["fuse"],
                            comp["spec"],
                            mode["delta_desc"],
                            comp["mgp"],
                            comp["cost"],
                            comp["torque"],
                            comp["zone"][0],
                            comp["zone"][1],
                            json.dumps(diy_steps),
                            f"/api/manuals/image/{issue_id}.svg",
                        )
                    )

        cur.executemany(
            """
            INSERT INTO alto800_master_issues (
                id, issue_code, dtc_code, title, category, manual_section, subsystem,
                severity, mileage_band, symptoms, root_cause, harness_routing,
                connector_pin, wire_color, ground_point, fuse_relay, expected_spec,
                realtime_fault_reading, mgp_part_number, part_cost_inr, torque_nm,
                zone_x, zone_y, diy_steps_json, image_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows_to_insert,
        )

        cur.execute("CREATE INDEX IF NOT EXISTS idx_issues_dtc ON alto800_master_issues(dtc_code)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_issues_cat ON alto800_master_issues(category)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_issues_sec ON alto800_master_issues(manual_section)")
        conn.commit()
        return len(rows_to_insert)
    finally:
        conn.close()


def query_master_issues(
    q: Optional[str] = None,
    category: Optional[str] = None,
    manual_section: Optional[str] = None,
    dtc_code: Optional[str] = None,
    severity: Optional[str] = None,
    page: int = 1,
    limit: int = 24,
) -> Dict[str, Any]:
    ensure_master_20k_database()
    conn = sqlite3.connect(MASTER_DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        clauses = []
        params: List[Any] = []

        if category and category != "ALL":
            clauses.append("category = ?")
            params.append(category)
        if manual_section and manual_section != "ALL":
            clauses.append("manual_section = ?")
            params.append(manual_section)
        if dtc_code and dtc_code != "ALL":
            clauses.append("dtc_code LIKE ?")
            params.append(f"%{dtc_code.strip().upper()}%")
        if severity and severity != "ALL":
            clauses.append("severity = ?")
            params.append(severity.upper())
        if q and q.strip():
            kw = f"%{q.strip()}%"
            clauses.append(
                "(title LIKE ? OR dtc_code LIKE ? OR issue_code LIKE ? OR subsystem LIKE ? OR mgp_part_number LIKE ? OR symptoms LIKE ? OR wire_color LIKE ? OR ground_point LIKE ?)"
            )
            params.extend([kw, kw, kw, kw, kw, kw, kw, kw])

        where_sql = ("WHERE " + " AND ".join(clauses)) if clauses else ""

        cur.execute(f"SELECT COUNT(*) FROM alto800_master_issues {where_sql}", params)
        total_matches = cur.fetchone()[0]

        offset = max(0, (page - 1) * limit)
        cur.execute(
            f"""
            SELECT * FROM alto800_master_issues
            {where_sql}
            ORDER BY id ASC
            LIMIT ? OFFSET ?
            """,
            params + [limit, offset],
        )
        items = []
        for r in cur.fetchall():
            d = dict(r)
            d["diy_steps"] = json.loads(d.pop("diy_steps_json", "[]"))
            items.append(d)

        return {
            "total_in_database": 20000,
            "total_matches": total_matches,
            "page": page,
            "limit": limit,
            "total_pages": max(1, (total_matches + limit - 1) // limit),
            "items": items,
        }
    finally:
        conn.close()


def get_single_issue_by_id(issue_id: int) -> Optional[Dict[str, Any]]:
    ensure_master_20k_database()
    conn = sqlite3.connect(MASTER_DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM alto800_master_issues WHERE id = ?", (issue_id,))
        row = cur.fetchone()
        if not row:
            return None
        d = dict(row)
        d["diy_steps"] = json.loads(d.pop("diy_steps_json", "[]"))
        return d
    finally:
        conn.close()


def render_issue_blueprint_svg(issue_id: int) -> str:
    issue = get_single_issue_by_id(issue_id)
    if not issue:
        issue = get_single_issue_by_id(1)

    zx = issue["zone_x"]
    zy = issue["zone_y"]
    sev_color = "#ef4444" if issue["severity"] == "CRITICAL" else ("#f59e0b" if issue["severity"] == "HIGH" else "#38bdf8")

    def esc(s: Any) -> str:
        return (
            str(s)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

    steps = issue.get("diy_steps", [])
    s1 = esc(steps[0]["detail"][:92] + "...") if len(steps) > 0 else ""
    s2 = esc(steps[1]["detail"][:92] + "...") if len(steps) > 1 else ""
    s3 = esc(steps[2]["detail"][:92] + "...") if len(steps) > 2 else ""
    s4 = esc(steps[3]["detail"][:92] + "...") if len(steps) > 3 else ""

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 540" width="100%" height="100%">
  <defs>
    <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">
      <path d="M 24 0 L 0 0 0 24" fill="none" stroke="#1e293b" stroke-width="0.8"/>
    </pattern>
    <radialGradient id="hotspot" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{sev_color}" stop-opacity="0.85"/>
      <stop offset="100%" stop-color="{sev_color}" stop-opacity="0.0"/>
    </radialGradient>
  </defs>

  <!-- Blueprint Background -->
  <rect width="960" height="540" fill="#070b14"/>
  <rect width="960" height="540" fill="url(#grid)"/>
  <rect x="8" y="8" width="944" height="524" rx="10" fill="none" stroke="#1e3a8a" stroke-width="2"/>

  <!-- Top Engineering Title Banner -->
  <rect x="16" y="16" width="928" height="54" rx="8" fill="#0f172a" stroke="#334155"/>
  <text x="28" y="38" fill="#60a5fa" font-family="monospace" font-size="13" font-weight="bold">
    AUTOFIX AI ENGINEERING BLUEPRINT • {esc(issue['issue_code'])} • MANUAL {esc(issue['manual_section'])} • IMAGE #{issue['id']} OF 20,000
  </text>
  <text x="28" y="58" fill="#ffffff" font-family="sans-serif" font-size="14" font-weight="bold">
    {esc(issue['title'][:88])}
  </text>
  <rect x="815" y="26" width="115" height="32" rx="6" fill="{sev_color}" fill-opacity="0.2" stroke="{sev_color}"/>
  <text x="872" y="47" fill="{sev_color}" font-family="monospace" font-size="12" font-weight="bold" text-anchor="middle">
    {esc(issue['dtc_code'])}
  </text>

  <!-- PANEL A: 2013 ALTO 800 (FB308) CHASSIS & F8D ENGINE BAY ROUTING TOPOLOGY -->
  <rect x="16" y="80" width="540" height="225" rx="8" fill="#0b1324" stroke="#1e293b"/>
  <text x="28" y="100" fill="#38bdf8" font-family="monospace" font-size="11" font-weight="bold">
    [A] 2013 ALTO 800 (FB308) CHASSIS &amp; F8D HARNESS ROUTING LOCATOR (X:{zx}, Y:{zy})
  </text>

  <!-- Top-Down Vehicle Silhouette (Scaled inside Panel A) -->
  <g transform="translate(-140, 42) scale(0.82)">
    <!-- Body Outline -->
    <rect x="250" y="70" width="560" height="160" rx="38" fill="#0f172a" stroke="#475569" stroke-width="2.5"/>
    <!-- Front Bumper & Radiator Core -->
    <rect x="262" y="95" width="18" height="110" rx="4" fill="#1e293b" stroke="#64748b"/>
    <!-- F8D 3-Cyl Engine Block & Cylinder Head -->
    <rect x="315" y="115" width="75" height="72" rx="6" fill="#1e293b" stroke="#60a5fa" stroke-width="1.8"/>
    <circle cx="340" cy="128" r="9" fill="#0f172a" stroke="#93c5fd"/>
    <circle cx="340" cy="150" r="9" fill="#0f172a" stroke="#93c5fd"/>
    <circle cx="340" cy="172" r="9" fill="#0f172a" stroke="#93c5fd"/>
    <text x="352" y="110" fill="#93c5fd" font-family="monospace" font-size="10">F8D 796cc</text>
    <!-- 5MT Gearbox -->
    <rect x="365" y="168" width="42" height="34" rx="4" fill="#1e293b" stroke="#38bdf8"/>
    <!-- Battery & Engine J/B -->
    <rect x="282" y="82" width="28" height="24" rx="3" fill="#172554" stroke="#3b82f6"/>
    <!-- Firewall & Dashboard DLC / ECM -->
    <line x1="425" y1="74" x2="425" y2="226" stroke="#f59e0b" stroke-width="2" stroke-dasharray="5,3"/>
    <!-- Main Harness Spine -->
    <path d="M 295 95 L 375 145 L 445 125 L 580 115 L 785 115" fill="none" stroke="#22d3ee" stroke-width="2" stroke-dasharray="4,2"/>
    <path d="M 375 145 L 350 175 L 395 185" fill="none" stroke="#a855f7" stroke-width="1.8"/>

    <!-- Active Fault Hotspot Crosshair -->
    <circle cx="{zx}" cy="{zy}" r="28" fill="url(#hotspot)"/>
    <circle cx="{zx}" cy="{zy}" r="8" fill="{sev_color}" stroke="#ffffff" stroke-width="2"/>
    <line x1="{zx - 16}" y1="{zy}" x2="{zx + 16}" y2="{zy}" stroke="#ffffff" stroke-width="1.5"/>
    <line x1="{zx}" y1="{zy - 16}" x2="{zx}" y2="{zy + 16}" stroke="#ffffff" stroke-width="1.5"/>
  </g>

  <text x="28" y="292" fill="#94a3b8" font-family="monospace" font-size="11">
    Ground Return: <tspan fill="#34d399" font-weight="bold">{esc(issue['ground_point'])}</tspan> |
    Fuse/Relay: <tspan fill="#fbbf24" font-weight="bold">{esc(issue['fuse_relay'])}</tspan> |
    Terminal: <tspan fill="#60a5fa" font-weight="bold">{esc(issue['connector_pin'])}</tspan>
  </text>

  <!-- PANEL B: LIVE ELECTRICAL SCHEMATIC & MULTIMETER PINOUT -->
  <rect x="568" y="80" width="376" height="225" rx="8" fill="#0b1324" stroke="#1e293b"/>
  <text x="580" y="100" fill="#34d399" font-family="monospace" font-size="11" font-weight="bold">
    [B] CIRCUIT PINOUT &amp; MULTIMETER VERIFICATION
  </text>

  <!-- Schematic Diagram Boxes -->
  <rect x="582" y="114" width="115" height="68" rx="6" fill="#0f172a" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="639" y="136" fill="#93c5fd" font-family="monospace" font-size="10" text-anchor="middle" font-weight="bold">BOSCH ME17.9.71</text>
  <text x="639" y="152" fill="#e2e8f0" font-family="monospace" font-size="10" text-anchor="middle">{esc(issue['connector_pin'][:16])}</text>
  <text x="639" y="168" fill="#fbbf24" font-family="monospace" font-size="9" text-anchor="middle">{esc(issue['fuse_relay'][:18])}</text>

  <!-- Wire Line -->
  <line x1="697" y1="138" x2="805" y2="138" stroke="#38bdf8" stroke-width="3"/>
  <text x="751" y="130" fill="#38bdf8" font-family="monospace" font-size="10" text-anchor="middle" font-weight="bold">{esc(issue['wire_color'][:18])}</text>
  <line x1="697" y1="164" x2="805" y2="164" stroke="#34d399" stroke-width="2" stroke-dasharray="4,2"/>
  <text x="751" y="178" fill="#34d399" font-family="monospace" font-size="9" text-anchor="middle">GND {esc(issue['ground_point'])}</text>

  <!-- Component Box -->
  <rect x="805" y="114" width="125" height="68" rx="6" fill="#0f172a" stroke="{sev_color}" stroke-width="1.8"/>
  <text x="867" y="135" fill="#ffffff" font-family="sans-serif" font-size="10" text-anchor="middle" font-weight="bold">{esc(issue['subsystem'][:18])}</text>
  <text x="867" y="152" fill="#22d3ee" font-family="monospace" font-size="10" text-anchor="middle">MGP {esc(issue['mgp_part_number'])}</text>
  <text x="867" y="168" fill="#fbbf24" font-family="monospace" font-size="10" text-anchor="middle">Torque: {issue['torque_nm']} Nm</text>

  <!-- Expected vs Fault Reading Readout -->
  <rect x="582" y="196" width="348" height="44" rx="6" fill="#052e16" fill-opacity="0.5" stroke="#10b981"/>
  <text x="592" y="213" fill="#6ee7b7" font-family="monospace" font-size="10" font-weight="bold">OEM EXPECTED SPEC:</text>
  <text x="592" y="230" fill="#ffffff" font-family="monospace" font-size="11">{esc(issue['expected_spec'][:52])}</text>

  <rect x="582" y="248" width="348" height="46" rx="6" fill="#450a0a" fill-opacity="0.6" stroke="#ef4444"/>
  <text x="592" y="265" fill="#fca5a5" font-family="monospace" font-size="10" font-weight="bold">REAL-TIME FAULT SIGNATURE:</text>
  <text x="592" y="282" fill="#ffffff" font-family="monospace" font-size="10">{esc(issue['realtime_fault_reading'][:54])}</text>

  <!-- PANEL C: STEP-BY-STEP DIY SOLUTION & MGP PART CALLOUT -->
  <rect x="16" y="316" width="928" height="206" rx="8" fill="#0b1324" stroke="#1e293b"/>
  <text x="28" y="338" fill="#fbbf24" font-family="monospace" font-size="11" font-weight="bold">
    [C] STEP-BY-STEP DIY SOLUTION PROCEDURE • MARUTI GENUINE PART #{esc(issue['mgp_part_number'])} (~INR {issue['part_cost_inr']}) • FASTENER TORQUE: {issue['torque_nm']} Nm
  </text>

  <rect x="28" y="348" width="904" height="34" rx="5" fill="#0f172a" stroke="#1e293b"/>
  <text x="38" y="369" fill="#e2e8f0" font-family="sans-serif" font-size="11">
    <tspan fill="#38bdf8" font-weight="bold">STEP 1 (ISOLATE):</tspan> {s1}
  </text>

  <rect x="28" y="388" width="904" height="34" rx="5" fill="#0f172a" stroke="#1e293b"/>
  <text x="38" y="409" fill="#e2e8f0" font-family="sans-serif" font-size="11">
    <tspan fill="#38bdf8" font-weight="bold">STEP 2 (ROUTING):</tspan> {s2}
  </text>

  <rect x="28" y="428" width="904" height="34" rx="5" fill="#0f172a" stroke="#1e293b"/>
  <text x="38" y="449" fill="#e2e8f0" font-family="sans-serif" font-size="11">
    <tspan fill="#34d399" font-weight="bold">STEP 3 (TEST):</tspan> {s3}
  </text>

  <rect x="28" y="468" width="904" height="38" rx="5" fill="#0f172a" stroke="#1e3a8a"/>
  <text x="38" y="491" fill="#ffffff" font-family="sans-serif" font-size="11">
    <tspan fill="#fbbf24" font-weight="bold">STEP 4 &amp; 5 (FIX &amp; VERIFY):</tspan> {s4}
  </text>
</svg>"""
    return svg
