import { defineStore} from "pinia";
import { appConfig } from "@/AppConfig";
import select from "daisyui/components/select";

export const UseSheetProjectsStore = defineStore("sheetProjectsStore", {
    state: () => ({
        selectedSheetProject: Object,
        sheetProjects: [],
    }),
    actions: {
        async fetchSheetProjects() {
            console.log("Fetching sheet projects...");
            try {
                const response = await fetch(appConfig.URLSheetProjects, {
                    method: "GET",
                    headers: appConfig.headers,
                });
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                this.sheetProjects = data.data;
            } catch (error) {
                console.error("Error fetching sheet projects:", error);
            }
        },
        selectedSheetProjectById(idSheetProject) {
            console.log("Setting selected sheet project with ID:", idSheetProject);
            this.selectedSheetProject = this.sheetProjects.find(
                (sheetProject) => sheetProject.id === idSheetProject
            );
        }
    }
});