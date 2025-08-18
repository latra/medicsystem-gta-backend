# Sistema de Registro Público de Usuarios

## 📋 Resumen de Cambios

Se ha modificado el sistema para permitir que **cualquier persona pueda registrarse como médico o policía** sin necesidad de autenticación previa. Además, se han eliminado las relaciones de creador/actualizador de usuarios y se ha mejorado la verificación de tokens para distinguir claramente entre roles.

## 🎯 Cambios Implementados

### ✅ **1. Registro Público de Médicos y Policías**
- **Nuevos endpoints públicos**: 
  - `POST /user/register/doctor` 
  - `POST /user/register/police`
- **Sin autenticación requerida**: Cualquiera puede registrarse
- **Proceso simplificado**: Solo información esencial requerida

### ✅ **2. Eliminación de Campos de Auditoría**
- **Removidos**: `created_by`, `last_updated_by`, `disabled_by`
- **Simplificado**: Solo `created_at` y `updated_at` se mantienen
- **Menos complejidad**: Sin tracking de quién creó/modificó usuarios

### ✅ **3. Separación Clara de Roles**
- **Médicos**: Acceso completo a endpoints médicos
- **Policías**: Acceso limitado a información médica
- **Verificación estricta**: Tokens verifican rol específico
- **Protección de recursos**: Endpoints médicos solo para doctores

### ✅ **4. Compatibilidad Mantenida**
- **API existente**: Sigue funcionando igual
- **Fallback automático**: Sistema legacy como respaldo
- **Sin breaking changes**: Transición transparente

---

## 🆕 Nuevos Endpoints de Registro

### **POST /user/register/doctor**

**Descripción**: Registro público de médico - cualquiera puede registrarse

**Autenticación**: ❌ No requerida (público)

**Body (JSON)**:
```json
{
  "name": "Dr. Juan Pérez",
  "dni": "12345678",
  "email": "juan.perez@email.com",
  "phone": "+1234567890",
  "specialty": "Cardiología",
  "medical_license": "MED-12345",
  "institution": "Hospital Central",
  "years_experience": 5
}
```

