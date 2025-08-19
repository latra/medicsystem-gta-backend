from pydantic import BaseModel, Field
from schemas import AttentionType, PatientStatus, Triage, VisitStatus
from schemas.patient import BloodAnalysisResponse, RadiologyStudyResponse
from datetime import datetime
from typing import Optional, List


# Esquemas para transferencia de datos (DTOs)

class VitalSignsBase(BaseModel):
    """Esquema base para signos vitales"""
    heart_rate: Optional[int] = Field(None, ge=30, le=300, description="Frecuencia cardíaca (bpm)")
    systolic_pressure: Optional[str] = Field(None, description="Presión sistólica (mmHg)")
    diastolic_pressure: Optional[str] = Field(None, description="Presión diastólica (mmHg)")
    temperature: Optional[str] = Field(None, description="Temperatura corporal (°C)")
    oxygen_saturation: Optional[str] = Field(None, description="Saturación de oxígeno (%)")
    respiratory_rate: Optional[str] = Field(None, description="Frecuencia respiratoria (rpm)")
    weight: Optional[str] = Field(None, description="Peso (kg)")
    height: Optional[str] = Field(None, description="Altura (cm)")
    notes: Optional[str] = Field(None, description="Observaciones sobre los signos vitales")


class VitalSignsResponse(VitalSignsBase):
    """Esquema de respuesta para signos vitales"""
    measurement_id: str = Field(..., description="ID único de la medición")
    measured_at: datetime = Field(..., description="Fecha y hora de la medición")
    measured_by: Optional[str] = Field(None, description="DNI del profesional que tomó la medición")


class DiagnosisCreate(BaseModel):
    """Esquema para crear un diagnóstico"""
    primary_diagnosis: str = Field(..., description="Diagnóstico principal")
    secondary_diagnoses: List[str] = Field(default_factory=list, description="Diagnósticos secundarios")
    icd10_code: Optional[str] = Field(None, description="Código CIE-10")
    severity: Optional[str] = Field(None, description="Severidad del diagnóstico")
    confirmed: bool = Field(False, description="Si el diagnóstico está confirmado")
    differential_diagnoses: List[str] = Field(default_factory=list, description="Diagnósticos diferenciales")


class DiagnosisResponse(DiagnosisCreate):
    """Esquema de respuesta para diagnósticos"""
    diagnosis_id: str = Field(..., description="ID único del diagnóstico")
    diagnosed_at: datetime = Field(..., description="Fecha y hora del diagnóstico")
    diagnosed_by: Optional[str] = Field(None, description="DNI del médico que realizó el diagnóstico")


class PrescriptionCreate(BaseModel):
    """Esquema para crear una prescripción"""
    medication_name: str = Field(..., description="Nombre del medicamento")
    dosage: str = Field(..., description="Dosis prescrita")
    frequency: str = Field(..., description="Frecuencia de administración")
    duration: str = Field(..., description="Duración del tratamiento")
    route: str = Field(..., description="Vía de administración")
    instructions: Optional[str] = Field(None, description="Instrucciones especiales")


class PrescriptionResponse(PrescriptionCreate):
    """Esquema de respuesta para prescripciones"""
    prescription_id: str = Field(..., description="ID único de la prescripción")
    prescribed_at: datetime = Field(..., description="Fecha y hora de prescripción")
    prescribed_by: Optional[str] = Field(None, description="DNI del médico que prescribió")


class MedicalProcedureCreate(BaseModel):
    """Esquema para crear un procedimiento médico"""
    procedure_type: str = Field(..., description="Tipo de procedimiento realizado")
    description: str = Field(..., description="Descripción detallada del procedimiento")
    duration_minutes: Optional[int] = Field(None, ge=0, description="Duración en minutos")
    complications: Optional[str] = Field(None, description="Complicaciones durante el procedimiento")
    outcome: Optional[str] = Field(None, description="Resultado del procedimiento")
    assistants: List[str] = Field(default_factory=list, description="DNIs de profesionales asistentes")


