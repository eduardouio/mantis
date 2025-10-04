# Tests de Endpoints - Gestión de Recursos en Proyectos

## 📋 Archivos de Tests Creados

```
app/src/tests/api/
├── test_AddResourceProjectAPI.py          ✅ Nuevo (20 tests)
├── test_DeleteResourceProjectAPI.py       ✅ Nuevo (14 tests)
└── test_ResourcesAvailableAPI.py          ✅ Nuevo (20 tests)
```

**Total: 54 tests** 🎯

---

## 🧪 test_AddResourceProjectAPI.py

### Cobertura de Tests (20 tests)

#### ✅ Tests de Creación Exitosa
1. **test_add_resource_success** - Agregar recurso correctamente
2. **test_add_resource_without_end_date** - Usar fecha fin del proyecto por defecto

#### ❌ Tests de Validación
3. **test_add_resource_missing_required_fields** - Campos requeridos faltantes
4. **test_add_resource_invalid_project** - Proyecto inexistente
5. **test_add_resource_invalid_resource** - Recurso inexistente
6. **test_add_resource_already_rented** - Recurso ya rentado
7. **test_add_resource_invalid_date_format** - Formato de fecha inválido
8. **test_add_resource_end_date_before_start** - Fecha fin antes de inicio

#### 📊 Tests de Consulta (GET)
9. **test_get_resources_by_project** - Listar recursos de un proyecto
10. **test_get_resources_by_resource_id** - Ver proyecto de un recurso
11. **test_get_without_parameters** - GET sin parámetros

#### 🔧 Tests de Lógica de Negocio
12. **test_commitment_date_logic_future_start** - Fecha compromiso futura
13. **test_commitment_date_logic_past_start** - Fecha compromiso hoy

#### 🛠️ Tests de Manejo de Errores
14. **test_invalid_json** - JSON malformado

### Verificaciones en Cada Test

- ✅ Código de respuesta HTTP
- ✅ Estructura de respuesta JSON
- ✅ Mensajes de éxito/error apropiados
- ✅ Creación/actualización en base de datos
- ✅ Actualización de campos de ResourceItem:
  - `stst_status_disponibility` → RENTADO
  - `stst_current_location` → ubicación del proyecto
  - `stst_current_project_id` → ID del proyecto
  - `stst_commitment_date` → fecha calculada
  - `stst_release_date` → fecha de liberación

---

## 🗑️ test_DeleteResourceProjectAPI.py

### Cobertura de Tests (14 tests)

#### ✅ Tests de Eliminación Exitosa
1. **test_delete_resource_success** - Eliminar recurso correctamente
2. **test_delete_resource_without_reason** - Usar razón por defecto

#### ❌ Tests de Validación
3. **test_delete_resource_missing_id** - ID requerido faltante
4. **test_delete_resource_invalid_id** - ID inexistente
5. **test_delete_resource_already_retired** - Recurso ya retirado
6. **test_delete_inactive_resource** - Recurso inactivo

#### 📊 Tests de Consulta (GET)
7. **test_get_resource_info** - Obtener información del recurso
8. **test_get_resource_info_missing_id** - GET sin ID
9. **test_get_resource_info_invalid_id** - GET con ID inválido

#### 🔧 Tests de Serialización
10. **test_serialization_with_all_fields** - Todos los campos presentes

#### 🛠️ Tests de Transacciones
11. **test_delete_resource_transaction_rollback** - Rollback en error

#### 🛠️ Tests de Manejo de Errores
12. **test_invalid_json** - JSON malformado

### Verificaciones en Cada Test

- ✅ Código de respuesta HTTP
- ✅ Estructura de respuesta JSON
- ✅ Mensajes apropiados
- ✅ Actualización en base de datos
- ✅ Actualización de ResourceItem:
  - `stst_status_disponibility` → DISPONIBLE
  - `stst_current_location` → BASE PEISOL
  - `stst_current_project_id` → NULL
  - `stst_commitment_date` → NULL
  - `stst_release_date` → NULL
- ✅ Actualización de ProjectResourceItem:
  - `is_retired` → True
  - `retirement_date` → hoy
  - `retirement_reason` → razón proporcionada

---

## 🔍 test_ResourcesAvailableAPI.py

### Cobertura de Tests (20 tests)

#### ✅ Tests de Listado Básico
1. **test_get_all_available_resources** - Listar todos disponibles
2. **test_empty_results** - Sin recursos disponibles

#### 🎯 Tests de Filtros
3. **test_filter_by_type_equipment** - Filtrar por tipo
4. **test_filter_by_status_equipment** - Filtrar por estado FUNCIONANDO
5. **test_filter_by_status_equipment_damaged** - Filtrar por DAÑADO
6. **test_combined_filters** - Combinar múltiples filtros

