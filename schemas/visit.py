from pydantic import BaseModel, Field
from schemas import AttentionType, PatientStatus, Triage, VisitStatus
from datetime import datetime
from typing import Optional

class VisitBase(BaseModel):
    patient_dni: str = Field(..., description="The DNI of the patient")
    reason: str = Field(..., description="The reason of the attention")
    attention_type: AttentionType = Field(..., description="The type of the attention")
    location: str = Field(..., description="The location of the attention")
    admission_status: PatientStatus = Field(None, description="The status of the patient on admission")
    admission_heart_rate: Optional[int] = Field(None, description="The heart rate of the patient")
    admission_blood_pressure: Optional[int] = Field(None, description="The blood pressure of the patient")
    admission_temperature: Optional[float] = Field(None, description="The temperature of the patient")
    admission_oxygen_saturation: Optional[int] = Field(None, description="The oxygen saturation of the patient")
    triage: Optional[Triage] = Field(None, description="The triage of the patient")

class Visit(VisitBase):
    visit_id: str = Field(..., description="The ID of the visit")
    visit_status: VisitStatus = Field(..., description="The status of the visit")
    date_of_admission: Optional[datetime] = Field(None, description="The date of the admission")

    # Doctor information
    doctor_dni: str = Field(..., description="The DNI of the doctor")
    doctor_name: str = Field(..., description="The name of the doctor")
    doctor_email: Optional[str] = Field(None, description="The email of the doctor")
    doctor_specialty: Optional[str] = Field(None, description="The specialty of the doctor")
    
    diagnosis: Optional[str|None] = Field(None, description="The diagnosis of the patient",)
    tests: Optional[str|None] = Field(None, description="The tests of the patient")
    treatment: Optional[str|None] = Field(None, description="The treatment of the patient")
    evolution: Optional[str|None] = Field(None, description="The evolution of the patient")
    recommendations: Optional[str|None] = Field(None, description="The recommendations of the patient")
    medication: Optional[str|None] = Field(None, description="The medication of the patient")
    date_of_discharge: Optional[datetime|None] = Field(None, description="The date of the discharge")
    specialist_follow_up: Optional[str|None] = Field(None, description="The specialist follow up of the patient")
    additional_observations: Optional[str|None] = Field(None, description="The additional observations of the patient")
    notes: Optional[str|None] = Field(None, description="The notes of the patient")

class VisitUpdate(BaseModel):
    reason: Optional[str|None] = Field(None, description="The reason of the attention")
    admission_heart_rate: Optional[int|None] = Field(None, description="The heart rate of the patient")
    admission_blood_pressure: Optional[int|None] = Field(None, description="The blood pressure of the patient")
    admission_temperature: Optional[float|None] = Field(None, description="The temperature of the patient")
    admission_oxygen_saturation: Optional[int|None] = Field(None, description="The oxygen saturation of the patient")
    triage: Optional[Triage|None] = Field(None, description="The triage of the patient")
    diagnosis: Optional[str|None] = Field(None, description="The diagnosis of the patient",)
    tests: Optional[str|None] = Field(None, description="The tests of the patient")
    treatment: Optional[str|None] = Field(None, description="The treatment of the patient")
    evolution: Optional[str|None] = Field(None, description="The evolution of the patient")
    recommendations: Optional[str|None] = Field(None, description="The recommendations of the patient")
    medication: Optional[str|None] = Field(None, description="The medication of the patient")
    specialist_follow_up: Optional[str|None] = Field(None, description="The specialist follow up of the patient")
    additional_observations: Optional[str|None] = Field(None, description="The additional observations of the patient")
    notes: Optional[str|None] = Field(None, description="The notes of the patient")

class VisitSummary(BaseModel):
    visit_id: str = Field(..., description="The ID of the visit")
    visit_status: VisitStatus = Field(..., description="The status of the visit")
    doctor_dni: str = Field(..., description="The DNI of the doctor")
    doctor_name: str = Field(..., description="The name of the doctor")
    doctor_email: Optional[str] = Field(None, description="The email of the doctor")
    doctor_specialty: Optional[str] = Field(None, description="The specialty of the doctor")
    date_of_admission: datetime = Field(..., description="The date of the admission")
    date_of_discharge: Optional[datetime|None] = Field(None, description="The date of the discharge")
    reason: str = Field(..., description="The reason of the attention")
    attention_type: AttentionType = Field(..., description="The type of the attention")
    location: str = Field(..., description="The location of the attention")