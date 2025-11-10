import { defineStore } from "pinia";
import { appConfig } from "@/AppConfig";


export const UseResourcesStore = defineStore("resourcesStore", {
    state: () => ({
        selectedResource: Object,
        resourcesAvailable: [],
        resourcesProject: [],
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
                this.resourcesAvailable = data;
            } catch (error) {
                console.error("Error fetching available resources:", error);
            }
        }
    },
    setSelectedResource(idResource) {
        console.log("Setting selected resource with ID:", idResource);
        this.selectedResource = this.resourcesAvailable.find(
            (resource) => resource.id === idResource
        );
    }   
}); 