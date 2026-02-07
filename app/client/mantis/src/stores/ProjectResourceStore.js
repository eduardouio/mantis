import { defineStore } from "pinia"
import { appConfig } from "@/AppConfig"

export const UseProjectResourceStore = defineStore("projectResourcesStore", {
    state: () => ({
        resources: [], // Inicializar como array vacío
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
            console.log("Fetching project resources")

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
                const cleanResources = resources.map(resource => {
                    const baseData = {
                        project_id: appConfig.idProject,
                        resource_id: resource.resource_id,
                        detailed_description: resource.detailed_description,
                        cost: resource.cost || 0,
                        maintenance_cost: resource.maintenance_cost || 0,
                        operation_start_date: resource.operation_start_date,
                        include_maintenance: resource.include_maintenance,
                        frequency_type: resource.include_maintenance ? (resource.frequency_type || 'DAY') : null,
                        physical_equipment_code: resource.physical_equipment_code || null
                    }
                    
                    // Solo enviar los datos del intervalo correspondiente al tipo seleccionado
                    if (resource.include_maintenance) {
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
                    }
                    
                    return baseData
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
        }
    }
})