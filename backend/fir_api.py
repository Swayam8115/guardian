# backend/fir_api.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db import SessionLocal
from database.models import FIRModel

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/fir-data")
def get_fir_data(db: Session = Depends(get_db)):
    rows = db.query(
        FIRModel.latitude,
        FIRModel.longitude,
        FIRModel.crime_categories,
        FIRModel.incident_summary
    ).all()

    # Return only rows that have valid lat/lon
    return [
        {
            "latitude": r.latitude,
            "longitude": r.longitude,
            "crime_categories": r.crime_categories,
            "incident_summary": r.incident_summary
        }
        for r in rows
    ]
