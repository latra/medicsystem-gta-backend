import os
import sys
from pathlib import Path

# Add the src directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir
sys.path.insert(0, str(src_dir))

import fastapi
from fastapi import Depends, FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

from config import Config
from auth import FirebaseAuth
from models import Medico, MedicoCreate, MedicoUpdate, CargoMedico, Paciente, PacienteCreate, PacienteUpdate, Consulta, ConsultaCreate, ConsultaUpdate, TipoAtencion
from services.firestore_service import FirestoreService
from services.paciente_service import PacienteService
from services.consulta_service import ConsultaService

config = Config()

app = FastAPI(
    title="MedicApp API",
    description="API para aplicación médica con autenticación Firebase, gestión de médicos, pacientes y consultas",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
firebase_auth = FirebaseAuth(config.FIREBASE_CREDENTIALS_PATH)
firestore_service = FirestoreService()
paciente_service = PacienteService()
consulta_service = ConsultaService()

@app.get("/")
async def root():
    return {"message": "Bienvenido a MedicApp API"}

@app.get("/health")
async def health():
    return {"status": "ok", "environment": config.ENVIRONMENT}

@app.get("/secure-data")
async def secure_data(current_user=Depends(firebase_auth.verify_token)):
    """
    Endpoint protegido que requiere autenticación con Bearer token
    """
    return {
        "message": "Datos seguros accedidos correctamente",
        "user": current_user
    }

@app.get("/user/profile")
async def get_user_profile(current_user=Depends(firebase_auth.verify_token)):
    """
    Obtener perfil del usuario autenticado
    """
    return {
        "uid": current_user["uid"],
        "email": current_user["email"],
        "name": current_user.get("name"),
        "email_verified": current_user.get("email_verified", False),
        "picture": current_user.get("picture")
    }

# Endpoints para médicos (protegidos)

@app.post("/medicos", response_model=Medico, status_code=status.HTTP_201_CREATED)
async def create_medico(
    medico_data: MedicoCreate,
    current_user=Depends(firebase_auth.verify_token)
):
    """
    Crear un nuevo médico (también crea usuario en Firebase Auth con DNI como contraseña)
    """
    try:
        medico = await firestore_service.create_medico(medico_data)
        return medico
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/medicos", response_model=List[Medico])
async def get_all_medicos(current_user=Depends(firebase_auth.verify_token)):
    """
    Obtener todos los médicos
    """
    try:
        medicos = await firestore_service.get_all_medicos()
        return medicos
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/medicos/{medico_id}", response_model=Medico)
async def get_medico(
    medico_id: str,
    current_user=Depends(firebase_auth.verify_token)
):
    """
    Obtener un médico por ID
    """
    try:
        medico = await firestore_service.get_medico(medico_id)
        if medico is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Médico no encontrado"
            )
        return medico
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.put("/medicos/{medico_id}", response_model=Medico)
async def update_medico(
    medico_id: str,
    medico_data: MedicoUpdate,
    current_user=Depends(firebase_auth.verify_token)
):
    """
    Actualizar un médico (también actualiza datos en Firebase Auth)
    """
    try:
        medico = await firestore_service.update_medico(medico_id, medico_data)
        if medico is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Médico no encontrado"
            )
        return medico
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.delete("/medicos/{medico_id}")
async def delete_medico(
    medico_id: str,
    current_user=Depends(firebase_auth.verify_token)
):
    """
    Eliminar un médico (también elimina usuario de Firebase Auth)
    """
    try:
        deleted = await firestore_service.delete_medico(medico_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Médico no encontrado"
            )
        return {"message": "Médico eliminado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/medicos/cargo/{cargo}", response_model=List[Medico])
async def get_medicos_by_cargo(
    cargo: CargoMedico,
    current_user=Depends(firebase_auth.verify_token)
):
    """
    Buscar médicos por cargo
    """
    try:
        medicos = await firestore_service.search_medicos_by_cargo(cargo)
        return medicos
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/medicos/dni/{dni}", response_model=Medico)
async def get_medico_by_dni(
    dni: str,
    current_user=Depends(firebase_auth.verify_token)
):
    """
    Buscar médico por DNI
    """
    try:
        medico = await firestore_service.search_medicos_by_dni(dni)
        if medico is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Médico no encontrado"
            )
        return medico
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/medicos/email/{email}", response_model=Medico)
async def get_medico_by_email(
    email: str,
    current_user=Depends(firebase_auth.verify_token)
):
    """
    Buscar médico por email
    """
    try:
        medico = await firestore_service.search_medicos_by_email(email)
        if medico is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Médico no encontrado"
            )
        return medico
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Endpoints para pacientes (protegidos)

