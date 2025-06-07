# Remover importaciones circulares que causan AppRegistryNotReady
# Las vistas se importarán cuando sean necesarias, no al nivel del módulo

__all__ = [
    'VehicleListView',
    'VehicleDetailView',
    'VehicleCreateView',
    'VehicleUpdateView',
    'VehicleDeleteView'
]
