from pydantic import BaseModel, Field
from schemas import BloodType, Gender, AttentionType, Triage

class Patient(BaseModel):
    name: str = Field(..., description="The name of the patient")
    dni: str = Field(..., description="The DNI of the patient")
    age: int = Field(..., description="The age of the patient")
    sex: Gender = Field(..., description="The sex of the patient")
    phone: str = Field(None, description="The phone number of the patient")
    blood_type: BloodType = Field(..., description="The blood type of the patient")
    allergies: str = Field(..., description="The allergies of the patient")
    medical_notes: str = Field(..., description="The medical history of the patient")
    notes: str = Field(..., description="The notes of the patient")

class PatientCreate(Patient):
    enabled: bool = Field(..., description="The enabled status of the patient")
    disabled_by: str = Field(None, description="The doctor who disabled the patient")

class PatientUpdate(BaseModel):
    age: int = Field(None, description="The age of the patient")
    phone: str = Field(None, description="The phone number of the patient")
    allergies: str = Field(None, description="The allergies of the patient")
    medical_notes: str = Field(None, description="The medical history of the patient")
    notes: str = Field(None, description="The notes of the patient")

class PatientAdmitted(BaseModel):
    name: str = Field(..., description="The name of the patient")
    dni: str = Field(..., description="The DNI of the patient")
    visit_id: str = Field(..., description="The ID of the visit")
    reason: str = Field(..., description="The reason of the attention")
    attention_type: AttentionType = Field(..., description="The type of the attention")
    triage: Triage = Field(..., description="The triage of the patient")
    doctor_dni: str = Field(..., description="The DNI of the doctor")
    doctor_name: str = Field(..., description="The name of the doctor")