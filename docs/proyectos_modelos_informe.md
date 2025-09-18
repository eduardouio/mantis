# Informe de Modelos (Módulo Proyectos)

Propósito: Documentar la estructura actual de los modelos relacionados a gestión de proyectos para revisión y aprobación de campos (nombres, tipos, restricciones y relaciones). Incluye observaciones y puntos a definir.

Modelos cubiertos:
- Partner
- Project
- ProjectResourceItem
- SheetProject
- SheetProjectDetail
- CustodyChain
- ChainCustodyDetail
- FinalDispositionCertificate
- FinalDispositionCertificateDetail

Campos heredados comunes (BaseModel):
- notes: TextField (nullable, opcional) – Observaciones generales del registro.
- created_at: DateTime (auto_now_add) – Sello de creación.
- updated_at: DateTime (auto_now) – Última actualización.
- is_active: Boolean (default=True) – Estado lógico (activo/inactivo).
- is_deleted: Boolean (default=False) – Marcador de eliminación lógica (no usado aún para filtrar en managers específicos en estos modelos, evaluar consistencia con is_active).
- id_user_created: PositiveInteger (id usuario creador, 0 anónimo).
- id_user_updated: PositiveInteger (id usuario último editor).
- history: simple_history (auditoría completa de cambios).

---
## 1. Partner
Cliente final facturable.

| Campo | Tipo | Reglas | Notas |
|-------|------|--------|-------|
| id | AutoField (PK) | PK | Incremental. |
| business_tax_id ("RUC") | Char(15) | unique | Identificador fiscal único. Validar longitud real RUC. |
| name ("Nombre") | Char(255) | requerido | Razón social / nombre comercial. |
| email | EmailField(255) | null/blank | Opcional. |
| phone | Char(20) | null/blank | Formato no validado todavía (posible regex). |
| address ("Dirección") | Char(255) | requerido | Domicilio principal. |
| name_contact ("Nombre de Contacto") | Char(255) | null/blank | Persona de contacto. |
| notes (BaseModel) | Text | opcional | Ver si duplicado con notes heredado (ya está). |

Observaciones:
- Duplicidad potencial: se redefine "notes"? (En este modelo se declara nuevamente `notes`? No, sólo el heredado.) Confirmado sin conflicto.
- Considerar índice sobre business_tax_id (ya unique => índice implícito).

---
## 2. Project
Proyecto asociado a un Partner.

| Campo | Tipo | Reglas | Notas |
|-------|------|--------|-------|
| id | AutoField (PK) | PK | |
| partner | FK → Partner | PROTECT | Evita pérdida histórica. |
| location ("Campamento") | Char(50) | null/blank | Ubicación principal. |
| contact_name | Char(255) | requerido | Contacto operativo. |
| contact_phone | Char(15) | requerido | Falta validación de formato. |
| start_date | Date | requerido | Fecha de inicio contractual. |
| end_date | Date | requerido | Fecha de fin contractual (¿permitir null si abierto?). |
| is_closed | Boolean | default=False | Control lógico de cierre. |

Observaciones:
- end_date obligatoria: ¿escenarios de proyectos indefinidos? Podría ser null=True.
- No se guarda estado intermedio avanzado más allá de is_closed.

---
## 3. ProjectResourceItem
Asociación de un recurso físico a un proyecto con costos y ventana operativa.

| Campo | Tipo | Reglas | Notas |
|-------|------|--------|-------|
| id | AutoField (PK) | PK | |
| project | FK → Project | PROTECT | |
| resource_item | FK → equipment.ResourceItem | PROTECT | |
| rent_cost | Decimal(10,2) | requerido | Costo de renta (moneda base). |
| maintenance_cost | Decimal(10,2) | requerido | Costo de mantenimiento. |
| maintenance_interval_days | PositiveInteger | default=1 | Frecuencia (días). (Ver si mínimo >0). |
| operation_start_date | Date | requerido | Inicio uso recurso en proyecto. |
| operation_end_date | Date | requerido | Fin uso. (Permitir null si activo?). |
| is_retired | Boolean | default=False | Estado de retiro. |
| retirement_date | Date | null/blank | Fecha de retiro real. |
| retirement_reason | Text | null/blank | Motivo. |

Observaciones:
- Validación sugerida: si is_retired=True => retirement_date obligatorio.
- Posible constraint: operation_start_date <= operation_end_date.

---
## 4. SheetProject
Planilla / período facturable de un Project.

