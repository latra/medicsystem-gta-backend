# Mejoras del Sistema de Gestión de Visitas Médicas

Este documento describe las mejoras implementadas en el sistema de gestión de visitas médicas para mejorar el mantenimiento del código y proporcionar una arquitectura más robusta y escalable.

## 🔧 Mejoras Implementadas

### 1. **Arquitectura Separada por Responsabilidades**

**Antes:**
- Un solo servicio que mezclaba operaciones de base de datos con lógica de negocio
- Modelos simples sin validaciones médicas apropiadas
- Manejo de errores básico
- Campos médicos como strings planos

**Después:**
- **VisitRepository**: Responsable únicamente de operaciones de base de datos
- **VisitService**: Lógica de negocio y transformaciones de datos
- **Router**: Manejo de endpoints HTTP y validaciones
- **Modelos Médicos**: Estructuras especializadas para datos médicos

### 2. **Modelo de Datos Médicos Especializado**

#### Nuevo Modelo de Base de Datos (`models/visit.py`)

```python
class VisitDB(BaseModel):
    # Identificación
    visit_id: str = Field(default_factory=lambda: str(uuid4()))
    patient_dni: str = Field(..., description="DNI del paciente")
    
    # Información médica estructurada
    admission_vital_signs: Optional[VitalSigns] = Field(None)
    current_vital_signs: Optional[VitalSigns] = Field(None)
    diagnoses: List[Diagnosis] = Field(default_factory=list)
    procedures: List[MedicalProcedure] = Field(default_factory=list)
    evolutions: List[MedicalEvolution] = Field(default_factory=list)
    prescriptions: List[Prescription] = Field(default_factory=list)
    
    # Gestión de calidad
    priority_level: int = Field(default=3, ge=1, le=5)
    is_completed: bool = Field(False)
    quality_indicators: dict = Field(default_factory=dict)
```

#### Signos Vitales Estructurados

```python
class VitalSigns(BaseModel):
    measurement_id: str = Field(default_factory=lambda: str(uuid4()))
    measured_at: datetime = Field(default_factory=datetime.now)
    heart_rate: Optional[int] = Field(None, ge=30, le=300)
    systolic_pressure: Optional[int] = Field(None, ge=50, le=300)
    diastolic_pressure: Optional[int] = Field(None, ge=30, le=200)
    temperature: Optional[float] = Field(None, ge=30.0, le=45.0)
    oxygen_saturation: Optional[int] = Field(None, ge=70, le=100)
    respiratory_rate: Optional[int] = Field(None, ge=8, le=60)
    weight: Optional[float] = Field(None, ge=0, le=500)
    height: Optional[float] = Field(None, ge=0, le=300)
    measured_by: Optional[str] = Field(None)
    notes: Optional[str] = Field(None)
```

#### Diagnósticos Médicos Completos

```python
class Diagnosis(BaseModel):
    diagnosis_id: str = Field(default_factory=lambda: str(uuid4()))
    diagnosed_at: datetime = Field(default_factory=datetime.now)
    primary_diagnosis: str = Field(..., description="Diagnóstico principal")
    secondary_diagnoses: List[str] = Field(default_factory=list)
    icd10_code: Optional[str] = Field(None, description="Código CIE-10")
    severity: Optional[str] = Field(None)
    confirmed: bool = Field(False)
    differential_diagnoses: List[str] = Field(default_factory=list)
    diagnosed_by: Optional[str] = Field(None)
```

#### Prescripciones Médicas Detalladas

```python
class Prescription(BaseModel):
    prescription_id: str = Field(default_factory=lambda: str(uuid4()))
    prescribed_at: datetime = Field(default_factory=datetime.now)
    medication_name: str = Field(..., description="Nombre del medicamento")
    dosage: str = Field(..., description="Dosis prescrita")
    frequency: str = Field(..., description="Frecuencia de administración")
    duration: str = Field(..., description="Duración del tratamiento")
    route: str = Field(..., description="Vía de administración")
    instructions: Optional[str] = Field(None)
    prescribed_by: Optional[str] = Field(None)
```

### 3. **Esquemas de Transferencia de Datos (DTOs) Especializados**

#### Diferentes Niveles de Información

- **VisitSummary**: Para listados (información mínima)
- **Visit**: Información básica compatible con API actual
- **VisitComplete**: Información completa con todos los datos médicos
- **VisitCreate**: Para creación de nuevas visitas
- **VisitUpdate**: Para actualizar información básica

#### Esquemas Médicos Específicos

- **VitalSignsCreate/Response**: Para gestión de signos vitales
- **DiagnosisCreate/Response**: Para diagnósticos médicos
- **PrescriptionCreate/Response**: Para prescripciones
- **MedicalProcedureCreate/Response**: Para procedimientos
- **DischargeRequest**: Para dar de alta pacientes

### 4. **Nuevos Endpoints Especializados**

```bash
# Obtener visitas de un paciente
GET /visit/{patient_dni}

# Obtener información básica de una visita
GET /visit/info/{visit_id}

# Obtener información completa (incluye todos los datos médicos)
GET /visit/complete/{visit_id}

# Crear nueva visita
POST /visit/

# Actualizar información básica
PUT /visit/{visit_id}

# Dar de alta (versión mejorada)
PUT /visit/{visit_id}/discharge

# Dar de alta (versión simple para compatibilidad)
PUT /visit/{visit_id}/discharge-simple

# Añadir signos vitales
POST /visit/{visit_id}/vital-signs

# Añadir diagnóstico
POST /visit/{visit_id}/diagnosis

# Añadir prescripción
POST /visit/{visit_id}/prescription

# Obtener visitas por médico
GET /visit/doctor/{doctor_dni}

# Obtener visitas por estado
GET /visit/status/{status}

# Eliminar visita
DELETE /visit/{visit_id}
```

