import { defineStore } from "pinia";
import { appConfig } from "@/AppConfig";


export const UseCustodyChainStore = defineStore("custodyChainStore", {
    state: () => ({
        custodyChains: [],
        sheetProjectInfo: null,
        selectedCustodyChain: null,
        loading: false,
        error: null,
        newCustodyChain: {
            id: null,
            id_sheet_project: null,
            issue_date: null,
            consecutive: "00000",
            activity_date: null,
            location: null,
            total_gallons: 0.0,
            duration_hours: 0.0,
        }
    }),
    actions: {
        async fetchCustodyChainsBySheet(sheetProjectId) {
            this.loading = true;
            this.error = null;
            console.log("Fetching custody chains for sheet project ID:", sheetProjectId);
            
            try {
                const url = appConfig.URLAllCustodyChains.replace("${id_sheet_project}", sheetProjectId);
                const response = await fetch(url, {
                    method: "GET",
                    headers: appConfig.headers,
                });
                
                if (!response.ok) {
                    throw new Error("Failed to fetch custody chains");
                }
                
                const data = await response.json();
                
                if (data.success && data.data) {
                    this.custodyChains = data.data.custody_chains || [];
                    this.sheetProjectInfo = {
                        sheet_project_id: data.data.sheet_project_id,
                        sheet_project_code: data.data.sheet_project_code,
                        project_id: data.data.project_id,
                        project_name: data.data.project_name,
                        total_chains: data.data.total_chains
                    };
                }
            } catch (error) {
                console.error("Error fetching custody chains:", error);
                this.error = error.message;
                this.custodyChains = [];
                this.sheetProjectInfo = null;
            } finally {
                this.loading = false;
            }
        },
        async addCustodyChain(custodyChain) {
            console.log("Adding new custody chain", custodyChain);
            try {
                const response = await fetch(appConfig.URLCreateCustodyChain, {
                    method: "POST",
                    headers: appConfig.headers,
                    body: JSON.stringify(custodyChain)
                });
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.message || "Failed to create custody chain");
                }
                const data = await response.json();
                
                // Agregar a la lista local
                this.custodyChains.push(data.data);
                
                // Resetear newCustodyChain
                this.resetNewCustodyChain();
                
                return data.data;
            } catch (error) {
                console.error("Error creating custody chain:", error);
                throw error;
            }
        },
        resetNewCustodyChain() {
            this.newCustodyChain = {
                id: null,
                id_sheet_project: null,
                issue_date: new Date().toISOString().split('T')[0],
                consecutive: "00000",
                activity_date: new Date().toISOString().split('T')[0],
                location: null,
                total_gallons: 0.0,
                duration_hours: 0.0,
            };
        },
        async fetchCustodyCapphainDetail(id) {
            this.loading = true;
            this.error = null;
            console.log("Fetching custody chain detail for ID:", id);
            
            try {
                const url = appConfig.URLCustodyChainDetail.replace("${id}", id);
                const response = await fetch(url, {
                    method: "GET",
                    headers: appConfig.headers,
                });
                
                if (!response.ok) {
                    throw new Error("Failed to fetch custody chain detail");
                }
                
                const data = await response.json();
                this.selectedCustodyChain = data.data;
            } catch (error) {
                console.error("Error fetching custody chain detail:", error);
                this.error = error.message;
            } finally {
                this.loading = false;
            }
        }
    }
});