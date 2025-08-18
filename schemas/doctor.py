from pydantic import BaseModel, Field
from typing import Optional
from schemas.user import Doctor as DoctorNew, DoctorCreate as DoctorCreateNew, DoctorLegacy

# Mantener compatibilidad hacia atrás
# Estos esquemas redirigen a los nuevos esquemas de user.py

class Doctor(DoctorLegacy):
    """Esquema de doctor para compatibilidad hacia atrás"""
    pass

class DoctorCreate(BaseModel):
    """Esquema para crear un nuevo doctor (compatible hacia atrás)"""
    name: str = Field(..., description="Nombre del doctor")
    dni: str = Field(..., description="DNI del doctor")
    email: str = Field(..., description="Email del doctor")
    specialty: Optional[str] = Field(None, description="Especialidad del doctor")
    medical_license: Optional[str] = Field(None, description="Número de licencia médica")
    institution: Optional[str] = Field(None, description="Institución médica")
    years_experience: Optional[int] = Field(None, ge=0, description="Años de experiencia")