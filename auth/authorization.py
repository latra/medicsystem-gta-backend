from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth
from services.user import UserService
from schemas.user import User, Doctor, Police
from schemas.enums import UserRole
from typing import Optional, List, Union
import logging

security = HTTPBearer()
user_service = UserService()
logger = logging.getLogger(__name__)


class AuthorizationService:
    """Servicio de autorización por roles"""
    
    def __init__(self):
        self.user_service = UserService()
    
    async def verify_token_and_get_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
        """Verifica el token de Firebase y obtiene el usuario"""
        try:
            token = credentials.credentials
            decoded_token = auth.verify_id_token(token)
            
            if not decoded_token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, 
                    detail="Invalid authentication credentials"
                )
            
            user = self.user_service.get_user_by_firebase_uid(decoded_token["uid"])
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, 
                    detail="User not found"
                )
            
            if not user.enabled:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, 
                    detail="User account is disabled"
                )
            
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    async def verify_doctor(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> Doctor:
        """Verifica que el usuario sea un doctor"""
        try:
            token = credentials.credentials
            decoded_token = auth.verify_id_token(token)
            
            if not decoded_token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, 
                    detail="Invalid authentication credentials"
                )
            
            doctor = self.user_service.get_doctor_by_firebase_uid(decoded_token["uid"])
            if not doctor:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, 
                    detail="Access denied: Doctor role required"
                )
            
            return doctor
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error verifying doctor token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    async def verify_police(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> Police:
        """Verifica que el usuario sea un policía"""
        try:
            token = credentials.credentials
            decoded_token = auth.verify_id_token(token)
            
            if not decoded_token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, 
                    detail="Invalid authentication credentials"
                )
            
            police = self.user_service.get_police_by_firebase_uid(decoded_token["uid"])
            if not police:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, 
                    detail="Access denied: Police role required"
                )
            
            return police
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error verifying police token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    async def verify_admin(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
        """Verifica que el usuario sea administrador"""
        user = await self.verify_token_and_get_user(credentials)
        
        if not user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Access denied: Administrator role required"
            )
        
        return user
    
    async def verify_roles(self, allowed_roles: List[UserRole], credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
        """Verifica que el usuario tenga uno de los roles permitidos"""
        user = await self.verify_token_and_get_user(credentials)
        
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail=f"Access denied: One of these roles required: {[role.value for role in allowed_roles]}"
            )
        
        return user
    
    async def verify_doctor_or_admin(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> Union[Doctor, User]:
        """Verifica que el usuario sea doctor o administrador"""
        user = await self.verify_token_and_get_user(credentials)
        
        if user.role == UserRole.DOCTOR:
            doctor = self.user_service.get_doctor_by_firebase_uid(user.firebase_uid)
            if not doctor:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, 
                    detail="Access denied: Doctor profile not found"
                )
            return doctor
        elif user.is_admin:
            return user
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Access denied: Doctor or Administrator role required"
            )


# Instancia global del servicio de autorización
auth_service = AuthorizationService()


# Funciones de dependencia para usar en los endpoints

def require_authentication() -> User:
    """Requiere autenticación válida"""
    return Depends(auth_service.verify_token_and_get_user)

def require_doctor() -> Doctor:
    """Requiere que el usuario sea doctor"""
    return Depends(auth_service.verify_doctor)

def require_police() -> Police:
    """Requiere que el usuario sea policía"""
    return Depends(auth_service.verify_police)

def require_admin() -> User:
    """Requiere que el usuario sea administrador"""
    return Depends(auth_service.verify_admin)

def require_doctor_or_admin():
    """Requiere que el usuario sea doctor o administrador"""
    return Depends(auth_service.verify_doctor_or_admin)

def require_roles(allowed_roles: List[UserRole]):
    """Requiere uno de los roles especificados"""
    async def verify(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
        return await auth_service.verify_roles(allowed_roles, credentials)
    return Depends(verify)

def require_medical_access() -> Doctor:
    """Requiere acceso médico (solo doctores)"""
    return Depends(auth_service.verify_doctor)

def require_police_access() -> Police:
    """Requiere acceso policial (solo policías)"""
    return Depends(auth_service.verify_police)

def require_medical_or_admin():
    """Requiere acceso médico o de administrador"""
    return Depends(auth_service.verify_doctor_or_admin)

def require_exam_access():
    """Requiere acceso a exámenes (doctores y policías)"""
    return require_roles([UserRole.DOCTOR, UserRole.POLICE])

def require_exam_admin():
    """Requiere permisos de administrador para gestionar exámenes"""
    return require_admin()


# Compatibilidad hacia atrás con el sistema anterior
class FirebaseAuthCompatibility:
    """Clase para mantener compatibilidad con el sistema anterior"""
    
    def __init__(self):
        self.auth_service = AuthorizationService()
    
    async def verify_token(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> Doctor:
        """Método compatible con el sistema anterior - SOLO permite doctores"""
        # IMPORTANTE: Este método está diseñado para proteger endpoints médicos
        # Solo permite acceso a usuarios con rol DOCTOR
        try:
            doctor = await self.auth_service.verify_doctor(credentials)
            if not doctor:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, 
                    detail="Access denied: Medical endpoints require Doctor role"
                )
            return doctor
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error verifying doctor token for medical access: {e}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Medical endpoints require Doctor role",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    async def verify_admin_token(self, credentials: HTTPAuthorizationCredentials = Depends(security)):
        """Método compatible para verificar tokens de admin"""
        return await self.auth_service.verify_admin(credentials)


# Instancia para compatibilidad
firebase_auth_compat = FirebaseAuthCompatibility()
