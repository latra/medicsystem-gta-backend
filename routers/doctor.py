from fastapi import APIRouter, Depends
from schemas import Doctor, DoctorCreate
from auth.firebase import FirebaseAuth
from services.doctor import DoctorService
doctor_router = APIRouter(prefix="/doctor", tags=["doctor"])
firebase_auth = FirebaseAuth() 
doctor_service = DoctorService()

@doctor_router.get("/me", response_model=Doctor)
async def get_logged_doctor(current_user: dict = Depends(firebase_auth.verify_token)):
    return current_user

@doctor_router.get("/", response_model=list[Doctor])
async def get_doctors(current_user: dict = Depends(firebase_auth.verify_token)):
    return doctor_service.get_all_doctors()

@doctor_router.post("/", response_model=Doctor)
async def create_doctor(doctor: DoctorCreate):
    doctor = doctor_service.create_doctor(doctor)
    return doctor

@doctor_router.get("/{doctor_dni}", response_model=Doctor)
async def get_doctor(doctor_dni: str, current_user: dict = Depends(firebase_auth.verify_token)):
    return doctor_service.get_doctor(doctor_dni)

@doctor_router.put("/", response_model=Doctor)
async def update_logged_doctor(doctor: Doctor, current_user: dict = Depends(firebase_auth.verify_token)):
    return doctor
