import { defineStore } from "pinia";
import { appConfig } from "@/AppConfig";


export const UseResourcesStore = defineStore("resourcesStore", {
    state: () => ({
        selectedResource: null,
        resourcesAvailable: [],
        resourcesProject: [],
        newResource: {
            "id": null,
            "code": null,
            "name": null,
            "type": null,
            "type_equipment": null,
            "type_equipment_display": null,
            "brand": null,
            "model": null,
            "status_equipment": null,
            "status_disponibility": null,
            "current_location": null,
            "capacity_gallons": null,
            "is_selected": false,
            "is_confirm_delete": false,
            "is_retired": false
        }
    }),
    actions: {
        async fetchResourcesAvailable() {
            console.log("Fetching available resources...");
            try {
                const response = await fetch(appConfig.URLSourcesAvailable, {
                    method: "GET",
                    headers: appConfig.headers,
                });
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                this.resourcesAvailable = data.data
            } catch (error) {
                console.error("Error fetching available resources:", error);
            }
        },
        setSelectedResource(idResource) {
            console.log("Setting selected resource with ID:", idResource);
            this.selectedResource = this.resourcesAvailable.find(
                (resource) => resource.id === idResource
            );
        }
    },
});