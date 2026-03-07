import { defineStore } from "pinia";
import { appConfig } from "@/AppConfig";
import { getLocalDateString } from "@/utils/formatters";


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
            have_logistic: 'NA',
        }
    }),
    actions: {
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
                    const errorMessage =
                        errorData?.message ||
                        errorData?.error ||
                        `Failed to create custody chain (HTTP ${response.status})`;
                    throw new Error(errorMessage);
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
                issue_date: getLocalDateString(),
                consecutive: "00000",
                activity_date: getLocalDateString(),
                location: null,
                total_gallons: 0.0,
                duration_hours: 0.0,
                have_logistic: 'NA',
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
                return data.data;
            } catch (error) {
                console.error("Error fetching custody chain detail:", error);
                this.error = error.message;
                throw error;
            } finally {
                this.loading = false;
            }
        },
        async updateCustodyChain(custodyChainId, custodyChainData) {
            this.loading = true;
            this.error = null;
            console.log("Updating custody chain", custodyChainId, custodyChainData);
            
            try {
                const url = appConfig.URLUpdateCustodyChain.replace("${id}", custodyChainId);
                const response = await fetch(url, {
                    method: "PUT",
                    headers: appConfig.headers,
                    body: JSON.stringify(custodyChainData)
                });
                
                if (!response.ok) {
                    const errorData = await response.json();
                    const errorMessage =
                        errorData?.message ||
                        errorData?.error ||
                        `Failed to update custody chain (HTTP ${response.status})`;
                    throw new Error(errorMessage);
                }
                
                const data = await response.json();
                
                // Actualizar la cadena en la lista local si existe
                const index = this.custodyChains.findIndex(cc => cc.id === custodyChainId);
                if (index !== -1) {
                    // Reemplazar con los nuevos datos
                    this.custodyChains[index] = { ...this.custodyChains[index], ...data.data };
                }
                
                return data.data;
            } catch (error) {
                console.error("Error updating custody chain:", error);
                this.error = error.message;
                throw error;
            } finally {
                this.loading = false;
            }
        }
    }
});