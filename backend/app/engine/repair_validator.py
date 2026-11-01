from typing import Dict, Any
from app.engine.dtc_engine import KnowledgeBaseLoader


def validate_repair_execution(
    before_test: Dict[str, Any],
    after_test: Dict[str, Any],
) -> Dict[str, Any]:
    kb = KnowledgeBaseLoader.get()
    ranges = kb.vehicle_spec.get("electronics_and_diagnostics", {}).get("live_pid_normal_ranges_warm_idle", {})

    before_dtcs = before_test.get("dtc_codes", [])
    after_dtcs = after_test.get("dtc_codes", [])
    dtcs_cleared = len(after_dtcs) == 0

    parameter_comparisons = []
    all_params_in_spec = True
    checked_count = 0

    for pid_key, spec in ranges.items():
        if pid_key not in after_test and pid_key not in before_test:
            continue
        b_val = before_test.get(pid_key)
        a_val = after_test.get(pid_key)
        if a_val is None:
            continue
        try:
            a_float = float(a_val)
            b_float = float(b_val) if b_val is not None else None
        except (ValueError, TypeError):
            continue

        checked_count += 1
        min_v = float(spec["min"])
        max_v = float(spec["max"])
        in_spec = min_v <= a_float <= max_v
        if not in_spec:
            all_params_in_spec = False

        delta = round(a_float - b_float, 2) if b_float is not None else None
        parameter_comparisons.append({
            "parameter": pid_key,
            "before_value": b_float,
            "after_value": a_float,
            "delta": delta,
            "unit": spec.get("unit", ""),
            "oem_target_range": f"{min_v} - {max_v} {spec.get('unit', '')}",
            "passed": in_spec,
        })

    verified = dtcs_cleared and (all_params_in_spec if checked_count > 0 else True)

    if verified:
        verdict = "VERIFIED PASS — All DTCs cleared and post-repair F8D warm-idle parameters meet Maruti Suzuki OEM service specifications."
    elif not dtcs_cleared:
        verdict = f"VERIFICATION INCOMPLETE — Active fault codes remain in ECM memory: {', '.join(after_dtcs)}."
    else:
        verdict = "PARTIAL FIX — DTCs cleared, but one or more live engine parameters remain outside the F8D warm-idle specification."

    return {
        "verified": verified,
        "dtcs_before": before_dtcs,
        "dtcs_after": after_dtcs,
        "dtcs_cleared": dtcs_cleared,
        "parameter_comparisons": parameter_comparisons,
        "engineering_verdict": verdict,
    }


def validate_multimeter_measurement(
    circuit_id: str,
    ref_voltage_v: float = None,
    signal_voltage_v: float = None,
    resistance_ohms: float = None,
    mode: str = "idle",
) -> Dict[str, Any]:
    kb = KnowledgeBaseLoader.get()
    circuits = kb.wiring_data.get("circuits", {})
    circuit = circuits.get(circuit_id)
    if not circuit:
        return {"valid": False, "error": f"Unknown circuit_id: {circuit_id}"}

    rules = circuit.get("multimeter_validation_rules", {})
    checks = []
    overall_pass = True

    if ref_voltage_v is not None and "ref_voltage_min" in rules:
        passed = rules["ref_voltage_min"] <= ref_voltage_v <= rules["ref_voltage_max"]
        if not passed:
            overall_pass = False
        checks.append({
            "test": "5V / 12V Reference Supply Voltage",
            "measured": f"{ref_voltage_v} V",
            "expected": f"{rules['ref_voltage_min']} - {rules['ref_voltage_max']} V",
            "passed": passed,
            "diagnosis": "Reference supply OK." if passed else "Open/short in ECM reference supply wire or blown fuse.",
        })

    if signal_voltage_v is not None:
        min_key = "koeo_signal_min" if mode == "koeo" and "koeo_signal_min" in rules else "idle_signal_min"
        max_key = "koeo_signal_max" if mode == "koeo" and "koeo_signal_max" in rules else "idle_signal_max"
        if min_key in rules and max_key in rules:
            passed = rules[min_key] <= signal_voltage_v <= rules[max_key]
            if not passed:
                overall_pass = False
            checks.append({
                "test": f"Sensor Output Signal Voltage ({mode.upper()})",
                "measured": f"{signal_voltage_v} V",
                "expected": f"{rules[min_key]} - {rules[max_key]} V",
                "passed": passed,
                "diagnosis": (
                    "Sensor signal voltage is within OEM specification."
                    if passed
                    else f"Signal out of range — inspect {circuit.get('mgp_part', 'sensor')} or signal wire to ECM."
                ),
            })

    if resistance_ohms is not None and "resistance_20c_min" in rules:
        passed = rules["resistance_20c_min"] <= resistance_ohms <= rules["resistance_20c_max"]
        if not passed:
            overall_pass = False
        checks.append({
            "test": "Component Coil / Thermistor Resistance (@ ~20°C)",
            "measured": f"{resistance_ohms} Ω",
            "expected": f"{rules['resistance_20c_min']} - {rules['resistance_20c_max']} Ω",
            "passed": passed,
            "diagnosis": (
                "Internal winding/thermistor resistance OK."
                if passed
                else f"Internal component failure — replace MGP Part #{circuit.get('mgp_part', 'N/A')}."
            ),
        })

    return {
        "circuit_id": circuit_id,
        "circuit_name": circuit.get("name"),
        "mgp_part": circuit.get("mgp_part"),
        "overall_pass": overall_pass,
        "checks": checks,
    }
