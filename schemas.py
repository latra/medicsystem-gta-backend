from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from typing import Optional

class UserRole(str, Enum):
    ADMIN = "admin"
    MEDIC = "medic"
    PATIENT = "patient"

class AttentionType(str, Enum):
    STREET = "street"
    HOSPITAL = "hospital"
    TRASLAD = "traslad"

class PatientStatus(str, Enum):
    CONSCIOUS = "conscious"
    UNCONSCIOUS = "unconscious"
    IN_DANGER = "in_danger"
    STABLE = "stable"
    CRITICAL = "critical"

class BloodType(str, Enum):
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"

