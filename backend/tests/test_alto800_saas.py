from fastapi.testclient import TestClient
from app.main import app


def test_health_and_dashboard():
    with TestClient(app) as client:
        res = client.get("/api/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ok"
        assert "Alto 800" in data["target_vehicle"]
        assert data["master_issues_count"] == 20000
        assert data["realtime_solution_images_count"] == 20000

        html_res = client.get("/")
        assert html_res.status_code == 200
        assert "20,000 Issues" in html_res.text


def test_vehicle_registration_and_alto800_spec():
    with TestClient(app) as client:
        v_res = client.get("/api/vehicles")
        assert v_res.status_code == 200
        vehicles = v_res.json()
        assert len(vehicles) >= 1
        assert vehicles[0]["model"] == "Alto 800"
        assert vehicles[0]["year"] == 2013

        spec_res = client.get("/api/vehicles/spec/alto-800-2013")
        assert spec_res.status_code == 200
        spec = spec_res.json()
        assert spec["engine"]["code"] == "F8D"
        assert spec["engine"]["displacement_cc"] == 796


def test_workshop_manuals_and_20000_issues_and_images():
    with TestClient(app) as client:
        man_res = client.get("/api/manuals/workshop")
        assert man_res.status_code == 200
        man = man_res.json()
        assert len(man["manual_sections"]) == 14
        assert len(man["ground_points"]) == 14

        issues_res = client.get("/api/manuals/issues?q=P0105&limit=10")
        assert issues_res.status_code == 200
        issues_data = issues_res.json()
        assert issues_data["total_in_database"] == 20000
        assert issues_data["total_matches"] > 0
        assert len(issues_data["items"]) == 10

        for target_id in (1, 10000, 20000):
            det_res = client.get(f"/api/manuals/issues/{target_id}")
            assert det_res.status_code == 200
            det = det_res.json()
            assert det["id"] == target_id
            assert len(det["diy_steps"]) == 5

            img_res = client.get(f"/api/manuals/image/{target_id}.svg")
            assert img_res.status_code == 200
            assert "image/svg+xml" in img_res.headers["content-type"]
            assert f"IMAGE #{target_id} OF 20,000" in img_res.text


def test_ai_diagnostic_engine_and_correlation():
    with TestClient(app) as client:
        diag_res = client.post(
            "/api/diagnosis/analyze",
            json={
                "dtc_codes": ["P0105", "P0171"],
                "symptoms": ["rough_idle"],
                "live_telemetry": {"rpm": 1150, "map_kpa": 65, "stft_bank1_percent": 19.5},
                "qa_responses": {"q_map_idle": "yes"},
            },
        )
        assert diag_res.status_code == 200
        body = diag_res.json()
        diag = body["diagnosis"]
        assert "P0105" in diag["evaluated_dtc_codes"]
        assert diag["multi_dtc_correlation"] is not None
        assert len(diag["ranked_probable_causes"]) > 0
        assert len(diag["guided_repair_procedures"]) > 0


def test_multimeter_pinout_validator():
    with TestClient(app) as client:
        mm_res = client.post(
            "/api/diagnosis/multimeter-check",
            json={
                "circuit_id": "MAP_IAT_SENSOR",
                "mode": "idle",
                "ref_voltage_v": 5.01,
                "signal_voltage_v": 1.32,
            },
        )
        assert mm_res.status_code == 200
        mm_data = mm_res.json()
        assert mm_data["overall_pass"] is True


def test_repair_verification_validator():
    with TestClient(app) as client:
        rep_res = client.post(
            "/api/reports",
            json={
                "repair_description": "Replaced MAP sensor O-ring MGP 09280-10016 and cleaned intake port",
                "replaced_parts": [{"name": "MAP O-Ring", "mgp_part_number": "09280-10016"}],
                "before_test": {"dtc_codes": ["P0105"], "rpm": 1150, "map_kpa": 64},
                "after_test": {"dtc_codes": [], "rpm": 800, "map_kpa": 32},
            },
        )
        assert rep_res.status_code == 200
        rep_data = rep_res.json()
        assert rep_data["verified"] is True
        assert rep_data["verification_report"]["dtcs_cleared"] is True
