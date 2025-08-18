from pydantic import BaseModel, Field
from schemas import BloodType, Gender, AttentionType, Triage
from typing import Optional, List
from datetime import datetime


# Esquemas para transferencia de datos (DTOs)

class PatientBase(BaseModel):
    """Esquema base para datos básicos de paciente"""
    name: str = Field(..., min_length=2, description="Nombre completo del paciente")
    dni: str = Field(..., description="DNI del paciente")
    age: int = Field(..., ge=0, le=150, description="Edad del paciente")
    sex: Gender = Field(..., description="Género del paciente")
    phone: Optional[str] = Field(None, description="Número de teléfono del paciente")
    blood_type: BloodType = Field(..., description="Tipo de sangre del paciente")


class PatientCreate(PatientBase):
    """Esquema para crear un nuevo paciente"""
    
    # Historial médico inicial
    allergies: List[str] = Field(default_factory=list, description="Lista de alergias del paciente")
    medical_notes: str = Field("", description="Notas médicas generales")
    major_surgeries: List[str] = Field(default_factory=list, description="Cirugías mayores")
    current_medications: List[str] = Field(default_factory=list, description="Medicamentos actuales")
    chronic_conditions: List[str] = Field(default_factory=list, description="Condiciones crónicas")
    family_history: str = Field("", description="Historial familiar")


class PatientUpdate(BaseModel):
    """Esquema para actualizar datos básicos de paciente"""
    name: Optional[str] = Field(None, min_length=2, description="Nombre completo del paciente")
    age: Optional[int] = Field(None, ge=0, le=150, description="Edad del paciente")
    phone: Optional[str] = Field(None, description="Número de teléfono del paciente")
    discapacity_level: Optional[int] = Field(None, description="Nivel de discapacidad del paciente")



class PatientMedicalHistoryUpdate(BaseModel):
    """Esquema para actualizar historial médico"""
    allergies: Optional[List[str]] = Field(None, description="Lista de alergias del paciente")
    medical_notes: Optional[str] = Field(None, description="Notas médicas generales")
    major_surgeries: Optional[List[str]] = Field(None, description="Cirugías mayores")
    current_medications: Optional[List[str]] = Field(None, description="Medicamentos actuales")
    chronic_conditions: Optional[List[str]] = Field(None, description="Condiciones crónicas")
    family_history: Optional[str] = Field(None, description="Historial familiar")

class BloodAnalysisCreate(BaseModel):
    """Esquema para crear un análisis de sangre"""
    red_blood_cells: float = Field(..., ge=0, description="Glóbulos rojos (millones/μL)")
    hemoglobin: float = Field(..., ge=0, description="Hemoglobina (g/dL)")
    hematocrit: float = Field(..., ge=0, le=100, description="Hematocrito (%)")
    platelets: int = Field(..., ge=0, description="Plaquetas (/μL)")
    lymphocytes: float = Field(..., ge=0, le=100, description="Linfocitos (%)")
    glucose: int = Field(..., ge=0, description="Glucosa (mg/dL)")
    cholesterol: int = Field(..., ge=0, description="Colesterol (mg/dL)")
    urea: int = Field(..., ge=0, description="Urea (mg/dL)")
    cocaine: float = Field(0, ge=0, description="Nivel de cocaína (ng/mL)")
    alcohol: float = Field(0, ge=0, description="Nivel de alcohol (mg/dL)")
    mdma: float = Field(0, ge=0, description="Nivel de MDMA (ng/mL)")
    fentanyl: float = Field(0, ge=0, description="Nivel de fentanilo (ng/mL)")
    notes: Optional[str] = Field(None, description="Notas adicionales del análisis")


class BloodAnalysisCreateForVisit(BloodAnalysisCreate):
    """Esquema para crear un análisis de sangre relacionado con una visita específica"""
    visit_id: str = Field(..., description="ID de la visita relacionada")


class BloodAnalysisResponse(BloodAnalysisCreate):
    """Esquema de respuesta para análisis de sangre"""
    analysis_id: str = Field(..., description="ID único del análisis")
    date_performed: datetime = Field(..., description="Fecha del análisis")
    performed_by_dni: Optional[str] = Field(None, description="DNI del médico que realizó el análisis")
    performed_by_name: Optional[str] = Field(None, description="Nombre del médico que realizó el análisis")
    visit_related_id: Optional[str] = Field(None, description="ID de la visita relacionada")


