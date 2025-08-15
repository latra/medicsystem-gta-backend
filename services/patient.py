from services.firestore import FirestoreService
from schemas import Patient, VisitStatus, PatientCreate, PatientUpdate, PatientAdmitted
from services.visits import VisitService

class PatientService(FirestoreService):
    def __init__(self):
        super().__init__()
        self.patients_collection = "patients"
        self.visit_service = VisitService()

    def get_whole_patient(self, patient_dni: str):
        doc = self.db.collection(self.patients_collection).document(patient_dni).get()
        if doc.exists:
            return PatientCreate(**doc.to_dict())
        return None

    def get_patient(self, patient_dni: str):
        doc = self.db.collection(self.patients_collection).document(patient_dni).get()
        if doc.exists and doc.to_dict()["enabled"]:
            return Patient(**doc.to_dict())
        return None
    
    def create_patient(self, patient: Patient):
        patient_db: Patient = PatientCreate(enabled=True, disabled_by="", **patient.model_dump())
        self.db.collection(self.patients_collection).document(patient.dni).set(patient_db.model_dump())
        return patient_db

    def update_patient(self, patient_dni: str, patient_update: PatientUpdate):
        patient = self.get_whole_patient(patient_dni)
        for field in patient_update.model_dump().keys():
            print(field)
            value = getattr(patient_update, field)
            if value is not None:
                setattr(patient, field, value)

        self.db.collection(self.patients_collection).document(patient_dni).set(patient.model_dump())

    def delete_patient(self, patient_dni: str, disabled_by: str):
        patient = self.get_whole_patient(patient_dni)
        patient.enabled = False
        patient.disabled_by = disabled_by
        self.db.collection(self.patients_collection).document(patient_dni).set(patient.model_dump())

    def get_all_patients(self):
        docs = self.db.collection(self.patients_collection).get()
        return [Patient(**doc.to_dict()) for doc in docs if doc.to_dict()["enabled"]]

    def get_all_patients_by_dni(self, dni: str):
        docs = self.db.collection(self.patients_collection).where("dni", "==", dni).get()
        return [Patient(**doc.to_dict()) for doc in docs if doc.to_dict()["enabled"]]

    def get_all_patients_by_name(self, name: str):
        docs = self.db.collection(self.patients_collection).where("name", ">=", name.lower()).where("name", "<=", name.lower() + '\uf8ff').get()
        return [Patient(**doc.to_dict()) for doc in docs if doc.to_dict()["enabled"]]

    def get_admitted_patients(self):
        """
        Get all patients who have at least one visit with status ADMISSION
        """
        # Get all visits with ADMISSION status
        admitted_visits = self.visit_service.get_all_visits_by_status(VisitStatus.ADMISSION)
        admitted_patients: list[PatientAdmitted] = []
        for visit in admitted_visits:
            patient = self.get_patient(visit.patient_dni)
            admitted_patients.append(PatientAdmitted(name=patient.name, dni=patient.dni, visit_id=visit.visit_id, reason=visit.reason, attention_type=visit.attention_type, triage=visit.triage, doctor_dni=visit.doctor_dni, doctor_name=visit.doctor_name))
        
        return admitted_patients