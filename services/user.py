from services.firestore import FirestoreService
from models.user import UserDB, DoctorDB, PoliceDB
from schemas.user import (
    User, UserCreate, UserUpdate, UserSummary,
    Doctor, DoctorCreate, DoctorUpdate, DoctorSummary, DoctorProfile, DoctorRegister,
    Police, PoliceCreate, PoliceUpdate, PoliceSummary, PoliceProfile, PoliceRegister,
    UserSearchFilters
)
from schemas.enums import UserRole
from firebase_admin import auth
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserRepository(FirestoreService):
    """Repositorio para operaciones de base de datos de usuarios"""
    
    def __init__(self):
        super().__init__()
        self.users_collection = "users"
        self.doctors_collection = "doctors"
        self.police_collection = "police"
    
    def _document_to_user_db(self, doc) -> Optional[UserDB]:
        """Convierte un documento de Firestore a UserDB"""
        try:
            if not doc.exists:
                return None
            
            data = doc.to_dict()
            # Convertir timestamps de string a datetime si es necesario
            for field in ['created_at', 'updated_at']:
                if field in data and isinstance(data[field], str):
                    try:
                        data[field] = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
                    except ValueError:
                        data[field] = datetime.now()
            
            return UserDB(**data)
        except Exception as e:
            logger.error(f"Error converting document to UserDB: {e}")
            return None
    
    def get_user_by_firebase_uid(self, firebase_uid: str) -> Optional[UserDB]:
        """Obtiene un usuario por Firebase UID"""
        try:
            docs = self.db.collection(self.users_collection).where("firebase_uid", "==", firebase_uid).get()
            if docs:
                return self._document_to_user_db(docs[0])
            return None
        except Exception as e:
            logger.error(f"Error getting user by Firebase UID {firebase_uid}: {e}")
            return None
    
    def get_user_by_dni(self, dni: str) -> Optional[UserDB]:
        """Obtiene un usuario por DNI"""
        try:
            doc = self.db.collection(self.users_collection).document(dni).get()
            return self._document_to_user_db(doc)
        except Exception as e:
            logger.error(f"Error getting user by DNI {dni}: {e}")
            return None
    
    def create_user(self, user_db: UserDB) -> bool:
        """Crea un nuevo usuario"""
        try:
            user_dict = user_db.model_dump()
            for field in ['created_at', 'updated_at']:
                if field in user_dict and isinstance(user_dict[field], datetime):
                    user_dict[field] = user_dict[field].isoformat()
            
            self.db.collection(self.users_collection).document(user_db.dni).set(user_dict)
            logger.info(f"User {user_db.dni} created successfully")
            return True
        except Exception as e:
            logger.error(f"Error creating user {user_db.dni}: {e}")
            return False
    
    def update_user(self, user_db: UserDB) -> bool:
        """Actualiza un usuario existente"""
        try:
            user_db.update_timestamp()
            user_dict = user_db.model_dump()
            for field in ['created_at', 'updated_at']:
                if field in user_dict and isinstance(user_dict[field], datetime):
                    user_dict[field] = user_dict[field].isoformat()
            
            self.db.collection(self.users_collection).document(user_db.dni).set(user_dict)
            logger.info(f"User {user_db.dni} updated successfully")
            return True
        except Exception as e:
            logger.error(f"Error updating user {user_db.dni}: {e}")
            return False
    
    def get_doctor_profile(self, user_id: str) -> Optional[DoctorDB]:
        """Obtiene el perfil específico de doctor"""
        try:
            docs = self.db.collection(self.doctors_collection).where("user_id", "==", user_id).get()
            if docs:
                data = docs[0].to_dict()
                for field in ['created_at', 'updated_at']:
                    if field in data and isinstance(data[field], str):
                        try:
                            data[field] = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
                        except ValueError:
                            data[field] = datetime.now()
                return DoctorDB(**data)
            return None
        except Exception as e:
            logger.error(f"Error getting doctor profile for user {user_id}: {e}")
            return None
    
    def create_doctor_profile(self, doctor_db: DoctorDB) -> bool:
        """Crea el perfil específico de doctor"""
        try:
            doctor_dict = doctor_db.model_dump()
            for field in ['created_at', 'updated_at']:
                if field in doctor_dict and isinstance(doctor_dict[field], datetime):
                    doctor_dict[field] = doctor_dict[field].isoformat()
            
            self.db.collection(self.doctors_collection).document(doctor_db.user_id).set(doctor_dict)
            return True
        except Exception as e:
            logger.error(f"Error creating doctor profile: {e}")
            return False
    
    def get_police_profile(self, user_id: str) -> Optional[PoliceDB]:
        """Obtiene el perfil específico de policía"""
        try:
            docs = self.db.collection(self.police_collection).where("user_id", "==", user_id).get()
            if docs:
                data = docs[0].to_dict()
                for field in ['created_at', 'updated_at']:
                    if field in data and isinstance(data[field], str):
                        try:
                            data[field] = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
                        except ValueError:
                            data[field] = datetime.now()
                return PoliceDB(**data)
            return None
        except Exception as e:
            logger.error(f"Error getting police profile for user {user_id}: {e}")
            return None
    
    def create_police_profile(self, police_db: PoliceDB) -> bool:
        """Crea el perfil específico de policía"""
        try:
            police_dict = police_db.model_dump()
            for field in ['created_at', 'updated_at']:
                if field in police_dict and isinstance(police_dict[field], datetime):
                    police_dict[field] = police_dict[field].isoformat()
            
            self.db.collection(self.police_collection).document(police_db.user_id).set(police_dict)
            return True
        except Exception as e:
            logger.error(f"Error creating police profile: {e}")
            return False


