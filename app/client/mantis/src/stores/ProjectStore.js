import { defineStore } from "pinia";
import { appConfig } from "@/AppConfig";

export const UseProjectStore = defineStore("projectStore", {
    state: () => ({
        // Datos del proyecto actual
        project: {
            id: null,
            partner_id: null,
            partner_name: null,
            location: null,
            cardinal_point: null,
            contact_name: null,
            contact_phone: null,
            start_date: null,
            end_date: null,
            is_closed: false,
        },
        // Órdenes de trabajo del proyecto actual
        workOrders: [],
        workOrdersCount: 0,
        totalCustodyChains: 0,
        // Estado de carga
        loading: false,
        error: null,
    }),
    getters: {
        // Obtener todas las cadenas de custodia de todas las órdenes
        allCustodyChains: (state) => {
            return state.workOrders.flatMap(wo => wo.custody_chains || []);
        },
        // Obtener orden de trabajo por ID
        getWorkOrderById: (state) => (id) => {
            return state.workOrders.find(wo => wo.id === id);
        },
        // Obtener cadena de custodia por ID
        getCustodyChainById: (state) => (id) => {
            for (const workOrder of state.workOrders) {
                const chain = workOrder.custody_chains?.find(cc => cc.id === id);
                if (chain) return chain;
            }
            return null;
        },
        // Estadísticas rápidas
        projectStats: (state) => ({
            totalWorkOrders: state.workOrdersCount,
            totalCustodyChains: state.totalCustodyChains,
            inProgressWorkOrders: state.workOrders.filter(wo => wo.status === 'IN_PROGRESS').length,
            invoicedWorkOrders: state.workOrders.filter(wo => wo.status === 'INVOICED').length,
        }),
    },
    actions: {
        /**
         * Obtener información completa del proyecto actual
         * Incluye: datos del proyecto, órdenes de trabajo y cadenas de custodia
         * Usa el projectId configurado en AppConfig
         */
        async fetchProjectData() {
            this.loading = true;
            this.error = null;
            console.log(`Fetching all info for project ${appConfig.idProject}...`);
            
            try {
                const response = await fetch(appConfig.URLProjectData, {
                    method: "GET",
                    headers: appConfig.headers
                });
                
                if (!response.ok) {
                    throw new Error(`Failed to fetch project info: ${response.status}`);
                }
                
                const responseData = await response.json();
                
                if (responseData.success && responseData.data) {
                    // Actualizar datos del proyecto
                    this.project = responseData.data.project;
                    
                    // Actualizar órdenes de trabajo
                    this.workOrders = responseData.data.work_orders || [];
                    this.workOrdersCount = responseData.data.work_orders_count || 0;
                    this.totalCustodyChains = responseData.data.total_custody_chains || 0;
                    
                    console.log(`Project ${this.project.id} loaded successfully with ${this.workOrdersCount} work orders`);
                } else {
                    throw new Error(responseData.error || "Invalid response format");
                }
            } catch (error) {
                console.error("Error fetching project data:", error);
                this.error = error.message;
                // Resetear datos en caso de error
                this.resetProjectData();
            } finally {
                this.loading = false;
            }
        },

        /**
         * Obtener información completa de un proyecto específico
         * @param {number} projectId - ID del proyecto a consultar
         */
        async fetchProjectAllInfo(projectId) {
            this.loading = true;
            this.error = null;
            console.log(`Fetching all info for project ${projectId}...`);
            
            try {
                const url = `${appConfig.apiBaseUrl}/api/projects/all-info/${projectId}/`;
                const response = await fetch(url, {
                    method: "GET",
                    headers: appConfig.headers
                });
                
                if (!response.ok) {
                    throw new Error(`Failed to fetch project info: ${response.status}`);
                }
                
                const responseData = await response.json();
                
                if (responseData.success && responseData.data) {
                    // Actualizar datos del proyecto
                    this.project = responseData.data.project;
                    
                    // Actualizar órdenes de trabajo
                    this.workOrders = responseData.data.work_orders || [];
                    this.workOrdersCount = responseData.data.work_orders_count || 0;
                    this.totalCustodyChains = responseData.data.total_custody_chains || 0;
                    
                    console.log(`Project ${projectId} loaded successfully with ${this.workOrdersCount} work orders`);
                } else {
                    throw new Error(responseData.error || "Invalid response format");
                }
            } catch (error) {
                console.error("Error fetching project all info:", error);
                this.error = error.message;
                // Resetear datos en caso de error
                this.resetProjectData();
            } finally {
                this.loading = false;
            }
        },

        /**
         * Resetear los datos del proyecto actual
         */
        resetProjectData() {
            this.project = {
                id: null,
                partner_id: null,
                partner_name: null,
                location: null,
                cardinal_point: null,
                contact_name: null,
                contact_phone: null,
                start_date: null,
                end_date: null,
                is_closed: false,
            };
            this.workOrders = [];
            this.workOrdersCount = 0;
            this.totalCustodyChains = 0;
        },

        /**
         * Actualizar una orden de trabajo específica
         */
        updateWorkOrder(workOrderId, updatedData) {
            const index = this.workOrders.findIndex(wo => wo.id === workOrderId);
            if (index !== -1) {
                this.workOrders[index] = { ...this.workOrders[index], ...updatedData };
            }
        },

        /**
         * Actualizar una cadena de custodia específica
         */
        updateCustodyChain(custodyChainId, updatedData) {
            for (const workOrder of this.workOrders) {
                const index = workOrder.custody_chains?.findIndex(cc => cc.id === custodyChainId);
                if (index !== -1 && index !== undefined) {
                    workOrder.custody_chains[index] = { 
                        ...workOrder.custody_chains[index], 
                        ...updatedData 
                    };
                    break;
                }
            }
        },

        /**
         * Recargar los datos del proyecto actual
         */
        async refreshCurrentProject() {
            await this.fetchProjectData();
        },
    }
});