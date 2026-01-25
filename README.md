# generamos las migraciones
```bash
python manage.py makemigrations accounts
python manage.py makemigrations equipment projects
python manage.py migrate
python manage.py sowseed

manage.py populate_history --auto   
```


# linea a linea para unix
```bash
./manage.py makemigrations accounts equipment projects
./manage.py migrate
./manage.py sowseed
./manage.py populate_history --auto   
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


## exportar datos a json
``` bash
python manage.py dumpdata \
  --natural-foreign \
  --natural-primary \
  --exclude auth.permission \
  --exclude contenttypes \
  --exclude admin.logentry \
  > data.json

## importar datos desde json, especificar la ruta

``` bash
python manage.py loaddata data.json
./manage.py loaddata ../../docs/sql/data-2026125154557.json -v 3  


```python

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

TODO
-[] Cuando un recurso se asigna se marca como no disponible, no aplica con SERVICIOS


``` sql
-- detalle de proyectos
select * from projects_project pp where pp.id = 6;


-- recursos de proyectos
select * from projects_projectresourceitem pp where pp.project_id  = 6

-- hojas de trabajo de proyecto
select * from projects_sheetproject ps  where ps.project_id = 4;
-- cadenas de custodia de la planilla anterior

select * from projects_custodychain pc where pc.sheet_project_id = 174;


-- detalles de cadena de custodia 1
select * from projects_chaincustodydetail pc where pc.custody_chain_id = 174

-- detalles de cadena de custodia 42
select * from projects_chaincustodydetail pc where pc.custody_chain_id = 42

-- listar migraciones 
select * from django_migrations dm 