"""
Servicio para gestión y verificación de índices de Firestore.
Este servicio se encarga de verificar que existan todos los índices necesarios
para las consultas de la aplicación y crearlos automáticamente si no existen.
"""

import json
import logging
from typing import Dict, List, Optional
from firebase_admin import firestore
from google.cloud.firestore_admin_v1 import FirestoreAdminClient
from google.cloud.firestore_admin_v1.types import Index, Field
from services.firestore import FirestoreService
import os

logger = logging.getLogger(__name__)

class FirestoreIndexService(FirestoreService):
    """Servicio para gestión de índices de Firestore"""
    
    def __init__(self):
        super().__init__()
        self.admin_client = None
        self.project_id = None
        self.database_name = "(default)"
        
        # Inicializar el cliente de administración
        try:
            # Obtener el project_id desde las credenciales
            firebase_credentials_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json")
            if os.path.exists(firebase_credentials_path):
                with open(firebase_credentials_path, 'r') as f:
                    credentials_data = json.load(f)
                    self.project_id = credentials_data.get('project_id')
            
            if self.project_id:
                self.admin_client = FirestoreAdminClient()
                logger.info(f"Firestore Admin Client initialized for project: {self.project_id}")
            else:
                logger.warning("Could not determine project_id from credentials")
        except Exception as e:
            logger.error(f"Error initializing Firestore Admin Client: {e}")
    
    def load_required_indexes(self) -> List[Dict]:
        """Carga los índices requeridos desde el archivo firestore.indexes.json"""
        try:
            indexes_file_path = "firestore.indexes.json"
            if not os.path.exists(indexes_file_path):
                logger.warning("firestore.indexes.json file not found")
                return []
            
            with open(indexes_file_path, 'r') as f:
                data = json.load(f)
                return data.get('indexes', [])
        except Exception as e:
            logger.error(f"Error loading required indexes: {e}")
            return []
    
    def get_parent_path(self) -> str:
        """Obtiene el path padre para las operaciones de administración"""
        return f"projects/{self.project_id}/databases/{self.database_name}"
    
    def get_existing_indexes(self) -> List[Index]:
        """Obtiene los índices existentes en Firestore"""
        try:
            if not self.admin_client or not self.project_id:
                logger.error("Admin client not properly initialized")
                return []
            
            parent = self.get_parent_path()
            indexes = list(self.admin_client.list_indexes(parent=parent))
            
            logger.info(f"Found {len(indexes)} existing indexes in Firestore")
            return indexes
        except Exception as e:
            logger.error(f"Error getting existing indexes: {e}")
            return []
    
    def index_exists(self, required_index: Dict, existing_indexes: List[Index]) -> bool:
        """Verifica si un índice requerido ya existe"""
        try:
            required_collection = required_index.get('collectionGroup')
            required_fields = required_index.get('fields', [])
            
            for existing_index in existing_indexes:
                # Verificar si es la misma colección
                if existing_index.collection_group != required_collection:
                    continue
                
                # Verificar si los campos coinciden
                if len(existing_index.fields) != len(required_fields):
                    continue
                
                fields_match = True
                for i, existing_field in enumerate(existing_index.fields):
                    if i >= len(required_fields):
                        fields_match = False
                        break
                    
                    required_field = required_fields[i]
                    
                    # Verificar nombre del campo
                    if existing_field.field_path != required_field.get('field_path'):
                        fields_match = False
                        break
                    
                    # Verificar orden (convertir a entero para comparación)
                    required_order = required_field.get('order', 'ASCENDING')
                    existing_order_int = existing_field.order
                    
                    # Convertir orden a entero para comparación
                    if required_order == 'ASCENDING' and existing_order_int != Field.Order.ASCENDING:
                        fields_match = False
                        break
                    elif required_order == 'DESCENDING' and existing_order_int != Field.Order.DESCENDING:
                        fields_match = False
                        break
                
                if fields_match:
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error checking if index exists: {e}")
            return False
    
    def create_index(self, index_definition: Dict) -> bool:
        """Crea un índice en Firestore"""
        try:
            if not self.admin_client or not self.project_id:
                logger.error("Admin client not properly initialized")
                return False
            
            # Construir el objeto Index
            fields = []
            for field_def in index_definition.get('fields', []):
                order = Field.Order.ASCENDING
                if field_def.get('order') == 'DESCENDING':
                    order = Field.Order.DESCENDING
                
                field = Field(
                    field_path=field_def.get('field_path'),
                    order=order
                )
                fields.append(field)
            
            index = Index(
                collection_group=index_definition.get('collectionGroup'),
                fields=fields,
                query_scope=Index.QueryScope.COLLECTION
            )
            
            # Crear el índice
            parent = self.get_parent_path()
            operation = self.admin_client.create_index(parent=parent, index=index)
            
            # Los índices se crean de forma asíncrona, pero podemos loggear el inicio
            logger.info(f"Started creating index for collection '{index_definition.get('collectionGroup')}' with fields: {[f.get('field_path') for f in index_definition.get('fields', [])]}")
            
            return True
        except Exception as e:
            logger.error(f"Error creating index: {e}")
            return False
    
    def verify_and_create_indexes(self) -> bool:
        """Verifica todos los índices requeridos y crea los que faltan"""
        try:
            if not self.admin_client or not self.project_id:
                logger.warning("Firestore Admin Client not available. Skipping index verification.")
                return True  # No fallar si no se puede verificar
            
            logger.info("Starting Firestore indexes verification...")
            
            # Cargar índices requeridos
            required_indexes = self.load_required_indexes()
            if not required_indexes:
                logger.warning("No required indexes found in configuration")
                return True
            
            # Obtener índices existentes
            existing_indexes = self.get_existing_indexes()
            
            # Verificar cada índice requerido
            indexes_created = 0
            indexes_already_exist = 0
            
            for required_index in required_indexes:
                collection_name = required_index.get('collectionGroup', 'unknown')
                field_names = [f.get('field_path') for f in required_index.get('fields', [])]
                
                if self.index_exists(required_index, existing_indexes):
                    logger.info(f"✓ Index already exists for '{collection_name}' with fields: {field_names}")
                    indexes_already_exist += 1
                else:
                    logger.info(f"✗ Index missing for '{collection_name}' with fields: {field_names}")
                    if self.create_index(required_index):
                        logger.info(f"✓ Started creating index for '{collection_name}' with fields: {field_names}")
                        indexes_created += 1
                    else:
                        logger.error(f"✗ Failed to create index for '{collection_name}' with fields: {field_names}")
            
            total_required = len(required_indexes)
            logger.info(f"Index verification completed:")
            logger.info(f"  - Total required: {total_required}")
            logger.info(f"  - Already existing: {indexes_already_exist}")
            logger.info(f"  - Created: {indexes_created}")
            
            if indexes_created > 0:
                logger.info("⚠️  Note: Index creation is asynchronous and may take a few minutes to complete.")
            
            return True
            
        except Exception as e:
            logger.error(f"Error during index verification and creation: {e}")
            return False
    
    def list_all_indexes(self) -> List[Dict]:
        """Lista todos los índices existentes (para debugging)"""
        try:
            existing_indexes = self.get_existing_indexes()
            indexes_info = []
            
            for index in existing_indexes:
                fields_info = []
                for field in index.fields:
                    order_str = "ASCENDING" if field.order == Field.Order.ASCENDING else "DESCENDING"
                    fields_info.append({
                        "field_path": field.field_path,
                        "order": order_str
                    })
                
                index_info = {
                    "collection_group": index.collection_group,
                    "fields": fields_info,
                    "state": index.state.name if index.state else "UNKNOWN"
                }
                indexes_info.append(index_info)
            
            return indexes_info
        except Exception as e:
            logger.error(f"Error listing indexes: {e}")
            return []

# Instancia global del servicio
firestore_index_service = FirestoreIndexService()
