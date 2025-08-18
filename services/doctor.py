from services.firestore import FirestoreService
from services.user import UserService
from schemas import Doctor, DoctorCreate
from schemas.user import DoctorCreate as DoctorCreateNew, DoctorProfile
from schemas.enums import UserRole
from firebase_admin import auth
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class DoctorService(FirestoreService):
    """Servicio de doctor con compatibilidad hacia atrás"""
    
    def __init__(self):
        super().__init__()
        self.doctors_collection = "doctors"  # Mantener para compatibilidad
        self.user_service = UserService()

    def get_doctor(self, doctor_uid: str) -> Optional[Doctor]:
        """Obtiene un doctor por Firebase UID (compatible hacia atrás)"""
        try:
            # Intentar usar el nuevo sistema primero
            doctor = self.user_service.get_doctor_by_firebase_uid(doctor_uid)
            if doctor:
                # Convertir a formato legacy para compatibilidad
                return Doctor(
                    name=doctor.name,
                    dni=doctor.dni,
                    email=doctor.email,
                    specialty=doctor.specialty,
                    enabled=doctor.enabled,
                    is_admin=doctor.is_admin,
                    firebase_uid=doctor.firebase_uid
                )
            
            # Fallback al sistema legacy si no se encuentra en el nuevo
            doc = self.db.collection(self.doctors_collection).where("firebase_uid", "==", doctor_uid).get()
            if doc:
                return Doctor(**doc[0].to_dict())
            return None
            
        except Exception as e:
            logger.error(f"Error getting doctor {doctor_uid}: {e}")
            return None

    def get_all_doctors(self) -> List[Doctor]:
        """Obtiene todos los doctores (compatible hacia atrás)"""
        try:
            # TODO: Implementar en el UserService para obtener todos los doctores
            # Por ahora usar el sistema legacy
            docs = self.db.collection(self.doctors_collection).get()
            return [Doctor(**doc.to_dict()) for doc in docs]
        except Exception as e:
            logger.error(f"Error getting all doctors: {e}")
            return []

    def create_doctor(self, doctor: DoctorCreate) -> Optional[Doctor]:
        """Crea un nuevo doctor (compatible hacia atrás)"""
        try:
            # Usar el método simplificado de registro
            from schemas.user import DoctorRegister
            
            doctor_register = DoctorRegister(
                name=doctor.name,
                dni=doctor.dni,
                email=doctor.email,
                phone=None,
                specialty=doctor.specialty,
                medical_license=getattr(doctor, 'medical_license', None),
                institution=getattr(doctor, 'institution', None),
                years_experience=getattr(doctor, 'years_experience', None)
            )
            
            # Crear usando el nuevo sistema simplificado
            new_doctor = self.user_service.register_doctor(doctor_register)
            if new_doctor:
                # Convertir a formato legacy para compatibilidad
                return Doctor(
                    name=new_doctor.name,
                    dni=new_doctor.dni,
                    email=new_doctor.email,
                    specialty=new_doctor.specialty,
                    enabled=new_doctor.enabled,
                    is_admin=new_doctor.is_admin,
                    firebase_uid=new_doctor.firebase_uid
                )
            return None
            
        except Exception as e:
            logger.error(f"Error creating doctor: {e}")
            # Fallback al sistema legacy
            return self._create_doctor_legacy(doctor)
    
    def _create_doctor_legacy(self, doctor: DoctorCreate) -> Optional[Doctor]:
        """Método legacy para crear doctor"""
        try:
            doctor_dict = doctor.model_dump()
            doctor_dict["enabled"] = True
            doctor_dict["is_admin"] = False
            password = self._format_password(doctor_dict['dni'])
            
            user_record = auth.create_user(
                email=doctor_dict['email'],
                password=password,
                display_name=f"{doctor_dict['name']}",
                email_verified=False
            )
            
            doctor_dict['firebase_uid'] = user_record.uid
            self.db.collection(self.doctors_collection).document(doctor.dni).set(doctor_dict)
            
            return self.get_doctor(doctor_dict['firebase_uid'])
            
        except auth.EmailAlreadyExistsError:
            raise Exception(f"Ya existe un usuario con el email {doctor_dict['email']}")
        except Exception as e:
            raise Exception(f"Error al crear usuario en Firebase Auth: {str(e)}")
    
    def update_doctor(self, doctor: Doctor):
        """Actualiza un doctor (compatible hacia atrás)"""
        self.db.collection(self.doctors_collection).document(doctor.dni).set(doctor.model_dump())

    def delete_doctor(self, doctor_dni: str):
        """Elimina un doctor (compatible hacia atrás)"""
        self.db.collection(self.doctors_collection).document(doctor_dni).delete()

    def _format_password(self, dni: str) -> str:
        """Genera password por defecto basado en DNI"""
        if len(dni) < 6:
            return dni.zfill(6)
        return dni