class RadiologyStudyCreate(BaseModel):
    """Esquema para crear un estudio radiológico"""
    study_type: str = Field(..., description="Tipo de estudio (Rayos X, CT, MRI, etc.)")
    body_part: str = Field(..., description="Parte del cuerpo estudiada")
    findings: str = Field(..., description="Hallazgos del estudio")
    image_url: Optional[str] = Field(None, description="URL de la imagen si está disponible")

class RadiologyStudyCreateForVisit(RadiologyStudyCreate):
    """Esquema para crear un estudio radiológico relacionado con una visita específica"""
    visit_id: str = Field(..., description="ID de la visita relacionada")


class RadiologyStudyResponse(RadiologyStudyCreate):
    """Esquema de respuesta para estudios radiológicos"""
    study_id: str = Field(..., description="ID único del estudio")
    date_performed: datetime = Field(..., description="Fecha del estudio")
    performed_by_dni: Optional[str] = Field(None, description="DNI del médico que realizó el estudio")
    performed_by_name: Optional[str] = Field(None, description="Nombre del médico que realizó el estudio")
    visit_related_id: Optional[str] = Field(None, description="ID de la visita relacionada")


class MedicalHistoryResponse(BaseModel):
    """Esquema de respuesta para historial médico completo"""
    allergies: List[str] = Field(..., description="Lista de alergias del paciente")
    medical_notes: str = Field(..., description="Notas médicas generales")
    major_surgeries: List[str] = Field(..., description="Cirugías mayores")
    current_medications: List[str] = Field(..., description="Medicamentos actuales")
    chronic_conditions: List[str] = Field(..., description="Condiciones crónicas")
    family_history: str = Field(..., description="Historial familiar")
    blood_analyses: List[BloodAnalysisResponse] = Field(..., description="Análisis de sangre")
    radiology_studies: List[RadiologyStudyResponse] = Field(..., description="Estudios radiológicos")
    last_updated: datetime = Field(..., description="Última actualización del historial")
    updated_by: Optional[str] = Field(None, description="DNI del médico que actualizó el historial")


class Patient(PatientBase):
    """Esquema de respuesta básica de paciente (sin historial completo)"""
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Última actualización")


class PatientComplete(Patient):
    """Esquema de respuesta completa de paciente (con historial médico)"""
    medical_history: MedicalHistoryResponse = Field(..., description="Historial médico completo")
    created_by: Optional[str] = Field(None, description="DNI del médico que creó el registro")
    last_updated_by: Optional[str] = Field(None, description="DNI del último médico que actualizó")


class PatientSummary(BaseModel):
    """Esquema resumido de paciente para listados"""
    name: str = Field(..., description="Nombre completo del paciente")
    dni: str = Field(..., description="DNI del paciente")
    age: int = Field(..., description="Edad del paciente")
    sex: Gender = Field(..., description="Género del paciente")
    blood_type: BloodType = Field(..., description="Tipo de sangre del paciente")
    last_visit: Optional[datetime] = Field(None, description="Fecha de última visita")


class PatientAdmitted(BaseModel):
    """Esquema para pacientes admitidos"""
    name: str = Field(..., description="Nombre del paciente")
    dni: str = Field(..., description="DNI del paciente")
    visit_id: str = Field(..., description="ID de la visita")
    reason: str = Field(..., description="Razón de la atención")
    attention_place: AttentionType = Field(..., description="Tipo de atención")
    attention_details: Optional[str] = Field(None, description="Detalles de la atención")
    triage: Triage = Field(..., description="Triage del paciente")
    doctor_dni: str = Field(..., description="DNI del médico")
    doctor_name: str = Field(..., description="Nombre del médico")
    admission_date: datetime = Field(..., description="Fecha de admisión")


# Esquemas para búsquedas y filtros
class PatientSearchFilters(BaseModel):
    """Filtros para búsqueda de pacientes"""
    name: Optional[str] = Field(None, description="Nombre a buscar")
    dni: Optional[str] = Field(None, description="DNI a buscar")
    blood_type: Optional[BloodType] = Field(None, description="Tipo de sangre")
    age_min: Optional[int] = Field(None, ge=0, description="Edad mínima")
    age_max: Optional[int] = Field(None, le=150, description="Edad máxima")
    has_allergies: Optional[bool] = Field(None, description="Filtrar por presencia de alergias")
    enabled_only: bool = Field(True, description="Solo pacientes habilitados")