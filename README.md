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

## TODO:
# - [ ] Vista de proyecto
# - [ ] Que pasa cuando el proyecto es de mantenimiento
# - [ ] Como se manejan las liberaciones de los equipos
# - [ ] al agregar el equipo debes cambiar el estado y completar los datos adciionales en la fichja del euiqpo
# - [ ] En el listado de equipos, debe mostrar el cliente el proyecto y la ubicacion
# - [ ] Quitar el nombre de vehiculos
# - [ ] En la vista de proyectos mostyrar el detalle del equipo 


-- planes

# Equipos Django Model Refactor Plan

## Notes
- User wants to focus only on the Django model for equipos.
- The model can be rewritten if needed; no need to back up.
- All requirements must be taken from docs/EquiposDocs.md.
- User prefers best practices and suggestions for improvements.
- Model updated to include precio_base, servilletas, unique_together, and other doc requirements.
- All model verbose_names translated to English per user request.
- Admin registration and display fields updated to include new/changed fields.
- ResourceItemAdmin in admin.py updated to use English field names.
- Field names motor_brand/motor_model cambiados a engine_brand/engine_model en modelo y formulario.
- User requested ALL model fields, methods, and labels in English (full refactor), including method names and field names; this will require updating usages in views/forms and a migration.
- User instructed to use app/src/accounts/models/Technical.py as a reference for style and naming, and to refactor ResourceItem.py fully to English without worrying about migrations.
- All form field names and validation logic in ResourceItemForm.py have been refactored to English to match the model.
- Los tests de ResourceItem deben actualizarse para usar los nuevos nombres de campo tras el refactor.

## Task List
- [x] Review docs/EquiposDocs.md for model requirements
- [x] Refactor or rewrite the equipos Django model as needed
- [x] Ensure model follows Django best practices
- [x] Present model for user review and feedback
- [x] Refactor all model field names, methods, and labels to English
- [x] Update usages in admin, forms, and views to match new field names
- [x] Actualizar admin y forms tras cambios a engine_brand/engine_model
- [x] Generate and apply migration for renamed fields
- [ ] Present refactored model for user review
- [ ] Actualizar y validar tests de ResourceItem

## Current Goal
Actualizar y validar tests de ResourceItem

