from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import Optional, List
from schemas import (
    Patient, PatientCreate, PatientUpdate, PatientAdmitted, PatientComplete,
    PatientSummary, PatientMedicalHistoryUpdate, BloodAnalysisCreate, 
    BloodAnalysisResponse, RadiologyStudyCreate, RadiologyStudyResponse,
    MedicalHistoryResponse, Doctor
)
from services.patient import PatientService
from auth.firebase import FirebaseAuth

patients_router = APIRouter(prefix="/patients", tags=["patients"])
patient_service = PatientService()
firebase_auth = FirebaseAuth() 


@patients_router.get("/", response_model=List[PatientSummary])
async def get_patients(
    name: Optional[str] = Query(None, description="Filtrar por nombre del paciente"),
    current_user: Doctor = Depends(firebase_auth.verify_token)
):
    """Obtiene todos los pacientes habilitados o busca por nombre si se proporciona"""
    try:
        if name:
            patients = patient_service.search_patients(name)
        else:
            patients = patient_service.get_all_patients()
        return patients
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving patients: {str(e)}"
        )


@patients_router.post("/", response_model=Patient, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient: PatientCreate, 
    current_user: Doctor = Depends(firebase_auth.verify_token)
):
    """Crea un nuevo paciente"""
    try:
        created_patient = patient_service.create_patient(patient, created_by=current_user.dni)
        if not created_patient:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Patient with this DNI already exists"
            )
        return created_patient
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating patient: {str(e)}"
        )


@patients_router.get("/admitted", response_model=List[PatientAdmitted])
async def get_admitted_patients(current_user: Doctor = Depends(firebase_auth.verify_token)):
    """Obtiene todos los pacientes actualmente admitidos"""
    try:
        return patient_service.get_admitted_patients()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving admitted patients: {str(e)}"
        )


@patients_router.get("/{patient_dni}", response_model=Patient)
async def get_patient(
    patient_dni: str, 
    current_user: Doctor = Depends(firebase_auth.verify_token)
):
    """Obtiene información básica de un paciente por DNI"""
    try:
        patient = patient_service.get_patient(patient_dni)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Patient not found"
            )
        return patient
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving patient: {str(e)}"
        )


@patients_router.get("/{patient_dni}/complete", response_model=PatientComplete)
async def get_patient_complete(
    patient_dni: str, 
    current_user: Doctor = Depends(firebase_auth.verify_token)
):
    """Obtiene información completa de un paciente incluyendo historial médico"""
    try:
        patient = patient_service.get_patient_complete(patient_dni)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Patient not found"
            )
        return patient
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving complete patient data: {str(e)}"
        )


@patients_router.put("/{patient_dni}", response_model=Patient)
async def update_patient_basic(
    patient_dni: str, 
    patient_update: PatientUpdate, 
    current_user: Doctor = Depends(firebase_auth.verify_token)
):
    """Actualiza información básica del paciente"""
    try:
        updated_patient = patient_service.update_patient_basic(
            patient_dni, patient_update, updated_by=current_user.dni
        )
        if not updated_patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Patient not found"
            )
        return updated_patient
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating patient: {str(e)}"
        )


@patients_router.put("/{patient_dni}/medical-history", response_model=MedicalHistoryResponse)
async def update_patient_medical_history(
    patient_dni: str,
    medical_update: PatientMedicalHistoryUpdate,
    current_user: Doctor = Depends(firebase_auth.verify_token)
):
    """Actualiza el historial médico del paciente"""
    try:
        updated_history = patient_service.update_medical_history(
            patient_dni, medical_update, updated_by=current_user.dni
        )
        if not updated_history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        return updated_history
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating medical history: {str(e)}"
        )


@patients_router.post("/{patient_dni}/blood-analysis", response_model=BloodAnalysisResponse)
async def add_blood_analysis(
    patient_dni: str,
    analysis_data: BloodAnalysisCreate,
    current_user: Doctor = Depends(firebase_auth.verify_token)
):
    """Añade un nuevo análisis de sangre al paciente"""
    try:
        analysis = patient_service.add_blood_analysis(
            patient_dni, analysis_data, performed_by_dni=current_user.dni, performed_by_name=current_user.name
        )
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding blood analysis: {str(e)}"
        )


@patients_router.post("/{patient_dni}/radiology-study", response_model=RadiologyStudyResponse)
async def add_radiology_study(
    patient_dni: str,
    study_data: RadiologyStudyCreate,
    current_user: Doctor = Depends(firebase_auth.verify_token)
):
    """Añade un nuevo estudio radiológico al paciente"""
    try:
        study = patient_service.add_radiology_study(
            patient_dni, study_data, performed_by_dni=current_user.dni, performed_by_name=current_user.name
        )
        if not study:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        return study
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding radiology study: {str(e)}"
        )


@patients_router.delete("/{patient_dni}", status_code=status.HTTP_200_OK)
async def delete_patient(
    patient_dni: str, 
    current_user: Doctor = Depends(firebase_auth.verify_admin_token)
):
    """Deshabilita un paciente (soft delete)"""
    try:
        # Verificar que el paciente existe antes de intentar eliminarlo
        patient = patient_service.get_patient(patient_dni)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Patient not found"
            )
        
        success = patient_service.delete_patient(patient_dni, disabled_by=current_user.dni)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete patient"
            )
        
        return {"message": "Patient deleted successfully", "dni": patient_dni}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting patient: {str(e)}"
        )

