-- ============================================================================
-- SCRIPT DE VALIDACIÓN PARA MIGRACIÓN
-- ============================================================================
-- Este script contiene consultas SELECT para validar el estado de los datos
-- ANTES y DESPUÉS de ejecutar cada UPDATE del script de migración
-- ============================================================================

-- ============================================================================
-- 1. VALIDACIÓN: Actualización del detalle al nuevo formato de los recursos
-- ============================================================================

-- ANTES: Ver registros que serán actualizados y su formato actual
SELECT 
    id,
    detailed_description AS formato_actual,
    CASE
        WHEN detailed_description ~ ' - ' THEN 'Formato con guion'
        ELSE 'Formato sin guion'
    END AS tipo_formato,
    CASE
        WHEN detailed_description ~ ' - ' THEN
            regexp_replace(
                detailed_description,
                '^([A-Z]+)\s+([A-Z0-9\-]+)\s+-\s+(.+)$',
                '\1 / \2 / \3'
            )
        ELSE
            regexp_replace(
                detailed_description,
                '^([A-Z]+)\s+([A-Z0-9\-]+)$',
                '\1 / \2'
            )
    END AS formato_nuevo_preview
FROM projects_projectresourceitem
WHERE detailed_description IS NOT NULL
ORDER BY id;

-- DESPUÉS: Verificar que el formato se actualizó correctamente
SELECT 
    id,
    detailed_description AS formato_actualizado,
    CASE
        WHEN detailed_description ~ ' / ' THEN 'Formato actualizado correctamente'
        ELSE 'Formato NO actualizado'
    END AS estado_validacion
FROM projects_projectresourceitem
WHERE detailed_description IS NOT NULL
ORDER BY id;

-- Contar registros actualizados vs no actualizados
SELECT 
    CASE
        WHEN detailed_description ~ ' / ' THEN 'Actualizado'
        ELSE 'No actualizado'
    END AS estado,
    COUNT(*) AS cantidad
FROM projects_projectresourceitem
WHERE detailed_description IS NOT NULL
GROUP BY estado;


-- ============================================================================
-- 2. VALIDACIÓN: Agregar referencia al equipo físico para tipo EQUIPO
-- ============================================================================

-- ANTES: Ver equipos que serán actualizados
SELECT 
    id,
    resource_item_id,
    type_resource,
    detailed_description,
    physical_equipment_code AS codigo_actual,
    resource_item_id AS codigo_nuevo_preview
FROM projects_projectresourceitem
WHERE type_resource = 'EQUIPO'
  AND physical_equipment_code = 0
ORDER BY id;

-- Contar registros a actualizar
SELECT 
    COUNT(*) AS equipos_a_actualizar
FROM projects_projectresourceitem
WHERE type_resource = 'EQUIPO'
  AND physical_equipment_code = 0;

-- DESPUÉS: Verificar que se actualizó correctamente
SELECT 
    id,
    resource_item_id,
    type_resource,
    detailed_description,
    physical_equipment_code,
    CASE
        WHEN physical_equipment_code = resource_item_id THEN 'OK'
        ELSE 'ERROR'
    END AS validacion
FROM projects_projectresourceitem
WHERE type_resource = 'EQUIPO'
  AND resource_item_id IS NOT NULL
ORDER BY id;

-- Contar equipos con y sin código físico
SELECT 
    CASE
        WHEN physical_equipment_code = 0 THEN 'Sin código'
        ELSE 'Con código'
    END AS estado,
    COUNT(*) AS cantidad
FROM projects_projectresourceitem
WHERE type_resource = 'EQUIPO'
GROUP BY estado;


-- ============================================================================
-- 3. VALIDACIÓN: Actualizar código físico para SERVICIO con PSL-
-- ============================================================================

