from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from schemas.enums import ExamResultStatus

# Esquemas para creación de exámenes
class QuestionCreate(BaseModel):
    question: str
    options: List[str]
    correct_option: str

class CategoryCreate(BaseModel):
    name: str
    description: str
    questions: List[QuestionCreate]

class ExamCreate(BaseModel):
    name: str
    max_error_allowed: int
    description: str
    categories: List[CategoryCreate]

# Esquemas para visualización de exámenes
class QuestionResponse(BaseModel):
    question_id: str
    question: str
    options: List[str]
    # No incluimos correct_option en la respuesta para el paciente

class CategoryResponse(BaseModel):
    category_id: str
    name: str
    description: str
    questions: List[QuestionResponse]

class ExamResponse(BaseModel):
    exam_id: str
    name: str
    description: str
    max_error_allowed: int
    categories: List[CategoryResponse]

# Esquemas para resultados de exámenes
class QuestionAnswer(BaseModel):
    """Esquema para las respuestas del paciente"""
    question_id: str = Field(..., description="ID de la pregunta")
    selected_option: str = Field(..., description="Opción seleccionada por el paciente")

class ExamSubmission(BaseModel):
    """Esquema para enviar las respuestas del examen"""
    exam_id: str = Field(..., description="ID del examen realizado")
    patient_dni: str = Field(..., description="DNI del paciente")
    answers: List[QuestionAnswer] = Field(..., description="Respuestas del paciente")
    notes: Optional[str] = Field(None, description="Notas adicionales del examinador")
    observations: Optional[str] = Field(None, description="Observaciones del examen")

class QuestionAnswerResult(BaseModel):
    """Esquema para mostrar el resultado de una pregunta"""
    question_id: str = Field(..., description="ID de la pregunta")
    question: str = Field(..., description="Texto de la pregunta")
    selected_option: str = Field(..., description="Opción seleccionada")
    correct_option: str = Field(..., description="Opción correcta")
    is_correct: bool = Field(..., description="Si la respuesta es correcta")

class ExamResultResponse(BaseModel):
    """Esquema de respuesta para el resultado del examen"""
    result_id: str = Field(..., description="ID único del resultado")
    exam_id: str = Field(..., description="ID del examen")
    exam_name: str = Field(..., description="Nombre del examen")
    patient_dni: str = Field(..., description="DNI del paciente")
    patient_name: str = Field(..., description="Nombre del paciente")
    
    # Resultados
    total_questions: int = Field(..., description="Total de preguntas")
    correct_answers: int = Field(..., description="Respuestas correctas")
    incorrect_answers: int = Field(..., description="Respuestas incorrectas")
    score_percentage: float = Field(..., description="Porcentaje de aciertos")
    
    # Estado
    status: ExamResultStatus = Field(..., description="Estado del resultado")
    is_approved: bool = Field(..., description="Si aprobó el examen")
    
    # Examinador
    examiner_dni: str = Field(..., description="DNI del examinador")
    examiner_name: str = Field(..., description="Nombre del examinador")
    examiner_role: str = Field(..., description="Rol del examinador")
    
    # Notas
    notes: Optional[str] = Field(None, description="Notas del examinador")
    observations: Optional[str] = Field(None, description="Observaciones")
    
    # Fechas
    exam_date: datetime = Field(..., description="Fecha del examen")
    created_at: datetime = Field(..., description="Fecha de creación")

class ExamResultSummary(BaseModel):
    """Esquema resumido para listado de resultados"""
    result_id: str = Field(..., description="ID del resultado")
    exam_name: str = Field(..., description="Nombre del examen")
    patient_name: str = Field(..., description="Nombre del paciente")
    is_approved: bool = Field(..., description="Si aprobó")
    score_percentage: float = Field(..., description="Porcentaje obtenido")
    exam_date: datetime = Field(..., description="Fecha del examen")
    examiner_name: str = Field(..., description="Nombre del examinador")

class ExamResultDetailResponse(ExamResultResponse):
    """Esquema detallado que incluye todas las respuestas"""
    answers: List[QuestionAnswerResult] = Field(..., description="Detalle de todas las respuestas")

class PatientExamHistoryResponse(BaseModel):
    """Esquema para el historial de exámenes de un paciente"""
    patient_dni: str = Field(..., description="DNI del paciente")
    patient_name: str = Field(..., description="Nombre del paciente")
    exam_results: List[ExamResultResponse] = Field(..., description="Lista de resultados de exámenes")
    total_exams: int = Field(..., description="Total de exámenes realizados")
    passed_exams: int = Field(..., description="Exámenes aprobados")
    failed_exams: int = Field(..., description="Exámenes reprobados")

class PatientExamSummary(BaseModel):
    """Esquema resumido de paciente con información de exámenes"""
    patient_dni: str = Field(..., description="DNI del paciente")
    patient_name: str = Field(..., description="Nombre del paciente")
    total_exams: int = Field(..., description="Total de exámenes realizados")
    passed_exams: int = Field(..., description="Exámenes aprobados")
    failed_exams: int = Field(..., description="Exámenes reprobados")
    last_exam_date: Optional[datetime] = Field(None, description="Fecha del último examen")
    last_exam_result: Optional[bool] = Field(None, description="Resultado del último examen")
    has_valid_license: bool = Field(..., description="Si tiene licencia psicotécnica vigente")

class PatientsWithExamsResponse(BaseModel):
    """Esquema para lista de pacientes que han realizado exámenes"""
    total_patients: int = Field(..., description="Total de pacientes que han realizado exámenes")
    patients: List[PatientExamSummary] = Field(..., description="Lista de pacientes con resumen de exámenes")

class ExamStatisticsResponse(BaseModel):
    """Esquema para estadísticas generales de exámenes"""
    total_exams_performed: int = Field(..., description="Total de exámenes realizados")
    total_patients_examined: int = Field(..., description="Total de pacientes examinados")
    total_passed: int = Field(..., description="Total de exámenes aprobados")
    total_failed: int = Field(..., description="Total de exámenes reprobados")
    pass_rate_percentage: float = Field(..., description="Porcentaje de aprobación")
    exams_by_month: List[dict] = Field(..., description="Exámenes agrupados por mes")
    most_recent_exams: List[ExamResultSummary] = Field(..., description="Exámenes más recientes")