class MedicalProcedureResponse(MedicalProcedureCreate):
    """Esquema de respuesta para procedimientos médicos"""
    procedure_id: str = Field(..., description="ID único del procedimiento")
    performed_at: datetime = Field(..., description="Fecha y hora del procedimiento")
    performed_by: Optional[str] = Field(None, description="DNI del profesional que realizó el procedimiento")


class MedicalEvolutionCreate(BaseModel):
    """Esquema para crear una evolución médica"""
    clinical_status: PatientStatus = Field(..., description="Estado clínico del paciente")
    symptoms: List[str] = Field(default_factory=list, description="Síntomas reportados")
    physical_examination: str = Field("", description="Hallazgos del examen físico")
    clinical_impression: str = Field("", description="Impresión clínica")
    plan: str = Field("", description="Plan de tratamiento")


class MedicalEvolutionResponse(MedicalEvolutionCreate):
    """Esquema de respuesta para evoluciones médicas"""
    evolution_id: str = Field(..., description="ID único de la evolución")
    recorded_at: datetime = Field(..., description="Fecha y hora del registro")
    recorded_by: Optional[str] = Field(None, description="DNI del profesional que registró la evolución")


class VisitBase(BaseModel):
    """Esquema base para datos básicos de visita"""
    patient_dni: str = Field(..., description="DNI del paciente")
    reason: str = Field(..., min_length=3, description="Motivo de la consulta")
    attention_place: AttentionType = Field(..., description="Lugar de atención")
    attention_details: Optional[str] = Field(None, description="Detalles del lugar de atención")
    location: str = Field(..., description="Ubicación específica")
    triage: Optional[Triage] = Field(None, description="Clasificación de triage")


class VisitCreate(VisitBase):
    """Esquema para crear una nueva visita"""
    priority_level: int = Field(default=3, ge=1, le=5, description="Nivel de prioridad (1=máxima, 5=mínima)")
    
    # Signos vitales de admisión (campos compatibles con API actual)
    admission_heart_rate: Optional[int] = Field(None, ge=30, le=300, description="Frecuencia cardíaca de admisión")
    admission_blood_pressure: Optional[str] = Field(None, description="Presión arterial de admisión")
    admission_temperature: Optional[float] = Field(None, ge=30.0, le=45.0, description="Temperatura de admisión")
    admission_oxygen_saturation: Optional[int] = Field(None, ge=70, le=100, description="Saturación de oxígeno de admisión")
    admission_status: Optional[PatientStatus] = Field(None, description="Estado del paciente en admisión")


class VisitUpdate(BaseModel):
    """Esquema para actualizar una visita"""
    reason: Optional[str] = Field(None, min_length=3, description="Motivo de la consulta")
    attention_details: Optional[str] = Field(None, description="Detalles del lugar de atención")
    triage: Optional[Triage] = Field(None, description="Clasificación de triage")
    priority_level: Optional[int] = Field(None, ge=1, le=5, description="Nivel de prioridad")
    
    # Campos compatibles con API actual
    admission_heart_rate: Optional[int] = Field(None, ge=30, le=300, description="Frecuencia cardíaca")
    admission_blood_pressure: Optional[str] = Field(None, description="Presión arterial")
    admission_temperature: Optional[float] = Field(None, ge=30.0, le=45.0, description="Temperatura")
    admission_oxygen_saturation: Optional[int] = Field(None, ge=70, le=100, description="Saturación de oxígeno")
    
    # Información médica básica (compatibilidad con API actual)
    diagnosis: Optional[str] = Field(None, description="Diagnóstico principal")
    tests: Optional[str] = Field(None, description="Pruebas realizadas")
    treatment: Optional[str] = Field(None, description="Tratamiento aplicado")
    evolution: Optional[str] = Field(None, description="Evolución del paciente")
    recommendations: Optional[str] = Field(None, description="Recomendaciones")
    medication: Optional[str] = Field(None, description="Medicación prescrita")
    specialist_follow_up: Optional[str] = Field(None, description="Seguimiento por especialista")
    additional_observations: Optional[str] = Field(None, description="Observaciones adicionales")
    notes: Optional[str] = Field(None, description="Notas generales")


