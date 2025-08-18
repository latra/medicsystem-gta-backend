from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import Optional, List
from schemas import (
    VisitBase, Visit, VisitCreate, VisitStatus, VisitUpdate, VisitSummary, 
    VisitComplete, VitalSignsBase, VitalSignsResponse, DiagnosisCreate, 
    DiagnosisResponse, PrescriptionCreate, PrescriptionResponse,
    DischargeRequest, Doctor
)
from schemas.patient import (
    BloodAnalysisCreate, BloodAnalysisResponse, RadiologyStudyCreate, RadiologyStudyResponse
)
from services.visits import VisitService
from auth.firebase import FirebaseAuth

visit_router = APIRouter(prefix="/visit", tags=["visit"])
visit_service = VisitService()
firebase_auth = FirebaseAuth() 


@visit_router.get("/{patient_dni}", response_model=List[VisitSummary])
async def get_visits_by_patient(
    patient_dni: str, 
    current_user: Doctor = Depends(firebase_auth.verify_token)
):
    """Obtiene todas las visitas de un paciente como resumen"""
    try:
        visits = visit_service.get_all_visits_by_patient_dni(patient_dni)
        return visits
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving visits for patient: {str(e)}"
        )


@visit_router.get("/info/{visit_id}", response_model=VisitComplete)
async def get_visit(
    visit_id: str, 
    current_user: Doctor = Depends(firebase_auth.verify_token)
):
    """Obtiene información completa de una visita por ID incluyendo análisis y estudios"""
    try:
        visit = visit_service.get_visit_complete(visit_id)
        if not visit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Visit not found"
            )
        return visit
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving visit: {str(e)}"
        )


@visit_router.get("/complete/{visit_id}", response_model=VisitComplete)
async def get_visit_complete(
    visit_id: str,
    current_user: Doctor = Depends(firebase_auth.verify_token)
):
    """Obtiene información completa de una visita con todos los datos médicos"""
    try:
        visit = visit_service.get_visit_complete(visit_id)
        if not visit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Visit not found"
            )
        return visit
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving complete visit data: {str(e)}"
        )


@visit_router.post("/", response_model=Visit, status_code=status.HTTP_201_CREATED)
async def create_visit(
    visit: VisitCreate, 
    current_user: Doctor = Depends(firebase_auth.verify_token)
):
    """Crea una nueva visita"""
    try:
        created_visit = visit_service.create_visit(visit, current_user)
        if not created_visit:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create visit"
            )
        return created_visit
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating visit: {str(e)}"
        )


@visit_router.put("/{visit_id}", response_model=Visit)
async def update_visit(
    visit_id: str, 
    visit_update: VisitUpdate, 
    current_user: Doctor = Depends(firebase_auth.verify_token)
):
    """Actualiza información básica de una visita"""
    try:
        updated_visit = visit_service.update_visit(
            visit_id, visit_update, updated_by=current_user.dni
        )
        if not updated_visit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Visit not found"
            )
        return updated_visit
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating visit: {str(e)}"
        )


@visit_router.put("/{visit_id}/discharge", response_model=Visit)
async def discharge_visit(
    visit_id: str,
    discharge_request: DischargeRequest,
    current_user: Doctor = Depends(firebase_auth.verify_token)
):
    """Da de alta a un paciente (versión mejorada)"""
    try:
        visit = visit_service.discharge_visit(
            visit_id, discharge_request, discharged_by=current_user.dni
        )
        if not visit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Visit not found"
            )
        return visit
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error discharging patient: {str(e)}"
        )


@visit_router.put("/{visit_id}/discharge-simple", response_model=Visit)
async def discharge_visit_simple(
    visit_id: str, 
    current_user: Doctor = Depends(firebase_auth.verify_token)
):
    """Da de alta a un paciente (versión simple para compatibilidad)"""
    try:
        # Crear request básico para compatibilidad con API anterior
        discharge_request = DischargeRequest(
            discharge_summary="Alta médica",
            discharge_instructions="Seguir indicaciones médicas",
            follow_up_required=False
        )
        
        visit = visit_service.discharge_visit(
            visit_id, discharge_request, discharged_by=current_user.dni
        )
        if not visit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Visit not found"
            )
        return visit
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error discharging patient: {str(e)}"
        )


@visit_router.post("/{visit_id}/vital-signs", response_model=VitalSignsResponse)
async def add_vital_signs(
    visit_id: str,
    vital_signs: VitalSignsBase,
    current_user: Doctor = Depends(firebase_auth.verify_token)
):
    """Añade signos vitales a una visita"""
    try:
        result = visit_service.add_vital_signs(
            visit_id, vital_signs, measured_by=current_user.dni
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Visit not found"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding vital signs: {str(e)}"
        )


