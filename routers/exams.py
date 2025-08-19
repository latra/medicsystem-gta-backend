from fastapi import APIRouter, HTTPException, Query, Depends, status
from schemas.exam import (
    ExamCreate, CategoryCreate, QuestionCreate, ExamSubmission,
    ExamResultResponse, ExamResultDetailResponse, PatientExamHistoryResponse,
    PatientsWithExamsResponse, ExamStatisticsResponse, PatientExamSummary
)
from schemas.exam_certificate import ExamCertificateResponse
from services.exam import exam_service
from services.exam_results import exam_result_service
from auth.authorization import require_exam_admin, require_exam_access
from schemas.user import User
from typing import Optional

exam_router = APIRouter(
    prefix="/exams",
    tags=["exams"]
) 

@exam_router.post("/")
def create_exam(exam: ExamCreate, current_user: User = require_exam_admin()):
    """
    Create a new exam with categories and questions
    Only admins (doctors or police with admin role) can create exams
    """
    try:
        result = exam_service.create_exam(exam, created_by=current_user.dni)
        if result:
            return result
        else:
            raise HTTPException(status_code=400, detail="Failed to create exam")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@exam_router.get("/{exam_id}")
def get_exam(exam_id: str, current_user: User = require_exam_access()):
    """
    Get an exam by its ID
    Accessible by doctors and police officers
    """
    try:
        result = exam_service.get_exam(exam_id)
        if result:
            return result
        else:
            raise HTTPException(status_code=404, detail="Exam not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@exam_router.put("/{exam_id}")
def update_exam(exam_id: str, exam: ExamCreate, current_user: User = require_exam_admin()):
    """
    Update an existing exam
    Only admins (doctors or police with admin role) can update exams
    """
    try:
        result = exam_service.update_exam(exam_id, exam, updated_by=current_user.dni)
        if result:
            return result
        else:
            raise HTTPException(status_code=404, detail="Exam not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@exam_router.delete("/{exam_id}")
def delete_exam(exam_id: str, current_user: User = require_exam_admin()):
    """
    Delete an exam (soft delete)
    Only admins (doctors or police with admin role) can delete exams
    """
    try:
        success = exam_service.delete_exam(exam_id, deleted_by=current_user.dni)
        if success:
            return {"message": "Exam deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Exam not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@exam_router.get("/")
def list_exams(
    search: Optional[str] = Query(None, description="Search exams by name"),
    current_user: User = require_exam_access()
):
    """
    List all exams or search by name
    Accessible by doctors and police officers
    """
    try:
        if search:
            return exam_service.search_exams(search)
        else:
            return exam_service.list_exams()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@exam_router.post("/{exam_id}/categories")
def add_category_to_exam(
    exam_id: str, 
    category: CategoryCreate, 
    current_user: User = require_exam_admin()
):
    """
    Add a new category to an existing exam
    Only admins (doctors or police with admin role) can add categories
    """
    try:
        result = exam_service.add_category_to_exam(exam_id, category, updated_by=current_user.dni)
        if result:
            return result
        else:
            raise HTTPException(status_code=404, detail="Exam not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@exam_router.post("/{exam_id}/categories/{category_id}/questions")
def add_question_to_category(
    exam_id: str, 
    category_id: str, 
    question: QuestionCreate, 
    current_user: User = require_exam_admin()
):
    """
    Add a new question to a specific category in an exam
    Only admins (doctors or police with admin role) can add questions
    """
    try:
        result = exam_service.add_question_to_category(exam_id, category_id, question, updated_by=current_user.dni)
        if result:
            return result
        else:
            raise HTTPException(status_code=404, detail="Exam or category not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@exam_router.get("/{exam_id}/questions")
def get_questions_by_exam(exam_id: str, current_user: User = require_exam_access()):
    """
    Get all questions by exam
    Accessible by doctors and police officers
    """
    try:
        result = exam_service.get_questions_by_exam(exam_id)
        if result:
            return result
        else:
            raise HTTPException(status_code=404, detail="Exam not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@exam_router.post("/results")
def submit_exam_result(submission: ExamSubmission, current_user: User = require_exam_access()):
    """
    Submit exam results for a patient
    Accessible by doctors and police officers who can administer exams
    """
    try:
        result = exam_result_service.submit_exam_result(
            submission=submission,
            examiner_dni=current_user.dni,
            examiner_name=current_user.name,
            examiner_role=current_user.role.value
        )
        if result:
            return result
        else:
            raise HTTPException(status_code=400, detail="Failed to submit exam result")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@exam_router.get("/results/{result_id}")
def get_exam_result(result_id: str, current_user: User = require_exam_access()):
    """
    Get exam result by ID
    Accessible by doctors and police officers
    """
    try:
        result = exam_result_service.get_exam_result(result_id)
        if result:
            return result
        else:
            raise HTTPException(status_code=404, detail="Exam result not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@exam_router.get("/results/{result_id}/detail")
def get_exam_result_detail(result_id: str, current_user: User = require_exam_access()):
    """
    Get detailed exam result with all answers
    Accessible by doctors and police officers
    """
    try:
        result = exam_result_service.get_exam_result_detail(result_id)
        if result:
            return result
        else:
            raise HTTPException(status_code=404, detail="Exam result not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@exam_router.get("/patients/{patient_dni}/history")
def get_patient_exam_history(patient_dni: str, current_user: User = require_exam_access()):
    """
    Get exam history for a specific patient by DNI
    Accessible by doctors and police officers
    """
    try:
        result = exam_result_service.get_patient_exam_history(patient_dni)
        if result:
            return result
        else:
            raise HTTPException(status_code=404, detail="Patient not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@exam_router.get("/results")
def get_all_exam_results(
    limit: Optional[int] = Query(None, description="Limit number of results"),
    current_user: User = require_exam_access()
):
    """
    Get all exam results
    Accessible by doctors and police officers
    """
    try:
        return exam_result_service.get_all_exam_results(limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@exam_router.get("/patients")
def get_patients_with_exams(
    search: Optional[str] = Query(None, description="Search patients by name or DNI"),
    current_user: User = require_exam_access()
):
    """
    Get list of patients who have taken exams
    Useful for police to see who has psychotechnical licenses
    Accessible by doctors and police officers
    """
    try:
        if search:
            # Buscar pacientes específicos
            patients = exam_result_service.search_patients_by_name_or_dni(search)
            return {
                "total_patients": len(patients),
                "patients": patients
            }
        else:
            # Obtener todos los pacientes con exámenes
            result = exam_result_service.get_patients_with_exams_summary()
            if result:
                return result
            else:
                return PatientsWithExamsResponse(total_patients=0, patients=[])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@exam_router.get("/statistics")
def get_exam_statistics(
    days_back: Optional[int] = Query(30, description="Number of days back to analyze"),
    current_user: User = require_exam_access()
):
    """
    Get exam statistics and analytics
    Useful for monitoring exam performance and trends
    Accessible by doctors and police officers
    """
    try:
        result = exam_result_service.get_exam_statistics(days_back)
        if result:
            return result
        else:
            raise HTTPException(status_code=500, detail="Unable to generate statistics")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@exam_router.get("/patients/search/{search_term}")
def search_patients_with_exams(
    search_term: str,
    current_user: User = require_exam_access()
):
    """
    Search patients who have taken exams by name or DNI
    Specifically useful for police to quickly find drivers
    Accessible by doctors and police officers
    """
    try:
        patients = exam_result_service.search_patients_by_name_or_dni(search_term)
        return {
            "search_term": search_term,
            "total_found": len(patients),
            "patients": patients
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@exam_router.get("/get_certificate/{exam_id}/{patient_dni}", response_model=ExamCertificateResponse)
async def get_exam_certificate(
    exam_id: str,
    patient_dni: str,
    current_user: User = require_exam_access()
):
    """Obtiene el certificado del último examen realizado por un paciente"""
    try:
        certificate = exam_result_service.get_latest_exam_certificate(exam_id, patient_dni)
        if not certificate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No exam results found for patient {patient_dni} and exam {exam_id}"
            )
        return certificate
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving exam certificate: {str(e)}"
        )