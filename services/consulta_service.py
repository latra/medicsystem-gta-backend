import firebase_admin
from firebase_admin import firestore
from typing import List, Optional
from datetime import datetime
from models import Consulta, ConsultaCreate, ConsultaUpdate

class ConsultaService:
    def __init__(self):
        """Initialize Firestore client"""
        if not firebase_admin._apps:
            # Initialize Firebase Admin SDK if not already initialized
            firebase_admin.initialize_app()
        
        self.db = firestore.client()
        self.consultas_collection = "consultas"
    
    async def create_consulta(self, consulta_data: ConsultaCreate, medico_dni: str, medico_nombre: str, medico_apellido: str) -> Consulta:
        """Crear una nueva consulta en Firestore"""
        try:
            # Convertir el modelo a dict
            consulta_dict = consulta_data.model_dump()
            
            # Agregar timestamp de creación
            consulta_dict['fecha_creacion'] = datetime.now()
            
            consulta_dict['medico_nombre'] = medico_nombre
            consulta_dict['medico_apellido'] = medico_apellido
            consulta_dict['medico_dni'] = medico_dni

            # Crear documento en Firestore
            doc_ref = self.db.collection(self.consultas_collection).document()
            consulta_dict['id'] = doc_ref.id
            
            # Guardar en Firestore
            doc_ref.set(consulta_dict)
            
            return Consulta(**consulta_dict)
            
        except Exception as e:
            raise Exception(f"Error al crear consulta: {str(e)}")
    
    async def get_consulta(self, consulta_id: str) -> Optional[Consulta]:
        """Obtener una consulta por ID"""
        try:
            doc_ref = self.db.collection(self.consultas_collection).document(consulta_id)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                # Convertir timestamp de Firestore a datetime
                if 'fecha_creacion' in data:
                    data['fecha_creacion'] = data['fecha_creacion'].replace(tzinfo=None)
                return Consulta(**data)
            else:
                return None
                
        except Exception as e:
            raise Exception(f"Error al obtener consulta: {str(e)}")
    
    async def get_all_consultas(self) -> List[Consulta]:
        """Obtener todas las consultas"""
        try:
            docs = self.db.collection(self.consultas_collection).order_by('fecha_creacion', direction=firestore.Query.DESCENDING).stream()
            consultas = []
            
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                # Convertir timestamp de Firestore a datetime
                if 'fecha_creacion' in data:
                    data['fecha_creacion'] = data['fecha_creacion'].replace(tzinfo=None)
                consultas.append(Consulta(**data))
            
            return consultas
            
        except Exception as e:
            raise Exception(f"Error al obtener consultas: {str(e)}")
    
    async def get_consultas_by_paciente_dni(self, paciente_dni: str) -> List[Consulta]:
        """Obtener todas las consultas de un paciente por DNI"""
        try:
            docs = self.db.collection(self.consultas_collection).where('paciente_dni', '==', paciente_dni).order_by('fecha_creacion', direction=firestore.Query.DESCENDING).stream()
            consultas = []
            
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                # Convertir timestamp de Firestore a datetime
                if 'fecha_creacion' in data:
                    data['fecha_creacion'] = data['fecha_creacion'].replace(tzinfo=None)
                consultas.append(Consulta(**data))
            
            return consultas
            
        except Exception as e:
            raise Exception(f"Error al obtener consultas del paciente: {str(e)}")
    
    async def get_consultas_by_medico_dni(self, medico_dni: str) -> List[Consulta]:
        """Obtener todas las consultas realizadas por un médico por DNI"""
        try:
            docs = self.db.collection(self.consultas_collection).where('medico_dni', '==', medico_dni).order_by('fecha_creacion', direction=firestore.Query.DESCENDING).stream()
            consultas = []
            
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                # Convertir timestamp de Firestore a datetime
                if 'fecha_creacion' in data:
                    data['fecha_creacion'] = data['fecha_creacion'].replace(tzinfo=None)
                consultas.append(Consulta(**data))
            
            return consultas
            
        except Exception as e:
            raise Exception(f"Error al obtener consultas del médico: {str(e)}")
    
    async def update_consulta(self, consulta_id: str, consulta_data: ConsultaUpdate) -> Optional[Consulta]:
        """Actualizar una consulta"""
        try:
            doc_ref = self.db.collection(self.consultas_collection).document(consulta_id)
            
            # Obtener datos actuales
            doc = doc_ref.get()
            if not doc.exists:
                return None
            
            # Preparar datos de actualización (solo campos no None)
            update_data = {}
            for field, value in consulta_data.model_dump().items():
                if value is not None:
                    update_data[field] = value
            
            # Actualizar en Firestore
            doc_ref.update(update_data)
            
            # Obtener documento actualizado
            updated_doc = doc_ref.get()
            data = updated_doc.to_dict()
            data['id'] = updated_doc.id
            # Convertir timestamp de Firestore a datetime
            if 'fecha_creacion' in data:
                data['fecha_creacion'] = data['fecha_creacion'].replace(tzinfo=None)
            
            return Consulta(**data)
            
        except Exception as e:
            raise Exception(f"Error al actualizar consulta: {str(e)}")
    
    async def delete_consulta(self, consulta_id: str) -> bool:
        """Eliminar una consulta"""
        try:
            doc_ref = self.db.collection(self.consultas_collection).document(consulta_id)
            doc = doc_ref.get()
            
            if doc.exists:
                doc_ref.delete()
                return True
            else:
                return False
                
        except Exception as e:
            raise Exception(f"Error al eliminar consulta: {str(e)}")
    
    async def search_consultas_by_tipo_atencion(self, tipo_atencion: str) -> List[Consulta]:
        """Buscar consultas por tipo de atención"""
        try:
            docs = self.db.collection(self.consultas_collection).where('tipo_atencion', '==', tipo_atencion).order_by('fecha_creacion', direction=firestore.Query.DESCENDING).stream()
            consultas = []
            
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                # Convertir timestamp de Firestore a datetime
                if 'fecha_creacion' in data:
                    data['fecha_creacion'] = data['fecha_creacion'].replace(tzinfo=None)
                consultas.append(Consulta(**data))
            
            return consultas
            
        except Exception as e:
            raise Exception(f"Error al buscar consultas por tipo de atención: {str(e)}")
    
    async def get_consultas_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Consulta]:
        """Obtener consultas en un rango de fechas"""
        try:
            docs = self.db.collection(self.consultas_collection).where('fecha_creacion', '>=', start_date).where('fecha_creacion', '<=', end_date).order_by('fecha_creacion', direction=firestore.Query.DESCENDING).stream()
            consultas = []
            
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                # Convertir timestamp de Firestore a datetime
                if 'fecha_creacion' in data:
                    data['fecha_creacion'] = data['fecha_creacion'].replace(tzinfo=None)
                consultas.append(Consulta(**data))
            
            return consultas
            
        except Exception as e:
            raise Exception(f"Error al obtener consultas por rango de fechas: {str(e)}") 