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

# Plan para corrección de error TemplateSyntaxError en equipment_form.html

## Notes
- Se detectó un TemplateSyntaxError por uso de `{% static %}` sin haber cargado el tag.
- Se corrigió agregando `{% load static %}` después de `{% extends 'base/base.html' %}` en el template.
- El script jQuery del template ya está implementado (y mejorado) en `resourceitem_app.js` usando Vue.js, por lo que no es necesario migrar ni duplicar la lógica.
- El contenedor `#resourceItemApp` ya fue agregado al template para que Vue.js funcione correctamente.
- Ya se revisó el modelo completo y la documentación, por lo que la estructura y campos de equipos y servicios están claros para el diseño del asistente.
- Ya se implementó la estructura básica del asistente paso a paso en el template y en el archivo Vue.js. Falta verificar el flujo visual y de interacción.
- Ya se implementó la lógica de visibilidad de campos dinámica y específica para cada tipo y subtipo de equipo en el asistente.
- Se detectó un nuevo TemplateSyntaxError por el uso de expresiones Vue.js (`{{ index + 1 }}`) que Django intenta procesar como template propio.
- Se está corrigiendo usando los tags `{% verbatim %}` y `{% endverbatim %}` para rodear los bloques Vue en el template y evitar el conflicto.
- Se añadió `{% endverbatim %}` al final del bloque Vue.js para evitar errores de renderizado.
- Se solicitó suavizar los colores de los bordes y usar componentes `card` de Tailwind para las opciones del asistente, mejorando la experiencia visual.
- Mejora visual de tarjetas implementada en pasos 1 y 2 del asistente.
- Se reportó bug: el asistente inicia en el paso 2 en vez de en el paso 1, se debe corregir para que siempre inicie en el paso 1.
- Se identificó que la lógica en el método mounted() de Vue avanza el paso automáticamente si detecta valores en el formulario, lo cual debe ajustarse para nuevos registros.
- Se corrigió la lógica para que el asistente siempre inicie en el paso 1 en formularios de creación.
- Se solicitó eliminar el encabezado "Registrar Nuevo Equipo" de la parte superior del formulario.
- Encabezado eliminado correctamente del template.
- Advertencia detectada: "Identifier 'ResourceItemApp' has already been declared". Revisar y corregir posibles dobles inclusiones del script o doble inicialización de Vue, ya que esto bloquea la funcionalidad.
- Doble inclusión de Vue.js corregida en base.html, usando solo la versión de producción.
- El error de doble declaración de 'ResourceItemApp' persiste. Probable doble inclusión del script resourceitem_app.js. Revisar cómo y dónde se incluye este archivo en los templates.
- Doble inclusión de resourceitem_app.js corregida usando el bloque script_app en equipment_form.html, evitando conflictos y doble inicialización.
- Recordatorio: siempre cargar los tags necesarios (`static`, `humanize`, etc.) al inicio de los templates que los usen.

## Task List
- [x] Identificar la causa del TemplateSyntaxError en equipment_form.html
- [x] Agregar `{% load static %}` al inicio del template para habilitar el uso del tag `{% static %}`
- [x] Verificar que el elemento Vue (`#resourceItemApp`) esté presente en el HTML para que la app funcione correctamente
- [x] Revisar y corregir la doble inclusión del script o doble inicialización de Vue (error Identifier 'ResourceItemApp' has already been declared)
- [x] Revisar y corregir la doble inclusión del script resourceitem_app.js (error Identifier 'ResourceItemApp' has already been declared)
- [ ] Verificar que el template renderiza correctamente y no aparecen nuevos errores
- [ ] Verificar que la app Vue funciona correctamente y controla la visibilidad de campos dinámicos
- [x] Diseñar el asistente paso a paso para el formulario según el modelo y EquiposDocs.md
  - [x] Definir los pasos del asistente (tipo de registro, tipo de equipo, campos específicos)
  - [x] Definir la lógica de visibilidad de campos para cada tipo/subtipo
- [x] Agregar `{% endverbatim %}` donde corresponda en el template para cerrar el bloque y evitar errores de renderizado
- [x] Suavizar los colores de los bordes y usar `card` de Tailwind para las opciones del asistente
- [x] Analizar y ubicar la causa del bug de inicio en paso 2
- [x] Corregir: el asistente debe iniciar siempre en el paso 1, no en el paso 2
- [x] Eliminar el encabezado "Registrar Nuevo Equipo" del formulario

## Current Goal
Validar visual y funcionalmente el asistente y el formulario dinámico