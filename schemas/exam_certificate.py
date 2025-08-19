from pydantic import BaseModel, Field
from datetime import datetime

class ExamCertificateResponse(BaseModel):
    """Esquema para certificado de examen"""
    citizen_dni: str = Field(..., description="DNI del ciudadano")
    citizen_name: str = Field(..., description="Nombre del ciudadano")
    exam_pass: bool = Field(..., description="Si aprobó el examen")
    exam_date: datetime = Field(..., description="Fecha del examen")
    doctor_dni: str = Field(..., description="DNI del doctor examinador")
    doctor_name: str = Field(..., description="Nombre del doctor examinador")
