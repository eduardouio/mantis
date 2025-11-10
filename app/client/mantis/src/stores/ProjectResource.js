import { defineStore } from "pinia";
import { appConfig } from "@/AppConfig";

export const UseProjectResourceStore = defineStore("projectResourcesStore", {
    state: () => ({
        selectedResource: Object,
        resourcesProject: [],
        newResource: {
            project: null,
            id_resource_item: null,
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
    },
    addResourceToProject(resource) {
        this.resourcesProject.push(resource);
    }
});