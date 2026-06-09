from sqlalchemy import Column, Integer, String, Text, JSON, TIMESTAMP, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UserModel(Base):
    __tablename__ = "users"

    id           = Column(Integer, primary_key=True, index=True)
    name         = Column(String, nullable=False)
    email        = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=True)   # None for Google-auth users
    picture      = Column(String, nullable=True)
    provider     = Column(String, default="manual") # "google" or "manual"
    created_at   = Column(TIMESTAMP)

class FIRModel(Base):
    __tablename__ = "fir_records"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, nullable=False)

    fir_number = Column(String)
    police_station = Column(String)
    district = Column(String)
    state = Column(String)
    date_of_incident = Column(Text)
    date_of_filing = Column(Text)

    complainant_name = Column(String)
    complainant_contact = Column(String)

    accused_names = Column(JSON)
    victim_names = Column(JSON)
    crime_categories = Column(JSON)
    sections_invoked = Column(JSON)

    location = Column(Text)
    generalised_location = Column(Text)
    latitude = Column(Float, nullable=True)        # FIXED
    longitude = Column(Float, nullable=True) 
    incident_summary = Column(Text)
    actions_taken = Column(Text)
    attachments_mentioned = Column(JSON)
    translation_quality_notes = Column(Text)

    raw_json = Column(JSON, nullable=False)
    created_at = Column(TIMESTAMP)
