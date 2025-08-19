from services.firestore import FirestoreService
from models.exam import ExamDB, CategoryDB, QuestionDB, ExamResultDB, QuestionAnswerDB
from schemas.exam import (
    ExamCreate, CategoryCreate, QuestionCreate, ExamSubmission, 
    ExamResultResponse, ExamResultDetailResponse, PatientExamHistoryResponse,
    QuestionResponse, CategoryResponse, ExamResponse, QuestionAnswerResult
)
from schemas.enums import ExamResultStatus
from typing import Optional, List
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExamRepository(FirestoreService):
    """Repositorio para operaciones de base de datos de exámenes"""
    
    def __init__(self):
        super().__init__()
        self.exams_collection = "exams"
    
    def _document_to_exam_db(self, doc) -> Optional[ExamDB]:
        """Convierte un documento de Firestore a ExamDB"""
        try:
            if not doc.exists:
                return None
            
            data = doc.to_dict()
            # Convertir timestamps de string a datetime si es necesario
            for field in ['created_at', 'updated_at']:
                if field in data and isinstance(data[field], str):
                    try:
                        data[field] = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
                    except ValueError:
                        data[field] = datetime.now()
            
            return ExamDB(**data)
        except Exception as e:
            logger.error(f"Error converting document to ExamDB: {e}")
            return None
    
    def get_by_id(self, exam_id: str) -> Optional[ExamDB]:
        """Obtiene un examen por ID"""
        try:
            doc = self.db.collection(self.exams_collection).document(exam_id).get()
            return self._document_to_exam_db(doc)
        except Exception as e:
            logger.error(f"Error getting exam by ID {exam_id}: {e}")
            return None
    
    def create(self, exam_db: ExamDB) -> bool:
        """Crea un nuevo examen"""
        try:
            # Convertir el modelo a diccionario con timestamps como strings ISO
            exam_dict = exam_db.model_dump()
            for field in ['created_at', 'updated_at']:
                if field in exam_dict and isinstance(exam_dict[field], datetime):
                    exam_dict[field] = exam_dict[field].isoformat()
            
            self.db.collection(self.exams_collection).document(exam_db.exam_id).set(exam_dict)
            logger.info(f"Exam {exam_db.exam_id} created successfully")
            return True
        except Exception as e:
            logger.error(f"Error creating exam {exam_db.exam_id}: {e}")
            return False
    
    def update(self, exam_db: ExamDB) -> bool:
        """Actualiza un examen existente"""
        try:
            # Convertir a diccionario con manejo de timestamps
            exam_dict = exam_db.model_dump()
            for field in ['created_at', 'updated_at']:
                if field in exam_dict and isinstance(exam_dict[field], datetime):
                    exam_dict[field] = exam_dict[field].isoformat()
            
            self.db.collection(self.exams_collection).document(exam_db.exam_id).set(exam_dict)
            logger.info(f"Exam {exam_db.exam_id} updated successfully")
            return True
        except Exception as e:
            logger.error(f"Error updating exam {exam_db.exam_id}: {e}")
            return False
    
    def get_all_enabled(self) -> List[ExamDB]:
        """Obtiene todos los exámenes habilitados"""
        try:
            docs = self.db.collection(self.exams_collection).where("enabled", "==", True).get()
            exams = []
            for doc in docs:
                exam = self._document_to_exam_db(doc)
                if exam:
                    exams.append(exam)
            return exams
        except Exception as e:
            logger.error(f"Error getting all enabled exams: {e}")
            return []
    
    def search_by_name(self, name: str) -> List[ExamDB]:
        """Busca exámenes por nombre"""
        try:
            name_lower = name.lower()
            docs = self.db.collection(self.exams_collection)\
                .where("enabled", "==", True)\
                .where("name", ">=", name_lower)\
                .where("name", "<=", name_lower + '\uf8ff')\
                .get()
            
            exams = []
            for doc in docs:
                exam = self._document_to_exam_db(doc)
                if exam:
                    exams.append(exam)
            return exams
        except Exception as e:
            logger.error(f"Error searching exams by name {name}: {e}")
            return []

    def delete(self, exam_id: str) -> bool:
        """Elimina un examen (soft delete estableciendo enabled=False)"""
        try:
            exam_db = self.get_by_id(exam_id)
            if not exam_db:
                return False
            
            exam_db.enabled = False
            exam_db.updated_at = datetime.now()
            
            return self.update(exam_db)
        except Exception as e:
            logger.error(f"Error deleting exam {exam_id}: {e}")
            return False


