from pydantic import BaseModel, Field
from typing import Optional

class Doctor(BaseModel):
    name: str = Field(..., description="The name of the doctor")
    dni: str = Field(..., description="The DNI of the doctor")
    email: str = Field(..., description="The email of the doctor")
    specialty: Optional[str] = Field(None, description="The specialty of the doctor")
    enabled: bool = Field(..., description="The enabled status of the doctor")
    is_admin: Optional[bool] = Field(None, description="The admin status of the doctor")

class DoctorCreate(BaseModel):
    name: str = Field(..., description="The name of the doctor")
    dni: str = Field(..., description="The DNI of the doctor")
    email: str = Field(..., description="The email of the doctor")
    specialty: Optional[str] = Field(None, description="The specialty of the doctor")