from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime


class Especialidad(str, Enum):
    """Enum para las especialidades de médicos disponibles"""
    CARDIOLOGIA = "Cardiología"
    NEUROLOGIA = "Neurología"
    GINECOLOGIA = "Ginecología"
    PEDIATRIA = "Pediatría"

class CargoMedico(str, Enum):
    """Enum para los cargos de médicos disponibles"""
    PRACTICANTE = "Practicante"
    TECNICO_ENFERMERO = "Técnico enfermero"
    RECLUTADOR_MEDICO = "Reclutador médico"
    MEDICO_PRINCIPAL = "Médico principal"

class TipoAtencion(str, Enum):
    """Enum para los tipos de atención de consultas"""
    CALLE = "Calle"
    HOSPITAL = "Hospital"
    CALLE_TRASLADADO_HOSPITAL = "Calle con traslado"

class MedicoBase(BaseModel):
    """Modelo base para médicos"""
    dni: str = Field(..., description="DNI del médico")
    email: str = Field(..., description="Email del médico")
    nombre: str = Field(..., description="Nombre del médico")
    apellido: str = Field(..., description="Apellido del médico")
    cargo: CargoMedico = Field(..., description="Cargo del médico")
    especialidades: Optional[list[Especialidad]] = Field(None, description="Especialidad del médico")

class MedicoCreate(MedicoBase):
    """Modelo para crear un nuevo médico"""
    pass

class MedicoUpdate(BaseModel):
    """Modelo para actualizar un médico (campos opcionales)"""
    dni: Optional[str] = Field(None, description="DNI del médico")
    email: Optional[str] = Field(None, description="Email del médico")
    nombre: Optional[str] = Field(None, description="Nombre del médico")
    apellido: Optional[str] = Field(None, description="Apellido del médico")
    cargo: Optional[CargoMedico] = Field(None, description="Cargo del médico")
    especialidades: Optional[list[Especialidad]] = Field(None, description="Especialidad del médico")

class Medico(MedicoBase):
    """Modelo completo de médico con ID y Firebase UID"""
    id: str = Field(..., description="ID único del médico")
    firebase_uid: Optional[str] = Field(None, description="UID de Firebase Authentication")
    
    class Config:
        from_attributes = True

# Modelos para Pacientes

class PacienteBase(BaseModel):
    """Modelo base para pacientes"""
    nombre: str = Field(..., description="Nombre del paciente")
    apellido: str = Field(..., description="Apellido del paciente")
    dni: str = Field(..., description="DNI del paciente")
    telefono_contacto: Optional[str] = Field(None, description="Teléfono de contacto del paciente")
    tipo_sanguineo: Optional[str] = Field(None, description="Tipo sanguíneo del paciente")
    profesion_conocida: Optional[str] = Field(None, description="Profesión conocida del paciente")

class PacienteCreate(PacienteBase):
    """Modelo para crear un nuevo paciente"""
    pass

class PacienteUpdate(BaseModel):
    """Modelo para actualizar un paciente (campos opcionales)"""
    nombre: Optional[str] = Field(None, description="Nombre del paciente")
    apellido: Optional[str] = Field(None, description="Apellido del paciente")
    dni: Optional[str] = Field(None, description="DNI del paciente")
    telefono_contacto: Optional[str] = Field(None, description="Teléfono de contacto del paciente")
    tipo_sanguineo: Optional[str] = Field(None, description="Tipo sanguíneo del paciente")
    profesion_conocida: Optional[str] = Field(None, description="Profesión conocida del paciente")

class Paciente(PacienteBase):
    """Modelo completo de paciente con ID"""
    id: str = Field(..., description="ID único del paciente")
    
    class Config:
        from_attributes = True

# Modelos para Consultas

class ConsultaBase(BaseModel):
    """Modelo base para consultas médicas"""
    medico_dni: str = Field(..., description="DNI del médico que realizó la consulta")
    paciente_dni: str = Field(..., description="DNI del paciente atendido")
    tipo_atencion: TipoAtencion = Field(..., description="Tipo de atención recibida")
    motivo_consulta: str = Field(..., description="Motivo de la consulta")
    tratamiento_aplicado: str = Field(..., description="Tratamiento aplicado")

class ConsultaCreate(ConsultaBase):
    """Modelo para crear una nueva consulta"""
    pass

class ConsultaUpdate(BaseModel):
    """Modelo para actualizar una consulta (campos opcionales)"""
    medico_dni: Optional[str] = Field(None, description="DNI del médico que realizó la consulta")
    paciente_dni: Optional[str] = Field(None, description="DNI del paciente atendido")
    tipo_atencion: Optional[TipoAtencion] = Field(None, description="Tipo de atención recibida")
    motivo_consulta: Optional[str] = Field(None, description="Motivo de la consulta")
    tratamiento_aplicado: Optional[str] = Field(None, description="Tratamiento aplicado")

class Consulta(ConsultaBase):
    """Modelo completo de consulta con ID y timestamp"""
    id: str = Field(..., description="ID único de la consulta")
    fecha_creacion: datetime = Field(default_factory=datetime.now, description="Fecha y hora de creación de la consulta")
    medico_nombre: Optional[str] = Field(None, description="Nombre del médico que realizó la consulta")
    medico_apellido: Optional[str] = Field(None, description="Apellido del médico que realizó la consulta")

    class Config:
        from_attributes = True 