# Documentación Módulo de Equipos y Servicios - PEISOL MANTIS

## Introducción

El módulo de Equipos y Servicios de MANTIS es el sistema de gestión de recursos físicos y servicios de PEISOL S.A. Este módulo centraliza toda la información relacionada con equipos de campo, su estado, características técnicas, ubicación y disponibilidad para proyectos.

## Arquitectura del Sistema

### Modelo Base (BaseModel)

Todos los modelos del sistema heredan de `BaseModel`, que proporciona:

- **Auditoría automática**: Registra quién y cuándo creó/modificó cada registro
- **Historial de cambios**: Seguimiento completo de modificaciones
- **Eliminación lógica**: Los registros se marcan como inactivos en lugar de eliminarse
- **Campos comunes**:
  - `notes`: Notas adicionales
  - `created_at`: Fecha de creación
  - `updated_at`: Fecha de última actualización
  - `is_active`: Estado del registro
  - `id_user_created`: Usuario creador
  - `id_user_updated`: Usuario que actualizó

## Modelo ResourceItem - Equipos y Servicios

### Propósito
Gestión unificada de equipos físicos y servicios que ofrece PEISOL S.A., incluyendo control de estado, características técnicas, ubicación y disponibilidad.

### Tipos de Registro

#### 1. EQUIPO
Elementos físicos tangibles que se rentan o utilizan en proyectos:
- Lavamanos
- Baterías Sanitarias (Hombre/Mujer)
- Plantas de Tratamiento de Agua
- Tanques de Almacenamiento
- Camper Baño
- Estación Cuádruple Urinario

#### 2. SERVICIO
Servicios intangibles que ofrece la empresa:
- Mantenimiento preventivo
- Limpieza especializada
- Transporte de equipos
- Instalación y desinstalación
- Otros servicios técnicos

### Estados del Equipo

| Estado | Descripción |
|--------|-------------|
| **DISPONIBLE** | Equipo listo para ser rentado o asignado |
| **RENTADO** | Equipo actualmente en uso en un proyecto |
| **EN REPARACION** | Equipo fuera de servicio por mantenimiento |
| **FUERA DE SERVICIO** | Equipo no disponible permanentemente |

### Campos Comunes

#### Información Básica
- **Nombre**: Identificación descriptiva del equipo/servicio
- **Tipo**: EQUIPO o SERVICIO
- **Subtipo**: Clasificación específica según el tipo
- **Código**: Identificador único del equipo (obligatorio para equipos)
- **Número de Serie**: Identificador del fabricante
- **Marca**: Fabricante del equipo
- **Modelo**: Modelo específico del equipo
- **Fecha de Compra**: Fecha de adquisición
- **Estado**: Estado actual del equipo
- **Precio Base**: Valor de alquiler base

#### Dimensiones Físicas
- **Altura**: Medida en centímetros
- **Ancho**: Medida en centímetros
- **Profundidad**: Medida en centímetros
- **Peso**: Medida en kilogramos

#### Capacidad
- **Capacidad en Galones**: Para tanques y equipos con capacidad líquida
- **Capacidad de Planta**: Para plantas de tratamiento (10M3, 15M3, 25M3)

#### Control de Proyecto
- **Ubicación Actual**: Lugar donde se encuentra el equipo
- **ID Proyecto Actual**: Proyecto al que está asignado
- **Fecha de Ocupación**: Cuándo fue asignado al proyecto actual
- **Fecha de Liberación**: Cuándo estará disponible nuevamente

#### Reparaciones
- **Motivo de Reparación**: Descripción del problema (obligatorio cuando estado = EN REPARACION)

## Subtipos de Equipos y Características Específicas

### 1. LAVAMANOS

**Características específicas:**
- **Bombas de Pie**: Indica si tiene sistema de bombeo manual
- **Dispensador de Jabón**: Presencia de dispensador integrado
- **Toallas de Papel**: Disponibilidad de dispensador de papel

**Casos de uso:**
- Instalaciones temporales en campamentos
- Áreas de trabajo sin acceso a agua potable
- Cumplimiento de normas de higiene industrial

### 2. BATERIA SANITARIA HOMBRE

**Características específicas:**
- **Dispensador de Papel**: Dispensador de papel higiénico
- **Dispensador de Jabón**: Sistema de jabón líquido
- **Dispensador de Servilletas**: Dispensador de papel toalla
- **Urinales**: Presencia de urinales (específico para hombres)
- **Asientos**: Tipo y cantidad de asientos
- **Bomba de Baño**: Sistema de bombeo para desechos
- **Bomba de Lavamanos**: Sistema de bombeo para lavamanos integrado
- **Tapa de Inodoro**: Presencia de tapas en inodoros
- **Bases de Baños**: Tipo de base o anclaje
- **Tubo de Ventilación**: Sistema de ventilación

