from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from schemas.enums import BloodType, Gender
from uuid import uuid4


class BloodAnalysis(BaseModel):
    """Modelo para análisis de sangre del paciente"""
    analysis_id: str = Field(default_factory=lambda: str(uuid4()), description="ID único del análisis")
    date_performed: datetime = Field(default_factory=datetime.now, description="Fecha del análisis")
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
    performed_by_dni: Optional[str] = Field(None, description="DNI del médico que realizó el análisis")
    performed_by_name: Optional[str] = Field(None, description="Nombre del médico que realizó el análisis")
    notes: Optional[str] = Field(None, description="Notas adicionales del análisis")


class RadiologyStudy(BaseModel):
    """Modelo para estudios radiológicos del paciente"""
    study_id: str = Field(default_factory=lambda: str(uuid4()), description="ID único del estudio")
    date_performed: datetime = Field(default_factory=datetime.now, description="Fecha del estudio")
    study_type: str = Field(..., description="Tipo de estudio (Rayos X, CT, MRI, etc.)")
    body_part: str = Field(..., description="Parte del cuerpo estudiada")
    findings: str = Field(..., description="Hallazgos del estudio")
    image_url: Optional[str] = Field(None, description="URL de la imagen si está disponible")
    performed_by_dni: Optional[str] = Field(None, description="DNI del médico que realizó el estudio")
    performed_by_name: Optional[str] = Field(None, description="Nombre del médico que realizó el estudio")


class MedicalHistory(BaseModel):
    """Historial médico completo del paciente"""
    allergies: List[str] = Field(default_factory=list, description="Lista de alergias del paciente")
    medical_notes: str = Field("", description="Notas médicas generales")
    major_surgeries: List[str] = Field(default_factory=list, description="Cirugías mayores")
    current_medications: List[str] = Field(default_factory=list, description="Medicamentos actuales")
    chronic_conditions: List[str] = Field(default_factory=list, description="Condiciones crónicas")
    family_history: str = Field("", description="Historial familiar")
    blood_analyses: List[BloodAnalysis] = Field(default_factory=list, description="Análisis de sangre")
    radiology_studies: List[RadiologyStudy] = Field(default_factory=list, description="Estudios radiológicos")
    last_updated: datetime = Field(default_factory=datetime.now, description="Última actualización del historial")
    updated_by: Optional[str] = Field(None, description="DNI del médico que actualizó el historial")


class PatientDB(BaseModel):
    """Modelo completo de paciente para la base de datos"""
    # Información básica
    dni: str = Field(..., description="DNI del paciente (ID único)")
    name: str = Field(..., min_length=2, description="Nombre completo del paciente")
    age: int = Field(..., ge=0, le=150, description="Edad del paciente")
    sex: Gender = Field(..., description="Género del paciente")
    phone: Optional[str] = Field(None, description="Número de teléfono del paciente")
    blood_type: BloodType = Field(..., description="Tipo de sangre del paciente")
    
    medical_history: MedicalHistory = Field(default_factory=MedicalHistory, description="Historial médico completo")
    
    enabled: bool = Field(True, description="Estado del paciente en el sistema")
    disabled_by: Optional[str] = Field(None, description="DNI del médico que deshabilitó al paciente")
    created_at: datetime = Field(default_factory=datetime.now, description="Fecha de creación")
    updated_at: datetime = Field(default_factory=datetime.now, description="Última actualización")
    created_by: Optional[str] = Field(None, description="DNI del médico que creó el registro")
    last_updated_by: Optional[str] = Field(None, description="DNI del último médico que actualizó")
    discapacity_level: Optional[int] = Field(None, description="Nivel de discapacidad del paciente")
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
        
    def update_timestamp(self, updated_by: Optional[str] = None):
        """Actualiza el timestamp de modificación"""
        self.updated_at = datetime.now()
        if updated_by:
            self.last_updated_by = updated_by
            
    def add_blood_analysis(self, analysis: BloodAnalysis):
        """Añade un nuevo análisis de sangre al historial"""
        self.medical_history.blood_analyses.append(analysis)
        self.medical_history.last_updated = datetime.now()
        self.update_timestamp(analysis.performed_by_dni)
        
    def add_radiology_study(self, study: RadiologyStudy):
        """Añade un nuevo estudio radiológico al historial"""
        self.medical_history.radiology_studies.append(study)
        self.medical_history.last_updated = datetime.now()
        self.update_timestamp(study.performed_by_dni)
        
    def get_latest_blood_analysis(self) -> Optional[BloodAnalysis]:
        """Obtiene el análisis de sangre más reciente"""
        if not self.medical_history.blood_analyses:
            return None
        return max(self.medical_history.blood_analyses, key=lambda x: x.date_performed)
        
    def get_latest_radiology_study(self) -> Optional[RadiologyStudy]:
        """Obtiene el estudio radiológico más reciente"""
        if not self.medical_history.radiology_studies:
            return None
        return max(self.medical_history.radiology_studies, key=lambda x: x.date_performed)