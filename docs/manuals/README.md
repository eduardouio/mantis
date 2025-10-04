# API de Recursos en Proyectos

Este módulo contiene los endpoints para gestionar la asignación y liberación de recursos (equipos) en proyectos.

## Endpoints

### 1. ResourcesAvailableAPI
**Archivo**: `ResourcesAvailable.py`

Endpoint para listar recursos disponibles para asignar a un proyecto.

#### GET - Listar recursos disponibles
```
GET /api/projects/resources/available
GET /api/projects/resources/available?type_equipment=BTSNHM
GET /api/projects/resources/available?status_equipment=FUNCIONANDO
GET /api/projects/resources/available?search=BS-001
GET /api/projects/resources/available?exclude_services=false
```

**Parámetros query (todos opcionales):**
- `type_equipment`: Filtrar por tipo de equipo (LVMNOS, BTSNHM, etc.)
- `status_equipment`: Filtrar por estado (FUNCIONANDO, DAÑADO, etc.)
- `search`: Buscar por código o nombre
- `exclude_services`: Excluir servicios (default: true)

**Respuesta:**
```json
{
    "success": true,
    "count": 15,
    "data": [
        {
            "id": 5,
            "code": "BS-001",
            "name": "Batería Sanitaria Hombre",
            "type_equipment": "BTSNHM",
            "type_equipment_display": "BATERIA SANITARIA HOMBRE",
            "brand": "ACME",
            "model": "BS-2024",
            "status_equipment": "FUNCIONANDO",
            "status_disponibility": "DISPONIBLE",
            "current_location": "BASE PEISOL",
            "capacity_gallons": "500.00"
        },
        ...
    ]
}
```

---

### 2. AddResourceProjectAPI
**Archivo**: `AddResourceProject.py`

Endpoint para agregar recursos a un proyecto.

#### POST - Agregar recurso
```
POST /api/projects/resources/add
```

**Payload:**
```json
{
    "project_id": 1,
    "resource_item_id": 5,
    "rent_cost": 150.00,
    "maintenance_cost": 50.00,
    "maintenance_interval_days": 7,
    "operation_start_date": "2025-10-05",
    "operation_end_date": "2025-12-31"  // Opcional
}
```

**Respuesta exitosa:**
```json
{
    "success": true,
    "message": "Recurso BS-001 agregado al proyecto",
    "data": {
        "id": 10,
        "project_id": 1,
        "project_name": "Empresa XYZ",
        "resource_id": 5,
        "resource_code": "BS-001",
        "resource_name": "Batería Sanitaria Hombre",
        "rent_cost": "150.00",
        "maintenance_cost": "50.00",
        "maintenance_interval_days": 7,
        "operation_start_date": "2025-10-05",
        "operation_end_date": "2025-12-31",
        "is_retired": false,
        "retirement_date": null,
        "retirement_reason": null
    }
}
```

**Cambios en ResourceItem al agregar:**
- `stst_status_disponibility` → `'RENTADO'`
- `stst_current_location` → ubicación del proyecto (o nombre si no hay ubicación)
- `stst_current_project_id` → ID del proyecto
- `stst_commitment_date` → fecha de inicio de operación (o hoy si es pasada)
- `stst_release_date` → fecha de fin de operación (o fecha fin del proyecto)

#### GET - Listar recursos
```
GET /api/projects/resources/add?project_id=1
GET /api/projects/resources/add?resource_id=5
```

**Respuesta:**
```json
{
    "success": true,
    "data": [
        {
            "id": 10,
            "project_id": 1,
            "project_name": "Empresa XYZ",
            "resource_id": 5,
            "resource_code": "BS-001",
            "resource_name": "Batería Sanitaria Hombre",
            ...
        }
    ]
}
```

---

### 3. DeleteResourceProjectAPI
**Archivo**: `DeleteResourceProject.py`

Endpoint para eliminar (liberar) recursos de un proyecto.

#### DELETE - Eliminar recurso
```
DELETE /api/projects/resources/delete
```

