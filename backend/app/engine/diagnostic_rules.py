from typing import List, Dict, Any, Optional
from app.engine.dtc_engine import KnowledgeBaseLoader, decode_dtc, correlate_multiple_dtcs

SYMPTOM_TO_DTC_MAP = {
    "rough_idle": ["P0105", "P0505"],
    "stalls_with_ac": ["P0505", "P0105"],
    "cranks_no_start_hot": ["P0335"],
    "engine_shaking_misfire": ["P0300", "P0301"],
    "fan_always_on_cold": ["P0115"],
    "jerk_on_acceleration": ["P0120", "P0171"],
    "poor_fuel_mileage_black_smoke": ["P0130", "P0105"],
    "speedometer_dead_stalling": ["P0500"],
}


def analyze_live_telemetry(telemetry: Dict[str, Any]) -> List[Dict[str, Any]]:
    kb = KnowledgeBaseLoader.get()
    ranges = kb.vehicle_spec.get("electronics_and_diagnostics", {}).get("live_pid_normal_ranges_warm_idle", {})
    anomalies = []

    if not telemetry:
        return anomalies

    for key, spec in ranges.items():
        if key not in telemetry or telemetry[key] is None:
            continue
        try:
            val = float(telemetry[key])
        except (ValueError, TypeError):
            continue

        min_v = float(spec["min"])
        max_v = float(spec["max"])
        unit = spec.get("unit", "")

        if val < min_v or val > max_v:
            status = "LOW" if val < min_v else "HIGH"
            inferred_dtc = None
            engineering_note = ""
            if key == "map_kpa" and val > max_v:
                inferred_dtc = "P0105"
                engineering_note = (
                    f"MAP reading of {val} kPa at warm idle is above the 27-38 kPa F8D vacuum specification. "
                    "Indicates low manifold vacuum (intake leak, tight exhaust valves, or contaminated MAP sensor)."
                )
            elif key == "coolant_temp_c" and (val < 40 or val > 103):
                inferred_dtc = "P0115"
                engineering_note = (
                    f"Coolant temperature of {val}°C is outside normal warm operating window (85-98°C). "
                    "Check ECT sensor thermistor resistance or radiator fan relay operation."
                )
            elif key in ("stft_bank1_percent", "ltft_bank1_percent") and val > max_v:
                inferred_dtc = "P0171"
                engineering_note = (
                    f"Positive fuel trim (+{val}%) shows the F8D ECM is injecting extra petrol to compensate "
                    "for unmetered air (vacuum leak) or weak fuel pump pressure (<3.0 bar)."
                )
            elif key == "rpm" and (val < 700 or val > 950):
                inferred_dtc = "P0505"
                engineering_note = (
                    f"Idle speed ({val} RPM) deviates from the 800 ± 50 RPM specification. Inspect IACV bypass passage."
                )
            elif key == "tps_percent" and val > 2.5:
                inferred_dtc = "P0120"
                engineering_note = (
                    f"Closed-throttle TPS reads {val}% instead of 0.0-1.5%. Throttle butterfly may be held open by carbon or tight cable."
                )
            elif key == "battery_voltage_v" and val < 13.2:
                inferred_dtc = "P0562"
                engineering_note = (
                    f"Charging voltage ({val}V) is below 13.6V alternator output spec. Weak voltage causes erratic ECM sensor readings."
                )
            else:
                engineering_note = f"Parameter {key} ({val} {unit}) is {status} compared to OEM range ({min_v}-{max_v} {unit})."

            anomalies.append({
                "parameter": key,
                "measured_value": val,
                "unit": unit,
                "expected_range": f"{min_v} - {max_v} {unit}",
                "status": status,
                "inferred_dtc": inferred_dtc,
                "engineering_note": engineering_note,
            })

    return anomalies


