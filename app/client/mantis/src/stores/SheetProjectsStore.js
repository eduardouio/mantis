import { defineStore} from "pinia";
import { appConfig } from "@/AppConfig";

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
            service_type: "ALQUILER Y MANTENIMIENTO",
            contact_reference: null,
            contact_phone_reference: null
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
        async addSheetProject(sheetProject) {
            console.log("Adding new sheet project", sheetProject);
            try {
                const payload = {
                    project_id: sheetProject.project,
                    period_start: sheetProject.period_start,
                    service_type: sheetProject.service_type
                };
                
                if (sheetProject.contact_reference) {
                    payload.contact_reference = sheetProject.contact_reference;
                }
                if (sheetProject.contact_phone_reference) {
                    payload.contact_phone_reference = sheetProject.contact_phone_reference;
                }
                
                const response = await fetch(appConfig.URLAddSheetProject, {
                    method: "POST",
                    headers: appConfig.headers,
                    body: JSON.stringify(payload)
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || `HTTP error! status: ${response.status}`);
                }
                
                return data.data.id;
            } catch (error) {
                console.error("Error adding sheet project:", error);
                throw error;
            }
        },
        async closeSheetProject(sheetProjectID) {
            console.log("Closing sheet project with ID:", sheetProjectID);
        },
        async updateSheetProject(sheetProject) {
            console.log("Updating sheet project:", sheetProject);
        },
        initializeNewSheetProject(project) {
            this.newSheetProject = {
                id: null,
                project: project.id,
                issue_date: null,
                period_start: null,
                period_end: null,
                status: "IN_PROGRESS",
                series_code: "PSL-PS-00000-00",
                service_type: "ALQUILER Y MANTENIMIENTO",
                contact_reference: project.contact_name,
                contact_phone_reference: project.contact_phone
            };
        },
        getLastActiveSheetProjectID() {
            return this.sheetProjects.find(
                sheetProject => sheetProject.status === 'IN_PROGRESS'
            )?.id;
        }
    }
});