from sqlalchemy.orm import Session
from database.models import FIRModel
from datetime import datetime
import time

def insert_fir_record(db: Session, file_name: str, fir_json: dict):
    record = FIRModel(
        file_name=file_name,
        fir_number=fir_json.get("fir_number"),
        police_station=fir_json.get("police_station"),
        district=fir_json.get("district"),
        state=fir_json.get("state"),
        date_of_incident=fir_json.get("date_of_incident"),
        date_of_filing=fir_json.get("date_of_filing"),
        complainant_name=fir_json.get("complainant_name"),
        complainant_contact=fir_json.get("complainant_contact"),
        accused_names=fir_json.get("accused_names"),
        victim_names=fir_json.get("victim_names"),
        crime_categories=fir_json.get("crime_categories"),
        sections_invoked=fir_json.get("sections_invoked"),
        location=fir_json.get("location"),
        generalised_location=fir_json.get("generalised_location"),
        incident_summary=fir_json.get("incident_summary"),
        actions_taken=fir_json.get("actions_taken"),
        attachments_mentioned=fir_json.get("attachments_mentioned"),
        translation_quality_notes=fir_json.get("translation_quality_notes"),
        raw_json=fir_json,
        created_at=datetime.utcnow()
    )

    db.add(record)
    db.commit()
    db.refresh(record)
    return record

def get_rows_missing_coordinates(db: Session):
    return db.query(FIRModel).filter(
        (FIRModel.latitude == None) | (FIRModel.longitude == None)
    ).all()


def update_coordinates(db: Session, file_name: str, lat: float, lon: float):
    db.query(FIRModel).filter(FIRModel.file_name == file_name).update({
        "latitude": lat,
        "longitude": lon
    })
    db.commit()
    