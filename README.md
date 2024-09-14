# eliminar migraciones anteriores

# generamos las migraciones
python manage.py makemigrations accounts
python manage.py makemigrations equipment projects
python manage.py migrate
python manage.py sowseed


# linea a linea para unix
./manage.py makemigrations accounts
./manage.py makemigrations equipment projects
./manage.py migrate
./manage.py sowseed



# un solo comando para unix
./manage.py makemigrations accounts &&
./manage.py makemigrations equipment projects &&
./manage.py migrate &&
./manage.py sowseed 



