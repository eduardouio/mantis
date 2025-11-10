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
            detailed_description: null,
            cost: 0.0,
            interval_days: 3, 
            operation_start_date: null,
            operation_end_date: null,
            is_retired: false,
            retirement_date: null,
            retirement_reason: null,
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
        async addResourceToProject(resource) {
            if (!resource.cost || resource.cost <= 0) {
                throw new Error("El costo debe ser mayor a 0");
            }
            if (!resource.operation_start_date) {
                throw new Error("La fecha de inicio de operaciones es requerida");
            }
            if (!resource.interval_days || resource.interval_days < 1) {
                throw new Error("La frecuencia debe ser al menos 1 día");
            }

            try {
                const response = await fetch(appConfig.URLAddResourceToProject, {
                    method: "POST",
                    headers: appConfig.headers,
                    body: JSON.stringify(resource)
                });
                if (response.ok) {
                    this.resourcesProject.push(resource);
                } else {
                    alert("Error al agregar el recurso al proyecto");
                    throw new Error("Error al agregar el recurso al proyecto");
                }
            } catch (error) {
                console.error("Error adding resource to project:", error);
                throw error; 
            }
        }
    }
});