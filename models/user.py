from __future__ import annotations
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from schemas.enums import UserRole
from uuid import uuid4


class UserDB(BaseModel):
    """Modelo base de usuario para la base de datos"""
    # Identificación del usuario
    user_id: str = Field(default_factory=lambda: str(uuid4()), description="ID único del usuario")
    firebase_uid: str = Field(..., description="UID de Firebase Authentication")
    
    # Información personal básica
    name: str = Field(..., min_length=2, description="Nombre completo del usuario")
    dni: str = Field(..., description="DNI del usuario (único)")
    email: str = Field(..., description="Email del usuario")
    phone: Optional[str] = Field(None, description="Número de teléfono del usuario")
    
    # Rol y permisos
    role: UserRole = Field(..., description="Rol del usuario en el sistema")
    
    # Estado del usuario
    enabled: bool = Field(True, description="Estado del usuario en el sistema")
    is_admin: bool = Field(False, description="Si el usuario tiene permisos de administrador")
    
    # Metadatos del sistema
    created_at: datetime = Field(default_factory=datetime.now, description="Fecha de creación")
    updated_at: datetime = Field(default_factory=datetime.now, description="Última actualización")
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
        
    def update_timestamp(self):
        """Actualiza el timestamp de modificación"""
        self.updated_at = datetime.now()
    
    def disable_user(self):
        """Deshabilita el usuario"""
        self.enabled = False
        self.update_timestamp()
    
    def enable_user(self):
        """Habilita el usuario"""
        self.enabled = True
        self.update_timestamp()


class DoctorDB(BaseModel):
    """Modelo específico de doctor para la base de datos"""
    # Información del usuario base
    user_id: str = Field(..., description="ID del usuario base")
    
    # Información específica del doctor
    medical_license: Optional[str] = Field(None, description="Número de licencia médica")
    specialty: Optional[str] = Field(None, description="Especialidad médica")
    sub_specialty: Optional[str] = Field(None, description="Sub-especialidad médica")
    institution: Optional[str] = Field(None, description="Institución médica donde trabaja")
    
    # Información profesional
    years_experience: Optional[int] = Field(None, ge=0, description="Años de experiencia")
    can_prescribe: bool = Field(True, description="Puede prescribir medicamentos")
    can_diagnose: bool = Field(True, description="Puede realizar diagnósticos")
    can_perform_procedures: bool = Field(True, description="Puede realizar procedimientos médicos")
    
    # Metadatos
    created_at: datetime = Field(default_factory=datetime.now, description="Fecha de creación del perfil médico")
    updated_at: datetime = Field(default_factory=datetime.now, description="Última actualización del perfil médico")
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
        
    def update_timestamp(self):
        """Actualiza el timestamp de modificación"""
        self.updated_at = datetime.now()


class PoliceDB(BaseModel):
    """Modelo específico de policía para la base de datos"""
    # Información del usuario base
    user_id: str = Field(..., description="ID del usuario base")
    
    # Información específica del policía
    badge_number: Optional[str] = Field(None, description="Número de placa policial")
    rank: Optional[str] = Field(None, description="Rango policial")
    department: Optional[str] = Field(None, description="Departamento o unidad policial")
    station: Optional[str] = Field(None, description="Estación o comisaría asignada")
    
    # Información profesional
    years_service: Optional[int] = Field(None, ge=0, description="Años de servicio")
    can_arrest: bool = Field(True, description="Puede realizar arrestos")
    can_investigate: bool = Field(True, description="Puede realizar investigaciones")
    can_access_medical_info: bool = Field(False, description="Puede acceder a información médica limitada")
    
    # Metadatos
    created_at: datetime = Field(default_factory=datetime.now, description="Fecha de creación del perfil policial")
    updated_at: datetime = Field(default_factory=datetime.now, description="Última actualización del perfil policial")
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
        
    def update_timestamp(self):
        """Actualiza el timestamp de modificación"""
        self.updated_at = datetime.now()


# Función para reconstruir modelos si es necesario
def rebuild_user_models():
    """Reconstruye los modelos de usuario para resolver cualquier referencia forward"""
    try:
        UserDB.model_rebuild()
        DoctorDB.model_rebuild()
        PoliceDB.model_rebuild()
    except Exception:
        # Si falla, no es crítico
        pass
