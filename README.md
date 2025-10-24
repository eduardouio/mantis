# eliminar migraciones anteriores

# generamos las migraciones
```bash
python manage.py makemigrations accounts
python manage.py makemigrations equipment projects
python manage.py migrate
python manage.py sowseed
```


# linea a linea para unix
```bash
./manage.py makemigrations accounts equipment projects
./manage.py migrate
./manage.py sowseed
```


# un solo comando para **unix**
```bash
./manage.py makemigrations accounts &&
./manage.py makemigrations equipment projects &&
./manage.py migrate &&
./manage.py sowseed 
```

# un solo comando para windows
```bash
sudo systemctl daemon-reload
sudo systemctl restart mantis.service
sudo systemctl restart nginx

``` bash
sudo systemctl daemon-reload &&
sudo systemctl restart mantis.service &&
sudo systemctl restart nginx


```sql
-- Script para eliminar todas las tablas en el orden correcto
-- Primero eliminamos las tablas dependientes y luego las principales

-- Eliminar tablas de historial y dependientes primero
DROP TABLE IF EXISTS accounts_customusermodel_groups CASCADE;
DROP TABLE IF EXISTS accounts_customusermodel_user_permissions CASCADE;
DROP TABLE IF EXISTS accounts_historicallicense CASCADE;
DROP TABLE IF EXISTS accounts_historicalpasstechnical CASCADE;
DROP TABLE IF EXISTS accounts_historicaltechnical CASCADE;
DROP TABLE IF EXISTS accounts_historicalvaccinationrecord CASCADE;
DROP TABLE IF EXISTS accounts_license CASCADE;
DROP TABLE IF EXISTS accounts_passtechnical CASCADE;
DROP TABLE IF EXISTS accounts_vaccinationrecord CASCADE;
DROP TABLE IF EXISTS django_admin_log CASCADE;

-- Eliminar tablas de equipos
DROP TABLE IF EXISTS equipment_certificationvehicle CASCADE;
DROP TABLE IF EXISTS equipment_historicalcertificationvehicle CASCADE;
DROP TABLE IF EXISTS equipment_historicalpassvehicle CASCADE;
DROP TABLE IF EXISTS equipment_historicalresourceitem CASCADE;
DROP TABLE IF EXISTS equipment_historicalvehicle CASCADE;
DROP TABLE IF EXISTS equipment_passvehicle CASCADE;
DROP TABLE IF EXISTS equipment_resourceitem CASCADE;
DROP TABLE IF EXISTS equipment_vehicle CASCADE;

-- Eliminar tablas de proyectos
DROP TABLE IF EXISTS projects_historicalpartner CASCADE;
DROP TABLE IF EXISTS projects_historicalproject CASCADE;
DROP TABLE IF EXISTS projects_historicalprojectresourceitem CASCADE;
DROP TABLE IF EXISTS projects_historicalworkorder CASCADE;
DROP TABLE IF EXISTS projects_historicalworkorderdetail CASCADE;
DROP TABLE IF EXISTS projects_historicalworkordermaintenance CASCADE;
DROP TABLE IF EXISTS projects_partner CASCADE;
DROP TABLE IF EXISTS projects_project CASCADE;
DROP TABLE IF EXISTS projects_projectresourceitem CASCADE;
DROP TABLE IF EXISTS projects_workorder CASCADE;
DROP TABLE IF EXISTS projects_workorderdetail CASCADE;
DROP TABLE IF EXISTS projects_workordermaintenance CASCADE;

-- Eliminar tablas principales de accounts después de las dependientes
DROP TABLE IF EXISTS accounts_technical CASCADE;
DROP TABLE IF EXISTS accounts_customusermodel CASCADE;

-- Eliminar tablas de autenticación y Django
DROP TABLE IF EXISTS auth_group_permissions CASCADE;
DROP TABLE IF EXISTS auth_group CASCADE;
DROP TABLE IF EXISTS auth_permission CASCADE;
DROP TABLE IF EXISTS django_content_type CASCADE;
DROP TABLE IF EXISTS django_migrations CASCADE;
DROP TABLE IF EXISTS django_session CASCADE;

-- Eliminar tablas de user_sessions si existen
DROP TABLE IF EXISTS user_sessions_session CASCADE;


```bash

