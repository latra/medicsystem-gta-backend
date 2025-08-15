from fastapi import APIRouter
from schemas import BloodType, AttentionType, PatientStatus, UserRole

system_info_router = APIRouter(prefix="/system_info", tags=["system_info"])


@system_info_router.get("/blood_types", response_model=list[BloodType])
async def get_blood_types():
    return list(BloodType)

@system_info_router.get("/attention_types", response_model=list[AttentionType])
async def get_attention_types():
    return list(AttentionType)

@system_info_router.get("/patient_statuses", response_model=list[PatientStatus])
async def get_patient_statuses():
    return list(PatientStatus)

@system_info_router.get("/user_roles", response_model=list[UserRole])
async def get_user_roles():
    return list(UserRole)