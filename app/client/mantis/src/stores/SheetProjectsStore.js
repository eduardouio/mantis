import { defineStore} from "pinia";
import { appConfig } from "@/AppConfig";
import select from "daisyui/components/select";

export const UseSheetProjectsStore = defineStore("sheetProjectsStore", {
    state: () => ({
        selectedSheetProject: Object,
        sheetProjects: [],
        newSheetProject: {
            id: null,
            project: null,
            issue_date: null,
            period_start: null,
            period_end: null,
            status: "IN_PROGRESS",
            series_code: "PSL-PS-00000-00",
            service_type: "ALQUILER Y MANTENIMIENTO"
        }
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
        async addSheetProject() {
            console.log("Adding new sheet projec");

        },
        selectedSheetProjectById(idSheetProject) {
            console.log("Setting selected sheet project with ID:", idSheetProject);
            this.selectedSheetProject = this.sheetProjects.find(
                (sheetProject) => sheetProject.id === idSheetProject
            );
        }
    }
});