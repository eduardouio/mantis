
-- Actualizamos el detalle al nuevo formado de los recursos
UPDATE projects_projectresourceitem
SET detailed_description =
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
    END;


-- agregamos en los recusos del proyecto tipo equipo la referencia al equipos
-- real, en este caso es solo una copia del id a la nueva colimna, 
solo para os equipos y que tengas la columna en 0

UPDATE projects_projectresourceitem
SET physical_equipment_code = resource_item_id
WHERE type_resource = 'EQUIPO'
  AND physical_equipment_code = 0;

-- agremamos la misma validacion pero para los servicios que tengan la 
-- nueva columna en CERO y que sean SERIVICIO
UPDATE projects_projectresourceitem pp
SET physical_equipment_code = er.id
FROM equipment_resourceitem er
WHERE pp.type_resource = 'SERVICIO'
  AND pp.detailed_description ~ 'PSL-'
  AND er.code = regexp_replace(
        pp.detailed_description,
        '^.*(PSL-[A-Z0-9\-]+).*$', 
        '\1'
      );


-- casos especiales
update projects_projectresourceitem set physical_equipment_code = 281 where id = 233;
update projects_projectresourceitem set physical_equipment_code = 783 where id = 125;

-- Ahora actualizamos el detalle de las cadenas de custodia, para las columa
--  de equipo
UPDATE projects_chaincustodydetail cc
SET code_equipment = er.code
FROM projects_projectresourceitem pp
JOIN equipment_resourceitem er
  ON er.id = pp.physical_equipment_code
WHERE cc.project_resource_id = pp.id
  AND pp.physical_equipment_code <> 0
AND (cc.code_equipment IS NULL OR cc.code_equipment = '');

-- ahora camos con los casos  especiales
update 
    public.projects_chaincustodydetail 
    set code_equipment = 'PSL-LV-19-66866' 
    where project_resource_id = 233;

-- validacion de campos sueltos
select 
    cc.id, cc.equipment,
    pp.detailed_description,
    cc.code_equipment,
     cc.project_resource_id,
    er.code,
    pp.physical_equipment_code
 from public.projects_chaincustodydetail  cc
 left join public.projects_projectresourceitem pp on pp.id = cc.project_resource_id
 left join public.equipment_resourceitem er on er.id = pp.physical_equipment_code
where cc.code_equipment is null


-- ahora actulozamos para la columna de equipo BT LV etc
UPDATE projects_chaincustodydetail
SET equipment = regexp_replace(
    code_equipment,
    '^PSL-([A-Z]+).*$',
    '\1'
)
WHERE (equipment IS NULL OR equipment = '')
  AND code_equipment IS NOT NULL
  AND code_equipment <> '';


-- detalle de cadenas de custodia por servicio
update public.projects_chaincustodydetail set equipment = 'OT' where equipment is NULL ;


UPDATE projects_chaincustodydetail cc
SET code_equipment = pp.detailed_description
FROM projects_projectresourceitem pp
WHERE cc.project_resource_id = pp.id
  AND (cc.code_equipment IS NULL OR cc.code_equipment = '')
  AND pp.detailed_description IS NOT NULL
  AND pp.detailed_description <> '';
