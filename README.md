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