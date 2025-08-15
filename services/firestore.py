import firebase_admin
from firebase_admin import firestore, auth, credentials
import os

class FirestoreService:
    def __init__(self):
        """Initialize Firestore client"""
        if not firebase_admin._apps:
            # Initialize Firebase Admin SDK if not already initialized
            firebase_admin.initialize_app(credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS_PATH")))
        self.db = firestore.client()
