# Resumen de Endpoints - Gestión de Recursos en Proyectos

## 📋 Archivos Creados

```
app/src/api/projects/
├── __init__.py                    ✅ Actualizado
├── AddResourceProject.py          ✅ Nuevo
├── DeleteResourceProject.py       ✅ Nuevo  
├── ResourcesAvailable.py          ✅ Nuevo
├── AddDeleteResourceProject.py    ⚠️  Deprecado (usar los nuevos)
└── README.md                      ✅ Documentación
```

---

## 🎯 Endpoints Disponibles

### 1️⃣ **Recursos Disponibles**
```
GET /api/projects/resources/available
```
Lista recursos DISPONIBLES para asignar a proyectos.

**Filtros:**
- `type_equipment` - Tipo de equipo
- `status_equipment` - Estado del equipo  
- `search` - Buscar por código/nombre
- `exclude_services` - Excluir servicios (default: true)

---

### 2️⃣ **Agregar Recurso a Proyecto**
```
POST /api/projects/resources/add
GET  /api/projects/resources/add?project_id=1
GET  /api/projects/resources/add?resource_id=5
```

**POST - Campos requeridos:**
```json
{
  "project_id": 1,
  "resource_item_id": 5,
  "rent_cost": 150.00,
  "maintenance_cost": 50.00,
  "operation_start_date": "2025-10-05"
}
```

**Actualiza ResourceItem:**
- ✅ `stst_status_disponibility` → `RENTADO`
- ✅ `stst_current_location` → ubicación del proyecto
- ✅ `stst_current_project_id` → ID del proyecto
- ✅ `stst_commitment_date` → fecha inicio (o hoy)
- ✅ `stst_release_date` → fecha fin operación

---

### 3️⃣ **Eliminar Recurso de Proyecto**
```
DELETE /api/projects/resources/delete
GET    /api/projects/resources/delete?project_resource_id=10
```

**DELETE - Campos requeridos:**
```json
{
  "project_resource_id": 10,
  "retirement_reason": "Finalización del proyecto"  // Opcional
}
```

**Actualiza ResourceItem:**
- ✅ `stst_status_disponibility` → `DISPONIBLE`
- ✅ `stst_current_location` → `BASE PEISOL`
- ✅ `stst_current_project_id` → `NULL`
- ✅ `stst_commitment_date` → `NULL`
- ✅ `stst_release_date` → `NULL`

**Actualiza ProjectResourceItem:**
- ✅ `is_retired` → `True`
- ✅ `retirement_date` → hoy
- ✅ `retirement_reason` → razón proporcionada

---

## 🔄 Flujo de Trabajo

```
1. Consultar recursos disponibles
   GET /resources/available
   
2. Agregar recurso a proyecto
   POST /resources/add
   { project_id, resource_item_id, ... }
   
3. Consultar recursos del proyecto
   GET /resources/add?project_id=1
   
4. Liberar recurso del proyecto
   DELETE /resources/delete
   { project_resource_id }
```

---

## ✅ Características

- **Transacciones atómicas**: Garantiza consistencia de datos
- **Validaciones**: Fechas, disponibilidad, campos requeridos
- **Soft delete**: No se eliminan registros físicamente
- **Auditoría**: Registra usuario que realizó la acción
- **Historial**: Django Simple History registra cambios
- **Errores claros**: Respuestas JSON estructuradas

---

## 📝 Próximos Pasos

1. Registrar estos endpoints en `urls.py`
2. Probar con Postman/curl
3. Implementar validación de mantenimientos (TODO)
4. Considerar endpoint de actualización sin eliminar
5. Frontend para gestión visual de recursos

---

## 🧪 Ejemplo de Prueba

```bash
# 1. Ver recursos disponibles
curl -X GET "http://localhost:8000/api/projects/resources/available"

# 2. Agregar recurso a proyecto
curl -X POST "http://localhost:8000/api/projects/resources/add" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "resource_item_id": 5,
    "rent_cost": 150.00,
    "maintenance_cost": 50.00,
    "operation_start_date": "2025-10-05"
  }'

# 3. Ver recursos del proyecto
curl -X GET "http://localhost:8000/api/projects/resources/add?project_id=1"

# 4. Liberar recurso
curl -X DELETE "http://localhost:8000/api/projects/resources/delete" \
  -H "Content-Type: application/json" \
  -d '{
    "project_resource_id": 10,
    "retirement_reason": "Finalización del proyecto"
  }'
```
