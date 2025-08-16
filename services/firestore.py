import firebase_admin
from firebase_admin import firestore, auth, credentials
import os

class FirestoreService:
    def __init__(self):
        """Initialize Firestore client"""
        if not firebase_admin._apps:
            firebase_credentials_path = os.getenv("FIREBASE_CREDENTIALS_PATH") if os.getenv("FIREBASE_CREDENTIALS_PATH") else "firebase-credentials.json"
            # Initialize Firebase Admin SDK if not already initialized
            firebase_admin.initialize_app(credentials.Certificate(firebase_credentials_path))
        self.db = firestore.client()