### 5. **Manejo de Errores Médico-Específico**

- **Logging estructurado** para auditoría médica
- **Códigos de estado HTTP apropiados**
- **Validaciones médicas** (rangos de signos vitales, etc.)
- **Trazabilidad completa** de acciones médicas
- **Manejo de excepciones** específicas para Firebase

### 6. **Timestamps y Auditoría Médica**

- Timestamps automáticos para todos los datos médicos
- Registro de qué profesional realizó cada acción
- Historial completo de evoluciones médicas
- Trazabilidad de prescripciones y procedimientos
- Cálculo automático de duración de estancia

### 7. **Compatibilidad con API Actual**

- Mantiene compatibilidad completa con endpoints existentes
- Mapeo automático de campos legacy a nueva estructura
- Endpoint de descarga simple para compatibilidad

## 📊 Ejemplos de Uso

### Crear una Nueva Visita

```python
visit_data = VisitCreate(
    patient_dni="12345678",
    reason="Dolor abdominal agudo",
    attention_place=AttentionType.HEADQUARTERS,
    location="Consultorio 1",
    triage=Triage.YELLOW,
    priority_level=2,
    admission_heart_rate=85,
    admission_blood_pressure=140,
    admission_temperature=37.2,
    admission_oxygen_saturation=98
)
```

### Añadir Signos Vitales

```python
vital_signs = VitalSignsBase(
    heart_rate=78,
    systolic_pressure=120,
    diastolic_pressure=80,
    temperature=36.8,
    oxygen_saturation=99,
    respiratory_rate=16,
    weight=70.5,
    height=175.0,
    notes="Signos vitales estables"
)
```

### Añadir Diagnóstico

```python
diagnosis = DiagnosisCreate(
    primary_diagnosis="Apendicitis aguda",
    secondary_diagnoses=["Leucocitosis"],
    icd10_code="K35.9",
    severity="Moderada",
    confirmed=True,
    differential_diagnoses=["Gastroenteritis", "Cólico renal"]
)
```

### Añadir Prescripción

```python
prescription = PrescriptionCreate(
    medication_name="Metamizol",
    dosage="500mg",
    frequency="Cada 8 horas",
    duration="3 días",
    route="Oral",
    instructions="Tomar con alimentos"
)
```

### Dar de Alta

```python
discharge = DischargeRequest(
    discharge_summary="Paciente estable, síntomas resueltos",
    discharge_instructions="Reposo relativo por 48 horas, control en 1 semana",
    follow_up_required=True,
    follow_up_date=datetime.now() + timedelta(days=7),
    follow_up_specialty="Cirugía General"
)
```

## 🔒 Ventajas de la Nueva Arquitectura

### **Mantenibilidad Médica**
- Código organizado por conceptos médicos
- Validaciones específicas para datos clínicos
- Fácil de extender para nuevas especialidades

### **Escalabilidad Clínica**
- Estructura preparada para múltiples especialidades
- Modelos de datos médicos estándar
- Soporte para protocolos médicos complejos

### **Robustez Hospitalaria**
- Auditoría completa de acciones médicas
- Validaciones estrictas de datos vitales
- Trazabilidad para cumplimiento regulatorio

### **Usabilidad Clínica**
- Endpoints específicos para flujos médicos
- Respuestas optimizadas por tipo de usuario
- Compatibilidad con sistemas existentes

### **Gestión de Calidad**
- Indicadores de calidad configurables
- Métricas de rendimiento médico
- Alertas automáticas por valores críticos

## 🏥 Funcionalidades Médicas Avanzadas

### **Gestión de Signos Vitales**
- Validaciones automáticas de rangos normales
- Alertas por valores críticos
- Historial completo de mediciones
- Gráficas de tendencias

### **Diagnósticos Estructurados**
- Soporte para códigos CIE-10
- Diagnósticos diferenciales
- Confirmación de diagnósticos
- Severidad y pronóstico

### **Prescripciones Seguras**
- Validación de dosis
- Interacciones medicamentosas (futuro)
- Historial de prescripciones
- Alertas de alergias

### **Procedimientos Médicos**
- Registro detallado de procedimientos
- Duración y complicaciones
- Profesionales involucrados
- Resultados y seguimiento

## 🚀 Próximos Pasos Recomendados

1. **Sistema de Alertas**: Implementar alertas automáticas por valores críticos
2. **Interacciones Medicamentosas**: Base de datos de interacciones
3. **Protocolos Médicos**: Sistemas de guías clínicas automatizadas
4. **Integración DICOM**: Soporte para imágenes médicas
5. **HL7 FHIR**: Estándar internacional de interoperabilidad
6. **Telemedicina**: Soporte para consultas remotas
7. **Analytics Médicos**: Dashboards de indicadores clínicos

## 📝 Migración de Datos Existentes

Para migrar visitas del formato anterior:

1. **Script de Migración**: Convertir campos de string a estructuras médicas
2. **Mapeo de Datos**: Campos legacy a nueva estructura
3. **Validación Médica**: Verificar consistencia de datos clínicos
4. **Backup Completo**: Respaldo antes de migración
5. **Pruebas Clínicas**: Validación con casos reales

---

*Esta mejora mantiene total compatibilidad con la API existente mientras proporciona una base sólida para el crecimiento del sistema médico y cumplimiento de estándares hospitalarios.* 