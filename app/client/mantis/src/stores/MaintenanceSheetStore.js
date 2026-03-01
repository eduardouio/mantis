import { defineStore } from "pinia"
import { appConfig } from "@/AppConfig"

export const UseMaintenanceSheetStore = defineStore("maintenanceSheetStore", {
    state: () => ({
        sheets: [],
        selectedSheet: null,
        loading: false,
        error: null,
    }),
    actions: {
        async fetchSheetsBySheetProject(sheetProjectId) {
            this.loading = true
            this.error = null
            try {
                const url = appConfig.URLMaintenanceSheets + "?sheet_project_id=" + sheetProjectId
                const response = await fetch(url, {
                    method: "GET",
                    headers: appConfig.headers,
                })
                if (!response.ok) {
                    throw new Error("Error al obtener las hojas de mantenimiento")
                }
                const data = await response.json()
                this.sheets = data.data || []
                return this.sheets
            } catch (error) {
                console.error("Error fetching maintenance sheets:", error)
                this.error = error.message
                this.sheets = []
                throw error
            } finally {
                this.loading = false
            }
        },

        async fetchSheetDetail(sheetId) {
            this.loading = true
            this.error = null
            try {
                const url = appConfig.URLMaintenanceSheetDetail.replace("${id}", sheetId)
                const response = await fetch(url, {
                    method: "GET",
                    headers: appConfig.headers,
                })
                if (!response.ok) {
                    throw new Error("Error al obtener el detalle de la hoja de mantenimiento")
                }
                const data = await response.json()
                this.selectedSheet = data.data
                return data.data
            } catch (error) {
                console.error("Error fetching sheet detail:", error)
                this.error = error.message
                throw error
            } finally {
                this.loading = false
            }
        },

        async createSheet(sheetData) {
            this.loading = true
            this.error = null
            try {
                const response = await fetch(appConfig.URLMaintenanceSheets, {
                    method: "POST",
                    headers: appConfig.headers,
                    body: JSON.stringify(sheetData),
                })
                if (!response.ok) {
                    const errorData = await response.json()
                    throw new Error(errorData?.error || `Error al crear la hoja (HTTP ${response.status})`)
                }
                const data = await response.json()
                this.sheets.unshift(data.data)
                return data.data
            } catch (error) {
                console.error("Error creating maintenance sheet:", error)
                this.error = error.message
                throw error
            } finally {
                this.loading = false
            }
        },

        async updateSheet(sheetData) {
            this.loading = true
            this.error = null
            try {
                const response = await fetch(appConfig.URLMaintenanceSheets, {
                    method: "PUT",
                    headers: appConfig.headers,
                    body: JSON.stringify(sheetData),
                })
                if (!response.ok) {
                    const errorData = await response.json()
                    throw new Error(errorData?.error || `Error al actualizar la hoja (HTTP ${response.status})`)
                }
                const data = await response.json()
                const index = this.sheets.findIndex(s => s.id === sheetData.id)
                if (index !== -1) {
                    this.sheets[index] = data.data
                }
                return data.data
            } catch (error) {
                console.error("Error updating maintenance sheet:", error)
                this.error = error.message
                throw error
            } finally {
                this.loading = false
            }
        },

        async deleteSheet(sheetId) {
            this.loading = true
            this.error = null
            try {
                const url = appConfig.URLMaintenanceSheetDelete.replace("${id}", sheetId)
                const response = await fetch(url, {
                    method: "DELETE",
                    headers: appConfig.headers,
                })
                if (!response.ok) {
                    const errorData = await response.json()
                    throw new Error(errorData?.error || `Error al eliminar la hoja (HTTP ${response.status})`)
                }
                this.sheets = this.sheets.filter(s => s.id !== sheetId)
                return true
            } catch (error) {
                console.error("Error deleting maintenance sheet:", error)
                this.error = error.message
                throw error
            } finally {
                this.loading = false
            }
        },

        async changeStatus(sheetId, newStatus) {
            this.loading = true
            this.error = null
            try {
                const response = await fetch(appConfig.URLMaintenanceSheets, {
                    method: "PATCH",
                    headers: appConfig.headers,
                    body: JSON.stringify({ id: sheetId, status: newStatus }),
                })
                if (!response.ok) {
                    const errorData = await response.json()
                    throw new Error(errorData?.error || `Error al cambiar estado (HTTP ${response.status})`)
                }
                const data = await response.json()
                const index = this.sheets.findIndex(s => s.id === sheetId)
                if (index !== -1) {
                    this.sheets[index] = data.data
                }
                return data.data
            } catch (error) {
                console.error("Error changing maintenance sheet status:", error)
                this.error = error.message
                throw error
            } finally {
                this.loading = false
            }
        },
    },
})
