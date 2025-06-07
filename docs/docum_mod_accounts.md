# Documentación Módulo de Cuentas - PEISOL MANTIS

## Introducción

El módulo de cuentas de MANTIS es el sistema de gestión de usuarios, técnicos, licencias y certificaciones de PEISOL S.A. Este módulo centraliza toda la información relacionada con el personal técnico, sus certificaciones, vacunas, pases de acceso y licencias del sistema.

## Arquitectura del Sistema

### Modelo Base (BaseModel)

Todos los modelos del sistema heredan de `BaseModel`, que proporciona:

- **Auditoría automática**: Registra quién y cuándo creó/modificó cada registro
- **Historial de cambios**: Seguimiento completo de modificaciones
- **Eliminación lógica**: Los registros se marcan como inactivos en lugar de eliminarse
- **Campos comunes**:
  - `notes`: Notas adicionales
  - `created_at`: Fecha de creación
  - `updated_at`: Fecha de última actualización
  - `is_active`: Estado del registro
  - `id_user_created`: Usuario creador
  - `id_user_updated`: Usuario que actualizó

## Modelos del Sistema

### 1. CustomUserModel - Usuarios del Sistema

**Propósito**: Gestión de usuarios administrativos y técnicos del sistema MANTIS.

**Características principales**:
- Autenticación por correo electrónico (sin username)
- Gestión de roles (ADMINISTRATIVO/TECNICO)
- Confirmación de correo electrónico
- Imagen de perfil opcional

**Campos principales**:
- `email`: Correo electrónico (campo único de autenticación)
- `picture`: Imagen de perfil
- `is_confirmed_mail`: Estado de confirmación del email
- `role`: Rol del usuario (ADMINISTRATIVO/TECNICO)
- `notes`: Notas adicionales

**Casos de uso**:
- Acceso al sistema administrativo
- Gestión de permisos y roles
- Auditoría de cambios en el sistema

### 2. License - Licencias del Sistema

**Propósito**: Control de licencias de software y acceso al sistema.

**Características principales**:
- Licencias únicas por clave
- Control de activación y expiración
- Asignación a usuarios específicos
- Configuración de servidor remoto

**Campos principales**:
- `license_key`: Clave única de licencia
- `activated_on`: Fecha de activación
- `expires_on`: Fecha de expiración
- `licence_file`: Archivo de licencia
- `role`: Rol asociado a la licencia
- `enterprise`: Empresa (por defecto PEISOL S.A.)
- `url_server`: URL del servidor de licencias
- `user`: Usuario asignado

**Casos de uso**:
- Activación de nuevas instalaciones
- Control de vencimientos
- Gestión de accesos por empresa

### 3. Technical - Técnicos de Campo

**Propósito**: Registro completo de técnicos que realizan mantenimientos en campo.

**Áreas de trabajo disponibles**:
- Proyectos de Plantas de tratamiento de agua
- Técnico de baterías sanitarias
- Ayudante
- Mantenimientos y Logística
- Supervisor

**Información personal**:
- `first_name`, `last_name`: Nombres y apellidos
- `email`: Correo electrónico opcional
- `dni`: Cédula de identidad
- `nro_phone`: Número de celular
- `birth_date`: Fecha de nacimiento
- `date_joined`: Fecha de ingreso a la empresa

**Certificaciones y licencias**:
- **Licencia de conducir**: `license_issue_date`, `license_expiry_date`
- **Certificado de manejo defensivo**: `defensive_driving_certificate_issue_date`, `defensive_driving_certificate_expiry_date`
- **Certificado MAE**: `mae_certificate_issue_date`, `mae_certificate_expiry_date`
- **Certificado médico**: `medical_certificate_issue_date`, `medical_certificate_expiry_date`

**Información laboral**:
- `work_area`: Área de especialización
- `is_iess_affiliated`: Afiliación al IESS
- `has_life_insurance_policy`: Póliza de vida

**Información Quest**:
- `quest_ncst_code`: Código Quest NCST
- `quest_instructor`: Instructor asignado
- `quest_start_date`, `quest_end_date`: Fechas del programa Quest

### 4. VaccinationRecord - Registro de Vacunas

