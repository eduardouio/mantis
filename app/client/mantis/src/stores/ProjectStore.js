import { defineStore } from "pinia";
import { appConfig } from "@/AppConfig";

export const UseProjectStore = defineStore("projectStore", {
    state: () => ({
        project: {
            id: null,
            partner_id: null,
            partner_name: null,
            location: null,
            contact_name: null,
            contact_phone: null,
            start_date: null,
            end_date: null,
            is_closed: false,
        },
        allProjects: []
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
        async fetchAllProjects() {
            console.log("Fetching all projects...");
            try {
                const response = await fetch(appConfig.URLAllProjectData, {
                    method: "GET",
                    headers: appConfig.headers
                });
                if (!response.ok) {
                    throw new Error("Failed to fetch all projects");
                }
                const responseData = await response.json();
                this.allProjects = responseData.data;
            } catch (error) {
                console.error("Error fetching all projects:", error);
            }
        }
    }
});