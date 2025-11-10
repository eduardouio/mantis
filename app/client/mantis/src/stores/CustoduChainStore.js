import { defineStore } from "pinia";
import { appConfig } from "@/AppConfig";


export const UseCustodyChainStore = defineStore("custodyChainStore", {
    state: () => ({
        custodyChains: [],
        selectedCustodyChain: null,
        newCustodyChain: {
            id: null,
            id_sheet_project: null,
            consecutive: null,
            activity_date: null,
            location: null,
            start_time: null,
            end_time: null,
            total_gallons: 0.0,
            duration_hours: 0.0,
        }
    }),
    actions: {
    }
});