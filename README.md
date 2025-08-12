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
