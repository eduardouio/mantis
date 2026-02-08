import { defineStore } from "pinia";
import { appConfig } from "@/AppConfig";


export const UseResourcesStore = defineStore("resourcesStore", {
    state: () => ({
        selectedResource: null,
        resources: [],
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
    getters: {
        resourcesAvailable: (state) => state.resources,
        // Obtener solo equipos físicos (no servicios) que no están disponibles
        physicalEquipmentsNotAvailable: (state) => {
            return state.resources.filter(r => 
                r.type_equipment !== 'SERVIC' && 
                r.available === false
            )
        }
    },
    actions: {
        async fetchResourcesAvailable() {
            try {
                const response = await fetch(appConfig.URLSourcesAvailable, {
                    method: "GET",
                    headers: appConfig.headers,
                });
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                this.resources = data.data || []
            } catch (error) {
                console.error("Error fetching available resources:", error);
                this.resources = []
            }
        },
        setSelectedResource(idResource) {
            this.selectedResource = this.resources.find(
                (resource) => resource.id === idResource
            ) || null
        }
    },
});