| Campo | Tipo | Reglas | Notas |
|-------|------|--------|-------|
| id | AutoField (PK) | PK | |
| project | FK → Project | PROTECT | |
| issue_date | Date | null/blank | Fecha emisión documento. |
| period_start | Date | null/blank | Inicio período (en unique_together). |
| period_end | Date | null/blank | Fin período (en unique_together). |
| status | Char(50) | choices, default=IN_PROGRESS | Ciclo de la planilla. |
| series_code | Char(50) | default='PSL-PS-00000-00' | Formato codificado (definir patrón). |
| service_type | Char(50) | default='ALQUILER DE EQUIPOS' | Tipo de servicio facturable. |
| total_gallons | PositiveSmallInteger | default=0 | Acumulado. |
| total_barrels | PositiveSmallInteger | default=0 | Acumulado. |
| total_cubic_meters | PositiveSmallInteger | default=0 | Acumulado. |
| client_po_reference | Char(50) | null/blank | Referencia orden compra. |
| contact_reference | Char(50) | null/blank | Nombre de contacto para doc. |
| contact_phone_reference | Char(50) | null/blank | Teléfono. |
| final_disposition_reference | Char(50) | null/blank | Referencia CDF. |
| invoice_reference | Char(50) | null/blank | Número de factura emitida. |
| subtotal | Decimal(10,2) | default=0 | Monto base. |
| tax_amount | Decimal(10,2) | default=0 | IVA / impuesto. |
| total | Decimal(10,2) | default=0 | Total final. |

Constraints:
- unique_together: (project, period_start, period_end) — Permite identificar período. (Revisar si ambos pueden ser null simultáneamente; en ese caso la unicidad falla en lógica).

Observaciones:
- Sugerido: validar period_start <= period_end.
- Si se permiten nulls en período, entonces uniqueness puede tener colisiones múltiples (Django trata null como diferente, pero revisar DB). Definir si deben ser NOT NULL.

---
## 5. SheetProjectDetail
Detalle de líneas dentro de una planilla.

| Campo | Tipo | Reglas | Notas |
|-------|------|--------|-------|
| id | AutoField (PK) | PK | |
| sheet_project | FK → SheetProject | PROTECT | |
| resource_item | FK → equipment.ResourceItem | PROTECT | En unique_together. |
| detail | Text | null/blank | Descripción. |
| item_unity | Char(100) | choices(DIAS, UNIDAD) | Unidad comercial. |
| quantity | Decimal(10,2) | default=0 | Cantidad medida. |
| unit_price | Decimal(10,2) | default=0 | Precio unitario. |
| total_line | Decimal(10,2) | default=0 | (quantity * unit_price) esperado. |
| unit_measurement | Char(50) | choices(UNITY, DAIS) default=DAIS | Inconsistencia ortográfica ('DAIS' vs 'DIAS'). |
| total_price | Decimal(10,2) | default=0 | Parecería duplicado de total_line o monto con otra finalidad; aclarar. |

Constraints:
- unique_together: (sheet_project, resource_item)

Observaciones:
- Duplicidad conceptual: total_line vs total_price (definir diferencia o eliminar uno).
- Armonizar choices 'DIAS' y 'DAIS'.

---
## 6. CustodyChain
Registro operativo diario (cadena de custodia) vinculado a una planilla.

| Campo | Tipo | Reglas | Notas |
|-------|------|--------|-------|
| id | AutoField (PK) | PK | |
| technical | FK → accounts.Technical | PROTECT | Técnico responsable. |
| sheet_project | FK → SheetProject | PROTECT | Periodo facturable. |
| consecutive | Char(6) | null/blank | Consecutivo campo (no validado). |
| activity_date | Date | requerido | Fecha actividad. |
| location | Char(255) | null/blank | Lugar operativo. |
| start_time | Time | null/blank | Inicio. |
| end_time | Time | null/blank | Fin. |
| time_duration | Decimal(10,2) | null/blank | Horas totales (no calculado automáticamente). |
| contact_name | Char(255) | null/blank | Contacto local. |
| contact_position | Char(255) | null/blank | Cargo contacto. |
| total_gallons | PositiveSmallInteger | default=0 | Volumen. |
| total_barrels | PositiveSmallInteger | default=0 | Volumen. |
| total_cubic_meters | PositiveSmallInteger | default=0 | Volumen. |

Observaciones:
- Posible derivación de time_duration if start_time & end_time.
- Sugerir índice (sheet_project, activity_date) para consultas por período.

---
## 7. ChainCustodyDetail
Detalle de recursos usados en una Cadena de Custodia.

| Campo | Tipo | Reglas | Notas |
|-------|------|--------|-------|
| id | AutoField (PK) | PK | |
| custody_chain | FK → CustodyChain | PROTECT | |
| resource_item | FK → equipment.ResourceItem | PROTECT | |

Observaciones:
- No uniqueness: se permitirían múltiples filas mismo recurso; definir si debe haber cantidad u otras métricas (actualmente no hay campos adicionales).

---
## 8. FinalDispositionCertificate (CDF)
Certificado que consolida volúmenes al cierre del período.

