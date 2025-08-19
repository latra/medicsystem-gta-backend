import os
import logging
from fastapi import FastAPI
from routers.system_info import system_info_router
from auth.firebase import FirebaseAuth
from contextlib import asynccontextmanager
from routers.patients import patients_router
from routers.visit import visit_router
from routers.doctor import doctor_router
from routers.user import user_router
from routers.police import police_router
from fastapi.middleware.cors import CORSMiddleware
from routers.exams import exam_router
from services.firestore_indexes import firestore_index_service

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting API initialization...")
    
    # Inicializar Firebase Auth
    firebase_credentials_path = os.getenv("FIREBASE_CREDENTIALS_PATH") if os.getenv("FIREBASE_CREDENTIALS_PATH") else "firebase-credentials.json"
    app.firebase_auth = FirebaseAuth(firebase_credentials_path)
    logger.info("✓ Firebase Auth initialized")
    
    # Verificar y crear índices de Firestore
    try:
        logger.info("🔍 Verifying Firestore indexes...")
        firestore_index_service.verify_and_create_indexes()
        logger.info("✓ Firestore indexes verification completed")
    except Exception as e:
        logger.error(f"❌ Error during Firestore indexes verification: {e}")
        # No fallar el startup por problemas de índices, solo loggear
    
    logger.info("✅ API initialization completed successfully")
    
    yield
    
    logger.info("🔄 Shutting down API...")
    app.firebase_auth = None
    logger.info("✅ API shutdown completed")

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(system_info_router)
app.include_router(patients_router)
app.include_router(visit_router)
app.include_router(doctor_router)
app.include_router(user_router)
app.include_router(police_router)
app.include_router(exam_router)