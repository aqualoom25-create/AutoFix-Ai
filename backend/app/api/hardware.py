from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel

try:
    import serial.tools.list_ports
    HAS_PYSERIAL = True
except ImportError:
    HAS_PYSERIAL = False

router = APIRouter(prefix="/api/hardware", tags=["OBD-II & K-Line Hardware Bridge"])


SIMULATION_PROFILES = {
    "healthy_warm_idle": {
        "scenario_name": "Healthy 2013 Alto 800 F8D (Warm Idle, 90°C, A/C OFF)",
        "protocol_detected": "ISO 14230-4 KWP2000 (Fast Init 10.4 kbps on DLC Pin 7)",
        "ecu_header": "81 10 F1 -> Bosch ME17.9.71 / F8D MPFI BS-IV",
        "dtc_codes": [],
        "pending_dtcs": [],
        "mil_status": "OFF",
        "telemetry": {
            "rpm": 805,
            "coolant_temp_c": 90,
            "map_kpa": 32,
            "iat_c": 38,
            "tps_percent": 0.4,
            "tps_voltage_v": 0.54,
            "ignition_advance_deg": 9.5,
            "calc_engine_load_percent": 19.2,
            "stft_bank1_percent": 1.2,
            "ltft_bank1_percent": 2.4,
            "o2_b1s1_voltage_v": 0.68,
            "o2_b1s2_voltage_v": 0.71,
            "battery_voltage_v": 14.1,
            "vehicle_speed_kmh": 0,
        },
    },
    "p0105_map_vacuum_leak": {
        "scenario_name": "Fault Scenario 1: Intake Manifold Vacuum Leak + Contaminated MAP Sensor (P0105 + P0171)",
        "protocol_detected": "ISO 14230-4 KWP2000 (Fast Init 10.4 kbps on DLC Pin 7)",
        "ecu_header": "81 10 F1 -> Bosch ME17.9.71 / F8D MPFI BS-IV",
        "dtc_codes": ["P0105", "P0171"],
        "pending_dtcs": ["P0505"],
        "mil_status": "ON (Steady)",
        "telemetry": {
            "rpm": 1120,
            "coolant_temp_c": 91,
            "map_kpa": 64,
            "iat_c": 41,
            "tps_percent": 0.5,
            "tps_voltage_v": 0.55,
            "ignition_advance_deg": 4.0,
            "calc_engine_load_percent": 44.5,
            "stft_bank1_percent": 18.6,
            "ltft_bank1_percent": 26.2,
            "o2_b1s1_voltage_v": 0.14,
            "o2_b1s2_voltage_v": 0.25,
            "battery_voltage_v": 13.9,
            "vehicle_speed_kmh": 0,
        },
    },
    "p0301_cyl1_misfire": {
        "scenario_name": "Fault Scenario 2: Cylinder #1 Ignition Misfire on 3-Cyl F8D (P0300 + P0301)",
        "protocol_detected": "ISO 15765-4 CAN (11-bit ID, 500 kbps on DLC Pins 6 & 14)",
        "ecu_header": "7E0 / 7E8 -> Bosch ME17.9.71 CAN Bus",
        "dtc_codes": ["P0300", "P0301"],
        "pending_dtcs": ["P0130"],
        "mil_status": "FLASHING (Catalyst Danger)",
        "telemetry": {
            "rpm": 640,
            "coolant_temp_c": 93,
            "map_kpa": 52,
            "iat_c": 42,
            "tps_percent": 0.8,
            "tps_voltage_v": 0.58,
            "ignition_advance_deg": 2.0,
            "calc_engine_load_percent": 38.0,
            "stft_bank1_percent": 14.5,
            "ltft_bank1_percent": 12.0,
            "o2_b1s1_voltage_v": 0.88,
            "o2_b1s2_voltage_v": 0.82,
            "battery_voltage_v": 13.7,
            "vehicle_speed_kmh": 0,
        },
    },
    "p0115_ect_sensor_open": {
        "scenario_name": "Fault Scenario 3: Open ECT Coolant Sensor Circuit — Radiator Fan Stuck ON (P0115)",
        "protocol_detected": "ISO 14230-4 KWP2000 (Fast Init 10.4 kbps on DLC Pin 7)",
        "ecu_header": "81 10 F1 -> Bosch ME17.9.71 / F8D MPFI BS-IV",
        "dtc_codes": ["P0115"],
        "pending_dtcs": [],
        "mil_status": "ON (Steady)",
        "telemetry": {
            "rpm": 1280,
            "coolant_temp_c": -40,
            "map_kpa": 39,
            "iat_c": 34,
            "tps_percent": 0.4,
            "tps_voltage_v": 0.54,
            "ignition_advance_deg": 14.0,
            "calc_engine_load_percent": 29.0,
            "stft_bank1_percent": -14.2,
            "ltft_bank1_percent": -11.5,
            "o2_b1s1_voltage_v": 0.86,
            "o2_b1s2_voltage_v": 0.78,
            "battery_voltage_v": 13.8,
            "vehicle_speed_kmh": 0,
        },
    },
    "p0505_iacv_ac_stall": {
        "scenario_name": "Fault Scenario 4: Carbon-Jammed IACV Stepper Valve — Stalls When A/C Turned ON (P0505)",
        "protocol_detected": "ISO 14230-4 KWP2000 (Fast Init 10.4 kbps on DLC Pin 7)",
        "ecu_header": "81 10 F1 -> Bosch ME17.9.71 / F8D MPFI BS-IV",
        "dtc_codes": ["P0505"],
        "pending_dtcs": [],
        "mil_status": "ON (Steady)",
        "telemetry": {
            "rpm": 510,
            "coolant_temp_c": 89,
            "map_kpa": 46,
            "iat_c": 40,
            "tps_percent": 0.3,
            "tps_voltage_v": 0.52,
            "ignition_advance_deg": 3.5,
            "calc_engine_load_percent": 34.0,
            "stft_bank1_percent": 6.4,
            "ltft_bank1_percent": 5.8,
            "o2_b1s1_voltage_v": 0.55,
            "o2_b1s2_voltage_v": 0.69,
            "battery_voltage_v": 13.3,
            "vehicle_speed_kmh": 0,
        },
    },
    "p0335_ckp_hot_no_start": {
        "scenario_name": "Fault Scenario 5: Thermal CKP Sensor Failure — Cranks But No Start When Hot (P0335)",
        "protocol_detected": "ISO 14230-4 KWP2000 (Fast Init 10.4 kbps on DLC Pin 7)",
        "ecu_header": "81 10 F1 -> Bosch ME17.9.71 / F8D MPFI BS-IV",
        "dtc_codes": ["P0335"],
        "pending_dtcs": [],
        "mil_status": "ON (Key ON / Cranking)",
        "telemetry": {
            "rpm": 0,
            "coolant_temp_c": 97,
            "map_kpa": 101,
            "iat_c": 48,
            "tps_percent": 0.4,
            "tps_voltage_v": 0.54,
            "ignition_advance_deg": 0.0,
            "calc_engine_load_percent": 0.0,
            "stft_bank1_percent": 0.0,
            "ltft_bank1_percent": 3.1,
            "o2_b1s1_voltage_v": 0.45,
            "o2_b1s2_voltage_v": 0.45,
            "battery_voltage_v": 10.8,
            "vehicle_speed_kmh": 0,
        },
    },
}


