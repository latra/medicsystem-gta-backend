from services.firestore import FirestoreService
from services.exam import ExamRepository
from services.patient import PatientService
from models.exam import ExamResultDB, QuestionAnswerDB
from schemas.exam import (
    ExamSubmission, ExamResultResponse, ExamResultDetailResponse, 
    PatientExamHistoryResponse, QuestionAnswerResult, PatientExamSummary,
    PatientsWithExamsResponse, ExamStatisticsResponse, ExamResultSummary
)
from schemas.exam_certificate import ExamCertificateResponse
from schemas.enums import ExamResultStatus
from firebase_admin import firestore
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from collections import defaultdict
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExamResultRepository(FirestoreService):
    """Repositorio para operaciones de base de datos de resultados de exámenes"""
    
    def __init__(self):
        super().__init__()
        self.results_collection = "exam_results"
    
    def _document_to_result_db(self, doc) -> Optional[ExamResultDB]:
        """Convierte un documento de Firestore a ExamResultDB"""
        try:
            if not doc.exists:
                return None
            
            data = doc.to_dict()
            # Convertir timestamps
            for field in ['exam_date', 'created_at', 'updated_at']:
                if field in data and isinstance(data[field], str):
                    try:
                        data[field] = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
                    except ValueError:
                        data[field] = datetime.now()
            
            return ExamResultDB(**data)
        except Exception as e:
            logger.error(f"Error converting document to ExamResultDB: {e}")
            return None
    
    def create(self, result_db: ExamResultDB) -> bool:
        """Crea un nuevo resultado de examen"""
        try:
            # Convertir a diccionario con timestamps como strings
            result_dict = result_db.model_dump()
            for field in ['exam_date', 'created_at', 'updated_at']:
                if field in result_dict and isinstance(result_dict[field], datetime):
                    result_dict[field] = result_dict[field].isoformat()
            
            self.db.collection(self.results_collection).document(result_db.result_id).set(result_dict)
            logger.info(f"Exam result {result_db.result_id} created successfully")
            return True
        except Exception as e:
            logger.error(f"Error creating exam result {result_db.result_id}: {e}")
            return False
    
    def get_by_id(self, result_id: str) -> Optional[ExamResultDB]:
        """Obtiene un resultado por ID"""
        try:
            doc = self.db.collection(self.results_collection).document(result_id).get()
            return self._document_to_result_db(doc)
        except Exception as e:
            logger.error(f"Error getting exam result by ID {result_id}: {e}")
            return None
    
    def get_by_patient_dni(self, patient_dni: str) -> List[ExamResultDB]:
        """Obtiene todos los resultados de un paciente por DNI"""
        try:
            docs = self.db.collection(self.results_collection)\
                .where("patient_dni", "==", patient_dni)\
                .order_by("exam_date", direction="DESCENDING")\
                .get()
            
            results = []
            for doc in docs:
                result = self._document_to_result_db(doc)
                if result:
                    results.append(result)
            return results
        except Exception as e:
            logger.error(f"Error getting exam results for patient {patient_dni}: {e}")
            return []
    
    def get_by_exam_id(self, exam_id: str) -> List[ExamResultDB]:
        """Obtiene todos los resultados de un examen específico"""
        try:
            docs = self.db.collection(self.results_collection)\
                .where("exam_id", "==", exam_id)\
                .order_by("exam_date", direction="DESCENDING")\
                .get()
            
            results = []
            for doc in docs:
                result = self._document_to_result_db(doc)
                if result:
                    results.append(result)
            return results
        except Exception as e:
            logger.error(f"Error getting results for exam {exam_id}: {e}")
            return []
            
    def get_latest_by_exam_and_patient(self, exam_id: str, patient_dni: str) -> Optional[ExamResultDB]:
        """Obtiene el resultado más reciente de un examen específico para un paciente"""
        try:
            docs = self.db.collection(self.results_collection)\
                .where("exam_id", "==", exam_id)\
                .where("patient_dni", "==", patient_dni)\
                .order_by("exam_date", direction="DESCENDING")\
                .limit(1)\
                .get()
            
            for doc in docs:  # Solo debería haber uno por el limit(1)
                return self._document_to_result_db(doc)
            return None
        except Exception as e:
            logger.error(f"Error getting latest result for exam {exam_id} and patient {patient_dni}: {e}")
            return None
    
    def get_patients_with_exams(self) -> List[str]:
        """Obtiene lista de DNIs únicos de pacientes que han realizado exámenes"""
        try:
            docs = self.db.collection(self.results_collection).get()
            patient_dnis = set()
            for doc in docs:
                data = doc.to_dict()
                if 'patient_dni' in data:
                    patient_dnis.add(data['patient_dni'])
            return list(patient_dnis)
        except Exception as e:
            logger.error(f"Error getting patients with exams: {e}")
            return []
    
    def get_all_results(self, limit: Optional[int] = None) -> List[ExamResultDB]:
        """Obtiene todos los resultados"""
        try:
            query = self.db.collection(self.results_collection)\
                .order_by("exam_date", direction="DESCENDING")
            
            if limit:
                query = query.limit(limit)
            
            docs = query.get()
            results = []
            for doc in docs:
                result = self._document_to_result_db(doc)
                if result:
                    results.append(result)
            return results
        except Exception as e:
            logger.error(f"Error getting all exam results: {e}")
            return []