# configuraciuon en secrets 

DATABASES = {
    'TEST': {
        "ENGINE": "django.db.backends.postgresql",
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    },
    'PRODUCTION': {
        "ENGINE": "django.db.backends.postgresql",
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    },
    'DEVELOPMENT': {
        "ENGINE": "django.db.backends.postgresql",
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}


DEFAULT_DB = {
    'default': DATABASES['#ENVIRONMENT']
}

## Descripción del Proyecto
## Descripción del Proyecto PEISOL
Este es un proyecto web desarrollado en **Django** que utiliza **Tailwind CSS** con **DaisyUI** para el frontend y **PostgreSQL** como base de datos.

### Estructura de la Base de Datos
- **`common.BaseModel.BaseModel`**: 
  - Modelo base para todos los modelos del sistema
  - Hereda de `SimpleHistory` para auditoría automática
  - Contiene campos compartidos usados como metadata
  - **Eliminación lógica**: Los registros no se eliminan físicamente, se marcan como `is_active=False`

### Estructura de Clases (Vistas y Formularios)
- **Vistas**: Basadas en clases de Django (CBV) con nombres claros basados en el nombre del modelo que representan
- **Organización**: Separadas por módulo de Django
- **Nomenclatura**: nombres claros basados en el nombre del modelo que representan y el tipo de clase Template, For List `*View`
- **Formularios**: Siguen el patrón `{Modelo}Form`

### Estructura de Plantillas HTML
- **Herencia**: Todas heredan de `base.html` que incluye las librerías necesarias
- **Tecnologías**: Django Templates + Vue.js (vanilla JS)
- **APP VUE**: Vue.js se utiliza para mejorar la interactividad en las plantillas, se alamcenan en vanilla js en la carpeta static
- **Delimitadores**: Vue.js usa `${}` para evitar conflictos con Django `{{}}`
- **Consistencia**: Mantener el mismo diseño entre plantillas del mismo tipo

#### Tipos de Plantillas:
1. **Lista** (`*_list.html`):
   - Vista de tabla con DataTables.net
   - Filtros adicionales en cabecera
   - Exportación a Excel y PDF

2. **Presentation** (`*_presentation.html`):
   - Muestra información detallada del registro
   - Incluye metadatos de BaseModel
   - Objetos relacionados organizados en tabs
   - Funcionalidad Vue.js para agregar registros relacionados
   - Endpoints API para modelos relacionados cuando sea necesario

3. **Formulario** (`*_form.html`):
   - Formularios de creación/edición
   - Validación frontend y backend
   - Interface responsiva

### Control de Versiones
- **Git**: Para cada paso del desarrollo, por lo que no es necesario de crear archivos de respaldo, se puede trabajar directamente sobre el código.
- **No backups**: Cambios directos al código
- **Rollback**: cvon Git es posible Revertir cambios si hay problemas

### Convenciones de Desarrollo
- **Responsividad**: Uso de clases Tailwind/DaisyUI priorizando DaisyUI para mantener la coherencia visual.
- **Consistencia**: Seguir patrones existentes
- **Modularidad**: Separación clara por funcionalidad
- **Reutilización**: Componentes y templates base


- listado de adicionales
    documento de planilla
    subir adjunto de OC ordend de compra
    SIbir adjunto de cotizacion
    check list de equipos

    

## Tabla de Códigos de Equipos

| Código | Descripción |
|--------|-------------|
| LVMNOS | LAVAMANOS |
| BTSNHM | BATERIA SANITARIA HOMBRE |
| BTSNMU | BATERIA SANITARIA MUJER |
| PTRTAP | PLANTA DE TRATAMIENTO DE AGUA POTABLE |
| PTRTAR | PLANTA DE TRATAMIENTO DE AGUA RESIDUAL |
| TNQAAC | TANQUES DE ALMACENAMIENTO AGUA CRUDA |
| TNQAAR | TANQUES DE ALMACENAMIENTO AGUA RESIDUAL |
| EST4UR | ESTACION CUADRUPLE URINARIO |
| CMPRBN | CAMPER BAÑO |

## Documentación del Modelo ResourceItem

### Campos del Modelo

#### Campos Básicos
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| `id` | AutoField | ID único del registro | ✅ |
| `name` | CharField(255) | Nombre del Equipo/Servicio | ✅ |
| `is_service` | BooleanField | Tipo: True=Servicio, False=Equipo | ✅ |
| `code` | CharField(50) | Código único del equipo/servicio | ❌ |
| `type_equipment` | CharField | Subtipo de equipo (choices) | ❌ |
| `brand` | CharField(255) | Marca del equipo | ❌ |
| `model` | CharField(255) | Modelo del equipo | ❌ |
| `serial_number` | CharField(255) | Número de serie | ❌ |
| `date_purchase` | DateField | Fecha de compra | ❌ |

#### Dimensiones Físicas
| Campo | Tipo | Descripción | Unidad |
|-------|------|-------------|--------|
| `height` | PositiveSmallIntegerField | Altura del equipo | cm |
| `width` | PositiveSmallIntegerField | Ancho del equipo | cm |
| `depth` | PositiveSmallIntegerField | Profundidad del equipo | cm |
| `weight` | PositiveSmallIntegerField | Peso del equipo | kg |

#### Capacidades
| Campo | Tipo | Descripción | Uso |
|-------|------|-------------|-----|
| `capacity_gallons` | DecimalField(10,2) | Capacidad en galones | Equipos generales |
| `plant_capacity` | CharField(255) | Capacidad específica | Plantas de tratamiento |

#### Campos de Estado (stst_*)
| Campo | Tipo | Descripción | Valores |
|-------|------|-------------|---------|
| `stst_repair_reason` | TextField | Motivo de reparación | Texto libre |
| `stst_status_equipment` | CharField | Estado del equipo | FUNCIONANDO, DAÑADO, INCOMPLETO, EN REPARACION |
| `stst_status_disponibility` | CharField | Disponibilidad | DISPONIBLE, RENTADO, FUERA DE SERVICIO |
| `stst_current_location` | CharField(255) | Ubicación actual | Texto libre |
| `stst_current_project_id` | SmallIntegerField | ID del proyecto actual | Número |
| `stst_commitment_date` | DateField | Fecha de ocupación | Fecha |
| `stst_release_date` | DateField | Fecha de liberación | Fecha |

### Campos de Checklist (have_*)

#### Para Equipos Sanitarios
| Campo | Aplicable a | Descripción |
|-------|-------------|-------------|
| `have_foot_pumps` | LVMNOS, EST4UR, CMPRBN | Bombas de pie |
| `have_paper_dispenser` | BTSNHM, BTSNMJ, EST4UR, CMPRBN | Dispensador de papel |
| `have_soap_dispenser` | Todos los sanitarios | Dispensador de jabón |
| `have_napkin_dispenser` | Todos los sanitarios | Dispensador de servilletas |
| `have_paper_towels` | LVMNOS, EST4UR, CMPRBN | Toallas de papel |
| `have_urinals` | BTSNHM, EST4UR, CMPRBN | Urinarios |
| `have_seat` | BTSNHM, BTSNMJ, CMPRBN | Asientos |
| `have_toilet_pump` | Baterías sanitarias | Bomba de baño |
| `have_sink_pump` | Baterías sanitarias | Bomba de lavamanos |
| `have_toilet_lid` | Baterías sanitarias | Llave de baño |
| `have_bathroom_bases` | Baterías sanitarias | Bases de baño |
| `have_ventilation_pipe` | Baterías sanitarias | Tubo de ventilación |

#### Para Plantas de Tratamiento
| Campo | PTRTAP | PTRTAR | Descripción |
|-------|--------|--------|-------------|
| `have_blower_brand` | ✅ | ✅ | Tiene Blower |
| `have_belt_brand` | ✅ | ✅ | Tiene Banda |
| `have_blower_pulley` | ✅ | ✅ | Tiene Pulley del Blower |
| `have_motor_pulley` | ✅ | ✅ | Tiene Pulley del Motor |
| `have_electrical_panel` | ✅ | ✅ | Tiene Panel Eléctrico |
| `have_motor_guard` | ✅ | ✅ | Tiene Guarda Motor |
| `have_pump_dosing` | ✅ | ✅ | Tiene Bomba Dosificadora |
| `have_pump_pressure` | ✅ | ✅ | Tiene Bomba de Presión |
| `have_engine` | ✅ | ✅ | Tiene Motor |
| `have_engine_guard` | ✅ | ✅ | Tiene Guarda del Motor |
| `have_hidroneumatic_tank` | ✅ | ✅ | Tiene Tanque Hidroneumático |
| `have_relay_engine` | ✅ | ✅ | Tiene Relay del Motor |
| `have_relay_blower` | ✅ | ✅ | Tiene Relay del Blower |
| `have_uv_filter` | ✅ | ❌ | Tiene Filtro UV |
| `have_pump_filter` | ✅ | ❌ | Tiene Bomba de Filtración |
| `have_sand_carbon_filter` | ✅ | ❌ | Tiene Filtro de Arena y Carbón |

### Check Lists por Tipo de Equipo

#### LVMNOS - Lavamanos
```python
LVMNOS_FIELDS = [
    'have_foot_pumps',
    'have_soap_dispenser', 
    'have_napkin_dispenser',
    'have_paper_towels'
]
```

#### BTSNHM - Batería Sanitaria Hombre
```python
BTSNHM_CHECK_LIST_FIELDS = [
    'have_paper_dispenser',
    'have_soap_dispenser',
    'have_napkin_dispenser', 
    'have_urinals',
    'have_seat',
    'have_toilet_pump',
    'have_sink_pump',
    'have_toilet_lid',
    'have_bathroom_bases',
    'have_ventilation_pipe'
]
```

#### BTSNMJ - Batería Sanitaria Mujer
```python
BTSNMJ_CHECK_LIST_FIELDS = [
    'have_paper_dispenser',
    'have_soap_dispenser',
    'have_napkin_dispenser',
    'have_seat',
    'have_toilet_pump', 
    'have_sink_pump',
    'have_toilet_lid',
    'have_bathroom_bases',
    'have_ventilation_pipe'
]
```

#### EST4UR - Estación Cuádruple Urinario
```python
EST4UR_CHECK_LIST_FIELDS = [
    'have_paper_dispenser',
    'have_soap_dispenser',
    'have_napkin_dispenser',
    'have_urinals',
    'have_toilet_pump',
    'have_sink_pump', 
    'have_toilet_lid',
    'have_foot_pumps',
    'have_paper_towels'
]
```

#### CMPRBN - Camper Baño
```python
CMPRBN_CHECK_LIST_FIELDS = [
    'have_paper_dispenser',
    'have_soap_dispenser',
    'have_napkin_dispenser',
    'have_urinals',
    'have_seat',
    'have_toilet_pump',
    'have_sink_pump',
    'have_toilet_lid',
    'have_bathroom_bases',
    'have_ventilation_pipe',
    'have_foot_pumps',
    'have_paper_towels'
]
```

#### PTRTAP - Planta de Tratamiento de Agua Potable
```python
PTRTAP_CHECK_LIST_FIELDS = [
    'have_blower_brand',
    'have_belt_brand', 
    'have_blower_pulley',
    'have_motor_pulley',
    'have_electrical_panel',
    'have_motor_guard',
    'have_relay_engine',
    'have_relay_blower',
    'have_uv_filter',
    'have_pump_filter',
    'have_pump_dosing',
    'have_pump_pressure',
    'have_engine',
    'have_engine_guard',
    'have_hidroneumatic_tank', 
    'have_sand_carbon_filter'
]
```

#### PTRTAR - Planta de Tratamiento de Agua Residual
```python
PTRTAR_CHECK_LIST = [
    'have_blower_brand',
    'have_belt_brand',
    'have_blower_pulley',
    'have_motor_pulley',
    'have_electrical_panel',
    'have_motor_guard',
    'have_relay_engine',
    'have_relay_blower',
    'have_pump_dosing',
    'have_pump_pressure',
    'have_engine',
    'have_engine_guard',
    'have_hidroneumatic_tank'
]
```

### Validaciones del Modelo

#### Agrupaciones de Validación
| Grupo | Campos Incluidos | Uso |
|-------|------------------|-----|
| `lavamanos_fields` | have_foot_pumps, have_soap_dispenser, have_paper_towels | Solo para LVMNOS |
| `sanitary_fields` | have_paper_dispenser, have_soap_dispenser, have_napkin_dispenser, have_urinals, have_seat, have_toilet_pump, have_sink_pump, have_toilet_lid, have_bathroom_bases, have_ventilation_pipe | Para equipos sanitarios |
| `plant_common_fields` | have_blower_brand, have_belt_brand, have_blower_pulley, have_motor_pulley, have_electrical_panel, have_motor_guard, have_pump_dosing, have_pump_pressure, have_engine, have_engine_guard, have_hidroneumatic_tank | Común para ambas plantas |
| `plant_potable_only_fields` | have_uv_filter, have_pump_filter, have_sand_carbon_filter | Solo para PTRTAP |
| `plant_residual_only_fields` | have_relay_engine, have_relay_blower | Solo para PTRTAR |

#### Reglas de Validación por Tipo
| Tipo de Equipo | Campos Permitidos | Campos Prohibidos | Validaciones Especiales |
|----------------|-------------------|-------------------|------------------------|
| LVMNOS | lavamanos_fields | sanitary_fields + plant_* | - |
| BTSNHM, BTSNMJ, EST4UR, CMPRBN | sanitary_fields | lavamanos_fields + plant_* | BTSNMJ no puede tener urinals |
| PTRTAP | plant_common_fields + plant_potable_only_fields | sanitary_fields + lavamanos_fields + plant_residual_only_fields | - |
| PTRTAR | plant_common_fields + plant_residual_only_fields | sanitary_fields + lavamanos_fields + plant_potable_only_fields | Requiere plant_capacity |
| TNQAAC, TNQAAR | Ninguno específico | Todos los checklist | - |

#### Validaciones Especiales
- **Estado EN REPARACION**: Requiere `stst_repair_reason`
- **BATERIA SANITARIA MUJER**: No puede tener `have_urinals = True`
- **PLANTA DE TRATAMIENTO DE AGUA RESIDUAL**: Requiere `plant_capacity` no nulo

### Tabla Completa de Campos del Modelo

| Campo | Tipo de Dato | Obligatorio/Valor por Defecto |
|-------|--------------|-------------------------------|
| **Campos Básicos** | | |
| `id` | AutoField | Obligatorio (PK) |
| `name` | CharField(255) | Obligatorio |
| `is_service` | BooleanField | False |
| `code` | CharField(50) | None (unique=True) |
| `type_equipment` | CharField(255) | None |
| `brand` | CharField(255) | None |
| `model` | CharField(255) | 'N/A' |
| `serial_number` | CharField(255) | None |
| `date_purchase` | DateField | None |
| **Dimensiones Físicas** | | |
| `height` | PositiveSmallIntegerField | None |
| `width` | PositiveSmallIntegerField | None |
| `depth` | PositiveSmallIntegerField | None |
| `weight` | PositiveSmallIntegerField | None |
| **Capacidades** | | |
| `capacity_gallons` | DecimalField(10,2) | None |
| `plant_capacity` | CharField(255) | None |
| **Campos Checklist Sanitarios** | | |
| `have_foot_pumps` | BooleanField | False |
| `have_paper_dispenser` | BooleanField | False |
| `have_soap_dispenser` | BooleanField | False |
| `have_napkin_dispenser` | BooleanField | False |
| `have_paper_towels` | BooleanField | False |
| `have_urinals` | BooleanField | False |
| `have_seat` | BooleanField | False |
| `have_toilet_pump` | BooleanField | False |
| `have_sink_pump` | BooleanField | False |
| `have_toilet_lid` | BooleanField | False |
| `have_bathroom_bases` | BooleanField | False |
| `have_ventilation_pipe` | BooleanField | False |
| **Campos Checklist Plantas** | | |
| `have_blower_brand` | BooleanField | False |
| `have_belt_brand` | BooleanField | False |
| `have_blower_pulley` | BooleanField | False |
| `have_motor_pulley` | BooleanField | False |
| `have_electrical_panel` | BooleanField | False |
| `have_motor_guard` | BooleanField | False |
| `have_relay_engine` | BooleanField | False |
| `have_relay_blower` | BooleanField | False |
| `have_uv_filter` | BooleanField | False |
| `have_pump_filter` | BooleanField | False |
| `have_pump_dosing` | BooleanField | False |
| `have_pump_pressure` | BooleanField | False |
| `have_engine` | BooleanField | False |
| `have_engine_guard` | BooleanField | False |
| `have_hidroneumatic_tank` | BooleanField | False |
| `have_sand_carbon_filter` | BooleanField | False |
| **Equipos Especiales - Marca/Modelo** | | |
| `relay_engine` | CharField(255) | None |
| `relay_blower` | CharField(255) | None |
| `blower_brand` | CharField(255) | None |
| `blower_model` | CharField(255) | None |
| `engine_fases` | CharField(255) | None |
| `engine_brand` | CharField(255) | None |
| `engine_model` | CharField(255) | None |
| `belt_brand` | CharField(255) | None |
| `belt_model` | CharField(255) | None |
| `belt_type` | CharField(1) | None |
| `blower_pulley_brand` | CharField(255) | None |
| `blower_pulley_model` | CharField(255) | None |
| `motor_pulley_brand` | CharField(255) | None |
| `motor_pulley_model` | CharField(255) | None |
| `electrical_panel_brand` | CharField(255) | None |
| `electrical_panel_model` | CharField(255) | None |
| `engine_guard_brand` | CharField(255) | None |
| `engine_guard_model` | CharField(255) | None |
| **Plantas de Agua Potable** | | |
| `pump_filter` | CharField(255) | None |
| `pump_pressure` | CharField(255) | None |
| `pump_dosing` | CharField(255) | None |
| `sand_carbon_filter` | CharField(255) | None |
| `hidroneumatic_tank` | CharField(255) | None |
| `uv_filter` | CharField(255) | None |
| **Estado del Equipo** | | |
| `stst_repair_reason` | TextField | None |
| `stst_status_equipment` | CharField(255) | 'FUNCIONANDO' |
| `stst_status_disponibility` | CharField(255) | 'DISPONIBLE' |
| `stst_current_location` | CharField(255) | None |
| `stst_current_project_id` | SmallIntegerField | None |
| `stst_commitment_date` | DateField | None |
| `stst_release_date` | DateField | None |

```sql
-- Ajustar secuencias para tablas con datos preexistentes

SELECT setval('equipment_certificationvehicle_id_seq', (SELECT COALESCE(MAX(id), 0) FROM equipment_certificationvehicle)+1);
SELECT setval('equipment_historicalcertificationvehicle_history_id_seq', (SELECT COALESCE(MAX(history_id), 0) FROM equipment_historicalcertificationvehicle)+1);
SELECT setval('equipment_historicalpassvehicle_history_id_seq', (SELECT COALESCE(MAX(history_id), 0) FROM equipment_historicalpassvehicle)+1);
SELECT setval('equipment_historicalresourceitem_history_id_seq', (SELECT COALESCE(MAX(history_id), 0) FROM equipment_historicalresourceitem)+1);
SELECT setval('equipment_historicalvehicle_history_id_seq', (SELECT COALESCE(MAX(history_id), 0) FROM equipment_historicalvehicle)+1);
SELECT setval('equipment_passvehicle_id_seq', (SELECT COALESCE(MAX(id), 0) FROM equipment_passvehicle)+1);
SELECT setval('equipment_resourceitem_id_seq', (SELECT COALESCE(MAX(id), 0) FROM equipment_resourceitem)+1);
SELECT setval('equipment_vehicle_id_seq', (SELECT COALESCE(MAX(id), 0) FROM equipment_vehicle)+1);

-- === PROJECTS SEQUENCES ===
SELECT setval('projects_chaincustodydetail_id_seq', (SELECT COALESCE(MAX(id), 0) FROM projects_chaincustodydetail)+1);
SELECT setval('projects_custodychain_id_seq', (SELECT COALESCE(MAX(id), 0) FROM projects_custodychain)+1);
SELECT setval('projects_finaldispositioncertificate_id_seq', (SELECT COALESCE(MAX(id), 0) FROM projects_finaldispositioncertificate)+1);
SELECT setval('projects_finaldispositioncertificatedetail_id_seq', (SELECT COALESCE(MAX(id), 0) FROM projects_finaldispositioncertificatedetail)+1);
SELECT setval('projects_historicalchaincustodydetail_history_id_seq', (SELECT COALESCE(MAX(history_id), 0) FROM projects_historicalchaincustodydetail)+1);
SELECT setval('projects_historicalcustodychain_history_id_seq', (SELECT COALESCE(MAX(history_id), 0) FROM projects_historicalcustodychain)+1);
SELECT setval('projects_historicalfinaldispositioncertificate_history_id_seq', (SELECT COALESCE(MAX(history_id), 0) FROM projects_historicalfinaldispositioncertificate)+1);
SELECT setval('projects_historicalfinaldispositioncertificatedetail_history_id_seq', (SELECT COALESCE(MAX(history_id), 0) FROM projects_historicalfinaldispositioncertificatedetail)+1);
SELECT setval('projects_historicalpartner_history_id_seq', (SELECT COALESCE(MAX(history_id), 0) FROM projects_historicalpartner)+1);
SELECT setval('projects_historicalproject_history_id_seq', (SELECT COALESCE(MAX(history_id), 0) FROM projects_historicalproject)+1);
SELECT setval('projects_historicalprojectresourceitem_history_id_seq', (SELECT COALESCE(MAX(history_id), 0) FROM projects_historicalprojectresourceitem)+1);
SELECT setval('projects_historicalsheetproject_history_id_seq', (SELECT COALESCE(MAX(history_id), 0) FROM projects_historicalsheetproject)+1);
SELECT setval('projects_historicalsheetprojectdetail_history_id_seq', (SELECT COALESCE(MAX(history_id), 0) FROM projects_historicalsheetprojectdetail)+1);
SELECT setval('projects_partner_id_seq', (SELECT COALESCE(MAX(id), 0) FROM projects_partner)+1);
SELECT setval('projects_project_id_seq', (SELECT COALESCE(MAX(id), 0) FROM projects_project)+1);
SELECT setval('projects_projectresourceitem_id_seq', (SELECT COALESCE(MAX(id), 0) FROM projects_projectresourceitem)+1);
SELECT setval('projects_sheetproject_id_seq', (SELECT COALESCE(MAX(id), 0) FROM projects_sheetproject)+1);
SELECT setval('projects_sheetprojectdetail_id_seq', (SELECT COALESCE(MAX(id), 0) FROM projects_sheetprojectdetail)+1);

-- Verificar que las secuencias se ajustaron correctamente
SELECT 
    schemaname,
    sequencename,
    last_value
FROM pg_sequences 
WHERE schemaname = 'public'
    AND (sequencename LIKE 'equipment_%' OR sequencename LIKE 'projects_%')
ORDER BY sequencename;

-- Verificar los valores actuales de las secuencias
SELECT 
    schemaname,
    sequencename,
    last_value
FROM pg_sequences 
WHERE schemaname = 'public'
ORDER BY sequencename;