class DischargeRequest(BaseModel):
    """Esquema para dar de alta a un paciente"""
    discharge_summary: str = Field(..., description="Resumen de alta")
    discharge_instructions: str = Field(..., description="Instrucciones de alta")
    follow_up_required: bool = Field(False, description="Si requiere seguimiento")
    follow_up_date: Optional[datetime] = Field(None, description="Fecha de seguimiento")
    follow_up_specialty: Optional[str] = Field(None, description="Especialidad para seguimiento")


class Visit(VisitBase):
    """Esquema de respuesta básica de visita (compatible con API actual)"""
    visit_id: str = Field(..., description="ID único de la visita")
    visit_status: VisitStatus = Field(..., description="Estado de la visita")
    admission_date: datetime = Field(..., description="Fecha de admisión")
    discharge_date: Optional[datetime] = Field(None, description="Fecha de alta")
    
    # Información del médico (compatibilidad con API actual)
    doctor_dni: str = Field(..., description="DNI del médico tratante")
    doctor_name: str = Field(..., description="Nombre del médico")
    doctor_email: Optional[str] = Field(None, description="Email del médico")
    doctor_specialty: Optional[str] = Field(None, description="Especialidad del médico")
    
    # Información médica básica (compatibilidad)
    diagnosis: Optional[str] = Field(None, description="Diagnóstico principal")
    tests: Optional[str] = Field(None, description="Pruebas realizadas")
    treatment: Optional[str] = Field(None, description="Tratamiento aplicado")
    evolution: Optional[str] = Field(None, description="Evolución del paciente")
    recommendations: Optional[str] = Field(None, description="Recomendaciones")
    medication: Optional[str] = Field(None, description="Medicación prescrita")
    specialist_follow_up: Optional[str] = Field(None, description="Seguimiento por especialista")
    additional_observations: Optional[str] = Field(None, description="Observaciones adicionales")
    notes: Optional[str] = Field(None, description="Notas generales")
    
    # Metadatos
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Última actualización")
    
    # Para compatibilidad con API actual
    date_of_admission: Optional[datetime] = Field(None, description="Fecha de admisión (alias)")
    date_of_discharge: Optional[datetime] = Field(None, description="Fecha de alta (alias)")


class VisitComplete(BaseModel):
    """Esquema de respuesta completa de visita (con todos los datos médicos)"""
    # Información básica
    visit_id: str = Field(..., description="ID único de la visita")
    patient_dni: str = Field(..., description="DNI del paciente")
    reason: str = Field(..., description="Motivo de la consulta")
    attention_place: AttentionType = Field(..., description="Lugar de atención")
    attention_details: Optional[str] = Field(None, description="Detalles del lugar de atención")
    location: str = Field(..., description="Ubicación específica")
    
    # Estado y clasificación
    visit_status: VisitStatus = Field(..., description="Estado de la visita")
    triage: Optional[Triage] = Field(None, description="Clasificación de triage")
    priority_level: int = Field(..., description="Nivel de prioridad")
    
    # Profesionales
    attending_doctor_dni: str = Field(..., description="DNI del médico tratante")
    referring_doctor_dni: Optional[str] = Field(None, description="DNI del médico que refiere")
    
    # Datos médicos estructurados
    admission_vital_signs: Optional[VitalSignsResponse] = Field(None, description="Signos vitales de admisión")
    current_vital_signs: Optional[VitalSignsResponse] = Field(None, description="Signos vitales actuales")
    diagnoses: List[DiagnosisResponse] = Field(default_factory=list, description="Diagnósticos")
    procedures: List[MedicalProcedureResponse] = Field(default_factory=list, description="Procedimientos")
    evolutions: List[MedicalEvolutionResponse] = Field(default_factory=list, description="Evoluciones médicas")
    prescriptions: List[PrescriptionResponse] = Field(default_factory=list, description="Prescripciones")
    
    # Órdenes y referencias
    laboratory_orders: List[str] = Field(default_factory=list, description="Órdenes de laboratorio")
    imaging_orders: List[str] = Field(default_factory=list, description="Órdenes de imagenología")
    referrals: List[str] = Field(default_factory=list, description="Referencias a especialistas")
    
    # Análisis de sangre y estudios radiológicos relacionados con esta visita
    blood_analyses: List[BloodAnalysisResponse] = Field(default_factory=list, description="Análisis de sangre realizados durante esta visita")
    radiology_studies: List[RadiologyStudyResponse] = Field(default_factory=list, description="Estudios radiológicos realizados durante esta visita")
    
    # Información de alta
    discharge_summary: Optional[str] = Field(None, description="Resumen de alta")
    discharge_instructions: Optional[str] = Field(None, description="Instrucciones de alta")
    follow_up_required: bool = Field(False, description="Si requiere seguimiento")
    follow_up_date: Optional[datetime] = Field(None, description="Fecha de seguimiento")
    follow_up_specialty: Optional[str] = Field(None, description="Especialidad para seguimiento")
    
    # Observaciones
    nursing_notes: List[str] = Field(default_factory=list, description="Notas de enfermería")
    additional_observations: Optional[str] = Field(None, description="Observaciones adicionales")
    complications: List[str] = Field(default_factory=list, description="Complicaciones")
    
    # Metadatos
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Última actualización")
    admission_date: datetime = Field(..., description="Fecha de admisión")
    discharge_date: Optional[datetime] = Field(None, description="Fecha de alta")
    created_by: Optional[str] = Field(None, description="DNI del profesional que creó la visita")
    last_updated_by: Optional[str] = Field(None, description="DNI del último profesional que actualizó")
    is_completed: bool = Field(False, description="Si la visita está completa")
    length_of_stay_hours: Optional[int] = Field(None, description="Duración de la estancia en horas")


