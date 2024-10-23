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


## TODO:
# - [ ] Vista de proyecto
# - [ ] Que pasa cuando el proyecto es de mantenimiento
# - [ ] Como se manejan las liberaciones de los equipos
# - [ ] al agregar el equipo debes cambiar el estado y completar los datos adciionales en la fichja del euiqpo
# - [ ] En el listado de equipos, debe mostrar el cliente el proyecto y la ubicacion
# - [ ] Quitar el nombre de vehiculos