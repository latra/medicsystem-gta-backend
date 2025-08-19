from enum import Enum

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"

class VisitStatus(str, Enum):
    ADMISSION = "admission"
    DISCHARGE = "discharge"

class UserRole(str, Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"  # Cambiado de MEDIC a DOCTOR para mayor claridad
    POLICE = "police"  # Nueva figura de policía
    PATIENT = "patient"

class AttentionType(str, Enum):
    HOME = "home"
    HEADQUARTERS = "headquarters"
    STREET = "street"
    HOSPITAL = "hospital"
    TRASLAD = "traslad"
    OTHER = "other"

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

class Triage(str, Enum):
    UNKNOWN = "unknown"
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"
    BLACK = "black"

class ExamResultStatus(str, Enum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    CANCELLED = "cancelled"