class VisitSummary(BaseModel):
    """Esquema resumido de visita para listados"""
    visit_id: str = Field(..., description="ID único de la visita")
    patient_dni: str = Field(..., description="DNI del paciente")
    visit_status: VisitStatus = Field(..., description="Estado de la visita")
    reason: str = Field(..., description="Motivo de la consulta")
    attention_place: AttentionType = Field(..., description="Lugar de atención")
    attention_details: Optional[str] = Field(None, description="Detalles del lugar de atención")
    location: str = Field(..., description="Ubicación específica")
    triage: Optional[Triage] = Field(None, description="Clasificación de triage")
    
    # Información del médico (compatibilidad)
    doctor_dni: str = Field(..., description="DNI del médico")
    doctor_name: str = Field(..., description="Nombre del médico")
    doctor_email: Optional[str] = Field(None, description="Email del médico")
    doctor_specialty: Optional[str] = Field(None, description="Especialidad del médico")
    
    # Fechas
    admission_date: datetime = Field(..., description="Fecha de admisión")
    discharge_date: Optional[datetime] = Field(None, description="Fecha de alta")
    
    # Para compatibilidad con API actual
    date_of_admission: datetime = Field(..., description="Fecha de admisión (alias)")
    date_of_discharge: Optional[datetime] = Field(None, description="Fecha de alta (alias)")


# Esquemas para búsquedas y filtros
class VisitSearchFilters(BaseModel):
    """Filtros para búsqueda de visitas"""
    patient_dni: Optional[str] = Field(None, description="DNI del paciente")
    doctor_dni: Optional[str] = Field(None, description="DNI del médico")
    visit_status: Optional[VisitStatus] = Field(None, description="Estado de la visita")
    attention_place: Optional[AttentionType] = Field(None, description="Lugar de atención")
    triage: Optional[Triage] = Field(None, description="Clasificación de triage")
    admission_date_from: Optional[datetime] = Field(None, description="Fecha de admisión desde")
    admission_date_to: Optional[datetime] = Field(None, description="Fecha de admisión hasta")
    discharge_date_from: Optional[datetime] = Field(None, description="Fecha de alta desde")
    discharge_date_to: Optional[datetime] = Field(None, description="Fecha de alta hasta")
    priority_level: Optional[int] = Field(None, ge=1, le=5, description="Nivel de prioridad")
    is_completed: Optional[bool] = Field(None, description="Si la visita está completa")