-- ANTES: Ver servicios que serán actualizados
SELECT 
    pp.id,
    pp.type_resource,
    pp.detailed_description,
    pp.physical_equipment_code AS codigo_actual,
    regexp_replace(
        pp.detailed_description,
        '^.*(PSL-[A-Z0-9\-]+).*$', 
        '\1'
    ) AS codigo_psl_extraido,
    er.id AS id_equipo_relacionado,
    er.code AS codigo_equipo_relacionado
FROM projects_projectresourceitem pp
LEFT JOIN equipment_resourceitem er
  ON er.code = regexp_replace(
        pp.detailed_description,
        '^.*(PSL-[A-Z0-9\-]+).*$', 
        '\1'
      )
WHERE pp.type_resource = 'SERVICIO'
  AND pp.detailed_description ~ 'PSL-'
ORDER BY pp.id;

-- Contar servicios a actualizar
SELECT 
    COUNT(*) AS servicios_con_psl_a_actualizar
FROM projects_projectresourceitem pp
WHERE pp.type_resource = 'SERVICIO'
  AND pp.detailed_description ~ 'PSL-';

-- DESPUÉS: Verificar que se actualizó correctamente
SELECT 
    pp.id,
    pp.type_resource,
    pp.detailed_description,
    pp.physical_equipment_code,
    er.id AS id_equipo,
    er.code AS codigo_equipo,
    CASE
        WHEN pp.physical_equipment_code = er.id THEN 'OK'
        WHEN pp.physical_equipment_code = 0 THEN 'No actualizado'
        ELSE 'Verificar'
    END AS validacion
FROM projects_projectresourceitem pp
LEFT JOIN equipment_resourceitem er
  ON er.id = pp.physical_equipment_code
WHERE pp.type_resource = 'SERVICIO'
  AND pp.detailed_description ~ 'PSL-'
ORDER BY pp.id;


-- ============================================================================
-- 4. VALIDACIÓN: Casos especiales (IDs 233 y 125)
-- ============================================================================

-- ANTES: Ver estado actual de los casos especiales
SELECT 
    id,
    type_resource,
    detailed_description,
    physical_equipment_code,
    resource_item_id
FROM projects_projectresourceitem
WHERE id IN (233, 125);

-- DESPUÉS: Verificar casos especiales
SELECT 
    id,
    type_resource,
    detailed_description,
    physical_equipment_code,
    CASE
        WHEN id = 233 AND physical_equipment_code = 281 THEN 'OK'
        WHEN id = 125 AND physical_equipment_code = 783 THEN 'OK'
        ELSE 'ERROR'
    END AS validacion
FROM projects_projectresourceitem
WHERE id IN (233, 125);


-- ============================================================================
-- 5. VALIDACIÓN: Actualizar code_equipment en cadenas de custodia
-- ============================================================================

-- ANTES: Ver registros de cadena de custodia que serán actualizados
SELECT 
    cc.id,
    cc.project_resource_id,
    cc.code_equipment AS codigo_actual,
    cc.equipment AS tipo_equipo_actual,
    pp.detailed_description AS descripcion_recurso,
    pp.physical_equipment_code AS codigo_fisico_recurso,
    er.code AS codigo_equipo_relacionado
FROM projects_chaincustodydetail cc
JOIN projects_projectresourceitem pp
  ON cc.project_resource_id = pp.id
LEFT JOIN equipment_resourceitem er
  ON er.id = pp.physical_equipment_code
WHERE pp.physical_equipment_code <> 0
  AND (cc.code_equipment IS NULL OR cc.code_equipment = '')
ORDER BY cc.id;

-- Contar registros a actualizar
SELECT 
    COUNT(*) AS registros_cadena_custodia_a_actualizar
FROM projects_chaincustodydetail cc
JOIN projects_projectresourceitem pp
  ON cc.project_resource_id = pp.id
WHERE pp.physical_equipment_code <> 0
  AND (cc.code_equipment IS NULL OR cc.code_equipment = '');

