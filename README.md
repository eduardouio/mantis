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



# un solo comando para unix
```bash
./manage.py makemigrations accounts &&
./manage.py makemigrations equipment projects &&
./manage.py migrate &&
./manage.py sowseed 
```
