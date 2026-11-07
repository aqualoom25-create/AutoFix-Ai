import json
import os
from typing import Optional
from fastapi import APIRouter, HTTPException, Response
from app.engine.master_kb_builder import (
    KB_DIR,
    ensure_master_20k_database,
    query_master_issues,
    get_single_issue_by_id,
    render_issue_blueprint_svg,
    ALTO800_COMPONENTS,
    FAILURE_MODES,
)

router = APIRouter(prefix="/api/manuals", tags=["Service Manuals, Wiring Routings & 20,000 Issues DB"])


@router.get("/workshop")
def get_workshop_manual_and_routings():
    path = os.path.join(KB_DIR, "manuals", "alto_800_2013_workshop_manual.json")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Workshop manual file not found")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/stats")
def get_master_20k_stats():
    total = ensure_master_20k_database()
    return {
        "total_issues_in_db": total,
        "total_solution_images": total,
        "total_components_covered": len(ALTO800_COMPONENTS),
        "total_failure_modes": len(FAILURE_MODES),
        "categories": [
            "OBD-II Real-Time DTC",
            "Electrical & Wiring Routing",
            "Engine Mechanical",
            "Drivetrain & 5MT Gearbox",
            "Suspension, Steering & Brakes",
            "HVAC & Body Systems",
        ],
    }


@router.get("/issues")
def search_20000_issues(
    q: Optional[str] = None,
    category: Optional[str] = None,
    manual_section: Optional[str] = None,
    dtc_code: Optional[str] = None,
    severity: Optional[str] = None,
    page: int = 1,
    limit: int = 24,
):
    return query_master_issues(
        q=q,
        category=category,
        manual_section=manual_section,
        dtc_code=dtc_code,
        severity=severity,
        page=max(1, page),
        limit=min(100, max(1, limit)),
    )


@router.get("/issues/{issue_id}")
def get_issue_detail(issue_id: int):
    item = get_single_issue_by_id(issue_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Issue #{issue_id} not found (valid range: 1..20000)")
    return item


@router.get("/image/{issue_id}.svg")
def get_issue_realtime_blueprint_image(issue_id: int):
    if issue_id < 1 or issue_id > 20000:
        raise HTTPException(status_code=404, detail="Image ID must be between 1 and 20000")
    svg_content = render_issue_blueprint_svg(issue_id)
    return Response(content=svg_content, media_type="image/svg+xml")
