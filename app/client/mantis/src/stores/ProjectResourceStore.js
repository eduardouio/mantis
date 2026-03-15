import { defineStore } from "pinia"
import { appConfig } from "@/AppConfig"
import { UseResourcesStore } from "@/stores/ResourcesStore"

export const UseProjectResourceStore = defineStore("projectResourcesStore", {
    state: () => ({
        selectedResource: null,
        resourcesProject: [],
        newResourceProject: {
            id: null,
            project: null,
            resource: Object,
            type: null,
            detailed_description: null,
            cost: 0.0,  
            frecuency_type: "DAY",
            interval_days: 2, 
            week_days: null,
            month_days: null,
            operation_start_date: null,
            operation_end_date: null,
            is_retired: false,
            retirement_date: null,
            retirement_reason: null,
            is_active: true,
            is_selected: false,
            is_confirm_delete: false
        }
    }),
    actions: {
        async fetchResourcesProject() {
            try {
                const response = await fetch(appConfig.URLResourcesProject, {
                    method: "GET",
                    headers: appConfig.headers
                })
                if (!response.ok) {
                    throw new Error("Failed to fetch project resources")
                }
                const responseData = await response.json()
                this.resourcesProject = responseData.data
            } catch (error) {
                console.error("Error fetching project resources:", error)
                this.resourcesProject = []; // Asegurar que siempre sea array
            }
        },
        async addResourcesToProject(resources) {
            try {
                const cleanResources = []
                
                resources.forEach(resource => {
                    // Determinar el código del equipo físico
                    // Si es un servicio, usar el valor seleccionado (si no hay, usar 0)
                    // Si es un equipo, usar su propio ID
                    const isService = resource.resource?.type_equipment === 'SERVIC'
                    const physicalEquipmentCode = isService 
                        ? (resource.physical_equipment_code || 0)
                        : resource.resource_id
                    
                    const baseData = {
                        project_id: appConfig.idProject,
                        resource_id: resource.resource_id,
                        detailed_description: resource.detailed_description,
                        operation_start_date: resource.operation_start_date,
                        frequency_type: resource.frequency_type || 'MONTH',
                        physical_equipment_code: physicalEquipmentCode
                    }
                    
                    // Siempre enviar cost para el recurso principal (equipo o servicio)
                    baseData.cost = resource.cost || 0
                    
                    // Solo enviar los datos del intervalo correspondiente al tipo seleccionado
                    switch (resource.frequency_type) {
                        case 'DAY':
                            // Usar el valor del usuario, convertir a número entero
                            const intervalDays = parseInt(resource.interval_days)
                            baseData.interval_days = isNaN(intervalDays) || intervalDays < 1 ? 1 : intervalDays
                            break
                        case 'WEEK':
                            baseData.weekdays = resource.weekdays || []
                            break
                        case 'MONTH':
                            baseData.monthdays = resource.monthdays || []
                            break
                    }
                    
                    // Agregar el registro del equipo
                    cleanResources.push(baseData)
                    
                    // Si incluye mantenimiento y NO es un servicio, agregar un segundo registro para el mantenimiento
                    if (resource.include_maintenance && !isService) {
                        // Buscar el recurso de servicio PEISOL-SERV01 en el store de resources
                        const resourcesStore = UseResourcesStore()
                        const serviceResource = resourcesStore.resources.find(r => r.code === 'PEISOL-SERV01')
                        if (!serviceResource) {
                            throw new Error('Recurso de servicio PEISOL-SERV01 no encontrado. Contacte al administrador.')
                        }
                        const maintenanceData = {
                            project_id: appConfig.idProject,
                            resource_id: serviceResource.id,
                            detailed_description: `Mantenimiento - ${resource.detailed_description}`,
                            maintenance_cost: resource.maintenance_cost || 0,  // Usar maintenance_cost para que el backend lo identifique
                            operation_start_date: resource.operation_start_date,
                            frequency_type: resource.maintenance_frequency_type || 'DAY',
                            physical_equipment_code: resource.resource_id
                        }
                        
                        // Agregar datos de frecuencia según el tipo de mantenimiento
                        switch (resource.maintenance_frequency_type) {
                            case 'DAY':
                                const maintIntervalDays = parseInt(resource.maintenance_interval_days)
                                maintenanceData.interval_days = isNaN(maintIntervalDays) || maintIntervalDays < 1 ? 1 : maintIntervalDays
                                break
                            case 'WEEK':
                                maintenanceData.weekdays = resource.maintenance_weekdays || []
                                break
                            case 'MONTH':
                                maintenanceData.monthdays = resource.maintenance_monthdays || []
                                break
                        }
                        
                        cleanResources.push(maintenanceData)
                    }
                })

                const response = await fetch(appConfig.URLAddResourceToProject, {
                    method: "POST",
                    headers: appConfig.headers,
                    body: JSON.stringify(cleanResources)
                })
                
                const data = await response.json()
                
                if (!response.ok) {
                    throw new Error(data.error || `Error al agregar recursos. Se agregaron ${data.added || 0} de ${cleanResources.length}`)
                }
                
                return data
            } catch (error) {
                console.error("Error adding resources to project:", error)
                throw error
            }
        },
        async updateResourceProject(resource) {
            try {
                const response = await fetch(appConfig.URLUpdateResourceItem, {
                    method: "PUT",
                    headers: appConfig.headers,
                    body: JSON.stringify(resource)
                })
                
                const responseData = await response.json()
                
                if (!response.ok) {
                    throw new Error(responseData.error || "Failed to update project resource")
                }
                
                // Actualizar el recurso en el store
                const index = this.resourcesProject.findIndex(r => r.id === resource.id)
                if (index !== -1) {
                    this.resourcesProject[index] = { ...this.resourcesProject[index], ...responseData.data }
                }
                
                return responseData.data
            } catch (error) {
                console.error("Error updating project resource:", error)
                throw error
            }
        },
        async deleteResourceProject(id_project_resource) {
            try {
                const url = appConfig.URLDeleteResourceProject.replace("${id_project_resource}", id_project_resource)
                const response = await fetch(url, {
                    method: "DELETE",
                    headers: appConfig.headers
                })
                
                if (!response.ok) {
                    let errorMessage = "Failed to delete project resource"
                    try {
                        const data = await response.json()
                        errorMessage = data.error || errorMessage
                    } catch (e) {
                        // Si la respuesta no es JSON, intentar leer como texto
                        errorMessage = await response.text() || errorMessage
                    }
                    throw new Error(errorMessage)
                }
                
                // Solo eliminar el recurso del store si la petición fue exitosa
                this.resourcesProject = this.resourcesProject.filter(r => r.id !== id_project_resource)
                
            } catch (error) {
                console.error("Error deleting project resource:", error)
                throw error
            }
        },
        async releaseResourceProject(id_project_resource, retirement_date = null) {
            try {
                const body = { id: id_project_resource }
                if (retirement_date) body.retirement_date = retirement_date
                const response = await fetch(appConfig.URLReleaseResource, {
                    method: "PUT",
                    headers: appConfig.headers,
                    body: JSON.stringify(body)
                })

                const responseData = await response.json()

                if (!response.ok) {
                    throw new Error(responseData.error || "Failed to release project resource")
                }

                // Actualizar el recurso en el store marcándolo como retirado
                const index = this.resourcesProject.findIndex(r => r.id === id_project_resource)
                if (index !== -1) {
                    this.resourcesProject[index].is_retired = true
                    if (retirement_date) {
                        this.resourcesProject[index].retirement_date = retirement_date
                    }
                }

                // Si se liberaron servicios relacionados, marcarlos también
                if (responseData.related_services_released) {
                    responseData.related_services_released.forEach(serviceId => {
                        const sIndex = this.resourcesProject.findIndex(r => r.id === serviceId)
                        if (sIndex !== -1) {
                            this.resourcesProject[sIndex].is_retired = true
                        }
                    })
                }

                return responseData
            } catch (error) {
                console.error("Error releasing project resource:", error)
                throw error
            }
        },
        async reactivateResourceProject(id_project_resource) {
            try {
                const response = await fetch(appConfig.URLReactivateResource, {
                    method: "PUT",
                    headers: appConfig.headers,
                    body: JSON.stringify({ id: id_project_resource })
                })

                const responseData = await response.json()

                if (!response.ok) {
                    const err = new Error(responseData.error || "Error al reactivar el recurso")
                    err.active_project_id = responseData.active_project_id || null
                    throw err
                }

                // Actualizar el recurso en el store marcándolo como activo
                const index = this.resourcesProject.findIndex(r => r.id === id_project_resource)
                if (index !== -1) {
                    this.resourcesProject[index] = {
                        ...this.resourcesProject[index],
                        ...responseData.data
                    }
                }

                // Si se reactivaron servicios relacionados, actualizarlos también
                if (responseData.related_services_reactivated) {
                    responseData.related_services_reactivated.forEach(serviceId => {
                        const sIndex = this.resourcesProject.findIndex(r => r.id === serviceId)
                        if (sIndex !== -1) {
                            this.resourcesProject[sIndex].is_retired = false
                            this.resourcesProject[sIndex].retirement_date = null
                            this.resourcesProject[sIndex].retirement_reason = null
                        }
                    })
                }

                return responseData
            } catch (error) {
                console.error("Error reactivating project resource:", error)
                throw error
            }
        }
    }
})