### 3. BATERIA SANITARIA MUJER

**Características específicas:**
- **Dispensador de Papel**: Dispensador de papel higiénico
- **Dispensador de Jabón**: Sistema de jabón líquido
- **Dispensador de Servilletas**: Dispensador de papel toalla
- **Asientos**: Tipo y cantidad de asientos
- **Bomba de Baño**: Sistema de bombeo para desechos
- **Bomba de Lavamanos**: Sistema de bombeo para lavamanos integrado
- **Tapa de Inodoro**: Presencia de tapas en inodoros
- **Bases de Baños**: Tipo de base o anclaje
- **Tubo de Ventilación**: Sistema de ventilación

*Nota: Los urinales no aplican para baterías sanitarias de mujer*

### 4. PLANTA DE TRATAMIENTO DE AGUA

**Características específicas:**
- **Capacidad**: Volumen de procesamiento en galones
- **Componentes especializados:**
  - **Blower**: Marca y modelo del soplador
  - **Motor**: Marca y modelo del motor principal
  - **Banda**: Marca, modelo y tipo (A o B)
  - **Polea del Blower**: Especificaciones técnicas
  - **Polea del Motor**: Especificaciones técnicas
  - **Tablero Eléctrico**: Sistema de control eléctrico
  - **Guarda Motor**: Protección del motor

### 5. PLANTA DE TRATAMIENTO DE AGUA RESIDUAL

**Características específicas:**
- **Capacidad de Planta**: Volumen específico (10M3, 15M3, 25M3)
- **Componentes especializados:** (Mismos que planta de agua)
  - **Blower**: Marca y modelo del soplador
  - **Motor**: Marca y modelo del motor principal
  - **Banda**: Marca, modelo y tipo (A o B)
  - **Polea del Blower**: Especificaciones técnicas
  - **Polea del Motor**: Especificaciones técnicas
  - **Tablero Eléctrico**: Sistema de control eléctrico
  - **Guarda Motor**: Protección del motor

### 6. TANQUES DE ALMACENAMIENTO AGUA CRUDA

**Características específicas:**
- **Capacidad en Galones**: Volumen de almacenamiento
- **Componentes especializados:** (Mismos que plantas de tratamiento)

### 7. TANQUES DE ALMACENAMIENTO AGUA RESIDUAL

**Características específicas:**
- **Capacidad en Galones**: Volumen de almacenamiento
- **Componentes especializados:** (Mismos que plantas de tratamiento)

### 8. CAMPER BAÑO

**Características específicas:**
- Comparte todas las características de batería sanitaria incluyendo urinales
- Diseño móvil y autónomo
- Ideal para ubicaciones remotas

### 9. ESTACION CUADRUPLE URINARIO

**Características específicas:**
- Solo campos básicos del equipo
- Especializada en urinales múltiples
- Uso en eventos o concentraciones masivas

## Validaciones del Sistema

### Validaciones Automáticas

1. **Estado EN REPARACION**: Requiere especificar motivo obligatoriamente
2. **Urinales**: Solo permitidos en baterías sanitarias de hombre y camper baño
3. **Capacidad de Planta**: Obligatoria para plantas de tratamiento de agua residual
4. **Campos Especializados**: Solo visibles para plantas y tanques
5. **Código Único**: No se permite duplicar códigos de equipo
6. **Combinación Única**: Código + Número de Serie debe ser única

### Validaciones de Negocio

1. **Asignación de Proyecto**: Un equipo no puede estar en dos proyectos simultáneamente
2. **Disponibilidad**: Equipos EN REPARACION o FUERA DE SERVICIO no pueden asignarse
3. **Fecha de Liberación**: Debe ser posterior a la fecha de ocupación
4. **Capacidades**: Deben ser valores numéricos positivos

## Interfaz de Usuario

### Asistente de Creación

El sistema utiliza un asistente de 3 pasos para la creación de equipos:

#### Paso 1: Selección de Tipo
- Elegir entre EQUIPO o SERVICIO
- Información contextual según la selección

#### Paso 2: Selección de Subtipo (Solo para Equipos)
- Lista de subtipos disponibles
- Descripción de cada subtipo
- Saltado automáticamente para servicios

