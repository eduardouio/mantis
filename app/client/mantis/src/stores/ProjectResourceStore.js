import { defineStore } from "pinia";
import { appConfig } from "@/AppConfig";

export const UseProjectResourceStore = defineStore("projectResourcesStore", {
    state: () => ({
        selectedResource: Object,
        resourcesProject: [],
        newResourceProject: {
            id: null,
            project: null,
            resource: Object,
            type: null,
            detailed_description: null,
            cost: 0.0,
            interval_days: 3, 
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
            console.log("Fetching project resources");

            try {
                const response = await fetch(appConfig.URLResourcesProject, {
                    method: "GET",
                    headers: appConfig.headers
                });
                if (!response.ok) {
                    throw new Error("Failed to fetch project resources");
                }
                const responseData = await response.json();
                this.resourcesProject = responseData.data;
            } catch (error) {
                console.error("Error fetching project resources:", error);
            }
        },
        async addResourcesToProject(resources) {
            try {
                const cleanResources = resources.map(resource => ({
                    project_id: appConfig.idProject,
                    resource_id: resource.resource_id,
                    detailed_description: resource.detailed_description,
                    interval_days: resource.interval_days,
                    cost: resource.cost || 0,
                    maintenance_cost: resource.maintenance_cost || 0,
                    operation_start_date: resource.operation_start_date,
                    include_maintenance: resource.include_maintenance
                }))

                const response = await fetch(appConfig.URLAddResourceToProject, {
                    method: "POST",
                    headers: appConfig.headers,
                    body: JSON.stringify(cleanResources)
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || `Error al agregar recursos. Se agregaron ${data.added || 0} de ${cleanResources.length}`);
                }
                
                return data;
            } catch (error) {
                console.error("Error adding resources to project:", error);
                throw error;
            }
        },
        async updateResourceProject(resourceId, updatedData) {
            try {
                const response = await fetch(appConfig.URLUpdateResourceItem.replace('{id}', resourceId), {
                    method: "PUT",
                    headers: appConfig.headers,
                    body: JSON.stringify(updatedData)
                });
                
                if (!response.ok) {
                    throw new Error("Failed to update project resource");
                }
                
                const responseData = await response.json();
                
                // Actualizar el recurso en el store local
                const resourceIndex = this.resourcesProject.findIndex(r => r.id === resourceId);
                if (resourceIndex !== -1) {
                    this.resourcesProject[resourceIndex] = { ...this.resourcesProject[resourceIndex], ...responseData.data };
                }
                
                return responseData;
            } catch (error) {
                console.error("Error updating project resource:", error);
                throw error;
            }
        }
    }
});