class ExamResultService:
    """Servicio para gestión de resultados de exámenes"""
    
    def __init__(self):
        self.repository = ExamResultRepository()
        self.exam_repository = ExamRepository()
        self.patient_service = PatientService()
    
    def submit_exam_result(self, submission: ExamSubmission, examiner_dni: str, examiner_name: str, examiner_role: str) -> Optional[ExamResultResponse]:
        """Procesa y guarda el resultado de un examen"""
        try:
            # Obtener el examen para validar respuestas
            exam_db = self.exam_repository.get_by_id(submission.exam_id)
            if not exam_db or not exam_db.enabled:
                logger.error(f"Exam {submission.exam_id} not found or disabled")
                return None
            
            # Obtener información del paciente
            patient = self.patient_service.get_patient(submission.patient_dni)
            if not patient:
                logger.error(f"Patient {submission.patient_dni} not found")
                return None
            
            # Obtener todas las preguntas del examen
            all_questions = exam_db.get_all_questions()
            question_dict = {q.question_id: q for q in all_questions}
            
            # Validar y procesar respuestas
            processed_answers = []
            for answer in submission.answers:
                if answer.question_id not in question_dict:
                    logger.error(f"Question {answer.question_id} not found in exam {submission.exam_id}")
                    continue
                
                question = question_dict[answer.question_id]
                is_correct = answer.selected_option == question.correct_option
                
                processed_answer = QuestionAnswerDB(
                    question_id=answer.question_id,
                    selected_option=answer.selected_option,
                    correct_option=question.correct_option,
                    is_correct=is_correct
                )
                processed_answers.append(processed_answer)
            
            # Crear el resultado
            result_db = ExamResultDB(
                exam_id=submission.exam_id,
                exam_name=exam_db.name,
                patient_dni=submission.patient_dni,
                patient_name=patient.name,
                answers=processed_answers,
                total_questions=len(processed_answers),
                correct_answers=0,  # Se calculará
                incorrect_answers=0,  # Se calculará
                score_percentage=0,  # Se calculará
                status=ExamResultStatus.PENDING,  # Se calculará
                is_approved=False,  # Se calculará
                examiner_dni=examiner_dni,
                examiner_name=examiner_name,
                examiner_role=examiner_role,
                notes=submission.notes,
                observations=submission.observations
            )
            
            # Calcular resultados
            result_db.calculate_results(exam_db.max_error_allowed)
            
            # Guardar en la base de datos
            if self.repository.create(result_db):
                return self._result_db_to_response(result_db)
            
            return None
            
        except Exception as e:
            logger.error(f"Error submitting exam result: {e}")
            return None
    
    def get_patient_exam_history(self, patient_dni: str) -> Optional[PatientExamHistoryResponse]:
        """Obtiene el historial de exámenes de un paciente"""
        try:
            # Verificar que el paciente existe
            patient = self.patient_service.get_patient(patient_dni)
            if not patient:
                logger.error(f"Patient {patient_dni} not found")
                return None
            
            results_db = self.repository.get_by_patient_dni(patient_dni)
            
            # Convertir a respuestas
            exam_results = [self._result_db_to_response(result) for result in results_db]
            
            # Calcular estadísticas
            total_exams = len(results_db)
            passed_exams = sum(1 for result in results_db if result.is_approved)
            failed_exams = total_exams - passed_exams
            
            return PatientExamHistoryResponse(
                patient_dni=patient_dni,
                patient_name=patient.name,
                exam_results=exam_results,
                total_exams=total_exams,
                passed_exams=passed_exams,
                failed_exams=failed_exams
            )
            
        except Exception as e:
            logger.error(f"Error getting patient exam history for {patient_dni}: {e}")
            return None
    
    def get_exam_result_detail(self, result_id: str) -> Optional[ExamResultDetailResponse]:
        """Obtiene el detalle completo de un resultado incluyendo todas las respuestas"""
        try:
            result_db = self.repository.get_by_id(result_id)
            if not result_db:
                return None
            
            # Obtener el examen para tener los textos de las preguntas
            exam_db = self.exam_repository.get_by_id(result_db.exam_id)
            if not exam_db:
                return None
            
            # Crear diccionario de preguntas
            all_questions = exam_db.get_all_questions()
            question_dict = {q.question_id: q for q in all_questions}
            
            # Convertir respuestas a formato detallado
            detailed_answers = []
            for answer in result_db.answers:
                if answer.question_id in question_dict:
                    question = question_dict[answer.question_id]
                    detailed_answer = QuestionAnswerResult(
                        question_id=answer.question_id,
                        question=question.question,
                        selected_option=answer.selected_option,
                        correct_option=answer.correct_option,
                        is_correct=answer.is_correct
                    )
                    detailed_answers.append(detailed_answer)
            
            # Crear respuesta base
            base_response = self._result_db_to_response(result_db)
            
            # Crear respuesta detallada
            return ExamResultDetailResponse(
                **base_response.model_dump(),
                answers=detailed_answers
            )
            
        except Exception as e:
            logger.error(f"Error getting detailed exam result {result_id}: {e}")
            return None
    
    def get_exam_result(self, result_id: str) -> Optional[ExamResultResponse]:
        """Obtiene un resultado de examen por ID"""
        try:
            result_db = self.repository.get_by_id(result_id)
            if result_db:
                return self._result_db_to_response(result_db)
            return None
        except Exception as e:
            logger.error(f"Error getting exam result {result_id}: {e}")
            return None
            
    def get_latest_exam_certificate(self, exam_id: str, patient_dni: str) -> Optional[ExamCertificateResponse]:
        """Obtiene el certificado del último examen realizado por un paciente"""
        try:
            # Obtener el último resultado del examen para el paciente
            result_db = self.repository.get_latest_by_exam_and_patient(exam_id, patient_dni)
            if not result_db:
                return None
                
            # Crear el certificado
            return ExamCertificateResponse(
                citizen_dni=result_db.patient_dni,
                citizen_name=result_db.patient_name,
                exam_pass=result_db.is_approved,
                exam_date=result_db.exam_date,
                doctor_dni=result_db.examiner_dni,
                doctor_name=result_db.examiner_name
            )
            
        except Exception as e:
            logger.error(f"Error getting exam certificate for exam {exam_id} and patient {patient_dni}: {e}")
            return None
    
    def get_all_exam_results(self, limit: Optional[int] = None) -> List[ExamResultResponse]:
        """Obtiene todos los resultados de exámenes"""
        try:
            results_db = self.repository.get_all_results(limit)
            return [self._result_db_to_response(result) for result in results_db]
        except Exception as e:
            logger.error(f"Error getting all exam results: {e}")
            return []
    
    def get_patients_with_exams_summary(self) -> Optional[PatientsWithExamsResponse]:
        """Obtiene lista de pacientes que han realizado exámenes con resumen"""
        try:
            # Obtener todos los resultados agrupados por paciente
            patient_dnis = self.repository.get_patients_with_exams()
            
            if not patient_dnis:
                return PatientsWithExamsResponse(
                    total_patients=0,
                    patients=[]
                )
            
            patients_summary = []
            
            for patient_dni in patient_dnis:
                # Obtener resultados del paciente
                patient_results = self.repository.get_by_patient_dni(patient_dni)
                
                if not patient_results:
                    continue
                
                # Calcular estadísticas
                total_exams = len(patient_results)
                passed_exams = sum(1 for result in patient_results if result.is_approved)
                failed_exams = total_exams - passed_exams
                
                # Obtener información del último examen
                latest_result = patient_results[0] if patient_results else None
                last_exam_date = latest_result.exam_date if latest_result else None
                last_exam_result = latest_result.is_approved if latest_result else None
                
                # Determinar si tiene licencia vigente (último examen aprobado)
                has_valid_license = last_exam_result if last_exam_result is not None else False
                
                # Obtener nombre del paciente
                patient_name = latest_result.patient_name if latest_result else patient_dni
                
                patient_summary = PatientExamSummary(
                    patient_dni=patient_dni,
                    patient_name=patient_name,
                    total_exams=total_exams,
                    passed_exams=passed_exams,
                    failed_exams=failed_exams,
                    last_exam_date=last_exam_date,
                    last_exam_result=last_exam_result,
                    has_valid_license=has_valid_license
                )
                
                patients_summary.append(patient_summary)
            
            # Ordenar por fecha del último examen (más reciente primero)
            patients_summary.sort(
                key=lambda x: x.last_exam_date or datetime.min,
                reverse=True
            )
            
            return PatientsWithExamsResponse(
                total_patients=len(patients_summary),
                patients=patients_summary
            )
            
        except Exception as e:
            logger.error(f"Error getting patients with exams summary: {e}")
            return None
    
    def get_exam_statistics(self, days_back: Optional[int] = 30) -> Optional[ExamStatisticsResponse]:
        """Obtiene estadísticas generales de exámenes"""
        try:
            stats = self.repository.get_exam_statistics(days_back)
            
            # Obtener los exámenes más recientes
            recent_results = self.repository.get_all_results(limit=10)
            recent_summaries = []
            
            for result in recent_results:
                summary = ExamResultSummary(
                    result_id=result.result_id,
                    exam_name=result.exam_name,
                    patient_name=result.patient_name,
                    is_approved=result.is_approved,
                    score_percentage=result.score_percentage,
                    exam_date=result.exam_date,
                    examiner_name=result.examiner_name
                )
                recent_summaries.append(summary)
            
            # Calcular porcentaje de aprobación
            total_exams = stats['total_exams']
            passed_exams = stats['passed_exams']
            pass_rate = (passed_exams / total_exams * 100) if total_exams > 0 else 0
            
            # Convertir exams_by_month a lista de diccionarios
            exams_by_month_list = [
                {"month": month, "count": count} 
                for month, count in stats['exams_by_month'].items()
            ]
            
            return ExamStatisticsResponse(
                total_exams_performed=total_exams,
                total_patients_examined=stats['total_patients'],
                total_passed=passed_exams,
                total_failed=stats['failed_exams'],
                pass_rate_percentage=round(pass_rate, 2),
                exams_by_month=exams_by_month_list,
                most_recent_exams=recent_summaries
            )
            
        except Exception as e:
            logger.error(f"Error getting exam statistics: {e}")
            return None
    
    def search_patients_by_name_or_dni(self, search_term: str) -> List[PatientExamSummary]:
        """Busca pacientes que han realizado exámenes por nombre o DNI"""
        try:
            # Obtener todos los pacientes con exámenes
            all_patients = self.get_patients_with_exams_summary()
            
            if not all_patients:
                return []
            
            # Filtrar por término de búsqueda
            search_term_lower = search_term.lower()
            filtered_patients = []
            
            for patient in all_patients.patients:
                if (search_term_lower in patient.patient_dni.lower() or 
                    search_term_lower in patient.patient_name.lower()):
                    filtered_patients.append(patient)
            
            return filtered_patients
            
        except Exception as e:
            logger.error(f"Error searching patients: {e}")
            return []
    
    def _result_db_to_response(self, result_db: ExamResultDB) -> ExamResultResponse:
        """Convierte ExamResultDB a ExamResultResponse"""
        return ExamResultResponse(
            result_id=result_db.result_id,
            exam_id=result_db.exam_id,
            exam_name=result_db.exam_name,
            patient_dni=result_db.patient_dni,
            patient_name=result_db.patient_name,
            total_questions=result_db.total_questions,
            correct_answers=result_db.correct_answers,
            incorrect_answers=result_db.incorrect_answers,
            score_percentage=result_db.score_percentage,
            status=result_db.status,
            is_approved=result_db.is_approved,
            examiner_dni=result_db.examiner_dni,
            examiner_name=result_db.examiner_name,
            examiner_role=result_db.examiner_role,
            notes=result_db.notes,
            observations=result_db.observations,
            exam_date=result_db.exam_date,
            created_at=result_db.created_at
        )


# Instancia global del servicio
exam_result_service = ExamResultService()
