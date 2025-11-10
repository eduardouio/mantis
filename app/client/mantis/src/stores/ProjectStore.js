import { defineStore } from "pinia";
import { appConfig } from "@/AppConfig";

export const UseProjectStore = defineStore("projectStore", {
    state: () => ({
        project : Object,
    }),
    actions: {
        async fetchProjectData() {
            console.log("Fetching project data...");
            try {
                const response = await fetch(appConfig.URLProjectData, {
                    method: "GET",
                    headers: appConfig.headers
                });
                if (!response.ok) {
                    throw new Error("Failed to fetch project data");
                }
                const responseData = await response.json();
                this.project = responseData.data;
            } catch (error) {
                console.error("Error fetching project data:", error);
            }
        },
    },
});