#### Paso 3: Información Detallada
- Formulario dinámico según tipo/subtipo seleccionado
- Pestañas organizadas por categorías:
  - **Información General**: Datos básicos
  - **Dimensiones**: Medidas físicas
  - **Características Específicas**: Campos según subtipo
  - **Datos Técnicos**: Componentes especializados
  - **Notas**: Información adicional

### Características de la Interfaz

- **Campos Dinámicos**: Solo se muestran campos relevantes al subtipo
- **Validación en Tiempo Real**: Errores mostrados inmediatamente
- **Navegación Intuitiva**: Pasos claros y botones de navegación
- **Autoguardado**: Prevención de pérdida de datos
- **Responsive**: Adaptable a diferentes tamaños de pantalla

## Casos de Uso Principales

### 1. Registro de Nuevo Equipo
```
1. Seleccionar tipo: EQUIPO
2. Seleccionar subtipo: ej. LAVAMANOS
3. Completar información básica
4. Especificar características específicas
5. Configurar precio base
6. Guardar equipo
```

### 2. Asignación a Proyecto
```
1. Buscar equipo disponible
2. Verificar estado DISPONIBLE
3. Asignar ubicación actual
4. Establecer fecha de ocupación
5. Cambiar estado a RENTADO
6. Actualizar ID del proyecto
```

### 3. Mantenimiento de Equipo
```
1. Cambiar estado a EN REPARACION
2. Especificar motivo de reparación
3. Realizar mantenimiento
4. Documentar reparaciones
5. Cambiar estado a DISPONIBLE
6. Limpiar motivo de reparación
```

### 4. Consulta de Disponibilidad
```
1. Filtrar por tipo/subtipo
2. Filtrar por estado DISPONIBLE
3. Verificar fecha de liberación
4. Consultar ubicación actual
5. Verificar características requeridas
```

## Reportes y Consultas

### Reportes Disponibles

1. **Inventario Completo**: Listado de todos los equipos con su estado
2. **Equipos Disponibles**: Equipos listos para asignación
3. **Equipos en Reparación**: Control de mantenimientos
4. **Equipos por Proyecto**: Asignaciones actuales
5. **Vencimientos**: Fechas de liberación próximas
6. **Utilización**: Estadísticas de uso por equipo

### Filtros de Búsqueda

- **Por Tipo**: Equipos o Servicios
- **Por Subtipo**: Categoría específica
- **Por Estado**: Disponible, Rentado, En Reparación, Fuera de Servicio
- **Por Ubicación**: Lugar actual del equipo
- **Por Proyecto**: Asignación actual
- **Por Fecha**: Rangos de fechas de ocupación/liberación
- **Por Características**: Filtros específicos según subtipo

## Integración con Otros Módulos

### Módulo de Proyectos
- Asignación automática de equipos a proyectos
- Control de disponibilidad por fechas
- Cálculo automático de costos

### Módulo de Mantenimiento
- Programación de mantenimientos preventivos
- Registro de reparaciones
- Control de estado de equipos

### Módulo de Facturación
- Cálculo de costos por alquiler
- Tarifas según tipo de equipo
- Descuentos por volumen

### Módulo de Logística
- Planificación de transporte
- Rutas de entrega y recogida
- Control de ubicaciones

## Consideraciones Técnicas

### Rendimiento
- Índices en campos de búsqueda frecuente
- Consultas optimizadas para listados
- Carga lazy de características específicas

### Seguridad
- Auditoría completa de cambios
- Control de acceso por roles
- Validación de datos críticos

### Escalabilidad
- Diseño modular para nuevos subtipos
- Campos flexibles para características
- Estructura extensible

## Mantenimiento del Sistema

### Tareas Periódicas

1. **Diario**: Verificación de asignaciones y liberaciones
2. **Semanal**: Control de equipos en reparación
3. **Mensual**: Auditoría de inventario
4. **Trimestral**: Análisis de utilización
5. **Anual**: Revisión de precios base

### Respaldos
- Backup automático de datos críticos
- Historial de cambios preservado
- Recuperación punto en tiempo

## Glosario de Términos

- **Blower**: Equipo de soplado para aireación en plantas de tratamiento
- **Banda Tipo A/B**: Clasificación de bandas de transmisión
- **Capacidad M3**: Metros cúbicos por hora de procesamiento
- **Guarda Motor**: Protección eléctrica del motor
- **Polea**: Elemento de transmisión mecánica
- **Tablero Eléctrico**: Panel de control eléctrico

---

*Documento creado para PEISOL S.A. - Sistema MANTIS*  
*Fecha: Enero 2025*  
*Versión: 2.0*  
*Módulo: Equipos y Servicios*