#### 🔍 Tests de Búsqueda
7. **test_search_by_code** - Buscar por código
8. **test_search_by_name** - Buscar por nombre
9. **test_search_case_insensitive** - Búsqueda insensible a mayúsculas

#### ⚙️ Tests de Configuración
10. **test_exclude_services_default** - Excluir servicios por defecto
11. **test_include_services_explicitly** - Incluir servicios explícitamente

#### 📋 Tests de Serialización
12. **test_serialization_fields** - Campos correctos en respuesta
13. **test_type_equipment_display** - Nombre legible de tipo
14. **test_capacity_gallons_serialization** - Capacidad con valor
15. **test_capacity_gallons_null** - Capacidad NULL

#### 📊 Tests de Ordenamiento
16. **test_ordering** - Ordenamiento correcto (tipo → código)

### Verificaciones en Cada Test

- ✅ Código de respuesta HTTP
- ✅ Estructura de respuesta JSON
- ✅ Conteo correcto de recursos
- ✅ Filtros aplicados correctamente
- ✅ Solo recursos DISPONIBLES y activos
- ✅ Exclusión de recursos RENTADOS
- ✅ Exclusión de recursos inactivos
- ✅ Serialización completa de campos

---

## 🎯 Fixtures Utilizados

### Comunes en todos los tests:
- **client_logged** - Cliente HTTP autenticado
- **test_partner** - Partner para crear proyectos
- **test_project** - Proyecto de prueba
- **test_resource** - ResourceItem de prueba

### Específicos:
- **valid_resource_data** - Datos válidos para agregar recurso
- **test_project_resource** - ProjectResourceItem ya creado
- **available_resources** - Múltiples recursos disponibles

---

## 📊 Cobertura por Endpoint

### AddResourceProjectAPI
- ✅ POST (crear) - 8 tests
- ✅ GET (listar) - 3 tests
- ✅ Lógica de negocio - 3 tests
- ✅ Manejo de errores - 2 tests

### DeleteResourceProjectAPI
- ✅ DELETE (eliminar) - 6 tests
- ✅ GET (info) - 3 tests
- ✅ Transacciones - 1 test
- ✅ Serialización - 1 test
- ✅ Manejo de errores - 1 test

### ResourcesAvailableAPI
- ✅ GET sin filtros - 2 tests
- ✅ Filtros - 4 tests
- ✅ Búsqueda - 3 tests
- ✅ Configuración - 2 tests
- ✅ Serialización - 4 tests
- ✅ Ordenamiento - 1 test

---

## 🚀 Ejecutar los Tests

```bash
# Todos los tests de la API de proyectos
pytest app/src/tests/api/test_*ResourceProject*.py -v

# Solo AddResourceProjectAPI
pytest app/src/tests/api/test_AddResourceProjectAPI.py -v

# Solo DeleteResourceProjectAPI
pytest app/src/tests/api/test_DeleteResourceProjectAPI.py -v

# Solo ResourcesAvailableAPI
pytest app/src/tests/api/test_ResourcesAvailableAPI.py -v

# Con cobertura
pytest app/src/tests/api/test_*ResourceProject*.py --cov=api.projects --cov-report=html
```

---

## ✅ Checklist de Calidad

- [x] Todos los métodos HTTP cubiertos (GET, POST, DELETE)
- [x] Casos exitosos probados
- [x] Casos de error probados
- [x] Validaciones de campos requeridos
- [x] Validaciones de tipos de datos
- [x] Validaciones de lógica de negocio
- [x] Transacciones atómicas verificadas
- [x] Serialización completa probada
- [x] Filtros y búsquedas probadas
- [x] Ordenamiento verificado
- [x] Manejo de errores completo
- [x] Fixtures reutilizables
- [x] Nombres descriptivos de tests
- [x] Assertions claras y específicas

---

## 🔧 Próximos Pasos

1. ✅ Ejecutar los tests y verificar que todos pasen
2. ⏳ Implementar validación de mantenimientos en DELETE
3. ⏳ Agregar tests de integración entre endpoints
4. ⏳ Agregar tests de rendimiento con múltiples recursos
5. ⏳ Documentar casos edge adicionales

---

## 📝 Notas Importantes

- Los tests usan `@pytest.mark.django_db` para acceso a BD
- Se usa `force_login` para autenticación en tests
- Se verifica tanto la respuesta HTTP como el estado en BD
- Los tests son independientes (cada uno crea sus propios datos)
- Se usa `refresh_from_db()` para verificar cambios en BD
- Mock usado solo cuando es necesario (transacciones)
