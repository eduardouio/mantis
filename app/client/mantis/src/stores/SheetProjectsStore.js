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
            total_gallons: 0,
            total_barrels: 0,
            total_cubic_meters: 0,
            client_po_reference: null,
            contact_reference: null,
            contact_phone_reference: null,
            final_disposition_reference: null,
            invoice_reference: null,
            subtotal: 0,
            tax_amount: 0,
            total: 0,
            notes: '',
            sheet_project_file: null,
            certificate_final_disposition_file: null,
            invoice_file: null
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
         * Crear una nueva planilla con detalles de recursos
         */
        async addSheetProject(sheetProject, selectedResources = []) {
            this.loading = true;
            this.error = null;
            console.log("Adding new sheet project", sheetProject);
            console.log("Selected resources:", selectedResources);
            
            try {
                const payload = {
                    project_id: sheetProject.project,
                    period_start: sheetProject.period_start,
                    period_end: sheetProject.period_end,
                    service_type: sheetProject.service_type,
                    status: sheetProject.status || "IN_PROGRESS",
                    series_code: sheetProject.series_code || "PSL-PS-00000-00",
                    client_po_reference: sheetProject.client_po_reference || null,
                    invoice_reference: sheetProject.invoice_reference || null
                };
                
                // Agregar campos opcionales si existen
                if (sheetProject.issue_date) payload.issue_date = sheetProject.issue_date;
                if (sheetProject.contact_reference) payload.contact_reference = sheetProject.contact_reference;
                if (sheetProject.contact_phone_reference) payload.contact_phone_reference = sheetProject.contact_phone_reference;
                if (sheetProject.final_disposition_reference) payload.final_disposition_reference = sheetProject.final_disposition_reference;
                
                // Agregar detalles de recursos seleccionados (detail_id = 0 para nuevos)
                if (selectedResources && selectedResources.length > 0) {
                    payload.details = selectedResources.map(resource => ({
                        detail_id: 0,
                        project_resource_id: resource.id,
                        resource_item_id: resource.resource_item_id,
                        detailed_description: resource.detailed_description,
                        cost: resource.cost,
                        type_resource: resource.type_resource,
                        frequency_type: resource.frequency_type,
                        interval_days: resource.interval_days,
                        weekdays: resource.weekdays,
                        monthdays: resource.monthdays,
                        quantity: 0,
                        total_line: 0,
                        total_price: 0
                    }));
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
        async updateSheetProject(sheetProject, selectedResources = []) {
            this.loading = true;
            this.error = null;
            console.log("Updating sheet project:", sheetProject);
            console.log("Selected resources for update:", selectedResources);
            
            try {
                const payload = {
                    id: sheetProject.id,
                    period_start: sheetProject.period_start,
                    service_type: sheetProject.service_type,
                    series_code: sheetProject.series_code || null
                };
                
                // Agregar campos opcionales si existen
                if (sheetProject.period_end) payload.period_end = sheetProject.period_end;
                if (sheetProject.status) payload.status = sheetProject.status;
                if (sheetProject.contact_reference) payload.contact_reference = sheetProject.contact_reference;
                if (sheetProject.contact_phone_reference) payload.contact_phone_reference = sheetProject.contact_phone_reference;
                if (sheetProject.client_po_reference) payload.client_po_reference = sheetProject.client_po_reference;
                if (sheetProject.final_disposition_reference) payload.final_disposition_reference = sheetProject.final_disposition_reference;
                if (sheetProject.invoice_reference) payload.invoice_reference = sheetProject.invoice_reference;
                
                // Agregar detalles de recursos seleccionados (detail_id > 0 = existente, 0 = nuevo)
                if (selectedResources && selectedResources.length > 0) {
                    payload.details = selectedResources.map(resource => ({
                        detail_id: resource.detail_id || 0,
                        project_resource_id: resource.id,
                        resource_item_id: resource.resource_item_id,
                        resource_item_code: resource.resource_item_code,
                        resource_item_name: resource.resource_item_name,
                        detailed_description: resource.detailed_description,
                        cost: resource.cost,
                        type_resource: resource.type_resource,
                        frequency_type: resource.frequency_type,
                        interval_days: resource.interval_days,
                        weekdays: resource.weekdays,
                        monthdays: resource.monthdays,
                    }));
                }
                
                const response = await fetch(appConfig.URLUpdateSheetProject, {
                    method: "PUT",
                    headers: appConfig.headers,
                    body: JSON.stringify(payload)
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
         * Reabrir una planilla liquidada (volver a EN EJECUCIÓN)
         */
        async reopenSheetProject(sheetProjectId) {
            this.loading = true;
            this.error = null;

            try {
                const response = await fetch(appConfig.URLReopenSheetProject, {
                    method: "PUT",
                    headers: appConfig.headers,
                    body: JSON.stringify({ id: sheetProjectId }),
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
                console.error("Error reopening sheet project:", error);
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
                issue_date: new Date().toISOString().split('T')[0],
                period_start: null,
                period_end: null,
                status: "IN_PROGRESS",
                series_code: "PSL-PS-00000-00",
                service_type: "ALQUILER Y MANTENIMIENTO",
                total_gallons: 0,
                total_barrels: 0,
                total_cubic_meters: 0,
                client_po_reference: null,
                contact_reference: project.contact_name,
                contact_phone_reference: project.contact_phone,
                final_disposition_reference: null,
                invoice_reference: null,
                subtotal: 0,
                tax_amount: 0,
                total: 0,
                notes: '',
                sheet_project_file: null,
                certificate_final_disposition_file: null,
                invoice_file: null
            };
        },
        
        /**
         * Subir archivo de planilla, certificado o factura
         * @param {number} sheetId - ID de la planilla
         * @param {string} fieldName - 'sheet_project_file', 'certificate_final_disposition_file' o 'invoice_file'
         * @param {File} file - Archivo a subir
         * @param {Object} extraData - Datos adicionales (ej: { invoice_reference: '...' })
         */
        async uploadSheetFile(sheetId, fieldName, file, extraData = {}) {
            try {
                const formData = new FormData();
                formData.append('model_type', 'sheet_project');
                formData.append('object_id', sheetId);
                formData.append('field_name', fieldName);
                formData.append('file', file);

                // Agregar datos adicionales (ej: invoice_reference)
                for (const [key, value] of Object.entries(extraData)) {
                    if (value !== null && value !== undefined) {
                        formData.append(key, value);
                    }
                }

                const response = await fetch(appConfig.URLLoadFiles, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': appConfig.csrfToken
                    },
                    body: formData
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || 'Error al subir el archivo');
                }

                // Actualizar el store con la info del archivo
                this.newSheetProject[fieldName] = data.data.file_url;

                // Refrescar datos del proyecto
                const projectStore = UseProjectStore();
                await projectStore.refreshCurrentProject();

                return data.data;
            } catch (error) {
                console.error(`Error uploading ${fieldName}:`, error);
                throw error;
            }
        },

        /**
         * Consultar información de un archivo de la planilla
         * @param {number} sheetId - ID de la planilla
         * @param {string} fieldName - 'sheet_project_file' o 'certificate_final_disposition_file'
         */
        async getSheetFileInfo(sheetId, fieldName) {
            try {
                const params = new URLSearchParams({
                    model_type: 'sheet_project',
                    object_id: sheetId,
                    field_name: fieldName
                });

                const response = await fetch(`${appConfig.URLLoadFiles}?${params}`, {
                    method: 'GET',
                    headers: appConfig.headers
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || 'Error al consultar el archivo');
                }

                return data.data;
            } catch (error) {
                console.error(`Error getting file info for ${fieldName}:`, error);
                throw error;
            }
        },

        /**
         * Eliminar archivo de la planilla
         * @param {number} sheetId - ID de la planilla
         * @param {string} fieldName - 'sheet_project_file' o 'certificate_final_disposition_file'
         */
        async deleteSheetFile(sheetId, fieldName) {
            try {
                const params = new URLSearchParams({
                    model_type: 'sheet_project',
                    object_id: sheetId,
                    field_name: fieldName
                });

                const response = await fetch(`${appConfig.URLLoadFiles}?${params}`, {
                    method: 'DELETE',
                    headers: {
                        'X-CSRFToken': appConfig.csrfToken
                    }
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || 'Error al eliminar el archivo');
                }

                this.newSheetProject[fieldName] = null;

                const projectStore = UseProjectStore();
                await projectStore.refreshCurrentProject();

                return data.data;
            } catch (error) {
                console.error(`Error deleting ${fieldName}:`, error);
                throw error;
            }
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
                total_gallons: 0,
                total_barrels: 0,
                total_cubic_meters: 0,
                client_po_reference: null,
                contact_reference: null,
                contact_phone_reference: null,
                final_disposition_reference: null,
                invoice_reference: null,
                subtotal: 0,
                tax_amount: 0,
                total: 0,
                notes: '',
                sheet_project_file: null,
                certificate_final_disposition_file: null,
                invoice_file: null
            };
        },

        /**
         * Actualizar los días de cobro de alquiler de un detalle de planilla (equipos)
         * @param {number} detailId - ID del SheetProjectDetail
         * @param {Array<number>} monthdays - Lista de días del mes [1, 2, 3, ...]
         * @returns {Object} Datos actualizados del detalle y totales
         */
        async updateSheetDetailDays(detailId, monthdays) {
            this.loading = true;
            this.error = null;

            try {
                const url = appConfig.URLUpdateSheetDetailDays.replace('${detailId}', detailId);
                const response = await fetch(url, {
                    method: 'PUT',
                    headers: appConfig.headers,
                    body: JSON.stringify({ monthdays_apply_cost: monthdays })
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || `HTTP error! status: ${response.status}`);
                }

                // Refrescar datos del proyecto para actualizar totales
                const projectStore = UseProjectStore();
                await projectStore.refreshCurrentProject();

                return data.data;
            } catch (error) {
                console.error('Error updating sheet detail days:', error);
                this.error = error.message;
                throw error;
            } finally {
                this.loading = false;
            }
        },
    }
});