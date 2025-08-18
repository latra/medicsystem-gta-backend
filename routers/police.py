from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from schemas.user import Police, PoliceSummary
from services.user import UserService
from auth.authorization import require_police, require_admin
import logging

police_router = APIRouter(prefix="/police", tags=["police"])
user_service = UserService()
logger = logging.getLogger(__name__)


@police_router.get("/me", response_model=Police)
async def get_current_police_profile(
    current_police: Police = require_police()
):
    """Obtiene el perfil completo del policía actual"""
    return current_police


@police_router.get("/profile", response_model=Police)
async def get_police_profile(
    current_police: Police = require_police()
):
    """Alias para obtener el perfil del policía actual"""
    return current_police


# Futuros endpoints específicos para policías
@police_router.get("/colleagues", response_model=List[PoliceSummary])
async def get_police_colleagues(
    current_police: Police = require_police()
):
    """Obtiene lista de colegas policías de la misma estación"""
    try:
        # TODO: Implementar búsqueda por estación/departamento
        logger.info(f"Police {current_police.dni} requesting colleagues from {current_police.station}")
        return []
    except Exception as e:
        logger.error(f"Error retrieving police colleagues: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving colleagues: {str(e)}"
        )


@police_router.get("/department/{department}", response_model=List[PoliceSummary])
async def get_police_by_department(
    department: str,
    current_police: Police = require_police()
):
    """Obtiene lista de policías por departamento"""
    try:
        # TODO: Implementar búsqueda por departamento
        logger.info(f"Police {current_police.dni} requesting department {department}")
        return []
    except Exception as e:
        logger.error(f"Error retrieving police by department: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving police by department: {str(e)}"
        )


# Endpoints administrativos (solo para admins)
@police_router.get("/all", response_model=List[PoliceSummary])
async def get_all_police(
    current_user = require_admin()
):
    """Obtiene lista de todos los policías (solo admins)"""
    try:
        # TODO: Implementar en UserService
        logger.info(f"Admin {current_user.dni} requesting all police")
        return []
    except Exception as e:
        logger.error(f"Error retrieving all police: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving all police: {str(e)}"
        )
