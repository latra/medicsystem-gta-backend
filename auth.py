from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import auth, credentials
import os

# Security scheme for Bearer token
security = HTTPBearer()

class FirebaseAuth:
    def __init__(self, credentials_path: str):
        """Initialize Firebase Admin SDK"""
        if not firebase_admin._apps:
            cred = credentials.Certificate(credentials_path)
            firebase_admin.initialize_app(cred)
    
    async def verify_token(self, credentials: HTTPAuthorizationCredentials = Depends(security)):
        """
        Verify Firebase ID token from Bearer header
        """
        try:
            # Extract token from Bearer header
            token = credentials.credentials
            print(token)
            # Verify the token with Firebase
            decoded_token = auth.verify_id_token(token)
            
            # Return user info
            return {
                "uid": decoded_token["uid"],
                "email": decoded_token.get("email"),
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

# Dependency function for routes that require authentication
def get_current_user(auth_service: FirebaseAuth = Depends()):
    return auth_service.verify_token 