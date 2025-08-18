from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from schemas.enums import UserRole


# Esquemas base para usuarios

class UserBase(BaseModel):
    """Esquema base para datos básicos de usuario"""
    name: str = Field(..., min_length=2, description="Nombre completo del usuario")
    dni: str = Field(..., description="DNI del usuario")
    email: str = Field(..., description="Email del usuario")
    phone: Optional[str] = Field(None, description="Número de teléfono del usuario")


class UserCreate(UserBase):
    """Esquema para crear un nuevo usuario base"""
    role: UserRole = Field(..., description="Rol del usuario en el sistema")


class UserUpdate(BaseModel):
    """Esquema para actualizar datos básicos de usuario"""
    name: Optional[str] = Field(None, min_length=2, description="Nombre completo del usuario")
    phone: Optional[str] = Field(None, description="Número de teléfono del usuario")


class User(UserBase):
    """Esquema de respuesta básica de usuario"""
    user_id: str = Field(..., description="ID único del usuario")
    firebase_uid: str = Field(..., description="UID de Firebase Authentication")
    role: UserRole = Field(..., description="Rol del usuario")
    enabled: bool = Field(..., description="Estado del usuario")
    is_admin: bool = Field(..., description="Si tiene permisos de administrador")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Última actualización")


# Esquemas específicos para doctores

class DoctorProfile(BaseModel):
    """Esquema para perfil específico de doctor"""
    medical_license: Optional[str] = Field(None, description="Número de licencia médica")
    specialty: Optional[str] = Field(None, description="Especialidad médica")
    sub_specialty: Optional[str] = Field(None, description="Sub-especialidad médica")
    institution: Optional[str] = Field(None, description="Institución médica donde trabaja")
    years_experience: Optional[int] = Field(None, ge=0, description="Años de experiencia")
    can_prescribe: bool = Field(True, description="Puede prescribir medicamentos")
    can_diagnose: bool = Field(True, description="Puede realizar diagnósticos")
    can_perform_procedures: bool = Field(True, description="Puede realizar procedimientos médicos")


class DoctorCreate(UserCreate):
    """Esquema para crear un nuevo doctor"""
    role: UserRole = Field(UserRole.DOCTOR, description="Rol del usuario (siempre DOCTOR)")
    doctor_profile: DoctorProfile = Field(..., description="Perfil específico del doctor")


class DoctorRegister(BaseModel):
    """Esquema simplificado para registro público de doctor"""
    name: str = Field(..., min_length=2, description="Nombre completo del doctor")
    dni: str = Field(..., description="DNI del doctor")
    email: str = Field(..., description="Email del doctor")
    phone: Optional[str] = Field(None, description="Número de teléfono del doctor")
    specialty: Optional[str] = Field(None, description="Especialidad médica")
    medical_license: Optional[str] = Field(None, description="Número de licencia médica")
    institution: Optional[str] = Field(None, description="Institución médica donde trabaja")
    years_experience: Optional[int] = Field(None, ge=0, description="Años de experiencia")


class DoctorUpdate(UserUpdate):
    """Esquema para actualizar datos de doctor"""
    doctor_profile: Optional[DoctorProfile] = Field(None, description="Perfil específico del doctor")


class Doctor(User):
    """Esquema de respuesta completa de doctor (compatible con API anterior)"""
    # Campos específicos del doctor para compatibilidad
    specialty: Optional[str] = Field(None, description="Especialidad médica")
    medical_license: Optional[str] = Field(None, description="Número de licencia médica")
    institution: Optional[str] = Field(None, description="Institución médica")
    years_experience: Optional[int] = Field(None, description="Años de experiencia")


# Esquemas específicos para policías

class PoliceProfile(BaseModel):
    """Esquema para perfil específico de policía"""
    badge_number: Optional[str] = Field(None, description="Número de placa policial")
    rank: Optional[str] = Field(None, description="Rango policial")
    department: Optional[str] = Field(None, description="Departamento o unidad policial")
    station: Optional[str] = Field(None, description="Estación o comisaría asignada")
    years_service: Optional[int] = Field(None, ge=0, description="Años de servicio")
    can_arrest: bool = Field(True, description="Puede realizar arrestos")
    can_investigate: bool = Field(True, description="Puede realizar investigaciones")
    can_access_medical_info: bool = Field(False, description="Puede acceder a información médica limitada")