**Propósito**: Control de vacunación de técnicos para cumplimiento de protocolos de salud.

**Campos principales**:
- `technical`: Técnico vacunado (relación con Technical)
- `vaccine_type`: Tipo de vacuna aplicada
- `application_date`: Fecha de aplicación
- `next_dose_date`: Fecha de próxima dosis
- `batch_number`: Número de lote de la vacuna

**Casos de uso**:
- Control de esquemas de vacunación
- Seguimiento de dosis de refuerzo
- Reportes de cumplimiento sanitario

### 5. PassTechnical - Pases de Acceso

**Propósito**: Gestión de pases y credenciales para acceso a diferentes bloques petroleros y empresas.

**Bloques disponibles**:
- Petroecuador
- Shaya
- Consorcio Shushufindi
- ENAP SIPEC
- Orion
- Andes Petroleum
- Pardalis Services
- Frontera Energy
- Gran Tierra
- PCR
- Halliburton
- Gente Oil
- Tribiol Gas
- Adico
- Cuyaveno Petro
- Geopark

**Campos principales**:
- `technical`: Técnico titular del pase
- `bloque`: Empresa/bloque de acceso
- `fecha_caducidad`: Fecha de vencimiento del pase

## Relaciones entre Modelos

```
CustomUserModel (1) → (N) License
Technical (1) → (N) VaccinationRecord
Technical (1) → (N) PassTechnical
```

## Funcionalidades del Administrador

### Panel de Administración CustomUserModel
- Gestión completa de usuarios
- Asignación de roles y permisos
- Control de confirmación de correos
- Historial de cambios

### Panel de Administración License
- Activación y desactivación de licencias
- Control de vencimientos
- Asignación a usuarios
- Configuración de servidores

### Panel de Administración Technical
- Registro completo de técnicos
- Seguimiento de certificaciones
- Control de vencimientos
- Gestión de áreas de trabajo

### Panel de Administración VaccinationRecord
- Registro de vacunas aplicadas
- Programación de refuerzos
- Control por técnico
- Búsqueda por lote de vacuna

### Panel de Administración PassTechnical
- Asignación de pases por bloque
- Control de vencimientos
- Gestión por técnico

## Casos de Uso Principales

### 1. Incorporación de Nuevo Técnico
1. Crear registro en Technical con información personal
2. Registrar certificaciones vigentes
3. Crear registros de vacunación
4. Asignar pases según área de trabajo
5. Crear usuario del sistema si requiere acceso administrativo

### 2. Control de Vencimientos
1. Monitoreo de certificaciones próximas a vencer
2. Alertas de renovación de pases
3. Seguimiento de esquemas de vacunación
4. Control de licencias del sistema

### 3. Asignación de Trabajos
1. Verificar certificaciones vigentes del técnico
2. Confirmar pases de acceso al bloque
3. Validar estado de vacunación
4. Confirmar licencias del sistema

### 4. Reportes y Auditoría
1. Estado de certificaciones por técnico
2. Vencimientos próximos
3. Cobertura de vacunación
4. Uso de licencias del sistema

## Consideraciones de Seguridad

- Todos los cambios son auditados automáticamente
- Eliminación lógica previene pérdida de datos
- Control de acceso basado en roles
- Historial completo de modificaciones

## Integración con Otros Módulos

El módulo de cuentas se integra con:
- **Módulo de Mantenimientos**: Asignación de técnicos a órdenes de trabajo
- **Módulo de Reportes**: Generación de informes de personal
- **Módulo de Planificación**: Disponibilidad de técnicos certificados

## Mantenimiento del Sistema

### Tareas Periódicas Recomendadas
1. **Semanal**: Revisión de vencimientos próximos
2. **Mensual**: Actualización de certificaciones
3. **Trimestral**: Auditoría de licencias activas
4. **Anual**: Revisión completa de datos de técnicos

### Respaldos
- Los datos históricos se mantienen automáticamente
- Respaldo recomendado antes de actualizaciones masivas
- Exportación periódica de datos críticos

---

*Documento creado para PEISOL S.A. - Sistema MANTIS*
*Fecha: Mayo 2024*
*Versión: 1.0*