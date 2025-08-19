from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from uuid import uuid4
from datetime import datetime
from schemas.enums import ExamResultStatus


class QuestionDB(BaseModel):
    question_id: str = Field(default_factory=lambda: str(uuid4()), description="ID único de la pregunta")
    question: str = Field(..., description="Pregunta")
    options: List[str] = Field(..., description="Opciones de la pregunta")
    correct_option: str = Field(..., description="Opción correcta de la pregunta")  

class CategoryDB(BaseModel):
    category_id: str = Field(default_factory=lambda: str(uuid4()), description="ID único de la categoría")
    name: str = Field(..., description="Nombre de la categoría")
    description: str = Field(..., description="Descripción de la categoría")
    questions: List[QuestionDB] = Field(..., description="Preguntas de la categoría")

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

class ExamDB(BaseModel):
    exam_id: str = Field(default_factory=lambda: str(uuid4()), description="ID único del examen")
    name: str = Field(..., description="Nombre del examen")
    max_error_allowed: int = Field(..., description="Máximo de errores permitidos")
    description: str = Field(..., description="Descripción del examen")
    categories: List[CategoryDB] = Field(..., description="Categorías del examen")
    
    # Campos de auditoría
    enabled: bool = Field(True, description="Estado del examen en el sistema")
    disabled_by: Optional[str] = Field(None, description="DNI del usuario que deshabilitó el examen")
    created_at: datetime = Field(default_factory=datetime.now, description="Fecha de creación")
    updated_at: datetime = Field(default_factory=datetime.now, description="Última actualización")
    created_by: Optional[str] = Field(None, description="DNI del usuario que creó el examen")
    updated_by: Optional[str] = Field(None, description="DNI del último usuario que actualizó")

    class Config:   
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
        
    def update_timestamp(self, updated_by: Optional[str] = None):
        """Actualiza el timestamp de modificación"""
        self.updated_at = datetime.now()
        if updated_by:
            self.updated_by = updated_by
    
    def add_category(self, category: CategoryDB):
        """Añade una nueva categoría al examen"""
        self.categories.append(category)
        self.updated_at = datetime.now()
        return self

    def add_question(self, question: QuestionDB, category_id: str):
        """Añade una pregunta a una categoría específica"""
        category = next((c for c in self.categories if c.category_id == category_id), None)
        if category:
            category.questions.append(question)
            self.updated_at = datetime.now()
            return self
        return None
    
    def get_all_questions(self) -> List[QuestionDB]:
        """Obtiene todas las preguntas de todas las categorías"""
        all_questions = []
        for category in self.categories:
            all_questions.extend(category.questions)
        return all_questions


class QuestionAnswerDB(BaseModel):
    """Modelo para las respuestas de una pregunta específica"""
    question_id: str = Field(..., description="ID de la pregunta")
    selected_option: str = Field(..., description="Opción seleccionada por el paciente")
    correct_option: str = Field(..., description="Opción correcta")
    is_correct: bool = Field(..., description="Si la respuesta es correcta")
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }


class ExamResultDB(BaseModel):
    """Modelo para almacenar los resultados de un examen realizado por un paciente"""
    result_id: str = Field(default_factory=lambda: str(uuid4()), description="ID único del resultado")
    exam_id: str = Field(..., description="ID del examen realizado")
    exam_name: str = Field(..., description="Nombre del examen realizado")
    patient_dni: str = Field(..., description="DNI del paciente que realizó el examen")
    patient_name: str = Field(..., description="Nombre del paciente")
    
    # Respuestas del examen
    answers: List[QuestionAnswerDB] = Field(..., description="Respuestas del paciente")
    
    # Resultados calculados
    total_questions: int = Field(..., description="Total de preguntas del examen")
    correct_answers: int = Field(..., description="Número de respuestas correctas")
    incorrect_answers: int = Field(..., description="Número de respuestas incorrectas")
    score_percentage: float = Field(..., description="Porcentaje de aciertos")
    
    # Resultado final
    status: ExamResultStatus = Field(..., description="Estado del resultado del examen")
    is_approved: bool = Field(..., description="Si aprobó o no el examen")
    
    # Información del examinador
    examiner_dni: str = Field(..., description="DNI del médico/policía que administró el examen")
    examiner_name: str = Field(..., description="Nombre del examinador")
    examiner_role: str = Field(..., description="Rol del examinador (doctor/police)")
    
    # Notas adicionales
    notes: Optional[str] = Field(None, description="Notas adicionales del examinador")
    observations: Optional[str] = Field(None, description="Observaciones del examen")
    
    # Campos de auditoría
    exam_date: datetime = Field(default_factory=datetime.now, description="Fecha de realización del examen")
    created_at: datetime = Field(default_factory=datetime.now, description="Fecha de creación del registro")
    updated_at: datetime = Field(default_factory=datetime.now, description="Última actualización")
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
    
    def calculate_results(self, max_errors_allowed: int):
        """Calcula los resultados del examen"""
        self.correct_answers = sum(1 for answer in self.answers if answer.is_correct)
        self.incorrect_answers = len(self.answers) - self.correct_answers
        self.total_questions = len(self.answers)
        
        if self.total_questions > 0:
            self.score_percentage = (self.correct_answers / self.total_questions) * 100
        else:
            self.score_percentage = 0
        
        # Determinar si aprobó basado en errores máximos permitidos
        self.is_approved = self.incorrect_answers <= max_errors_allowed
        self.status = ExamResultStatus.PASSED if self.is_approved else ExamResultStatus.FAILED
    
    def update_timestamp(self):
        """Actualiza el timestamp de modificación"""
        self.updated_at = datetime.now()


def rebuild_exam_models():
    ExamDB.model_rebuild()
    CategoryDB.model_rebuild()
    QuestionDB.model_rebuild()
    ExamResultDB.model_rebuild()
    QuestionAnswerDB.model_rebuild()