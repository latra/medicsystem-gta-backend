from services.firestore import FirestoreService
from schemas import Visit, VisitStatus, VisitBase, VisitUpdate, VisitSummary, Doctor
from datetime import datetime
from services.doctor import DoctorService
import firebase_admin.firestore as firestore

class VisitService(FirestoreService):
    def __init__(self):
        super().__init__()
        self.visits_collection = "visits"
        self.doctor_service = DoctorService()

    def get_visit(self, visit_id: str):
        doc = self.db.collection(self.visits_collection).document(visit_id).get()
        if doc.exists:
            return Visit(**doc.to_dict())
        return None
    
    def create_visit(self, visit: VisitBase, doctor: Doctor):

        doc_ref = self.db.collection(self.visits_collection).document()
        visit_id = doc_ref.id
        
        # Create the visit object with the assigned ID and complete doctor information
        visit_created = Visit(
            visit_id=visit_id, 
            doctor_dni=doctor.dni, 
            doctor_name=doctor.name,
            doctor_email=doctor.email,
            doctor_specialty=doctor.specialty,
            visit_status=VisitStatus.ADMISSION, 
            date_of_admission=datetime.now(), 
            **visit.model_dump()
        )
        
        # Set the document data
        doc_ref.set(visit_created.model_dump())
        
        return visit_created

    def update_visit(self, visit_changes: VisitUpdate, visit: Visit):

        for field in visit_changes.model_dump().keys():
            print(field)
            value = getattr(visit_changes, field)
            if value is not None:
                setattr(visit, field, value)


        self.db.collection(self.visits_collection).document(visit.visit_id).set(visit.model_dump())
        return visit

    def delete_visit(self, visit_id: str):
        self.db.collection(self.visits_collection).document(visit_id).delete()

    def get_all_visits(self):
        docs = self.db.collection(self.visits_collection).get()
        return [Visit(**doc.to_dict()) for doc in docs]

    def get_all_visits_by_patient_dni(self, patient_dni: str) -> list[VisitSummary]:
        docs = self.db.collection(self.visits_collection).where("patient_dni", "==", patient_dni).order_by("date_of_admission", direction=firestore.Query.DESCENDING).get()
        return [VisitSummary(**doc.to_dict()) for doc in docs]

    def get_all_visits_by_doctor_dni(self, doctor_dni: str):
        docs = self.db.collection(self.visits_collection).where("doctor_dni", "==", doctor_dni).get()
        return [Visit(**doc.to_dict()) for doc in docs]

    def get_all_visits_by_status(self, status: VisitStatus):
        docs = self.db.collection(self.visits_collection).where("visit_status", "==", status).get()
        return [Visit(**doc.to_dict()) for doc in docs]
        
    def discharge_visit(self, visit_id: str):
        visit = self.get_visit(visit_id)
        if visit:
            visit.visit_status = VisitStatus.DISCHARGE
            visit.date_of_discharge = datetime.now()
            # Update the visit directly in Firestore
            self.db.collection(self.visits_collection).document(visit.visit_id).set(visit.model_dump())
            return visit
        return None