from services.firestore import FirestoreService
from models.patient import PatientDB, BloodAnalysis, RadiologyStudy, MedicalHistory
from schemas import (
    Patient, PatientCreate, PatientUpdate, PatientAdmitted, PatientComplete,
    PatientSummary, PatientMedicalHistoryUpdate, BloodAnalysisCreate, BloodAnalysisResponse,
    RadiologyStudyCreate, RadiologyStudyResponse, MedicalHistoryResponse,
    PatientSearchFilters, VisitStatus
)
from services.visits import VisitService
from firebase_admin import firestore
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PatientRepository(FirestoreService):
    """Repositorio para operaciones de base de datos de pacientes"""
    
    def __init__(self):
        super().__init__()
        self.patients_collection = "patients"
    
    def _document_to_patient_db(self, doc) -> Optional[PatientDB]:
        """Convierte un documento de Firestore a PatientDB"""
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
            
            return PatientDB(**data)
        except Exception as e:
            logger.error(f"Error converting document to PatientDB: {e}")
            return None
    
    def get_by_dni(self, dni: str) -> Optional[PatientDB]:
        """Obtiene un paciente por DNI"""
        try:
            doc = self.db.collection(self.patients_collection).document(dni).get()
            return self._document_to_patient_db(doc)
        except Exception as e:
            logger.error(f"Error getting patient by DNI {dni}: {e}")
            return None
    
    def create(self, patient_db: PatientDB) -> bool:
        """Crea un nuevo paciente"""
        try:
            # Convertir el modelo a diccionario con timestamps como strings ISO
            patient_dict = patient_db.model_dump()
            for field in ['created_at', 'updated_at']:
                if field in patient_dict and isinstance(patient_dict[field], datetime):
                    patient_dict[field] = patient_dict[field].isoformat()
            
            # También convertir timestamps en historial médico
            if 'medical_history' in patient_dict:
                medical_history = patient_dict['medical_history']
                if 'last_updated' in medical_history and isinstance(medical_history['last_updated'], datetime):
                    medical_history['last_updated'] = medical_history['last_updated'].isoformat()
                
                # Convertir timestamps en análisis de sangre
                for analysis in medical_history.get('blood_analyses', []):
                    if 'date_performed' in analysis and isinstance(analysis['date_performed'], datetime):
                        analysis['date_performed'] = analysis['date_performed'].isoformat()
                
                # Convertir timestamps en estudios radiológicos
                for study in medical_history.get('radiology_studies', []):
                    if 'date_performed' in study and isinstance(study['date_performed'], datetime):
                        study['date_performed'] = study['date_performed'].isoformat()
            
            self.db.collection(self.patients_collection).document(patient_db.dni).set(patient_dict)
            logger.info(f"Patient {patient_db.dni} created successfully")
            return True
        except Exception as e:
            logger.error(f"Error creating patient {patient_db.dni}: {e}")
            return False
    
    def update(self, patient_db: PatientDB) -> bool:
        """Actualiza un paciente existente"""
        try:
            # Actualizar timestamp
            patient_db.update_timestamp()
            
            # Convertir a diccionario con manejo de timestamps
            patient_dict = patient_db.model_dump()
            for field in ['created_at', 'updated_at']:
                if field in patient_dict and isinstance(patient_dict[field], datetime):
                    patient_dict[field] = patient_dict[field].isoformat()
            
            # Manejar timestamps en historial médico
            if 'medical_history' in patient_dict:
                medical_history = patient_dict['medical_history']
                if 'last_updated' in medical_history and isinstance(medical_history['last_updated'], datetime):
                    medical_history['last_updated'] = medical_history['last_updated'].isoformat()
                
                for analysis in medical_history.get('blood_analyses', []):
                    if 'date_performed' in analysis and isinstance(analysis['date_performed'], datetime):
                        analysis['date_performed'] = analysis['date_performed'].isoformat()
                
                for study in medical_history.get('radiology_studies', []):
                    if 'date_performed' in study and isinstance(study['date_performed'], datetime):
                        study['date_performed'] = study['date_performed'].isoformat()
            
            self.db.collection(self.patients_collection).document(patient_db.dni).set(patient_dict)
            logger.info(f"Patient {patient_db.dni} updated successfully")
            return True
        except Exception as e:
            logger.error(f"Error updating patient {patient_db.dni}: {e}")
            return False
    
    def get_all_enabled(self) -> List[PatientDB]:
        """Obtiene todos los pacientes habilitados"""
        try:
            docs = self.db.collection(self.patients_collection).where("enabled", "==", True).get()
            patients = []
            for doc in docs:
                patient = self._document_to_patient_db(doc)
                if patient:
                    patients.append(patient)
            return patients
        except Exception as e:
            logger.error(f"Error getting all enabled patients: {e}")
            return []
    
    def search_by_name(self, name: str) -> List[PatientDB]:
        """Busca pacientes por nombre"""
        try:
            name_lower = name.lower()
            docs = self.db.collection(self.patients_collection)\
                .where("enabled", "==", True)\
                .where("name", ">=", name_lower)\
                .where("name", "<=", name_lower + '\uf8ff')\
                .get()
            
            patients = []
            for doc in docs:
                patient = self._document_to_patient_db(doc)
                if patient:
                    patients.append(patient)
            return patients
        except Exception as e:
            logger.error(f"Error searching patients by name {name}: {e}")
            return []


