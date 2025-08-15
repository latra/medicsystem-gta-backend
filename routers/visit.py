from fastapi import APIRouter, HTTPException, Depends
from schemas import VisitBase, Visit, VisitStatus, AttentionType, PatientStatus, VisitUpdate, VisitSummary, Doctor
from datetime import datetime
from services.visits import VisitService
from auth.firebase import FirebaseAuth

visit_router = APIRouter(prefix="/visit", tags=["visit"])
visit_service = VisitService()
firebase_auth = FirebaseAuth() 

@visit_router.get("/{patient_dni}", response_model=list[VisitSummary])
async def get_visits_by_patient(patient_dni: str, current_user: dict = Depends(firebase_auth.verify_token)):
    visits = visit_service.get_all_visits_by_patient_dni(patient_dni)
    return visits

@visit_router.get("/info/{visit_id}", response_model=Visit)
async def get_visit(visit_id: str, current_user: dict = Depends(firebase_auth.verify_token)):
    return visit_service.get_visit(visit_id)


@visit_router.post("/", response_model=Visit)
async def create_visit(visit: VisitBase, current_user: Doctor = Depends(firebase_auth.verify_token)):
    return visit_service.create_visit(visit, current_user)

@visit_router.put("/{visit_id}", response_model=Visit)
async def update_visit(visit_id: str, visit_update: VisitUpdate, current_user: dict = Depends(firebase_auth.verify_token)):
    existing_visit = visit_service.get_visit(visit_id)
    if existing_visit:
        return visit_service.update_visit(visit_update, existing_visit)
    else:
        raise HTTPException(status_code=404, detail="Visit not found")

@visit_router.put("/{visit_id}/discharge", response_model=Visit)
async def discharge_visit(visit_id: str, current_user: dict = Depends(firebase_auth.verify_token)):
    visit = visit_service.discharge_visit(visit_id)
    if visit:
        return visit
    else:
        raise HTTPException(status_code=404, detail="Visit not found")

@visit_router.delete("/{visit_id}", response_model=Visit)
async def delete_visit(visit_id: str, current_user: dict = Depends(firebase_auth.verify_token)):
    visit = visit_service.get_visit(visit_id)
    if visit:
        visit_service.delete_visit(visit_id)
        return {"message": "Visit deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Visit not found")