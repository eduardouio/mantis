import { defineStore } from "pinia";
import { appConfig } from "@/AppConfig";


export const UseCustodyChainStore = defineStore("custodyChainStore", {
    state: () => ({
        custodyChains: [],
        selectedCustodyChain: null,
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
        async fetchCustodyChains(id_sheet_project) {
            console.log("Fetching custody chains for sheet project ID:", id_sheet_project);
            try {
                const url = appConfig.URLAllCustodyChains.replace("${id_sheet_project}", id_sheet_project);
                const response = await fetch(url, {
                    method: "GET",
                    headers: appConfig.headers,
                });
                if (!response.ok) {
                    throw new Error("Failed to fetch custody chains");
                }
                const data = await response.json();
                this.custodyChains = data.data;
            } catch (error) {
                console.error("Error fetching custody chains:", error);
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
        async fetchCustodyChainDetail(id) {
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
            }   
        }
    }
});