-- DESPUÉS: Verificar actualización de code_equipment
SELECT 
    cc.id,
    cc.project_resource_id,
    cc.code_equipment,
    cc.equipment,
    pp.physical_equipment_code,
    er.code AS codigo_esperado,
    CASE
        WHEN cc.code_equipment = er.code THEN 'OK'
        WHEN cc.code_equipment IS NULL OR cc.code_equipment = '' THEN 'No actualizado'
        ELSE 'Verificar'
    END AS validacion
FROM projects_chaincustodydetail cc
JOIN projects_projectresourceitem pp
  ON cc.project_resource_id = pp.id
LEFT JOIN equipment_resourceitem er
  ON er.id = pp.physical_equipment_code
WHERE pp.physical_equipment_code <> 0
ORDER BY cc.id;


-- ============================================================================
-- 6. VALIDACIÓN: Caso especial de cadena de custodia (ID 233)
-- ============================================================================

-- ANTES: Ver estado del registro específico
SELECT 
    id,
    project_resource_id,
    code_equipment,
    equipment
FROM projects_chaincustodydetail
WHERE project_resource_id = 233;

-- DESPUÉS: Verificar caso especial
SELECT 
    id,
    project_resource_id,
    code_equipment,
    equipment,
    CASE
        WHEN code_equipment = 'PSL-LV-19-66866' THEN 'OK'
        ELSE 'ERROR'
    END AS validacion
FROM projects_chaincustodydetail
WHERE project_resource_id = 233;


-- ============================================================================
-- 7. VALIDACIÓN: Actualizar columna equipment con tipo de equipo
-- ============================================================================

-- ANTES: Ver registros que serán actualizados
SELECT 
    id,
    project_resource_id,
    code_equipment,
    equipment AS tipo_actual,
    regexp_replace(
        code_equipment,
        '^PSL-([A-Z]+).*$',
        '\1'
    ) AS tipo_extraido_preview
FROM projects_chaincustodydetail
WHERE (equipment IS NULL OR equipment = '')
  AND code_equipment IS NOT NULL
  AND code_equipment <> ''
ORDER BY id;

-- Contar registros a actualizar
SELECT 
    COUNT(*) AS registros_tipo_equipo_a_actualizar
FROM projects_chaincustodydetail
WHERE (equipment IS NULL OR equipment = '')
  AND code_equipment IS NOT NULL
  AND code_equipment <> '';

-- DESPUÉS: Verificar que se extrajo correctamente el tipo
SELECT 
    id,
    project_resource_id,
    code_equipment,
    equipment AS tipo_actualizado,
    CASE
        WHEN equipment IS NOT NULL AND equipment <> '' THEN 'OK'
        ELSE 'No actualizado'
    END AS validacion
FROM projects_chaincustodydetail
WHERE code_equipment IS NOT NULL
  AND code_equipment <> ''
ORDER BY id;

-- Verificar tipos extraídos
SELECT 
    equipment AS tipo_equipo,
    COUNT(*) AS cantidad
FROM projects_chaincustodydetail
WHERE equipment IS NOT NULL AND equipment <> ''
GROUP BY equipment
ORDER BY cantidad DESC;


-- ============================================================================
-- 8. VALIDACIÓN: Actualizar equipment a 'OT' para servicios sin tipo
-- ============================================================================

-- ANTES: Ver registros con equipment NULL
SELECT 
    id,
    project_resource_id,
    code_equipment,
    equipment
FROM projects_chaincustodydetail
WHERE equipment IS NULL
ORDER BY id;

-- Contar registros con equipment NULL
SELECT 
    COUNT(*) AS registros_sin_tipo_equipo
FROM projects_chaincustodydetail
WHERE equipment IS NULL;

-- DESPUÉS: Verificar que se asignó 'OT'
SELECT 
    id,
    project_resource_id,
    code_equipment,
    equipment,
    CASE
        WHEN equipment = 'OT' THEN 'OK'
        WHEN equipment IS NULL THEN 'No actualizado'
        ELSE 'Verificar'
    END AS validacion
