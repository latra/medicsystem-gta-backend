from services.firestore import FirestoreService
from schemas import Doctor, DoctorCreate
from firebase_admin import auth

class DoctorService(FirestoreService):
    def __init__(self):
        super().__init__()
        self.doctors_collection = "doctors"

    def get_doctor(self, doctor_uid: str) -> Doctor:
        doc = self.db.collection(self.doctors_collection).where("firebase_uid", "==", doctor_uid).get()
        if doc:
            return Doctor(**doc[0].to_dict())
        return None

    def get_all_doctors(self):
        docs = self.db.collection(self.doctors_collection).get()
        return [Doctor(**doc.to_dict()) for doc in docs]

    def create_doctor(self, doctor: DoctorCreate) -> Doctor:
        doctor_dict = doctor.model_dump()
        doctor_dict["enabled"] = True
        doctor_dict["is_admin"] = False
        password = self._format_password(doctor_dict['dni'])
        try:
                user_record = auth.create_user(
                    email=doctor_dict['email'],
                    password=password,
                    display_name=f"{doctor_dict['name']}",
                    email_verified=False
                )
                
                # Agregar el UID de Firebase Auth al médico
                doctor_dict['firebase_uid'] = user_record.uid
                
        except auth.EmailAlreadyExistsError:
            raise Exception(f"Ya existe un usuario con el email {doctor_dict['email']}")
        except Exception as e:
            raise Exception(f"Error al crear usuario en Firebase Auth: {str(e)}")
            
        self.db.collection(self.doctors_collection).document(doctor.dni).set(doctor_dict)


        doctor = self.get_doctor(doctor_dict['firebase_uid'])
        
        return doctor
    
    def update_doctor(self, doctor: Doctor):
        self.db.collection(self.doctors_collection).document(doctor.dni).set(doctor.model_dump())

    def delete_doctor(self, doctor_dni: str):
        self.db.collection(self.doctors_collection).document(doctor_dni).delete()

    def _format_password(self, dni: str) -> str:
        if len(dni) < 6:
            return dni.zfill(6)
        return dni