| Campo | Tipo | Reglas | Notas |
|-------|------|--------|-------|
| id | AutoField (PK) | PK | |
| payment_sheet | FK → SheetProject | PROTECT | Planilla correspondiente. |
| nro_document | Char(50) | null/blank | Formato 'PSL-CDF-YYYYMMDD-#####' (definir enforcement). |
| date | Date | null/blank | Fecha emisión. |
| text_document | Text | null/blank | Texto libre / cuerpo. |
| total_bbl | PositiveSmallInteger | default=0 | Suma barriles. |
| total_gallons | PositiveSmallInteger | default=0 | Suma galones. |
| total_m3 | PositiveSmallInteger | default=0 | Suma m³. |

Observaciones:
- Falta constraint de unicidad de nro_document.
- Validar coherencia: totales = suma detalles asociados.

---
## 9. FinalDispositionCertificateDetail
Detalle de cada cadena incluida en un CDF.

| Campo | Tipo | Reglas | Notas |
|-------|------|--------|-------|
| id | AutoField (PK) | PK | |
| final_disposition_certificate | FK → FinalDispositionCertificate | PROTECT | |
| custody_chain | FK → CustodyChain | PROTECT | |
| detail | Char(255) | default='AGUAS NEGRAS Y GRISES' | Descripción material/flujo. |
| quantity_bbl | PositiveSmallInteger | default=0 | Barriles. |
| quantity_gallons | PositiveSmallInteger | default=0 | Galones. |
| quantity_m3 | PositiveSmallInteger | default=0 | Metros cúbicos. |

Observaciones:
- Podría necesitar uniqueness (final_disposition_certificate, custody_chain) para evitar duplicados.

---
## 10. Relaciones Clave (Resumen Textual)
- Partner 1--* Project
- Project 1--* ProjectResourceItem
- Project 1--* SheetProject
- SheetProject 1--* SheetProjectDetail
- SheetProject 1--* CustodyChain
- CustodyChain 1--* ChainCustodyDetail
- SheetProject 1--* FinalDispositionCertificate
- FinalDispositionCertificate 1--* FinalDispositionCertificateDetail
- CustodyChain 1--* FinalDispositionCertificateDetail (indirecto, cada detalle enlaza ambos)

---
## 11. Riesgos / Inconsistencias Detectadas
| Tema | Descripción | Recomendación |
|------|-------------|---------------|
| Ortografía choices | 'DAIS' vs 'DIAS' / 'DÍAS' | Unificar a 'DIAS' (clave) y 'DÍAS' (label). |
| total_line vs total_price | Ambos parecen representar monto línea | Definir semántica y quizás eliminar uno. |
| time_duration manual | No se recalcula automáticamente | Implementar cálculo en save() o signal. |
| Fechas null en períodos | period_start/period_end permiten null pese a unique_together | Hacer NOT NULL si siempre debe existir. |
| operation_end_date obligatorio | No permite recurso aún en operación | Permitir null o validar estado activo. |
| Falta uniqueness en nro_document (CDF) | Posibles duplicados de certificados | Añadir unique=True. |
| Falta uniqueness en (final_disposition_certificate, custody_chain) | Duplicidad de detalle | Añadir unique_together. |
| Falta constraint horas | start_time <= end_time | Agregar validación limpia. |
| is_active vs is_deleted | Ambos flags | Definir política (quizá sólo uno). |

---
## 12. Preguntas Abiertas para Aprobación
1. ¿Project.end_date puede ser opcional para proyectos abiertos?
2. ¿Se requiere versionado / estados adicionales de Project (ej: ON_HOLD)?
3. ¿Confirmar formato definitivo de series_code y nro_document (regex)?
4. ¿Eliminar o redefinir total_price en SheetProjectDetail?
5. ¿Se agrega campo de cantidad a ChainCustodyDetail o se garantiza 1 registro por recurso?
6. ¿time_duration debe derivarse automáticamente? ¿Se redondea a 2 decimales?
7. ¿Unificar métricas de volumen (nombres bbl vs barrels) consistente en todos los modelos?
8. ¿Se requiere índice compuesto para consultas frecuentes (ej: CustodyChain.sheet_project + activity_date)?

---
## 13. Recomendaciones Técnicas (Resumen)
- Añadir validaciones de integridad (Model.clean / constraints). 
- Normalizar choices y nombres de campos para consistencia (barrels vs bbl).
- Implementar signals o métodos para recalcular subtotales y totales (SheetProject, CDF) desde detalles.
- Aplicar unique constraints propuestas para prevenir duplicados.
- Agregar índices en campos de filtrado frecuente (fechas y FK encadenadas).

---
## 14. Próximos Pasos Propuestos
1. Revisar este informe con negocio para aprobar/descartar ajustes.
2. Consolidar decisiones en una tabla final de cambios.
3. Generar migraciones para constraints y renombres.
4. Implementar validaciones y cálculos automáticos.
5. Actualizar documentación y pruebas unitarias.

---
Documento generado automáticamente (fecha de generación: 2025-08-16).