class ExamService:
    """Servicio principal para gestión de exámenes"""
    
    def __init__(self):
        self.repository = ExamRepository()
    
    def _exam_create_to_exam_db(self, exam_create: ExamCreate, created_by: Optional[str] = None) -> ExamDB:
        """Convierte ExamCreate a ExamDB"""
        # Convertir categorías
        categories = [
            CategoryDB(
                name=cat.name,
                description=cat.description,
                questions=[
                    QuestionDB(
                        question=q.question,
                        options=q.options,
                        correct_option=q.correct_option
                    ) for q in cat.questions
                ]
            ) for cat in exam_create.categories
        ]
        
        return ExamDB(
            name=exam_create.name,
            max_error_allowed=exam_create.max_error_allowed,
            description=exam_create.description,
            categories=categories,
            created_by=created_by
        )
    
    def create_exam(self, exam_create: ExamCreate, created_by: Optional[str] = None) -> Optional[ExamDB]:
        """Crea un nuevo examen"""
        try:
            exam_db = self._exam_create_to_exam_db(exam_create, created_by)
            
            if self.repository.create(exam_db):
                return exam_db
            return None
        except Exception as e:
            logger.error(f"Error in create_exam service: {e}")
            return None
    
    def get_exam(self, exam_id: str) -> Optional[ExamDB]:
        """Obtiene un examen por ID"""
        exam_db = self.repository.get_by_id(exam_id)
        if exam_db and exam_db.enabled:
            return exam_db
        return None
    
    def update_exam(self, exam_id: str, exam_create: ExamCreate, updated_by: Optional[str] = None) -> Optional[ExamDB]:
        """Actualiza un examen existente"""
        # Verificar que el examen existe
        existing_exam = self.repository.get_by_id(exam_id)
        if not existing_exam or not existing_exam.enabled:
            return None
        
        # Crear el examen actualizado manteniendo el ID y campos de auditoría
        updated_exam = self._exam_create_to_exam_db(exam_create, existing_exam.created_by)
        updated_exam.exam_id = exam_id
        updated_exam.created_at = existing_exam.created_at
        updated_exam.updated_at = datetime.now()
        updated_exam.updated_by = updated_by
        
        if self.repository.update(updated_exam):
            return updated_exam
        return None
    
    def delete_exam(self, exam_id: str, deleted_by: Optional[str] = None) -> bool:
        """Elimina un examen (soft delete)"""
        exam_db = self.repository.get_by_id(exam_id)
        if not exam_db:
            return False
        
        exam_db.enabled = False
        exam_db.disabled_by = deleted_by
        exam_db.updated_at = datetime.now()
        exam_db.updated_by = deleted_by
        
        return self.repository.update(exam_db)
    
    def list_exams(self) -> List[ExamDB]:
        """Lista todos los exámenes habilitados"""
        return self.repository.get_all_enabled()
    
    def search_exams(self, name: str) -> List[ExamDB]:
        """Busca exámenes por nombre"""
        return self.repository.search_by_name(name)
    
    def add_category_to_exam(self, exam_id: str, category_create: CategoryCreate, updated_by: Optional[str] = None) -> Optional[ExamDB]:
        """Añade una categoría a un examen existente"""
        exam_db = self.repository.get_by_id(exam_id)
        if not exam_db or not exam_db.enabled:
            return None
        
        # Crear nueva categoría
        new_category = CategoryDB(
            name=category_create.name,
            description=category_create.description,
            questions=[
                QuestionDB(
                    question=q.question,
                    options=q.options,
                    correct_option=q.correct_option
                ) for q in category_create.questions
            ]
        )
        
        exam_db.add_category(new_category)
        exam_db.updated_at = datetime.now()
        exam_db.updated_by = updated_by
        
        if self.repository.update(exam_db):
            return exam_db
        return None
    
    def add_question_to_category(self, exam_id: str, category_id: str, question_create: QuestionCreate, updated_by: Optional[str] = None) -> Optional[ExamDB]:
        """Añade una pregunta a una categoría específica de un examen"""
        exam_db = self.repository.get_by_id(exam_id)
        if not exam_db or not exam_db.enabled:
            return None
        
        # Crear nueva pregunta
        new_question = QuestionDB(
            question=question_create.question,
            options=question_create.options,
            correct_option=question_create.correct_option
        )
        
        exam_db.add_question(new_question, category_id)
        exam_db.updated_at = datetime.now()
        exam_db.updated_by = updated_by
        
        if self.repository.update(exam_db):
            return exam_db
        return None
    
    def get_questions_by_exam(self, exam_id: str) -> Optional[dict]:
        """Obtiene todas las preguntas de un examen para ser respondidas (sin respuestas correctas)"""
        exam_db = self.repository.get_by_id(exam_id)
        if not exam_db or not exam_db.enabled:
            return None
        
        # Convertir a formato de respuesta sin las respuestas correctas
        categories_response = []
        for category in exam_db.categories:
            questions_response = []
            for q in category.questions:
                questions_response.append({
                    "question_id": q.question_id,
                    "question": q.question,
                    "options": q.options
                })
            
            categories_response.append({
                "category_id": category.category_id,
                "name": category.name,
                "description": category.description,
                "questions": questions_response
            })
        
        return {
            "exam_id": exam_db.exam_id,
            "name": exam_db.name,
            "description": exam_db.description,
            "max_error_allowed": exam_db.max_error_allowed,
            "categories": categories_response
        }


# Instancia global del servicio
exam_service = ExamService()
