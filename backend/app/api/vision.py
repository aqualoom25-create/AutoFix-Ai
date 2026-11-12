from typing import Optional
from fastapi import APIRouter, File, Form, UploadFile
from pydantic import BaseModel
from app.engine.vision_warranty_engine import (
    inspect_uploaded_component_image,
    list_all_125_components_warranty_and_savings,
    list_vision_inspection_history,
)

router = APIRouter(
    prefix="/api/vision",
    tags=["AI Visual Inspector: Warranty, Durability & Part-Level Cost Saver"],
)


class VisionJsonInspectRequest(BaseModel):
    component_id: Optional[str] = "AUTO"
    filename: str = "alto800_component_photo.jpg"
    odometer_km: int = 68450
    part_age_months: Optional[int] = None
    part_km_driven: Optional[int] = None
    user_notes: str = ""
    record_history: bool = True


@router.post("/inspect")
async def inspect_vehicle_component_upload(
    file: Optional[UploadFile] = File(None),
    component_id: Optional[str] = Form("AUTO"),
    odometer_km: int = Form(68450),
    part_age_months: Optional[int] = Form(None),
    part_km_driven: Optional[int] = Form(None),
    user_notes: str = Form(""),
    record_history: bool = Form(True),
):
    img_bytes = b""
    fname = "uploaded_part_photo.jpg"
    if file is not None:
        img_bytes = await file.read()
        fname = file.filename or fname

    return inspect_uploaded_component_image(
        image_bytes=img_bytes,
        filename=fname,
        component_id=component_id or "AUTO",
        odometer_km=odometer_km,
        part_age_months=part_age_months,
        part_km_driven=part_km_driven,
        user_notes=user_notes,
        record_history=record_history,
    )


@router.post("/inspect-json")
def inspect_vehicle_component_json(payload: VisionJsonInspectRequest):
    return inspect_uploaded_component_image(
        image_bytes=payload.filename.encode("utf-8"),
        filename=payload.filename,
        component_id=payload.component_id or "AUTO",
        odometer_km=payload.odometer_km,
        part_age_months=payload.part_age_months,
        part_km_driven=payload.part_km_driven,
        user_notes=payload.user_notes,
        record_history=payload.record_history,
    )


@router.get("/history")
def get_vision_inspection_history(limit: int = 12):
    items = list_vision_inspection_history(limit=min(50, max(1, limit)))
    return {
        "total_returned": len(items),
        "history": items,
    }


@router.get("/components")
def get_all_components_warranty_and_part_level_savings(odometer_km: int = 68450):
    items = list_all_125_components_warranty_and_savings(odometer_km=odometer_km)
    total_dealer = sum(i["dealer_full_replacement_inr"] for i in items)
    total_part_level = sum(i["part_level_maintenance_inr"] for i in items)
    total_saved = total_dealer - total_part_level
    return {
        "total_components": len(items),
        "total_dealer_replacement_all_parts_inr": total_dealer,
        "total_part_level_maintenance_all_parts_inr": total_part_level,
        "total_potential_savings_inr": total_saved,
        "average_savings_percent": round((total_saved / float(total_dealer)) * 100.0, 1) if total_dealer else 0,
        "components": items,
    }