**Payload:**
```json
{
    "project_resource_id": 10,
    "retirement_reason": "Finalización del proyecto"  // Opcional
}
```

**Respuesta exitosa:**
```json
{
    "success": true,
    "message": "Recurso BS-001 liberado del proyecto",
    "data": {
        "resource_code": "BS-001",
        "resource_id": 5,
        "status": "DISPONIBLE",
        "location": "BASE PEISOL"
    }
}
```

**Cambios en ResourceItem al eliminar:**
- `stst_status_disponibility` → `'DISPONIBLE'`
- `stst_current_location` → `'BASE PEISOL'`
- `stst_current_project_id` → `NULL`
- `stst_commitment_date` → `NULL`
- `stst_release_date` → `NULL`

**Cambios en ProjectResourceItem:**
- `is_retired` → `True`
- `retirement_date` → fecha actual
- `retirement_reason` → razón proporcionada o "Liberado del proyecto"

#### GET - Obtener información de recurso en proyecto
```
GET /api/projects/resources/delete?project_resource_id=10
```

**Respuesta:**
```json
{
    "success": true,
    "data": {
        "id": 10,
        "project_id": 1,
        "resource_id": 5,
        ...
    }
}
```

---

## Validaciones

### AddResourceProjectAPI
- Campos requeridos: `project_id`, `resource_item_id`, `rent_cost`, `maintenance_cost`, `operation_start_date`
- El recurso debe estar DISPONIBLE (no RENTADO)
- Las fechas deben estar en formato YYYY-MM-DD
- `operation_end_date` no puede ser anterior a `operation_start_date`

### DeleteResourceProjectAPI
- Campo requerido: `project_resource_id`
- El recurso no debe estar retirado (`is_retired=False`)
- TODO: Validar que no tenga mantenimientos asociados

---

## Transacciones Atómicas

Ambos endpoints usan `@transaction.atomic` para garantizar que:
- Si falla la actualización del `ResourceItem`, se revierte la creación/actualización del `ProjectResourceItem`
- Se mantiene la consistencia de datos entre tablas

---

## Manejo de Errores

### Errores comunes:

**400 Bad Request**
- JSON inválido
- Campos requeridos faltantes
- Recurso ya rentado
- Fechas inválidas
- Validación de modelo fallida

**404 Not Found**
- Proyecto no existe o está inactivo
- Recurso no existe o está inactivo
- ProjectResourceItem no existe

**500 Internal Server Error**
- Errores no controlados (se registran en logs)

---

## Ejemplo de uso en URLs

```python
# api/projects/urls.py
from django.urls import path
from .ResourcesAvailable import ResourcesAvailableAPI
from .AddResourceProject import AddResourceProjectAPI
from .DeleteResourceProject import DeleteResourceProjectAPI

urlpatterns = [
    path(
        'resources/available',
        ResourcesAvailableAPI.as_view(),
        name='resources_available'
    ),
    path(
        'resources/add',
        AddResourceProjectAPI.as_view(),
        name='add_resource_project'
    ),
    path(
        'resources/delete',
        DeleteResourceProjectAPI.as_view(),
        name='delete_resource_project'
    ),
]
```

---

## Notas de implementación

1. **Autenticación**: Los endpoints verifican si hay un usuario autenticado para registrar quién realizó la acción
2. **Soft Delete**: No se eliminan registros físicamente, se marcan como `is_retired=True`
3. **Historial**: Todos los cambios se registran en el historial de Django Simple History
4. **Fechas**: Si no se proporciona `operation_end_date`, se usa la fecha de fin del proyecto
5. **Ubicación por defecto**: Si el proyecto no tiene ubicación, se usa "Proyecto {nombre_partner}"

---

## TODO
- [ ] Implementar validación de mantenimientos antes de eliminar un recurso
- [ ] Agregar endpoint para actualizar costos/fechas sin eliminar y volver a agregar
- [ ] Considerar endpoint para transferir recurso entre proyectos
