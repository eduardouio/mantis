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
        async fetchCustodyChains() {
            console.log("Fetching custody chains");
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
                    throw new Error("Failed to create custody chain");
                }
                const data = await response.json();
                return data.data;
            } catch (error) {
                console.error("Error creating custody chain:", error);
            }
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