class PatientService:
    """Servicio principal para gestión de pacientes"""
    
    def __init__(self):
        self.repository = PatientRepository()
        # Evitar import circular usando lazy import
        self._visit_service = None
    
    @property
    def visit_service(self):
        """Lazy loading del visit service para evitar imports circulares"""
        if self._visit_service is None:
            from services.visits import VisitService
            self._visit_service = VisitService()
        return self._visit_service
    
    def _patient_db_to_patient(self, patient_db: PatientDB) -> Patient:
        """Convierte PatientDB a esquema Patient (sin historial completo)"""
        return Patient(
            name=patient_db.name,
            dni=patient_db.dni,
            age=patient_db.age,
            sex=patient_db.sex,
            phone=patient_db.phone,
            blood_type=patient_db.blood_type,
            created_at=patient_db.created_at,
            updated_at=patient_db.updated_at
        )
    
    def _patient_db_to_complete(self, patient_db: PatientDB) -> PatientComplete:
        """Convierte PatientDB a esquema PatientComplete (con historial completo)"""
        # Convertir análisis de sangre
        blood_analyses = [
            BloodAnalysisResponse(
                analysis_id=analysis.analysis_id,
                date_performed=analysis.date_performed,
                red_blood_cells=analysis.red_blood_cells,
                hemoglobin=analysis.hemoglobin,
                hematocrit=analysis.hematocrit,
                platelets=analysis.platelets,
                lymphocytes=analysis.lymphocytes,
                glucose=analysis.glucose,
                cholesterol=analysis.cholesterol,
                urea=analysis.urea,
                cocaine=analysis.cocaine,
                alcohol=analysis.alcohol,
                mdma=analysis.mdma,
                fentanyl=analysis.fentanyl,
                performed_by_dni=analysis.performed_by_dni,
                performed_by_name=analysis.performed_by_name,
                notes=analysis.notes,
                visit_related_id=analysis.visit_related_id
            ) for analysis in patient_db.medical_history.blood_analyses
        ]
        
        # Convertir estudios radiológicos
        radiology_studies = [
            RadiologyStudyResponse(
                study_id=study.study_id,
                date_performed=study.date_performed,
                study_type=study.study_type,
                body_part=study.body_part,
                findings=study.findings,
                image_url=study.image_url,
                performed_by_dni=study.performed_by_dni,
                performed_by_name=study.performed_by_name,
                visit_related_id=study.visit_related_id
            ) for study in patient_db.medical_history.radiology_studies
        ]
        
        # Crear historial médico completo
        medical_history = MedicalHistoryResponse(
            allergies=patient_db.medical_history.allergies,
            medical_notes=patient_db.medical_history.medical_notes,
            major_surgeries=patient_db.medical_history.major_surgeries,
            current_medications=patient_db.medical_history.current_medications,
            chronic_conditions=patient_db.medical_history.chronic_conditions,
            family_history=patient_db.medical_history.family_history,
            blood_analyses=blood_analyses,
            radiology_studies=radiology_studies,
            last_updated=patient_db.medical_history.last_updated,
            updated_by=patient_db.medical_history.updated_by
        )
        
        return PatientComplete(
            name=patient_db.name,
            dni=patient_db.dni,
            age=patient_db.age,
            sex=patient_db.sex,
            phone=patient_db.phone,
            blood_type=patient_db.blood_type,
            created_at=patient_db.created_at,
            updated_at=patient_db.updated_at,
            medical_history=medical_history,
            created_by=patient_db.created_by,
            last_updated_by=patient_db.last_updated_by
        )
    
    def get_patient(self, patient_dni: str) -> Optional[Patient]:
        """Obtiene un paciente básico por DNI"""
        patient_db = self.repository.get_by_dni(patient_dni)
        if patient_db and patient_db.enabled:
            return self._patient_db_to_patient(patient_db)
        return None
    
    def get_patient_complete(self, patient_dni: str) -> Optional[PatientComplete]:
        """Obtiene un paciente completo con historial médico por DNI"""
        patient_db = self.repository.get_by_dni(patient_dni)
        if patient_db and patient_db.enabled:
            return self._patient_db_to_complete(patient_db)
        return None
    
    def create_patient(self, patient_create: PatientCreate, created_by: Optional[str] = None) -> Optional[Patient]:
        """Crea un nuevo paciente"""
        # Verificar si ya existe
        existing_patient = self.repository.get_by_dni(patient_create.dni)
        if existing_patient:
            logger.warning(f"Patient with DNI {patient_create.dni} already exists")
            return None
        
        # Crear historial médico inicial
        medical_history = MedicalHistory(
            allergies=patient_create.allergies,
            medical_notes=patient_create.medical_notes,
            major_surgeries=patient_create.major_surgeries,
            current_medications=patient_create.current_medications,
            chronic_conditions=patient_create.chronic_conditions,
            family_history=patient_create.family_history
        )
        
        # Crear paciente en BD
        patient_db = PatientDB(
            dni=patient_create.dni,
            name=patient_create.name,
            age=patient_create.age,
            sex=patient_create.sex,
            phone=patient_create.phone,
            blood_type=patient_create.blood_type,
            medical_history=medical_history,
            created_by=created_by
        )
        
        if self.repository.create(patient_db):
            return self._patient_db_to_patient(patient_db)
        return None
    
    def update_patient_basic(self, patient_dni: str, patient_update: PatientUpdate, updated_by: Optional[str] = None) -> Optional[Patient]:
        """Actualiza información básica del paciente"""
        patient_db = self.repository.get_by_dni(patient_dni)
        if not patient_db or not patient_db.enabled:
            return None
        
        # Actualizar campos básicos
        update_data = patient_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(patient_db, field, value)
        
        patient_db.update_timestamp(updated_by)
        
        if self.repository.update(patient_db):
            return self._patient_db_to_patient(patient_db)
        return None
    
    def update_medical_history(self, patient_dni: str, medical_update: PatientMedicalHistoryUpdate, updated_by: Optional[str] = None) -> Optional[MedicalHistoryResponse]:
        """Actualiza el historial médico del paciente"""
        patient_db = self.repository.get_by_dni(patient_dni)
        if not patient_db or not patient_db.enabled:
            return None
        
        # Actualizar campos del historial médico
        update_data = medical_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(patient_db.medical_history, field, value)
        
        patient_db.medical_history.last_updated = datetime.now()
        patient_db.medical_history.updated_by = updated_by
        patient_db.update_timestamp(updated_by)
        
        if self.repository.update(patient_db):
            complete_patient = self._patient_db_to_complete(patient_db)
            return complete_patient.medical_history
        return None
    
    def add_blood_analysis(self, patient_dni: str, analysis_data: BloodAnalysisCreate, performed_by_dni: Optional[str] = None, performed_by_name: Optional[str] = None, visit_id: Optional[str] = None) -> Optional[BloodAnalysisResponse]:
        """Añade un análisis de sangre al paciente"""
        patient_db = self.repository.get_by_dni(patient_dni)
        if not patient_db or not patient_db.enabled:
            return None
        
        # Crear análisis de sangre
        analysis = BloodAnalysis(
            red_blood_cells=analysis_data.red_blood_cells,
            hemoglobin=analysis_data.hemoglobin,
            hematocrit=analysis_data.hematocrit,
            platelets=analysis_data.platelets,
            lymphocytes=analysis_data.lymphocytes,
            glucose=analysis_data.glucose,
            cholesterol=analysis_data.cholesterol,
            urea=analysis_data.urea,
            cocaine=analysis_data.cocaine,
            alcohol=analysis_data.alcohol,
            mdma=analysis_data.mdma,
            fentanyl=analysis_data.fentanyl,
            notes=analysis_data.notes,
            performed_by_dni=performed_by_dni,
            performed_by_name=performed_by_name
        )
        
        patient_db.add_blood_analysis(analysis, visit_id)
        
        if self.repository.update(patient_db):
            return BloodAnalysisResponse(
                analysis_id=analysis.analysis_id,
                date_performed=analysis.date_performed,
                red_blood_cells=analysis.red_blood_cells,
                hemoglobin=analysis.hemoglobin,
                hematocrit=analysis.hematocrit,
                platelets=analysis.platelets,
                lymphocytes=analysis.lymphocytes,
                glucose=analysis.glucose,
                cholesterol=analysis.cholesterol,
                urea=analysis.urea,
                cocaine=analysis.cocaine,
                alcohol=analysis.alcohol,
                mdma=analysis.mdma,
                fentanyl=analysis.fentanyl,
                performed_by_dni=analysis.performed_by_dni,
                performed_by_name=analysis.performed_by_name,
                notes=analysis.notes,
                visit_related_id=analysis.visit_related_id
            )
        return None
    
    def add_radiology_study(self, patient_dni: str, study_data: RadiologyStudyCreate, performed_by_dni: Optional[str] = None, performed_by_name: Optional[str] = None, visit_id: Optional[str] = None) -> Optional[RadiologyStudyResponse]:
        """Añade un estudio radiológico al paciente"""
        patient_db = self.repository.get_by_dni(patient_dni)
        if not patient_db or not patient_db.enabled:
            return None
        
        # Crear estudio radiológico
        study = RadiologyStudy(
            study_type=study_data.study_type,
            body_part=study_data.body_part,
            findings=study_data.findings,
            image_url=study_data.image_url,
            performed_by_dni=performed_by_dni,
            performed_by_name=performed_by_name
        )
        
        patient_db.add_radiology_study(study, visit_id)
        
        if self.repository.update(patient_db):
            return RadiologyStudyResponse(
                study_id=study.study_id,
                date_performed=study.date_performed,
                study_type=study.study_type,
                body_part=study.body_part,
                findings=study.findings,
                image_url=study.image_url,
                performed_by_dni=study.performed_by_dni,
                performed_by_name=study.performed_by_name,
                visit_related_id=study.visit_related_id
            )
        return None
    
    def delete_patient(self, patient_dni: str, disabled_by: str) -> bool:
        """Deshabilita un paciente (soft delete)"""
        patient_db = self.repository.get_by_dni(patient_dni)
        if not patient_db:
            return False
        
        patient_db.enabled = False
        patient_db.disabled_by = disabled_by
        patient_db.update_timestamp(disabled_by)
        
        return self.repository.update(patient_db)
    
    def get_all_patients(self) -> List[PatientSummary]:
        """Obtiene todos los pacientes habilitados como resumen"""
        patients_db = self.repository.get_all_enabled()
        
        # TODO: Obtener fecha de última visita para cada paciente
        summaries = []
        for patient_db in patients_db:
            summaries.append(PatientSummary(
                name=patient_db.name,
                dni=patient_db.dni,
                age=patient_db.age,
                sex=patient_db.sex,
                blood_type=patient_db.blood_type,
                last_visit=None  # TODO: Implementar consulta de última visita
            ))
        
        return summaries
    
    def search_patients(self, name: str) -> List[PatientSummary]:
        """Busca pacientes por nombre"""
        patients_db = self.repository.search_by_name(name)
        
        summaries = []
        for patient_db in patients_db:
            summaries.append(PatientSummary(
                name=patient_db.name,
                dni=patient_db.dni,
                age=patient_db.age,
                sex=patient_db.sex,
                blood_type=patient_db.blood_type,
                last_visit=None  # TODO: Implementar consulta de última visita
            ))
        
        return summaries
    
    def get_admitted_patients(self) -> List[PatientAdmitted]:
        """Obtiene todos los pacientes admitidos"""
        admitted_visits = self.visit_service.get_all_visits_by_status(VisitStatus.ADMISSION)
        admitted_patients = []
        
        for visit in admitted_visits:
            patient = self.get_patient(visit.patient_dni)
            if patient:
                admitted_patients.append(PatientAdmitted(
                    name=patient.name,
                    dni=patient.dni,
                    visit_id=visit.visit_id,
                    reason=visit.reason,
                    attention_place=visit.attention_place,
                    attention_details=visit.attention_details,
                    triage=visit.triage,
                    doctor_dni=visit.doctor_dni,
                    doctor_name=visit.doctor_name,
                    admission_date=visit.created_at
                ))
        
        return admitted_patients