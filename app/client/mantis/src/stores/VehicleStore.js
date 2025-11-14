import { defineStore } from "pinia";
import { appConfig } from "@/AppConfig";

export const UseVehicleStore = defineStore("vehicleStore", {  
    state: () => ({
        vehicle: {

        },
        vehicles: []
    }),
    actions: {
        async fetchVehicles() {
            console.log("Fetching available vehicles...");
            try {
                const response = await fetch(appConfig.URLVehiclesAvailable, {
                    method: "GET",
                    headers: appConfig.headers
                });
                if (!response.ok) {
                    throw new Error("Failed to fetch vehicles");
                }
                const responseData = await response.json();
                this.vehicles = responseData.data;
            } catch (error) {
                console.error("Error fetching vehicles:", error);
            }
        }
    }
});