FROM projects_chaincustodydetail
ORDER BY id;

-- Distribución de tipos de equipo después de actualización
SELECT 
    equipment,
    COUNT(*) AS cantidad
FROM projects_chaincustodydetail
GROUP BY equipment
ORDER BY cantidad DESC;


-- ============================================================================
-- 9. VALIDACIÓN: Actualizar code_equipment con detailed_description
-- ============================================================================

-- ANTES: Ver registros que serán actualizados
SELECT 
    cc.id,
    cc.project_resource_id,
    cc.code_equipment AS codigo_actual,
    pp.detailed_description AS descripcion_a_copiar
FROM projects_chaincustodydetail cc
JOIN projects_projectresourceitem pp
  ON cc.project_resource_id = pp.id
WHERE (cc.code_equipment IS NULL OR cc.code_equipment = '')
  AND pp.detailed_description IS NOT NULL
ORDER BY cc.id;

-- Contar registros a actualizar
SELECT 
    COUNT(*) AS registros_descripcion_a_copiar
FROM projects_chaincustodydetail cc
JOIN projects_projectresourceitem pp
  ON cc.project_resource_id = pp.id
WHERE (cc.code_equipment IS NULL OR cc.code_equipment = '')
  AND pp.detailed_description IS NOT NULL;

-- DESPUÉS: Verificar que se copió la descripción
SELECT 
    cc.id,
    cc.project_resource_id,
    cc.code_equipment,
    pp.detailed_description,
    CASE
        WHEN cc.code_equipment = pp.detailed_description THEN 'OK'
        WHEN cc.code_equipment IS NULL OR cc.code_equipment = '' THEN 'No actualizado'
        ELSE 'Verificar'
    END AS validacion
FROM projects_chaincustodydetail cc
JOIN projects_projectresourceitem pp
  ON cc.project_resource_id = pp.id
ORDER BY cc.id;


-- ============================================================================
-- VALIDACIÓN GENERAL FINAL
-- ============================================================================

-- Resumen de registros en projects_projectresourceitem
SELECT 
    'projects_projectresourceitem' AS tabla,
    COUNT(*) AS total_registros,
    SUM(CASE WHEN physical_equipment_code <> 0 THEN 1 ELSE 0 END) AS con_codigo_fisico,
    SUM(CASE WHEN physical_equipment_code = 0 THEN 1 ELSE 0 END) AS sin_codigo_fisico,
    SUM(CASE WHEN detailed_description ~ ' / ' THEN 1 ELSE 0 END) AS formato_actualizado
FROM projects_projectresourceitem;

-- Resumen de registros en projects_chaincustodydetail
SELECT 
    'projects_chaincustodydetail' AS tabla,
    COUNT(*) AS total_registros,
    SUM(CASE WHEN code_equipment IS NOT NULL AND code_equipment <> '' THEN 1 ELSE 0 END) AS con_codigo_equipo,
    SUM(CASE WHEN code_equipment IS NULL OR code_equipment = '' THEN 1 ELSE 0 END) AS sin_codigo_equipo,
    SUM(CASE WHEN equipment IS NOT NULL AND equipment <> '' THEN 1 ELSE 0 END) AS con_tipo_equipo,
    SUM(CASE WHEN equipment IS NULL OR equipment = '' THEN 1 ELSE 0 END) AS sin_tipo_equipo
FROM projects_chaincustodydetail;

-- Validar integridad referencial
SELECT 
    cc.id AS cadena_id,
    cc.project_resource_id,
    cc.code_equipment,
    pp.id AS recurso_existe,
    CASE
        WHEN pp.id IS NULL THEN 'ERROR: Recurso no existe'
        ELSE 'OK'
    END AS validacion_integridad
FROM projects_chaincustodydetail cc
LEFT JOIN projects_projectresourceitem pp
  ON cc.project_resource_id = pp.id
WHERE pp.id IS NULL;
