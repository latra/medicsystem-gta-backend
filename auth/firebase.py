from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import auth, credentials
from services.doctor import DoctorService
import time
import os

security = HTTPBearer()
doctor_service = DoctorService()
class FirebaseAuth:
    def __init__(self, credentials_path: str = os.getenv("FIREBASE_CREDENTIALS_PATH")):
        """Initialize Firebase Admin SDK"""
        if not firebase_admin._apps:
            cred = credentials.Certificate(credentials_path)
            firebase_admin.initialize_app(cred)
    
    async def verify_admin_token(self, credentials: HTTPAuthorizationCredentials = Depends(security)):
        """
        Verify Firebase ID token from Bearer header
        """
        try:
            token = credentials.credentials
            print(token)
            decoded_token = auth.verify_id_token(token)
            if decoded_token:
                return decoded_token
            else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")

    async def verify_token(self, credentials: HTTPAuthorizationCredentials = Depends(security)):
        """
        Verify Firebase ID token from Bearer header
        """
        try:
            # Extract token from Bearer header
            token = credentials.credentials
            print(token)
            try:
                decoded_token = auth.verify_id_token(token)
                print(decoded_token)
            except Exception as e:
                print(e)
                time.sleep(0.5)
                decoded_token = auth.verify_id_token(token)

            if decoded_token:
                doctor = doctor_service.get_doctor(decoded_token["uid"])
                if doctor and doctor is not None:
                    return doctor
                else:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Doctor not found")
            else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")


            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

# Dependency function for routes that require authentication
def get_current_user(auth_service: FirebaseAuth = Depends()):
    return auth_service.verify_token 