@app.post("/pacientes", response_model=Paciente, status_code=status.HTTP_201_CREATED)
async def create_paciente(
    paciente_data: PacienteCreate,
    current_user=Depends(firebase_auth.verify_token)
):
    """
    Crear un nuevo paciente
    """
    try:
        paciente = await paciente_service.create_paciente(paciente_data)
        return paciente
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/pacientes", response_model=List[Paciente])
async def get_pacientes(
    dni: Optional[str] = Query(None, description="Buscar por DNI exacto"),
    nombre: Optional[str] = Query(None, description="Buscar por nombre (parcial)"),
    apellido: Optional[str] = Query(None, description="Buscar por apellido (parcial)"),
    nombre_completo: Optional[str] = Query(None, description="Buscar por nombre completo (parcial)"),
    current_user=Depends(firebase_auth.verify_token)
):
    """
    Obtener pacientes con filtros opcionales.
    Si no se proporcionan filtros, retorna todos los pacientes.
    Los filtros se pueden combinar.
    """
    try:
        # Si se proporciona DNI, buscar por DNI exacto
        if dni:
            paciente = await paciente_service.search_pacientes_by_dni(dni)
            if paciente:
                return [paciente]
            else:
                return []
        
        # Si se proporciona nombre completo, buscar por nombre completo
        if nombre_completo:
            return await paciente_service.search_pacientes_by_nombre_completo(nombre_completo)
        
        # Si se proporciona solo nombre, buscar por nombre
        if nombre and not apellido:
            return await paciente_service.search_pacientes_by_nombre(nombre)
        
        # Si se proporciona solo apellido, buscar por apellido
        if apellido and not nombre:
            return await paciente_service.search_pacientes_by_apellido(apellido)
        
        # Si se proporcionan ambos nombre y apellido, buscar por nombre completo
        if nombre and apellido:
            nombre_completo_search = f"{nombre} {apellido}"
            return await paciente_service.search_pacientes_by_nombre_completo(nombre_completo_search)
        
        # Si no se proporcionan filtros, retornar todos los pacientes
        return await paciente_service.get_all_pacientes()
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/pacientes/{paciente_dni}", response_model=Paciente)
async def get_paciente(
    paciente_dni: str,
    current_user=Depends(firebase_auth.verify_token)
):
    """
    Obtener un paciente por DNI
    """
    try:
        paciente = await paciente_service.get_paciente(paciente_dni)
        if paciente is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paciente no encontrado"
            )
        return paciente
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.put("/pacientes/{paciente_dni}", response_model=Paciente)
async def update_paciente(
    paciente_dni: str,
    paciente_data: PacienteUpdate,
    current_user=Depends(firebase_auth.verify_token)
):
    """
    Actualizar un paciente por DNI
    """
    try:
        paciente = await paciente_service.update_paciente(paciente_dni, paciente_data)
        if paciente is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paciente no encontrado"
            )
        return paciente
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.delete("/pacientes/{paciente_dni}")
async def delete_paciente(
    paciente_dni: str,
    current_user=Depends(firebase_auth.verify_token)
):
    """
    Eliminar un paciente por DNI
    """
    try:
        deleted = await paciente_service.delete_paciente(paciente_dni)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paciente no encontrado"
            )
        return {"message": "Paciente eliminado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Endpoints para consultas (protegidos)

@app.post("/consultas", response_model=Consulta, status_code=status.HTTP_201_CREATED)
async def create_consulta(
    consulta_data: ConsultaCreate,
    current_user=Depends(firebase_auth.verify_token)
):
    """
    Crear una nueva consulta médica
    """
    print(current_user)
    medico = await firestore_service.get_medico(current_user['uid'])
    if medico is None:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Médico no encontrado"
        )
    medico_nombre = medico.nombre
    medico_dni = medico.dni
    medico_apellido = medico.apellido
    print(medico_nombre, medico_apellido)
    consulta = await consulta_service.create_consulta(consulta_data, medico_dni, medico_nombre, medico_apellido)
    return consulta


@app.get("/consultas", response_model=List[Consulta])
async def get_consultas(
    paciente_dni: Optional[str] = Query(None, description="Filtrar por DNI del paciente"),
    medico_dni: Optional[str] = Query(None, description="Filtrar por DNI del médico"),
    tipo_atencion: Optional[TipoAtencion] = Query(None, description="Filtrar por tipo de atención"),
    current_user=Depends(firebase_auth.verify_token)
):
    """
    Obtener consultas con filtros opcionales.
    Si no se proporcionan filtros, retorna todas las consultas.
    Los filtros se pueden combinar.
    """
    try:
        # Si se proporciona DNI del paciente, buscar consultas del paciente
        if paciente_dni:
            return await consulta_service.get_consultas_by_paciente_dni(paciente_dni)
        
        # Si se proporciona DNI del médico, buscar consultas del médico
        if medico_dni:
            return await consulta_service.get_consultas_by_medico_dni(medico_dni)
        
        # Si se proporciona tipo de atención, buscar por tipo
        if tipo_atencion:
            return await consulta_service.search_consultas_by_tipo_atencion(tipo_atencion.value)
        
        # Si no se proporcionan filtros, retornar todas las consultas
        return await consulta_service.get_all_consultas()
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/consultas/{consulta_id}", response_model=Consulta)
async def get_consulta(
    consulta_id: str,
    current_user=Depends(firebase_auth.verify_token)
):
    """
    Obtener una consulta por ID
    """
    try:
        consulta = await consulta_service.get_consulta(consulta_id)
        if consulta is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consulta no encontrada"
            )
        return consulta
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.put("/consultas/{consulta_id}", response_model=Consulta)
async def update_consulta(
    consulta_id: str,
    consulta_data: ConsultaUpdate,
    current_user=Depends(firebase_auth.verify_token)
):
    """
    Actualizar una consulta
    """
    try:
        consulta = await consulta_service.update_consulta(consulta_id, consulta_data)
        if consulta is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consulta no encontrada"
            )
        return consulta
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.delete("/consultas/{consulta_id}")
async def delete_consulta(
    consulta_id: str,
    current_user=Depends(firebase_auth.verify_token)
):
    """
    Eliminar una consulta
    """
    try:
        deleted = await consulta_service.delete_consulta(consulta_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consulta no encontrada"
            )
        return {"message": "Consulta eliminada correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/consultas/paciente/{paciente_dni}", response_model=List[Consulta])
async def get_consultas_by_paciente_dni(
    paciente_dni: str,
    current_user=Depends(firebase_auth.verify_token)
):
    """
    Obtener todas las consultas de un paciente por DNI
    """
    try:
        consultas = await consulta_service.get_consultas_by_paciente_dni(paciente_dni)
        return consultas
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