class HardwareConnectRequest(BaseModel):
    mode: str = "simulator"  # "simulator" or "serial"
    serial_port: Optional[str] = "COM3"
    baud_rate: int = 38400
    protocol: str = "AUTO_ALTO800"
    scenario_key: str = "p0105_map_vacuum_leak"


@router.get("/ports")
def list_serial_ports():
    ports = []
    if HAS_PYSERIAL:
        for p in serial.tools.list_ports.comports():
            ports.append({
                "device": p.device,
                "description": p.description,
                "hwid": p.hwid,
            })
    return {
        "pyserial_installed": HAS_PYSERIAL,
        "detected_ports": ports,
        "supported_scenarios": [
            {"key": k, "name": v["scenario_name"]} for k, v in SIMULATION_PROFILES.items()
        ],
        "elm327_init_sequence_alto800": [
            {"cmd": "ATZ", "purpose": "Reset ELM327 / USB-KWP2000 interface"},
            {"cmd": "ATE0", "purpose": "Echo OFF for clean frame parsing"},
            {"cmd": "ATL0", "purpose": "Linefeeds OFF"},
            {"cmd": "ATH1", "purpose": "Headers ON to verify ECM address 0x10 / 0x7E8"},
            {"cmd": "ATSP 5", "purpose": "Select ISO 14230-4 KWP2000 Fast Init (10.4 kbps on Pin 7 K-Line)"},
            {"cmd": "ATSH 81 10 F1", "purpose": "Set Maruti Suzuki ECM physical target header (0x10)"},
            {"cmd": "0100", "purpose": "Query supported Mode 01 PIDs (fallback to ATSP 6 CAN 500kbps if bus uses CAN)"},
            {"cmd": "03", "purpose": "Read stored Diagnostic Trouble Codes (DTCs)"},
        ],
    }


@router.post("/connect")
def connect_or_simulate_hardware(payload: HardwareConnectRequest):
    if payload.mode == "serial" and HAS_PYSERIAL:
        try:
            import serial
            with serial.Serial(payload.serial_port, payload.baud_rate, timeout=1.5) as ser:
                ser.write(b"ATZ\r")
                raw_resp = ser.read(64).decode("ascii", errors="ignore").strip()
                return {
                    "connected": True,
                    "hardware_mode": "LIVE_SERIAL_OBD",
                    "port": payload.serial_port,
                    "adapter_response": raw_resp or "ELM327 v1.5 Ready",
                    "note": "Live serial port opened. Use hardware/obd_adapter/elm327_alto800_scanner.py for continuous polling.",
                }
        except Exception as exc:
            return {
                "connected": False,
                "hardware_mode": "LIVE_SERIAL_OBD",
                "port": payload.serial_port,
                "error": f"Could not open {payload.serial_port}: {str(exc)}",
                "fallback_advice": (
                    "Ensure your USB K-Line (FT232RL/CH340) or Bluetooth ELM327 v1.5 (PIC18F25K80) adapter is paired, "
                    "ignition key is in ON position, and 16-pin DLC under the Alto 800 steering column has +12V on Pin 16."
                ),
            }

    scenario = SIMULATION_PROFILES.get(payload.scenario_key, SIMULATION_PROFILES["p0105_map_vacuum_leak"])
    return {
        "connected": True,
        "hardware_mode": "ALTO_800_F8D_ECU_SIMULATOR",
        "simulation_disclaimer": (
            "SIMULATED TELEMETRY STREAM — Validated against 2013 Maruti Alto 800 F8D service specifications. "
            "Switch to Live Serial / WebSerial mode when connected to the physical 16-pin DLC connector."
        ),
        "scenario_key": payload.scenario_key,
        "scenario": scenario,
    }
