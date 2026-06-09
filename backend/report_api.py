from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from database.db import SessionLocal
from database.models import FIRModel
from datetime import datetime, timezone

router = APIRouter()


class ReportRequest(BaseModel):
    complainant_name: str
    complainant_contact: str
    crime_type: str
    date_of_incident: str
    location: str
    incident_summary: str


@router.post("/report")
def submit_report(body: ReportRequest):
    db = SessionLocal()
    try:
        raw = body.model_dump()
        record = FIRModel(
            file_name=f"citizen_report_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            complainant_name=body.complainant_name,
            complainant_contact=body.complainant_contact,
            crime_categories=[body.crime_type],
            date_of_incident=body.date_of_incident,
            date_of_filing=datetime.now(timezone.utc).date().isoformat(),
            location=body.location,
            incident_summary=body.incident_summary,
            raw_json=raw,
            created_at=datetime.now(timezone.utc),
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return {"success": True, "id": record.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
