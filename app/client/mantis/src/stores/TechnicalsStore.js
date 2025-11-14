import { defineStore } from "pinia";
import { appConfig } from "@/AppConfig";

export const UseTechnicalsStore = defineStore("technicalsStore", {
    state: () => ({
        technical: {

        },
        technicals: []
    }),
    actions: {
        async fetchTechnicalsAvailable() {
            console.log("Fetching available technicals...");
            try {
                const response = await fetch(appConfig.URLTechnicalsAvailable, {
                    method: "GET",
                    headers: appConfig.headers
                });
                if (!response.ok) {
                    throw new Error("Failed to fetch technicals");
                }
                const responseData = await response.json();
                this.technicals = responseData.data;
            } catch (error) {
                console.error("Error fetching technicals:", error);
            }
        }
    }
});