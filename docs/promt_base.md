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

### pruebas automatizadas
   Se esta usando pytest para las pruebas,el entornio se encuentra configuardo, existe un test  /app/src/tests/BaseTestView.py, este se hereda en todos los test que se hacen a vistas de django, tiene validaciones para sesion de usuario