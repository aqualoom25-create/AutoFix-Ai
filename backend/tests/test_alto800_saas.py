import io
import cv2
import numpy as np
from PIL import Image
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


def test_vision_image_warranty_and_part_level_saver():
    with TestClient(app) as client:
        # 1. Check all 125 components warranty & part-level cost-saving matrix
        all_res = client.get("/api/vision/components")
        assert all_res.status_code == 200
        all_data = all_res.json()
        assert all_data["total_components"] == 125
        assert all_data["total_potential_savings_inr"] > 100000

        # 2. Upload an image of an expired-warranty 2013 factory component (Alternator CMP-040)
        fake_image = b"\xff\xd8\xff\xe0\x00\x10JFIF" + (b"\x20\x80\xd0" * 500)
        up_res = client.post(
            "/api/vision/inspect",
            files={"file": ("alto800_alternator_photo.jpg", fake_image, "image/jpeg")},
            data={"component_id": "CMP-040", "odometer_km": "68450"},
        )
        assert up_res.status_code == 200
        up_data = up_res.json()
        assert up_data["warranty_and_guarantee"]["factory_warranty_expired"] is True
        assert up_data["durability_and_reliability"]["within_repairable_reliability_limit"] is True
        plan = up_data["anti_overcosting_part_level_plan"]
        assert plan["action_directive"] == "DO NOT REPLACE ASSEMBLY — PERFORM PART-LEVEL MAINTENANCE"
        assert plan["part_level_maintenance_cost_inr"] < plan["dealer_full_replacement_quote_inr"]
        assert plan["total_rupees_saved_inr"] > 5000

        # 3. Check recently replaced MGP part within guarantee window (3 months / 4000 km)
        guar_res = client.post(
            "/api/vision/inspect-json",
            json={
                "component_id": "CMP-001",
                "filename": "map_sensor_new.jpg",
                "odometer_km": 68450,
                "part_age_months": 2,
                "part_km_driven": 3000,
            },
        )
        assert guar_res.status_code == 200
        guar_data = guar_res.json()
        assert guar_data["warranty_and_guarantee"]["mgp_part_guarantee_active"] is True

        # 4. Auto-detect a studio twin-disc clutch photo uploaded with a random hex filename (.webp)
        canvas = np.full((320, 480, 3), 242, dtype=np.uint8)
        # Left clutch pressure plate (metallic ring + diaphragm fingers + inner bore)
        cv2.circle(canvas, (145, 160), 92, (150, 155, 162), -1)
        cv2.circle(canvas, (145, 160), 86, (195, 200, 208), 8)
        cv2.circle(canvas, (145, 160), 48, (70, 75, 82), -1)
        cv2.circle(canvas, (145, 160), 18, (235, 235, 235), -1)
        # Right friction disc (darker lining ring + hub springs)
        cv2.circle(canvas, (355, 160), 70, (68, 70, 74), -1)
        cv2.circle(canvas, (355, 160), 42, (130, 134, 140), -1)
        cv2.circle(canvas, (355, 160), 15, (45, 45, 48), -1)
        buf = io.BytesIO()
        Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)).save(buf, format="WEBP")

        auto_res = client.post(
            "/api/vision/inspect",
            files={
                "file": (
                    "08f32b83096e76075cd5fd386970355e.webp",
                    buf.getvalue(),
                    "image/webp",
                )
            },
            data={"component_id": "AUTO", "odometer_km": "68450", "record_history": "true"},
        )
        assert auto_res.status_code == 200
        auto_data = auto_res.json()
        assert auto_data["status_updated"] is True
        assert auto_data["ai_detection"]["auto_detected"] is True
        assert auto_data["component"]["comp_id"] == "CMP-086"
        assert auto_data["visual_examination"]["thumbnail_data_url"].startswith("data:image/jpeg;base64,")

        # 5. Verify previous uploaded image inspection is saved & retrievable for previewing
        hist_res = client.get("/api/vision/history?limit=10")
        assert hist_res.status_code == 200
        hist_data = hist_res.json()
        assert hist_data["total_returned"] >= 1
        latest = hist_data["history"][0]
        assert latest["comp_id"] == "CMP-086"
        assert latest["filename"] == "08f32b83096e76075cd5fd386970355e.webp"
        assert latest["thumbnail_data_url"].startswith("data:image/jpeg;base64,")
        assert latest["full_report"]["component"]["comp_id"] == "CMP-086"

