Existen diferentes tipos de equipos, aunque comparten ciertos campos son diferentes entre si
    Lavamanos
    Bombas
    Plantas de Tratamiento de Agua
    Tanques de Almacenamiento de Agua Cruda
    Tanques de Almacenamiento de Agua Residual
    Bateria Sanitaria Hombre
    Bateria Sanitaria Mujer
    Estacion Cuadruple Urinario
    Camper Baño

Todos estos comparten estos atributos
    id
    name
    brand
    model
    code -> unico
    serial_number -> unico junto con el code
    date_purchase
    height -> cm
    width -> cm
    depth -> cm
    weight -> kg
    status -> DISPONIBLE RENTADO, EN REPARACION, FUERA DE SERVICIO
    motivo_reparacion -> motivo de la reparacion
    precio_base -> valor alquiler

Dependiendo los tipos tenemos campos adicionales los vamos a mostrar con cada tipo, estos campos ayudan a conocer el estado de estos equipos

Bateria Sanitaria Hombre/Bateria Sanitaria Mujer
    dispensador_papel -> si o no
    dispensador_jabon -> si o no
    dispensador_servilletas -> si o no
    urinales -> si o no
    asientos -> si o no
    bomba_bano -> si o no
    bomba_lavamanos -> si o no
    tapa_inodoro -> si o no
    bases_banos -> si o no
    tubo_ventilacion -> si o no

Plantas de Tratamiento de Agua
    capacidad_planta -> 10M3, 15M3, 25M3 u otro valor libre en metros cubicos
    banda_blower_motor -> Tipo A o  Tipo B
    polea del motos -> texto
    tablero electrico -> texto
    guarda motor -> texto

Plantas de Tratamiento de Agua Residual
    capacidad_planta -> 10M3, 15M3, 25M3 u otro valor libre en metros cubicos
    banda_blower_motor -> Tipo A o  Tipo B
    polea del motos -> texto
    tablero electrico -> texto
    guarda motor -> texto

Tanques de Almacenamiento de Agua Cruda
    capacidad_galones -> capacidad en galones

Tanques de Almacenamiento de Agua Residual
    capacidad_galones -> capacidad en galones

Lavamanos
    bomba_lavamanos -> si o no
    dispensador_jabon_lavamanos -> si o no
    servilletas -> si o no

Camper Baño
    comparte los campos de bateria sanitaria hombre

Estacion Cuadruple Urinario
    solo campos base


Adicional concideraba usar el mismo modelo para los servicios
agregando un campo de tipo de registro