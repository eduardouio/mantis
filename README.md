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
sudo systemctl restart matis.service
sudo systemctl restart daem


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