from fastapi import APIRouter, HTTPException, Depends
from schemas import Patient, Doctor, PatientUpdate, PatientAdmitted
from services.patient import PatientService
from auth.firebase import FirebaseAuth

patients_router = APIRouter(prefix="/patients", tags=["patients"])
patient_service = PatientService()
firebase_auth = FirebaseAuth() 

@patients_router.get("/", response_model=list[Patient])
async def get_patients(current_user: Doctor = Depends(firebase_auth.verify_token)):
    return patient_service.get_all_patients()

@patients_router.post("/", response_model=Patient)
async def create_patient(patient: Patient, current_user: Doctor = Depends(firebase_auth.verify_token)):
    patient = patient_service.create_patient(patient)
    return patient

@patients_router.get("/admitted", response_model=list[PatientAdmitted])
async def get_admitted_patients(current_user: Doctor = Depends(firebase_auth.verify_token)):
    return patient_service.get_admitted_patients()

@patients_router.get("/{patient_dni}", response_model=Patient)
async def get_patient(patient_dni: str, current_user: Doctor = Depends(firebase_auth.verify_token)):
    patient = patient_service.get_patient(patient_dni)
    if patient:
        return patient
    else:
        raise HTTPException(status_code=404, detail="Patient not found")


@patients_router.put("/{patient_dni}", response_model=Patient)
async def update_patient(patient_dni: str, patient: PatientUpdate, current_user: Doctor = Depends(firebase_auth.verify_token)):
    patient_service.update_patient(patient_dni, patient)
    return patient_service.get_patient(patient_dni)

@patients_router.delete("/{patient_dni}")
async def delete_patient(patient_dni: str, current_user: Doctor = Depends(firebase_auth.verify_token)):
    patient = patient_service.get_patient(patient_dni)
    if patient:
        patient_service.delete_patient(patient_dni, current_user.dni)
        return {"message": "Patient deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Patient not found")

