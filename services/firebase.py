from firebase_admin import auth, credentials, initialize_app
from config import Config


class FirebaseService:
    def __init__(self, credentials_path: str):
        self.cred = credentials.Certificate(credentials_path)
        self.app = initialize_app(self.cred)

    def verify_token(self, token: str):
        try:
            decoded_token = auth.verify_id_token(token)
            return decoded_token
        except Exception as e:
            print(f"Error al verificar token de Firebase: {e}")