class PoliceCreate(UserCreate):
    """Esquema para crear un nuevo policía"""
    role: UserRole = Field(UserRole.POLICE, description="Rol del usuario (siempre POLICE)")
    police_profile: PoliceProfile = Field(..., description="Perfil específico del policía")


class PoliceRegister(BaseModel):
    """Esquema simplificado para registro público de policía"""
    name: str = Field(..., min_length=2, description="Nombre completo del policía")
    dni: str = Field(..., description="DNI del policía")
    email: str = Field(..., description="Email del policía")
    phone: Optional[str] = Field(None, description="Número de teléfono del policía")
    badge_number: str = Field(..., description="Número de placa policial")
    rank: Optional[str] = Field(None, description="Rango policial")
    department: Optional[str] = Field(None, description="Departamento de policía")
    station: Optional[str] = Field(None, description="Estación policial")
    years_service: Optional[int] = Field(None, ge=0, description="Años de servicio")


class PoliceUpdate(UserUpdate):
    """Esquema para actualizar datos de policía"""
    police_profile: Optional[PoliceProfile] = Field(None, description="Perfil específico del policía")


class Police(User):
    """Esquema de respuesta completa de policía"""
    # Campos específicos del policía
    badge_number: Optional[str] = Field(None, description="Número de placa policial")
    rank: Optional[str] = Field(None, description="Rango policial")
    department: Optional[str] = Field(None, description="Departamento policial")
    station: Optional[str] = Field(None, description="Estación asignada")
    years_service: Optional[int] = Field(None, description="Años de servicio")


# Esquemas para filtros y búsquedas

class UserSearchFilters(BaseModel):
    """Filtros para búsqueda de usuarios"""
    name: Optional[str] = Field(None, description="Nombre a buscar")
    dni: Optional[str] = Field(None, description="DNI a buscar")
    email: Optional[str] = Field(None, description="Email a buscar")
    role: Optional[UserRole] = Field(None, description="Rol del usuario")
    enabled_only: bool = Field(True, description="Solo usuarios habilitados")


# Esquemas de respuesta para listados

class UserSummary(BaseModel):
    """Esquema resumido de usuario para listados"""
    user_id: str = Field(..., description="ID único del usuario")
    name: str = Field(..., description="Nombre completo")
    dni: str = Field(..., description="DNI del usuario")
    email: str = Field(..., description="Email del usuario")
    role: UserRole = Field(..., description="Rol del usuario")
    enabled: bool = Field(..., description="Estado del usuario")
    created_at: datetime = Field(..., description="Fecha de creación")


class DoctorSummary(UserSummary):
    """Esquema resumido de doctor para listados"""
    specialty: Optional[str] = Field(None, description="Especialidad médica")
    institution: Optional[str] = Field(None, description="Institución médica")


class PoliceSummary(UserSummary):
    """Esquema resumido de policía para listados"""
    badge_number: Optional[str] = Field(None, description="Número de placa")
    rank: Optional[str] = Field(None, description="Rango policial")
    department: Optional[str] = Field(None, description="Departamento")


# Esquema para compatibilidad con la API anterior
# Mantiene la estructura exacta del Doctor original

class DoctorLegacy(BaseModel):
    """Esquema de doctor para compatibilidad con API anterior"""
    name: str = Field(..., description="Nombre del doctor")
    dni: str = Field(..., description="DNI del doctor")
    email: str = Field(..., description="Email del doctor")
    specialty: Optional[str] = Field(None, description="Especialidad del doctor")
    enabled: bool = Field(..., description="Estado del doctor")
    is_admin: Optional[bool] = Field(None, description="Si es administrador")
    firebase_uid: Optional[str] = Field(None, description="UID de Firebase")
