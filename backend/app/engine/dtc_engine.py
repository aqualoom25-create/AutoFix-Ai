import json
import os
from typing import Dict, Any, List, Optional

ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(os.path.dirname(ENGINE_DIR))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
KB_DIR = os.path.join(PROJECT_ROOT, "knowledge_base")


class KnowledgeBaseLoader:
    _instance = None

    def __init__(self):
        self.vehicle_spec = self._load_json("vehicles", "maruti_alto_800_2013_petrol.json")
        self.dtc_catalog = self._load_json("dtc_codes", "alto_800_dtc_catalog.json").get("dtc_codes", {})
        self.wiring_data = self._load_json("wiring_diagrams", "alto_800_f8d_ecm_wiring.json")
        self.procedures = self._load_json("repair_procedures", "alto_800_service_procedures.json").get("procedures", {})

    def _load_json(self, subfolder: str, filename: str) -> Dict[str, Any]:
        path = os.path.join(KB_DIR, subfolder, filename)
        if not os.path.exists(path):
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @classmethod
    def get(cls) -> "KnowledgeBaseLoader":
        if cls._instance is None:
            cls._instance = KnowledgeBaseLoader()
        return cls._instance


def decode_dtc(code: str) -> Dict[str, Any]:
    kb = KnowledgeBaseLoader.get()
    normalized = code.strip().upper()
    if normalized in kb.dtc_catalog:
        entry = dict(kb.dtc_catalog[normalized])
        proc_id = entry.get("repair_procedure_id")
        if proc_id and proc_id in kb.procedures:
            entry["repair_procedure"] = kb.procedures[proc_id]
        comp_id = entry.get("electrical_test", {}).get("component_id")
        if comp_id and comp_id in kb.wiring_data.get("circuits", {}):
            entry["circuit_diagram"] = kb.wiring_data["circuits"][comp_id]
        return entry

    prefix_map = {
        "P0": "ISO/SAE Standard Powertrain Fault (ECM)",
        "P1": "Maruti Suzuki Manufacturer-Specific Powertrain Fault",
        "P2": "ISO/SAE Fuel & Air Metering Auxiliary Fault",
        "P3": "Ignition / Cylinder Firing Fault",
        "C0": "Chassis / Electric Power Steering (EPS) / ABS Fault",
        "B0": "Body / Immobilizer / Airbag Fault",
        "U0": "CAN / K-Line Network Communication Bus Fault",
    }
    category = prefix_map.get(normalized[:2], "On-Board Diagnostic Trouble Code")
    return {
        "code": normalized,
        "title": f"{category} ({normalized})",
        "category": category,
        "severity": "MEDIUM",
        "mil_illumination": True,
        "f8d_specific_context": (
            f"Code {normalized} reported by the 2013 Alto 800 ECM. Verify wiring harness continuity "
            "at the 60-pin/94-pin ECM connector and check sensor 5V reference and ground."
        ),
        "common_symptoms": ["Check Engine Light illuminated", "Altered engine drivability"],
        "probable_causes": [
            {"cause": f"Sensor signal out of range or circuit fault for {normalized}", "probability": 0.60},
            {"cause": "Connector oxidation or loose pin at F8D engine harness", "probability": 0.40},
        ],
        "diagnostic_questions": [],
        "electrical_test": {
            "component_id": "GENERAL_ECM_HARNESS",
            "reference_voltage_v": "5.0 V Reference / 12.0 V Battery Supply",
            "signal_koeo_v": "Verify against service manual pinout",
            "signal_warm_idle_v": "Check live PID stream",
            "ecm_pins": "Inspect ECM connector pins for corrosion",
        },
        "repair_procedure_id": None,
    }


def correlate_multiple_dtcs(codes: List[str]) -> Optional[Dict[str, Any]]:
    normalized = {c.strip().upper() for c in codes if c.strip()}
    if {"P0105", "P0171"}.issubset(normalized) or {"P0107", "P0171"}.issubset(normalized):
        return {
            "correlation_title": "Combined MAP + Lean Fault (Unifying Root Cause Detected)",
            "explanation": (
                "Both a Manifold Absolute Pressure (MAP) code and System Too Lean (P0171) are active simultaneously. "
                "On the 2013 Alto 800 F8D engine, an unsealed intake manifold vacuum leak (such as a split brake booster "
                "hose, cracked PCV hose, or torn MAP sensor O-ring) reduces manifold vacuum (raising MAP kPa) while "
                "introducing unmetered air that drives Long Term Fuel Trim past +25%. Do NOT replace the O2 sensor — "
                "fix the intake manifold vacuum leak first."
            ),
            "primary_subsystem": "Intake Manifold Vacuum & MAP Seal",
        }
    if len(normalized.intersection({"P0300", "P0301", "P0302", "P0303"})) >= 2:
        return {
            "correlation_title": "Multi-Cylinder F8D Misfire Correlation",
            "explanation": (
                "Multiple cylinder misfire codes are present on the 3-cylinder F8D engine. Because Cylinders 1, 2, and 3 "
                "share fuel rail supply, battery +12V coil feed, and camshaft timing belt alignment, inspect spark plug "
                "condition across all 3 cylinders, check fuel pump pressure (3.5 bar), and verify timing belt marks before "
                "replacing individual injectors."
            ),
            "primary_subsystem": "Common Ignition Supply / Fuel Rail Pressure / Valve Timing",
        }
    if {"P0335", "P0300"}.issubset(normalized):
        return {
            "correlation_title": "Crankshaft Position Sensor Drop-Out Causing Misfire Detection",
            "explanation": (
                "P0335 (CKP Sensor Circuit) is present alongside P0300 (Misfire). The F8D ECM calculates misfires by "
                "measuring crankshaft tooth acceleration via the CKP sensor. A failing CKP sensor (MGP 33220-76G30) "
                "or dirty reluctor wheel causes false P0300 codes and sudden hot-stalling. Resolve P0335 first."
            ),
            "primary_subsystem": "Crankshaft Position Sensor (CKP) Circuit",
        }
    return None