@visit_router.post("/{visit_id}/diagnosis", response_model=DiagnosisResponse)
async def add_diagnosis(
    visit_id: str,
    diagnosis: DiagnosisCreate,
    current_user: Doctor = Depends(firebase_auth.verify_token)
):
    """Añade un diagnóstico a una visita"""
    try:
        result = visit_service.add_diagnosis(
            visit_id, diagnosis, diagnosed_by=current_user.dni
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Visit not found"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding diagnosis: {str(e)}"
        )


@visit_router.post("/{visit_id}/prescription", response_model=PrescriptionResponse)
async def add_prescription(
    visit_id: str,
    prescription: PrescriptionCreate,
    current_user: Doctor = Depends(firebase_auth.verify_token)
):
    """Añade una prescripción médica a una visita"""
    try:
        result = visit_service.add_prescription(
            visit_id, prescription, prescribed_by=current_user.dni
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Visit not found"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding prescription: {str(e)}"
        )


@visit_router.get("/doctor/{doctor_dni}", response_model=List[Visit])
async def get_visits_by_doctor(
    doctor_dni: str,
    current_user: Doctor = Depends(firebase_auth.verify_token)
):
    """Obtiene todas las visitas de un médico específico"""
    try:
        # Verificar que el usuario actual puede ver las visitas del médico solicitado
        # (podría ser él mismo o un admin)
        if current_user.dni != doctor_dni:
            # Aquí podrías añadir lógica adicional de permisos si es necesario
            pass
        
        visits = visit_service.get_all_visits_by_doctor_dni(doctor_dni)
        return visits
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving visits for doctor: {str(e)}"
        )


@visit_router.get("/status/{status}", response_model=List[Visit])
async def get_visits_by_status(
    status: VisitStatus,
    current_user: Doctor = Depends(firebase_auth.verify_token)
):
    """Obtiene todas las visitas por estado (ADMISSION, DISCHARGE, etc.)"""
    try:
        visits = visit_service.get_all_visits_by_status(status)
        return visits
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving visits by status: {str(e)}"
        )


@visit_router.get("/", response_model=List[Visit])
async def get_all_visits(
    limit: Optional[int] = Query(50, ge=1, le=500, description="Número máximo de visitas a retornar"),
    current_user: Doctor = Depends(firebase_auth.verify_token)
):
    """Obtiene todas las visitas del sistema (limitado)"""
    try:
        visits = visit_service.get_all_visits()
        # Aplicar límite
        return visits[:limit] if limit else visits
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving all visits: {str(e)}"
        )


@visit_router.post("/{visit_id}/blood-analysis", response_model=BloodAnalysisResponse)
async def add_blood_analysis_to_visit(
    visit_id: str,
    blood_analysis: BloodAnalysisCreate,
    current_user: Doctor = Depends(firebase_auth.verify_token)
):
    """Añade un análisis de sangre a una visita específica"""
    try:
        # Usar el método con sincronización automática para duplicar datos
        result = visit_service.add_blood_analysis_with_patient_sync(
            visit_id, 
            blood_analysis, 
            performed_by_dni=current_user.dni,
            performed_by_name=current_user.name
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Visit not found"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding blood analysis to visit: {str(e)}"
        )


@visit_router.post("/{visit_id}/radiology-study", response_model=RadiologyStudyResponse)
async def add_radiology_study_to_visit(
    visit_id: str,
    radiology_study: RadiologyStudyCreate,
    current_user: Doctor = Depends(firebase_auth.verify_token)
):
    """Añade un estudio radiológico a una visita específica"""
    try:
        # Usar el método con sincronización automática para duplicar datos
        result = visit_service.add_radiology_study_with_patient_sync(
            visit_id, 
            radiology_study, 
            performed_by_dni=current_user.dni,
            performed_by_name=current_user.name
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Visit not found"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding radiology study to visit: {str(e)}"
        )


@visit_router.delete("/{visit_id}", status_code=status.HTTP_200_OK)
async def delete_visit(
    visit_id: str, 
    current_user: Doctor = Depends(firebase_auth.verify_admin_token)
):
    """Elimina una visita del sistema"""
    try:
        # Verificar que la visita existe antes de intentar eliminarla
        visit = visit_service.get_visit(visit_id)
        if not visit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Visit not found"
            )
        
        success = visit_service.delete_visit(visit_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete visit"
            )
        
        return {"message": "Visit deleted successfully", "visit_id": visit_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting visit: {str(e)}"
        )