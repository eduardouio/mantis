import { defineStore } from "pinia";
import { appConfig } from "@/AppConfig";
import { UseProjectStore } from "./ProjectStore";

export const UseSheetProjectsStore = defineStore("sheetProjectsStore", {
    state: () => ({
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
        },
        loading: false,
        error: null,
    }),
    getters: {
        /**
         * Obtener las planillas desde el ProjectStore
         */
        sheetProjects: () => {
            const projectStore = UseProjectStore();
            return projectStore.workOrders || [];
        },
        
        /**
         * Obtener planilla por ID
         */
        getSheetProjectById: () => (id) => {
            const projectStore = UseProjectStore();
            return projectStore.getWorkOrderById(id);
        },
        
        /**
         * Verificar si hay una planilla en progreso
         */
        hasInProgressSheet: () => {
            const projectStore = UseProjectStore();
            return projectStore.workOrders.some(sheet => sheet.status === 'IN_PROGRESS');
        },
        
        /**
         * Obtener el ID de la última planilla activa
         */
        lastActiveSheetProjectID: () => {
            const projectStore = UseProjectStore();
            const inProgressSheet = projectStore.workOrders.find(
                sheet => sheet.status === 'IN_PROGRESS'
            );
            return inProgressSheet?.id || null;
        },
        
        /**
         * Obtener cadenas de custodia de una planilla específica
         */
        getCustodyChainsForSheet: () => (sheetId) => {
            const projectStore = UseProjectStore();
            const sheet = projectStore.getWorkOrderById(sheetId);
            return sheet?.custody_chains || [];
        },
    },
    actions: {
        /**
         * Crear una nueva planilla
         */
        async addSheetProject(sheetProject) {
            this.loading = true;
            this.error = null;
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
                
                // Refrescar los datos del proyecto para obtener la nueva planilla
                const projectStore = UseProjectStore();
                await projectStore.refreshCurrentProject();
                
                return data.data.id;
            } catch (error) {
                console.error("Error adding sheet project:", error);
                this.error = error.message;
                throw error;
            } finally {
                this.loading = false;
            }
        },
        
        /**
         * Actualizar una planilla existente
         */
        async updateSheetProject(sheetProject) {
            this.loading = true;
            this.error = null;
            console.log("Updating sheet project:", sheetProject);
            
            try {
                const response = await fetch(appConfig.URLUpdateSheetProject, {
                    method: "PUT",
                    headers: appConfig.headers,
                    body: JSON.stringify(sheetProject)
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || `HTTP error! status: ${response.status}`);
                }
                
                // Refrescar los datos del proyecto
                const projectStore = UseProjectStore();
                await projectStore.refreshCurrentProject();
                
                return data.data;
            } catch (error) {
                console.error("Error updating sheet project:", error);
                this.error = error.message;
                throw error;
            } finally {
                this.loading = false;
            }
        },
        
        /**
         * Cerrar una planilla (cambiar estado)
         */
        async closeSheetProject(sheetProjectID) {
            this.loading = true;
            this.error = null;
            console.log("Closing sheet project with ID:", sheetProjectID);
            
            try {
                // TODO: Implementar endpoint para cerrar planilla
                // Por ahora, solo actualizar el estado
                const projectStore = UseProjectStore();
                const sheet = projectStore.getWorkOrderById(sheetProjectID);
                
                if (!sheet) {
                    throw new Error("Planilla no encontrada");
                }
                
                // Actualizar con estado cerrado
                await this.updateSheetProject({
                    ...sheet,
                    status: "INVOICED",
                    period_end: new Date().toISOString().split('T')[0]
                });
                
                return true;
            } catch (error) {
                console.error("Error closing sheet project:", error);
                this.error = error.message;
                throw error;
            } finally {
                this.loading = false;
            }
        },
        
        /**
         * Inicializar formulario de nueva planilla con datos del proyecto
         */
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
        
        /**
         * Resetear el formulario de nueva planilla
         */
        resetNewSheetProject() {
            this.newSheetProject = {
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
            };
        },
    }
});