class UserService:
    """Servicio principal para gestión de usuarios"""
    
    def __init__(self):
        self.repository = UserRepository()
    
    def _user_db_to_user(self, user_db: UserDB) -> User:
        """Convierte UserDB a esquema User"""
        return User(
            user_id=user_db.user_id,
            firebase_uid=user_db.firebase_uid,
            name=user_db.name,
            dni=user_db.dni,
            email=user_db.email,
            phone=user_db.phone,
            role=user_db.role,
            enabled=user_db.enabled,
            is_admin=user_db.is_admin,
            created_at=user_db.created_at,
            updated_at=user_db.updated_at
        )
    
    def get_user_by_firebase_uid(self, firebase_uid: str) -> Optional[User]:
        """Obtiene un usuario por Firebase UID"""
        user_db = self.repository.get_user_by_firebase_uid(firebase_uid)
        if user_db and user_db.enabled:
            return self._user_db_to_user(user_db)
        return None
    
    def get_doctor_by_firebase_uid(self, firebase_uid: str) -> Optional[Doctor]:
        """Obtiene un doctor completo por Firebase UID"""
        user_db = self.repository.get_user_by_firebase_uid(firebase_uid)
        if not user_db or not user_db.enabled or user_db.role != UserRole.DOCTOR:
            return None
        
        doctor_profile = self.repository.get_doctor_profile(user_db.user_id)
        
        return Doctor(
            user_id=user_db.user_id,
            firebase_uid=user_db.firebase_uid,
            name=user_db.name,
            dni=user_db.dni,
            email=user_db.email,
            phone=user_db.phone,
            role=user_db.role,
            enabled=user_db.enabled,
            is_admin=user_db.is_admin,
            created_at=user_db.created_at,
            updated_at=user_db.updated_at,
            specialty=doctor_profile.specialty if doctor_profile else None,
            medical_license=doctor_profile.medical_license if doctor_profile else None,
            institution=doctor_profile.institution if doctor_profile else None,
            years_experience=doctor_profile.years_experience if doctor_profile else None
        )
    
    def get_police_by_firebase_uid(self, firebase_uid: str) -> Optional[Police]:
        """Obtiene un policía completo por Firebase UID"""
        user_db = self.repository.get_user_by_firebase_uid(firebase_uid)
        if not user_db or not user_db.enabled or user_db.role != UserRole.POLICE:
            return None
        
        police_profile = self.repository.get_police_profile(user_db.user_id)
        
        return Police(
            user_id=user_db.user_id,
            firebase_uid=user_db.firebase_uid,
            name=user_db.name,
            dni=user_db.dni,
            email=user_db.email,
            phone=user_db.phone,
            role=user_db.role,
            enabled=user_db.enabled,
            is_admin=user_db.is_admin,
            created_at=user_db.created_at,
            updated_at=user_db.updated_at,
            badge_number=police_profile.badge_number if police_profile else None,
            rank=police_profile.rank if police_profile else None,
            department=police_profile.department if police_profile else None,
            station=police_profile.station if police_profile else None,
            years_service=police_profile.years_service if police_profile else None
        )
    
    def create_doctor(self, doctor_create: DoctorCreate) -> Optional[Doctor]:
        """Crea un nuevo doctor"""
        # Verificar si ya existe
        existing_user = self.repository.get_user_by_dni(doctor_create.dni)
        if existing_user:
            logger.warning(f"User with DNI {doctor_create.dni} already exists")
            return None
        
        # Crear usuario en Firebase Auth
        password = self._format_password(doctor_create.dni)
        try:
            user_record = auth.create_user(
                email=doctor_create.email,
                password=password,
                display_name=doctor_create.name,
                email_verified=False
            )
        except auth.EmailAlreadyExistsError:
            raise Exception(f"Ya existe un usuario con el email {doctor_create.email}")
        except Exception as e:
            raise Exception(f"Error al crear usuario en Firebase Auth: {str(e)}")
        
        # Crear usuario base
        user_db = UserDB(
            firebase_uid=user_record.uid,
            name=doctor_create.name,
            dni=doctor_create.dni,
            email=doctor_create.email,
            phone=doctor_create.phone,
            role=UserRole.DOCTOR
        )
        
        if not self.repository.create_user(user_db):
            return None
        
        # Crear perfil de doctor
        doctor_profile = DoctorDB(
            user_id=user_db.user_id,
            specialty=doctor_create.specialty,
            medical_license=doctor_create.medical_license,
            institution=doctor_create.institution,
            years_experience=doctor_create.years_experience
        )
        
        if not self.repository.create_doctor_profile(doctor_profile):
            return None
        
        return self.get_doctor_by_firebase_uid(user_record.uid)
    
    def register_doctor(self, doctor_register: DoctorRegister) -> Optional[Doctor]:
        """Registra un nuevo doctor (método público simplificado)"""
        # Verificar si ya existe
        existing_user = self.repository.get_user_by_dni(doctor_register.dni)
        if existing_user:
            logger.warning(f"User with DNI {doctor_register.dni} already exists")
            return None
        
        # Crear usuario en Firebase Auth
        password = self._format_password(doctor_register.dni)
        try:
            user_record = auth.create_user(
                email=doctor_register.email,
                password=password,
                display_name=doctor_register.name,
                email_verified=False
            )
        except auth.EmailAlreadyExistsError:
            raise Exception(f"Ya existe un usuario con el email {doctor_register.email}")
        except Exception as e:
            raise Exception(f"Error al crear usuario en Firebase Auth: {str(e)}")
        
        # Crear usuario base
        user_db = UserDB(
            firebase_uid=user_record.uid,
            name=doctor_register.name,
            dni=doctor_register.dni,
            email=doctor_register.email,
            phone=doctor_register.phone,
            role=UserRole.DOCTOR
        )
        
        if not self.repository.create_user(user_db):
            return None
        
        # Crear perfil de doctor
        doctor_profile = DoctorDB(
            user_id=user_db.user_id,
            specialty=doctor_register.specialty,
            medical_license=doctor_register.medical_license,
            institution=doctor_register.institution,
            years_experience=doctor_register.years_experience
        )
        
        if not self.repository.create_doctor_profile(doctor_profile):
            return None
        
        return self.get_doctor_by_firebase_uid(user_record.uid)
    
    def register_police(self, police_register: PoliceRegister) -> Optional[Police]:
        """Registra un nuevo policía (método público simplificado)"""
        # Verificar si ya existe
        existing_user = self.repository.get_user_by_dni(police_register.dni)
        if existing_user:
            logger.warning(f"User with DNI {police_register.dni} already exists")
            return None
        
        # Crear usuario en Firebase Auth
        password = self._format_password(police_register.dni)
        try:
            user_record = auth.create_user(
                email=police_register.email,
                password=password,
                display_name=police_register.name,
                email_verified=False
            )
        except auth.EmailAlreadyExistsError:
            raise Exception(f"Ya existe un usuario con el email {police_register.email}")
        except Exception as e:
            raise Exception(f"Error al crear usuario en Firebase Auth: {str(e)}")
        
        # Crear usuario base
        user_db = UserDB(
            firebase_uid=user_record.uid,
            name=police_register.name,
            dni=police_register.dni,
            email=police_register.email,
            phone=police_register.phone,
            role=UserRole.POLICE
        )
        
        if not self.repository.create_user(user_db):
            return None
        
        # Crear perfil de policía
        police_profile = PoliceDB(
            user_id=user_db.user_id,
            badge_number=police_register.badge_number,
            rank=police_register.rank,
            department=police_register.department,
            station=police_register.station,
            years_service=police_register.years_service,
            can_arrest=True,  # Por defecto puede arrestar
            can_investigate=True,  # Por defecto puede investigar
            can_access_medical_info=False  # Por defecto NO puede acceder a info médica
        )
        
        if not self.repository.create_police_profile(police_profile):
            return None
        
        return self.get_police_by_firebase_uid(user_record.uid)
    
    def create_police(self, police_create: PoliceCreate) -> Optional[Police]:
        """Crea un nuevo policía"""
        # Verificar si ya existe
        existing_user = self.repository.get_user_by_dni(police_create.dni)
        if existing_user:
            logger.warning(f"User with DNI {police_create.dni} already exists")
            return None
        
        # Crear usuario en Firebase Auth
        password = self._format_password(police_create.dni)
        try:
            user_record = auth.create_user(
                email=police_create.email,
                password=password,
                display_name=police_create.name,
                email_verified=False
            )
        except auth.EmailAlreadyExistsError:
            raise Exception(f"Ya existe un usuario con el email {police_create.email}")
        except Exception as e:
            raise Exception(f"Error al crear usuario en Firebase Auth: {str(e)}")
        
        # Crear usuario base
        user_db = UserDB(
            firebase_uid=user_record.uid,
            name=police_create.name,
            dni=police_create.dni,
            email=police_create.email,
            phone=police_create.phone,
            role=UserRole.POLICE
        )
        
        if not self.repository.create_user(user_db):
            return None
        
        # Crear perfil de policía
        police_profile = PoliceDB(
            user_id=user_db.user_id,
            badge_number=police_create.police_profile.badge_number,
            rank=police_create.police_profile.rank,
            department=police_create.police_profile.department,
            station=police_create.police_profile.station,
            years_service=police_create.police_profile.years_service,
            can_arrest=police_create.police_profile.can_arrest,
            can_investigate=police_create.police_profile.can_investigate,
            can_access_medical_info=police_create.police_profile.can_access_medical_info
        )
        
        if not self.repository.create_police_profile(police_profile):
            return None
        
        return self.get_police_by_firebase_uid(user_record.uid)
    
    def _format_password(self, dni: str) -> str:
        """Genera password por defecto basado en DNI"""
        if len(dni) < 6:
            return dni.zfill(6)
        return dni
