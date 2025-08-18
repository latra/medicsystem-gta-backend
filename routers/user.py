from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import Optional, List
from schemas.user import (
    User, UserSummary, Doctor, DoctorCreate, DoctorSummary, DoctorRegister,
    Police, PoliceCreate, PoliceSummary, PoliceRegister, UserSearchFilters
)
from schemas.enums import UserRole
from services.user import UserService
from auth.authorization import require_admin, require_doctor_or_admin, require_authentication, require_doctor, require_police
import logging

user_router = APIRouter(prefix="/user", tags=["user"])
user_service = UserService()
logger = logging.getLogger(__name__)


@user_router.get("/me", response_model=User)
async def get_current_user_profile(
    current_user: User = require_authentication()
):
    """Obtiene el perfil básico del usuario actual"""
    return current_user


@user_router.get("/me/doctor", response_model=Doctor)
async def get_current_doctor_profile(
    current_doctor: Doctor = require_doctor()
):
    """Obtiene el perfil completo del doctor actual"""
    return current_doctor


@user_router.get("/me/police", response_model=Police)
async def get_current_police_profile(
    current_police: Police = require_police()
):
    """Obtiene el perfil completo del policía actual"""
    return current_police


@user_router.get("/doctors", response_model=List[DoctorSummary])
async def get_all_doctors(
    current_user: User = require_doctor_or_admin()
):
    """Obtiene lista de todos los doctores (solo doctores y admins)"""
    try:
        # TODO: Implementar en UserService
        return []
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving doctors: {str(e)}"
        )


@user_router.get("/police", response_model=List[PoliceSummary])
async def get_all_police(
    current_user: User = require_admin()
):
    """Obtiene lista de todos los policías (solo admins)"""
    try:
        # TODO: Implementar en UserService
        return []
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving police: {str(e)}"
        )


@user_router.post("/register/doctor", response_model=Doctor, status_code=status.HTTP_201_CREATED)
async def register_doctor(
    doctor: DoctorRegister
):
    """Registro público de doctor - cualquiera puede registrarse"""
    try:
        created_doctor = user_service.register_doctor(doctor)
        if not created_doctor:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to register doctor. DNI or email may already exist."
            )
        return created_doctor
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering doctor: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering doctor: {str(e)}"
        )

@user_router.post("/register/police", response_model=Police, status_code=status.HTTP_201_CREATED)
async def register_police(
    police: PoliceRegister
):
    """Registro público de policía - cualquiera puede registrarse"""
    try:
        created_police = user_service.register_police(police)
        if not created_police:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to register police. DNI or email may already exist."
            )
        return created_police
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering police: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering police: {str(e)}"
        )



@user_router.post("/doctor", response_model=Doctor, status_code=status.HTTP_201_CREATED)
async def create_doctor(
    doctor: DoctorCreate,
    current_user: User = require_admin()
):
    """Crea un nuevo doctor (solo admins) - método completo"""
    try:
        created_doctor = user_service.create_doctor(doctor)
        if not created_doctor:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create doctor"
            )
        return created_doctor
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating doctor: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating doctor: {str(e)}"
        )


@user_router.post("/police", response_model=Police, status_code=status.HTTP_201_CREATED)
async def create_police(
    police: PoliceCreate,
    current_user: User = require_admin()
):
    """Crea un nuevo policía (solo admins)"""
    try:
        created_police = user_service.create_police(police)
        if not created_police:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create police"
            )
        return created_police
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating police: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating police: {str(e)}"
        )


@user_router.get("/doctor/{doctor_dni}", response_model=Doctor)
async def get_doctor_by_dni(
    doctor_dni: str,
    current_user: User = require_doctor_or_admin()
):
    """Obtiene un doctor por DNI"""
    try:
        # TODO: Implementar get_doctor_by_dni en UserService
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Not implemented yet"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving doctor: {str(e)}"
        )


@user_router.get("/police/{police_dni}", response_model=Police)
async def get_police_by_dni(
    police_dni: str,
    current_user: User = require_admin()
):
    """Obtiene un policía por DNI (solo admins)"""
    try:
        # TODO: Implementar get_police_by_dni en UserService
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Not implemented yet"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving police: {str(e)}"
        )


@user_router.put("/disable/{user_dni}", response_model=User)
async def disable_user(
    user_dni: str,
    current_user: User = require_admin()
):
    """Deshabilita un usuario (solo admins)"""
    try:
        # TODO: Implementar disable_user en UserService
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Not implemented yet"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error disabling user: {str(e)}"
        )


@user_router.put("/enable/{user_dni}", response_model=User)
async def enable_user(
    user_dni: str,
    current_user: User = require_admin()
):
    """Habilita un usuario (solo admins)"""
    try:
        # TODO: Implementar enable_user en UserService
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Not implemented yet"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error enabling user: {str(e)}"
        )


@user_router.get("/search", response_model=List[UserSummary])
async def search_users(
    name: Optional[str] = Query(None, description="Buscar por nombre"),
    dni: Optional[str] = Query(None, description="Buscar por DNI"),
    role: Optional[UserRole] = Query(None, description="Filtrar por rol"),
    current_user: User = require_admin()
):
    """Busca usuarios con filtros (solo admins)"""
    try:
        filters = UserSearchFilters(
            name=name,
            dni=dni,
            role=role,
            enabled_only=True
        )
        # TODO: Implementar search_users en UserService
        return []
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching users: {str(e)}"
        )