def run_diagnostic_engine(
    dtc_codes: List[str],
    symptoms: List[str],
    live_telemetry: Optional[Dict[str, Any]] = None,
    qa_responses: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    live_telemetry = live_telemetry or {}
    qa_responses = qa_responses or {}

    normalized_codes = []
    for c in dtc_codes:
        clean = c.strip().upper()
        if clean and clean not in normalized_codes:
            normalized_codes.append(clean)

    telemetry_anomalies = analyze_live_telemetry(live_telemetry)

    inferred_codes = []
    for s in symptoms:
        s_key = s.strip().lower().replace(" ", "_")
        for mapped in SYMPTOM_TO_DTC_MAP.get(s_key, []):
            if mapped not in normalized_codes and mapped not in inferred_codes:
                inferred_codes.append(mapped)
        for keyword, dtc_list in [
            ("idle", ["P0505", "P0105"]),
            ("ac", ["P0505"]),
            ("misfire", ["P0300", "P0301"]),
            ("shake", ["P0300"]),
            ("vibrat", ["P0300"]),
            ("stall", ["P0335", "P0505"]),
            ("crank", ["P0335"]),
            ("fan", ["P0115"]),
            ("coolant", ["P0115"]),
            ("overheat", ["P0115"]),
            ("mileage", ["P0130", "P0105"]),
            ("smoke", ["P0105", "P0130"]),
            ("speed", ["P0500"]),
            ("jerk", ["P0120", "P0171"]),
            ("lean", ["P0171"]),
        ]:
            if keyword in s.lower():
                for mapped in dtc_list:
                    if mapped not in normalized_codes and mapped not in inferred_codes:
                        inferred_codes.append(mapped)

    for anomaly in telemetry_anomalies:
        inf = anomaly.get("inferred_dtc")
        if inf and inf not in normalized_codes and inf not in inferred_codes:
            inferred_codes.append(inf)

    all_active_codes = normalized_codes if normalized_codes else (inferred_codes[:2] or ["P0105"])

    decoded_dtcs = [decode_dtc(code) for code in all_active_codes]
    correlation = correlate_multiple_dtcs(all_active_codes)

    ranked_causes = []
    diagnostic_questions = []
    recommended_procedures = []
    electrical_tests = []
    safety_alerts = [
        "Verify vehicle is in Neutral with parking brake engaged and wheels chocked before running engine tests.",
        "Do NOT purchase or replace ECM/sensors blindly — perform the 5V Reference and Multimeter Pinout checks below first.",
    ]

    highest_severity = "LOW"
    severity_rank = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}

    for dtc in decoded_dtcs:
        sev = dtc.get("severity", "MEDIUM")
        if severity_rank.get(sev, 2) > severity_rank.get(highest_severity, 1):
            highest_severity = sev

        if sev == "CRITICAL":
            safety_alerts.insert(
                0,
                f"CRITICAL FAULT ({dtc['code']}): Avoid high-load driving to prevent catalytic converter or F8D engine damage.",
            )

        questions = dtc.get("diagnostic_questions", [])
        for q in questions:
            diagnostic_questions.append({
                "dtc_code": dtc["code"],
                "id": q["id"],
                "question": q["question"],
                "impact": q["impact"],
                "user_answer": qa_responses.get(q["id"], "UNANSWERED"),
            })

        causes = [dict(c) for c in dtc.get("probable_causes", [])]
        for q in questions:
            ans = str(qa_responses.get(q["id"], "")).lower()
            target_idx = q.get("yes_weight_cause", 0)
            if ans == "yes" and 0 <= target_idx < len(causes):
                causes[target_idx]["probability"] = min(0.92, round(causes[target_idx]["probability"] + 0.22, 2))
            elif ans == "no" and 0 <= target_idx < len(causes):
                causes[target_idx]["probability"] = max(0.08, round(causes[target_idx]["probability"] - 0.15, 2))

        total_p = sum(c["probability"] for c in causes) or 1.0
        for c in causes:
            norm_p = round((c["probability"] / total_p) * 100, 1)
            ranked_causes.append({
                "dtc_code": dtc["code"],
                "cause": c["cause"],
                "confidence_percent": norm_p,
            })

        if dtc.get("electrical_test"):
            etest = dict(dtc["electrical_test"])
            etest["dtc_code"] = dtc["code"]
            if dtc.get("circuit_diagram"):
                etest["circuit_diagram"] = dtc["circuit_diagram"]
            electrical_tests.append(etest)

        if dtc.get("repair_procedure"):
            proc = dtc["repair_procedure"]
            if not any(p["id"] == proc["id"] for p in recommended_procedures):
                recommended_procedures.append(proc)

    ranked_causes.sort(key=lambda x: x["confidence_percent"], reverse=True)

    primary_dtc = decoded_dtcs[0]
    top_cause = ranked_causes[0]["cause"] if ranked_causes else "Sensor circuit or vacuum anomaly"
    ai_summary = (
        f"Engineering Analysis for 2013 Maruti Suzuki Alto 800 (0.8L F8D MPFI Petrol): "
        f"Detected primary fault {primary_dtc['code']} — {primary_dtc['title']} (Severity: {highest_severity}). "
        f"{primary_dtc.get('f8d_specific_context', '')} "
        f"Based on rule evaluation{', live telemetry anomalies,' if telemetry_anomalies else ''} "
        f"and diagnostic weighting, the highest-probability root cause is: {top_cause} "
        f"({ranked_causes[0]['confidence_percent'] if ranked_causes else 60}% confidence)."
    )

    return {
        "vehicle_profile": "2013 Maruti Suzuki Alto 800 • 0.8L F8D 12V MPFI Petrol • BS-IV",
        "severity": highest_severity,
        "evaluated_dtc_codes": all_active_codes,
        "inferred_from_symptoms": len(normalized_codes) == 0,
        "ai_engineering_summary": ai_summary,
        "multi_dtc_correlation": correlation,
        "decoded_dtcs": decoded_dtcs,
        "ranked_probable_causes": ranked_causes,
        "telemetry_anomalies": telemetry_anomalies,
        "interactive_questions": diagnostic_questions,
        "electrical_pinout_tests": electrical_tests,
        "guided_repair_procedures": recommended_procedures,
        "safety_guardrails": safety_alerts,
    }
