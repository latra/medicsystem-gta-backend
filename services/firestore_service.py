import firebase_admin
from firebase_admin import firestore, auth
from typing import List, Optional, Dict, Any
from models import Medico, MedicoCreate, MedicoUpdate, CargoMedico

class FirestoreService:
    def __init__(self):
        """Initialize Firestore client"""
        if not firebase_admin._apps:
            # Initialize Firebase Admin SDK if not already initialized
            firebase_admin.initialize_app()
        
        self.db = firestore.client()
        self.medicos_collection = "medic"
    
    def _format_password(self, dni: str) -> str:
        """
        Formatea el DNI para usarlo como contraseña.
        Si tiene menos de 6 caracteres, rellena con ceros delante hasta 6.
        """
        if len(dni) < 6:
            return dni.zfill(6)
        return dni
    
    async def create_medico(self, medico_data: MedicoCreate) -> Medico:
        """Crear un nuevo médico en Firestore y usuario en Firebase Auth"""
        try:
            # Convertir el modelo a dict
            medico_dict = medico_data.model_dump()
            
            # Formatear contraseña (DNI con ceros delante si es necesario)
            password = self._format_password(medico_dict['dni'])
            
            # Crear usuario en Firebase Authentication
            try:
                user_record = auth.create_user(
                    email=medico_dict['email'],
                    password=password,  # DNI formateado como contraseña
                    display_name=f"{medico_dict['nombre']} {medico_dict['apellido']}",
                    email_verified=False
                )
                
                # Agregar el UID de Firebase Auth al médico
                medico_dict['firebase_uid'] = user_record.uid
                
            except auth.EmailAlreadyExistsError:
                raise Exception(f"Ya existe un usuario con el email {medico_dict['email']}")
            except Exception as e:
                raise Exception(f"Error al crear usuario en Firebase Auth: {str(e)}")
            
            # Crear documento en Firestore
            doc_ref = self.db.collection(self.medicos_collection).document()
            medico_dict['id'] = doc_ref.id
            
            # Guardar en Firestore
            doc_ref.set(medico_dict)
            
            return Medico(**medico_dict)
            
        except Exception as e:
            # Si hay error, intentar limpiar el usuario creado en Auth
            if 'firebase_uid' in medico_dict:
                try:
                    auth.delete_user(medico_dict['firebase_uid'])
                except:
                    pass  # Ignorar errores de limpieza
            raise Exception(f"Error al crear médico: {str(e)}")
    
    async def get_medico(self, firebase_uid: str) -> Optional[Medico]:
        """Obtener un médico por ID"""
        try:
            docs = self.db.collection(self.medicos_collection).where('firebase_uid', '==', firebase_uid).limit(1).stream()
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                return Medico(**data)
            return None
                
        except Exception as e:
            raise Exception(f"Error al obtener médico: {str(e)}")
    
    async def get_all_medicos(self) -> List[Medico]:
        """Obtener todos los médicos"""
        try:
            docs = self.db.collection(self.medicos_collection).stream()
            medicos = []
            
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                medicos.append(Medico(**data))
            
            return medicos
            
        except Exception as e:
            raise Exception(f"Error al obtener médicos: {str(e)}")
    
    async def update_medico(self, medico_id: str, medico_data: MedicoUpdate) -> Optional[Medico]:
        """Actualizar un médico"""
        try:
            doc_ref = self.db.collection(self.medicos_collection).document(medico_id)
            
            # Obtener datos actuales
            doc = doc_ref.get()
            if not doc.exists:
                return None
            
            current_data = doc.to_dict()
            
            # Preparar datos de actualización (solo campos no None)
            update_data = {}
            for field, value in medico_data.model_dump().items():
                if value is not None:
                    update_data[field] = value
            
            # Si se actualiza el email, también actualizar en Firebase Auth
            if 'email' in update_data and 'firebase_uid' in current_data:
                try:
                    auth.update_user(
                        current_data['firebase_uid'],
                        email=update_data['email']
                    )
                except Exception as e:
                    raise Exception(f"Error al actualizar email en Firebase Auth: {str(e)}")
            
            # Si se actualiza el nombre o apellido, actualizar display_name en Firebase Auth
            if ('nombre' in update_data or 'apellido' in update_data) and 'firebase_uid' in current_data:
                try:
                    new_nombre = update_data.get('nombre', current_data.get('nombre', ''))
                    new_apellido = update_data.get('apellido', current_data.get('apellido', ''))
                    display_name = f"{new_nombre} {new_apellido}".strip()
                    
                    auth.update_user(
                        current_data['firebase_uid'],
                        display_name=display_name
                    )
                except Exception as e:
                    raise Exception(f"Error al actualizar nombre en Firebase Auth: {str(e)}")
            
            # Actualizar en Firestore
            doc_ref.update(update_data)
            
            # Obtener documento actualizado
            updated_doc = doc_ref.get()
            data = updated_doc.to_dict()
            data['id'] = updated_doc.id
            
            return Medico(**data)
            
        except Exception as e:
            raise Exception(f"Error al actualizar médico: {str(e)}")
    
    async def delete_medico(self, medico_id: str) -> bool:
        """Eliminar un médico y su usuario de Firebase Auth"""
        try:
            doc_ref = self.db.collection(self.medicos_collection).document(medico_id)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                
                # Eliminar usuario de Firebase Auth si existe
                if 'firebase_uid' in data:
                    try:
                        auth.delete_user(data['firebase_uid'])
                    except Exception as e:
                        # Log el error pero continuar con la eliminación del documento
                        print(f"Error al eliminar usuario de Firebase Auth: {str(e)}")
                
                # Eliminar documento de Firestore
                doc_ref.delete()
                return True
            else:
                return False
                
        except Exception as e:
            raise Exception(f"Error al eliminar médico: {str(e)}")
    
    async def search_medicos_by_cargo(self, cargo: CargoMedico) -> List[Medico]:
        """Buscar médicos por cargo"""
        try:
            docs = self.db.collection(self.medicos_collection).where('cargo', '==', cargo.value).stream()
            medicos = []
            
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                medicos.append(Medico(**data))
            
            return medicos
            
        except Exception as e:
            raise Exception(f"Error al buscar médicos por cargo: {str(e)}")
    
    async def search_medicos_by_dni(self, dni: str) -> Optional[Medico]:
        """Buscar médico por DNI"""
        try:
            docs = self.db.collection(self.medicos_collection).where('dni', '==', dni).limit(1).stream()
            
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                return Medico(**data)
            
            return None
            
        except Exception as e:
            raise Exception(f"Error al buscar médico por DNI: {str(e)}")
    
    async def search_medicos_by_email(self, email: str) -> Optional[Medico]:
        """Buscar médico por email"""
        try:
            docs = self.db.collection(self.medicos_collection).where('email', '==', email).limit(1).stream()
            
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                return Medico(**data)
            
            return None
            
        except Exception as e:
            raise Exception(f"Error al buscar médico por email: {str(e)}") 