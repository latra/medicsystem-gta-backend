import firebase_admin
from firebase_admin import firestore
from typing import List, Optional
from models import Paciente, PacienteCreate, PacienteUpdate

class PacienteService:
    def __init__(self):
        """Initialize Firestore client"""
        if not firebase_admin._apps:
            # Initialize Firebase Admin SDK if not already initialized
            firebase_admin.initialize_app()
        
        self.db = firestore.client()
        self.pacientes_collection = "pacientes"
    
    async def create_paciente(self, paciente_data: PacienteCreate) -> Paciente:
        """Crear un nuevo paciente en Firestore"""
        try:
            # Convertir el modelo a dict
            paciente_dict = paciente_data.model_dump()
            
            # Crear documento en Firestore
            doc_ref = self.db.collection(self.pacientes_collection).document()
            paciente_dict['id'] = doc_ref.id
            
            # Guardar en Firestore
            doc_ref.set(paciente_dict)
            
            return Paciente(**paciente_dict)
            
        except Exception as e:
            raise Exception(f"Error al crear paciente: {str(e)}")
    
    async def get_paciente(self, paciente_dni: str) -> Optional[Paciente]:
        """Obtener un paciente por DNI"""
        try:
            docs = self.db.collection(self.pacientes_collection).where('dni', '==', paciente_dni).limit(1).stream()
            
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                return Paciente(**data)
            
            return None
                
        except Exception as e:
            raise Exception(f"Error al obtener paciente: {str(e)}")
    
    async def get_paciente_by_id(self, paciente_id: str) -> Optional[Paciente]:
        """Obtener un paciente por ID"""
        try:
            doc_ref = self.db.collection(self.pacientes_collection).document(paciente_id)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                return Paciente(**data)
            else:
                return None
                
        except Exception as e:
            raise Exception(f"Error al obtener paciente: {str(e)}")
    
    async def get_all_pacientes(self) -> List[Paciente]:
        """Obtener todos los pacientes"""
        try:
            docs = self.db.collection(self.pacientes_collection).stream()
            pacientes = []
            
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                pacientes.append(Paciente(**data))
            
            return pacientes
            
        except Exception as e:
            raise Exception(f"Error al obtener pacientes: {str(e)}")
    
    async def update_paciente(self, paciente_dni: str, paciente_data: PacienteUpdate) -> Optional[Paciente]:
        """Actualizar un paciente por DNI"""
        try:
            # Buscar el documento por DNI
            docs = self.db.collection(self.pacientes_collection).where('dni', '==', paciente_dni).limit(1).stream()
            
            doc_ref = None
            for doc in docs:
                doc_ref = doc.reference
                break
            
            if doc_ref is None:
                return None
            
            # Preparar datos de actualización (solo campos no None)
            update_data = {}
            for field, value in paciente_data.model_dump().items():
                if value is not None:
                    update_data[field] = value
            
            # Actualizar en Firestore
            doc_ref.update(update_data)
            
            # Obtener documento actualizado
            updated_doc = doc_ref.get()
            data = updated_doc.to_dict()
            data['id'] = updated_doc.id
            
            return Paciente(**data)
            
        except Exception as e:
            raise Exception(f"Error al actualizar paciente: {str(e)}")
    
    async def update_paciente_by_id(self, paciente_id: str, paciente_data: PacienteUpdate) -> Optional[Paciente]:
        """Actualizar un paciente por ID"""
        try:
            doc_ref = self.db.collection(self.pacientes_collection).document(paciente_id)
            
            # Obtener datos actuales
            doc = doc_ref.get()
            if not doc.exists:
                return None
            
            # Preparar datos de actualización (solo campos no None)
            update_data = {}
            for field, value in paciente_data.model_dump().items():
                if value is not None:
                    update_data[field] = value
            
            # Actualizar en Firestore
            doc_ref.update(update_data)
            
            # Obtener documento actualizado
            updated_doc = doc_ref.get()
            data = updated_doc.to_dict()
            data['id'] = updated_doc.id
            
            return Paciente(**data)
            
        except Exception as e:
            raise Exception(f"Error al actualizar paciente: {str(e)}")
    
    async def delete_paciente(self, paciente_dni: str) -> bool:
        """Eliminar un paciente por DNI"""
        try:
            # Buscar el documento por DNI
            docs = self.db.collection(self.pacientes_collection).where('dni', '==', paciente_dni).limit(1).stream()
            
            for doc in docs:
                doc.reference.delete()
                return True
            
            return False
                
        except Exception as e:
            raise Exception(f"Error al eliminar paciente: {str(e)}")
    
    async def delete_paciente_by_id(self, paciente_id: str) -> bool:
        """Eliminar un paciente por ID"""
        try:
            doc_ref = self.db.collection(self.pacientes_collection).document(paciente_id)
            doc = doc_ref.get()
            
            if doc.exists:
                doc_ref.delete()
                return True
            else:
                return False
                
        except Exception as e:
            raise Exception(f"Error al eliminar paciente: {str(e)}")
    
    async def search_pacientes_by_dni(self, dni: str) -> Optional[Paciente]:
        """Buscar paciente por DNI"""
        try:
            docs = self.db.collection(self.pacientes_collection).where('dni', '==', dni).limit(1).stream()
            
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                return Paciente(**data)
            
            return None
            
        except Exception as e:
            raise Exception(f"Error al buscar paciente por DNI: {str(e)}")
    
    async def search_pacientes_by_nombre(self, nombre: str) -> List[Paciente]:
        """Buscar pacientes por nombre (búsqueda parcial)"""
        try:
            # Obtener todos los pacientes y filtrar por nombre
            docs = self.db.collection(self.pacientes_collection).stream()
            pacientes = []
            
            for doc in docs:
                data = doc.to_dict()
                # Búsqueda case-insensitive
                if nombre.lower() in data.get('nombre', '').lower():
                    data['id'] = doc.id
                    pacientes.append(Paciente(**data))
            
            return pacientes
            
        except Exception as e:
            raise Exception(f"Error al buscar pacientes por nombre: {str(e)}")
    
    async def search_pacientes_by_apellido(self, apellido: str) -> List[Paciente]:
        """Buscar pacientes por apellido (búsqueda parcial)"""
        try:
            # Obtener todos los pacientes y filtrar por apellido
            docs = self.db.collection(self.pacientes_collection).stream()
            pacientes = []
            
            for doc in docs:
                data = doc.to_dict()
                # Búsqueda case-insensitive
                if apellido.lower() in data.get('apellido', '').lower():
                    data['id'] = doc.id
                    pacientes.append(Paciente(**data))
            
            return pacientes
            
        except Exception as e:
            raise Exception(f"Error al buscar pacientes por apellido: {str(e)}")
    
    async def search_pacientes_by_nombre_completo(self, nombre_completo: str) -> List[Paciente]:
        """Buscar pacientes por nombre completo (búsqueda parcial)"""
        try:
            # Obtener todos los pacientes y filtrar por nombre completo
            docs = self.db.collection(self.pacientes_collection).stream()
            pacientes = []
            
            for doc in docs:
                data = doc.to_dict()
                nombre = data.get('nombre', '')
                apellido = data.get('apellido', '')
                nombre_completo_paciente = f"{nombre} {apellido}".strip()
                
                # Búsqueda case-insensitive
                if nombre_completo.lower() in nombre_completo_paciente.lower():
                    data['id'] = doc.id
                    pacientes.append(Paciente(**data))
            
            return pacientes
            
        except Exception as e:
            raise Exception(f"Error al buscar pacientes por nombre completo: {str(e)}") 