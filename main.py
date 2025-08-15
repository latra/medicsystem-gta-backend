import os
from fastapi import FastAPI
from routers.system_info import system_info_router
from auth.firebase import FirebaseAuth
from contextlib import asynccontextmanager
from routers.patients import patients_router
from routers.visit import visit_router
from routers.doctor import doctor_router
from fastapi.middleware.cors import CORSMiddleware
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.firebase_auth = FirebaseAuth(os.getenv("FIREBASE_CREDENTIALS_PATH"))
    yield
    app.firebase_auth = None

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