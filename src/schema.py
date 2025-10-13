from typing import List, Optional
from pydantic import BaseModel, Field

class FIRRecord(BaseModel):
    language_detected: Optional[str] = Field(
        default=None,
        description="Language of the original FIR content, if identifiable."
    )
    fir_number: Optional[str] = Field(default=None, description="FIR number or identifier.")
    police_station: Optional[str] = Field(default=None, description="Name of the police station.")
    district: Optional[str] = Field(default=None, description="District associated with the FIR.")
    state: Optional[str] = Field(default=None, description="State/Province associated with the FIR.")
    date_of_incident: Optional[str] = Field(default=None, description="Date or date range of the alleged incident.")
    date_of_filing: Optional[str] = Field(default=None, description="Date the FIR was filed/registered.")
    complainant_name: Optional[str] = Field(default=None, description="Name of the complainant/informant.")
    complainant_contact: Optional[str] = Field(default=None, description="Contact details of complainant, if present.")
    accused_names: Optional[List[str]] = Field(default=None, description="List of accused persons, if named.")
    victim_names: Optional[List[str]] = Field(default=None, description="List of victims mentioned, if any.")
    sections_invoked: Optional[List[str]] = Field(
        default=None,
        description="Statutes/sections invoked (e.g., IPC 420, IT Act 66C)."
    )
    location: Optional[str] = Field(default=None, description="Primary incident location/address.")
    incident_summary: Optional[str] = Field(
        default=None,
        description="Concise English summary of the incident and allegations (120–250 words)."
    )
    actions_taken: Optional[str] = Field(
        default=None,
        description="Immediate actions taken by police, if mentioned (arrest, seizure, FIR registration)."
    )
    attachments_mentioned: Optional[List[str]] = Field(
        default=None,
        description="Any annexures/attachments referenced (statements, photographs, invoices)."
    )
    translation_quality_notes: Optional[str] = Field(
        default=None,
        description="Short note on translation uncertainties, illegible text, missing pages, etc."
    )