**Respuesta Exitosa (201)**:
```json
{
  "user_id": "user-uuid-123",
  "firebase_uid": "firebase-uid-456",
  "name": "Dr. Juan Pérez",
  "dni": "12345678",
  "email": "juan.perez@email.com",
  "phone": "+1234567890",
  "role": "doctor",
  "enabled": true,
  "is_admin": false,
  "specialty": "Cardiología",
  "medical_license": "MED-12345",
  "institution": "Hospital Central",
  "years_experience": 5,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### **POST /user/register/police**

**Descripción**: Registro público de policía - cualquiera puede registrarse

**Autenticación**: ❌ No requerida (público)

**Body (JSON)**:
```json
{
  "name": "Oficial Carlos García",
  "dni": "87654321",
  "email": "carlos.garcia@policia.gov",
  "phone": "+0987654321",
  "badge_number": "POL-001",
  "rank": "Teniente",
  "department": "Investigaciones",
  "station": "Comisaría Central",
  "years_service": 8
}
```

**Respuesta Exitosa (201)**:
```json
{
  "user_id": "user-uuid-789",
  "firebase_uid": "firebase-uid-101",
  "name": "Oficial Carlos García",
  "dni": "87654321",
  "email": "carlos.garcia@policia.gov",
  "phone": "+0987654321",
  "role": "police",
  "enabled": true,
  "is_admin": false,
  "badge_number": "POL-001",
  "rank": "Teniente",
  "department": "Investigaciones",
  "station": "Comisaría Central",
  "years_service": 8,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

## 📝 Ejemplos de Uso

### **Registro de Doctor con curl**
```bash
curl -X POST "http://localhost:8000/user/register/doctor" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dr. María García",
    "dni": "11223344",
    "email": "maria.garcia@email.com",
    "phone": "+0987654321",
    "specialty": "Pediatría",
    "medical_license": "MED-67890",
    "institution": "Clínica San Juan",
    "years_experience": 8
  }'
```

### **Registro de Policía con curl**
```bash
curl -X POST "http://localhost:8000/user/register/police" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sargento Ana López",
    "dni": "99887766",
    "email": "ana.lopez@policia.gov",
    "phone": "+5555678901",
    "badge_number": "POL-025",
    "rank": "Sargento",
    "department": "Patrulla",
    "station": "Comisaría Norte",
    "years_service": 4
  }'
```

### **Registro de Doctor con JavaScript**
```javascript
const response = await fetch('http://localhost:8000/user/register/doctor', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    name: 'Dr. Carlos López',
    dni: '33445566',
    email: 'carlos.lopez@email.com',
    specialty: 'Neurología',
    medical_license: 'MED-11223',
    institution: 'Hospital Universitario',
    years_experience: 12
  })
});

const doctor = await response.json();
console.log('Doctor registrado:', doctor);
```

### **Registro de Policía con JavaScript**
```javascript
const response = await fetch('http://localhost:8000/user/register/police', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    name: 'Inspector Miguel Torres',
    dni: '77889900',
    email: 'miguel.torres@policia.gov',
    badge_number: 'POL-087',
    rank: 'Inspector',
    department: 'Investigaciones',
    station: 'Comisaría Sur',
    years_service: 10
  })
});

const police = await response.json();
console.log('Policía registrado:', police);
```

### **Registro con Python**
```python
import requests

# Registrar Doctor
doctor_data = {
    "name": "Dr. Ana Rodríguez",
    "dni": "55667788",
    "email": "ana.rodriguez@email.com",
    "phone": "+5551234567",
    "specialty": "Ginecología",
    "medical_license": "MED-55667",
    "institution": "Centro Médico Los Andes",
    "years_experience": 6
}

response = requests.post(
    'http://localhost:8000/user/register/doctor',
    json=doctor_data
)

if response.status_code == 201:
    doctor = response.json()
    print(f"Doctor registrado: {doctor['name']}")

# Registrar Policía
police_data = {
    "name": "Capitán Roberto Silva",
    "dni": "44556677",
    "email": "roberto.silva@policia.gov",
    "phone": "+5559876543",
    "badge_number": "POL-045",
    "rank": "Capitán",
    "department": "Comando",
    "station": "Comisaría Oeste",
    "years_service": 15
}

response = requests.post(
    'http://localhost:8000/user/register/police',
    json=police_data
)

if response.status_code == 201:
    police = response.json()
    print(f"Policía registrado: {police['name']}")
```

---

## 🔧 Características del Sistema

### **Campos Requeridos por Tipo** ✅

#### **Doctores**
- `name`: Nombre completo del médico
- `dni`: DNI único del médico  
- `email`: Email único para autenticación

#### **Policías**
- `name`: Nombre completo del policía
- `dni`: DNI único del policía
- `email`: Email único para autenticación
- `badge_number`: Número de placa policial (**OBLIGATORIO**)

### **Campos Opcionales** 📝

#### **Doctores**
- `phone`: Número de teléfono
- `specialty`: Especialidad médica
- `medical_license`: Número de licencia médica
- `institution`: Institución donde trabaja
- `years_experience`: Años de experiencia

#### **Policías**
- `phone`: Número de teléfono
- `rank`: Rango policial (Oficial, Sargento, Teniente, etc.)
- `department`: Departamento (Patrulla, Investigaciones, etc.)
- `station`: Estación o comisaría asignada
- `years_service`: Años de servicio policial

### **Validaciones Automáticas** 🛡️
- **DNI único**: No se permiten DNIs duplicados entre todos los usuarios
- **Email único**: Cada email se puede usar solo una vez
- **Badge único**: No se permiten números de placa duplicados
- **Password automático**: Se genera basado en el DNI
- **Firebase Auth**: Usuario creado automáticamente

### **Permisos por Rol** 🔐

#### **Doctores** 👩‍⚕️
- **Acceso médico completo**: ✅ Todos los endpoints médicos
- **Crear pacientes**: ✅ Permitido
- **Gestionar visitas**: ✅ Permitido
- **Hacer análisis**: ✅ Permitido
- **Prescribir medicamentos**: ✅ Permitido
- **Ver información policial**: ❌ Restringido

#### **Policías** 👮‍♂️
- **Acceso médico limitado**: ❌ Solo información específica permitida
- **Ver pacientes**: ⚠️ Solo con permisos especiales
- **Realizar arrestos**: ✅ Permitido (según perfil)
- **Investigar casos**: ✅ Permitido (según perfil)
- **Gestionar información policial**: ✅ Permitido

#### **Ambos Roles** 🔒
- **No admin**: Por defecto no son administradores
- **Cuenta habilitada**: Lista para usar inmediatamente
- **Token específico**: Verificación estricta por rol

---

## 🔄 Proceso de Registro

### **Para Doctores** 👩‍⚕️
1. **Validación**: Se verifica que DNI y email sean únicos
2. **Firebase Auth**: Se crea usuario en Firebase Authentication
3. **Usuario Base**: Se crea registro en colección `users`
4. **Perfil Médico**: Se crea perfil específico en colección `doctors`
5. **Permisos**: Se asignan permisos médicos completos
6. **Respuesta**: Se retorna información completa del doctor

### **Para Policías** 👮‍♂️
1. **Validación**: Se verifica que DNI, email y badge_number sean únicos
2. **Firebase Auth**: Se crea usuario en Firebase Authentication
3. **Usuario Base**: Se crea registro en colección `users`
4. **Perfil Policial**: Se crea perfil específico en colección `police`
5. **Permisos**: Se asignan permisos policiales según configuración
6. **Respuesta**: Se retorna información completa del policía

### **Password Automático**
- **Basado en DNI**: Password = DNI (mínimo 6 dígitos)
- **Ejemplo**: DNI "123" → Password "000123"
- **Seguridad**: El usuario debe cambiar el password después del primer login

---

## 🔒 Seguridad y Autorización

### **Verificación por Rol** 🛡️
- **Tokens médicos**: Solo permiten acceso a endpoints médicos si el usuario es doctor
- **Tokens policiales**: Solo permiten acceso a endpoints policiales si el usuario es policía
- **Verificación estricta**: No hay acceso cruzado entre roles sin permisos específicos

### **Protección de Endpoints** 🚨
- **`/patients/*`**: Solo doctores ✅
- **`/visit/*`**: Solo doctores ✅
- **`/doctor/*`**: Solo doctores ✅
- **`/user/register/*`**: Público ✅
- **`/user/admin/*`**: Solo administradores ✅

### **Mensajes de Error Específicos** ⚠️
- **"Access denied: Medical endpoints require Doctor role"**: Policía intentando acceder a endpoints médicos
- **"Access denied: Police role required"**: Doctor intentando acceder a endpoints policiales
- **"Access denied: Doctor profile not found"**: Usuario doctor sin perfil médico completo

---

## 🚫 Errores Comunes

### **400 Bad Request - Doctor**
```json
{
  "detail": "Failed to register doctor. DNI or email may already exist."
}
```
**Causa**: DNI o email ya están registrados en el sistema

### **400 Bad Request - Policía**
```json
{
  "detail": "Failed to register police. DNI or email may already exist."
}
```
**Causa**: DNI, email o badge_number ya están registrados en el sistema

### **403 Forbidden - Acceso Médico**
```json
{
  "detail": "Access denied: Medical endpoints require Doctor role"
}
```
**Causa**: Usuario policía intentando acceder a endpoints médicos

### **403 Forbidden - Acceso Policial**
```json
{
  "detail": "Access denied: Police role required"
}
```
**Causa**: Usuario doctor intentando acceder a endpoints policiales

### **500 Internal Server Error**
```json
{
  "detail": "Error registering [doctor/police]: [mensaje específico]"
}
```
**Causas posibles**:
- Error de conexión con Firebase
- Problema con la base de datos
- Datos inválidos en el request
- Badge number duplicado (policías)

---

## 🔄 Migración y Compatibilidad

### **Endpoints Existentes**
- ✅ `/doctor/*` - Siguen funcionando igual
- ✅ `POST /doctor/` - Método legacy mantenido
- ✅ `GET /doctor/me` - Información del doctor actual

### **Autenticación**
- ✅ **Doctores nuevos**: Usan nuevo sistema
- ✅ **Doctores legacy**: Mantienen acceso
- ✅ **Tokens Firebase**: Siguen funcionando

### **Base de Datos**
- ✅ **Nuevas colecciones**: `users`, `doctors` (nuevos)
- ✅ **Colección legacy**: `doctors` (mantenida para compatibilidad)
- ✅ **Híbrido**: Sistema detecta automáticamente el origen

---

## ✨ Beneficios del Nuevo Sistema

### **Para Desarrolladores** 👨‍💻
- **API más simple**: Menos campos requeridos
- **Sin autenticación para registro**: Fácil integración
- **Mejor documentación**: Endpoints claros y bien definidos
- **Menor complejidad**: Sin tracking de auditoría
- **Roles bien definidos**: Separación clara de responsabilidades

### **Para Médicos** 👩‍⚕️
- **Registro fácil**: Sin necesidad de admin
- **Acceso médico completo**: Todas las funciones disponibles
- **Información detallada**: Perfil médico profesional
- **Compatibilidad**: Funciona con apps existentes
- **Seguridad**: Solo acceso a recursos médicos

### **Para Policías** 👮‍♂️
- **Registro directo**: Sin barreras administrativas
- **Perfil policial**: Información específica del cuerpo
- **Permisos apropiados**: Acceso limitado según función
- **Identificación clara**: Badge numbers únicos
- **Separación de roles**: Sin acceso inadecuado a datos médicos

### **Para el Sistema** 🏗️
- **Escalabilidad**: Más usuarios pueden registrarse
- **Mantenimiento**: Código más simple y limpio
- **Flexibilidad**: Fácil agregar nuevos tipos de usuario
- **Robustez**: Fallback automático a sistema legacy
- **Seguridad mejorada**: Verificación estricta por roles

---

## 🎉 Conclusión

El sistema ahora permite:

- ✅ **Registro público dual**: Cualquiera puede registrarse como médico o policía
- ✅ **Procesos simplificados**: Solo información esencial por rol
- ✅ **Separación estricta**: Médicos y policías con accesos diferenciados
- ✅ **Compatibilidad total**: API existente sigue funcionando
- ✅ **Sin complejidad**: Eliminadas relaciones de auditoría
- ✅ **Seguridad robusta**: Verificación estricta de tokens por rol
- ✅ **Listo para usar**: Acceso inmediato a funciones apropiadas

### **🚀 Endpoints Disponibles:**
- **`POST /user/register/doctor`** - Registro público de médicos
- **`POST /user/register/police`** - Registro público de policías
- **Todos los endpoints médicos** - Solo accesibles por doctores
- **Futuros endpoints policiales** - Solo accesibles por policías

¡El sistema está preparado para el crecimiento masivo con roles bien definidos y seguridad robusta! 🎯
