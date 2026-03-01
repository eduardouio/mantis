import { defineStore } from "pinia"
import { appConfig } from "@/AppConfig"

export const UseShippingGuideStore = defineStore("shippingGuideStore", {
    state: () => ({
        shippingGuides: [],
        selectedGuide: null,
        loading: false,
        error: null,
    }),
    actions: {
        async fetchGuidesByProject() {
            this.loading = true
            this.error = null
            try {
                const url = appConfig.URLShippingGuides + "?project_id=" + appConfig.idProject
                const response = await fetch(url, {
                    method: "GET",
                    headers: appConfig.headers,
                })
                if (!response.ok) {
                    throw new Error("Error al obtener las guías de remisión")
                }
                const data = await response.json()
                this.shippingGuides = data.data || []
                return this.shippingGuides
            } catch (error) {
                console.error("Error fetching shipping guides:", error)
                this.error = error.message
                this.shippingGuides = []
                throw error
            } finally {
                this.loading = false
            }
        },

        async fetchGuideDetail(guideId) {
            this.loading = true
            this.error = null
            try {
                const url = appConfig.URLShippingGuideDetail.replace("${id}", guideId)
                const response = await fetch(url, {
                    method: "GET",
                    headers: appConfig.headers,
                })
                if (!response.ok) {
                    throw new Error("Error al obtener el detalle de la guía")
                }
                const data = await response.json()
                this.selectedGuide = data.data
                return data.data
            } catch (error) {
                console.error("Error fetching guide detail:", error)
                this.error = error.message
                throw error
            } finally {
                this.loading = false
            }
        },

        async createGuide(guideData) {
            this.loading = true
            this.error = null
            try {
                const response = await fetch(appConfig.URLShippingGuides, {
                    method: "POST",
                    headers: appConfig.headers,
                    body: JSON.stringify(guideData),
                })
                if (!response.ok) {
                    const errorData = await response.json()
                    throw new Error(errorData?.error || `Error al crear la guía (HTTP ${response.status})`)
                }
                const data = await response.json()
                this.shippingGuides.unshift(data.data)
                return data.data
            } catch (error) {
                console.error("Error creating shipping guide:", error)
                this.error = error.message
                throw error
            } finally {
                this.loading = false
            }
        },

        async updateGuide(guideData) {
            this.loading = true
            this.error = null
            try {
                const response = await fetch(appConfig.URLShippingGuides, {
                    method: "PUT",
                    headers: appConfig.headers,
                    body: JSON.stringify(guideData),
                })
                if (!response.ok) {
                    const errorData = await response.json()
                    throw new Error(errorData?.error || `Error al actualizar la guía (HTTP ${response.status})`)
                }
                const data = await response.json()

                // Actualizar en la lista local
                const index = this.shippingGuides.findIndex(g => g.id === guideData.id)
                if (index !== -1) {
                    this.shippingGuides[index] = data.data
                }

                return data.data
            } catch (error) {
                console.error("Error updating shipping guide:", error)
                this.error = error.message
                throw error
            } finally {
                this.loading = false
            }
        },

        async deleteGuide(guideId) {
            this.loading = true
            this.error = null
            try {
                const url = appConfig.URLShippingGuideDelete.replace("${id}", guideId)
                const response = await fetch(url, {
                    method: "DELETE",
                    headers: appConfig.headers,
                })
                if (!response.ok) {
                    const errorData = await response.json()
                    throw new Error(errorData?.error || `Error al eliminar la guía (HTTP ${response.status})`)
                }
                // Remover de la lista local
                this.shippingGuides = this.shippingGuides.filter(g => g.id !== guideId)
                return true
            } catch (error) {
                console.error("Error deleting shipping guide:", error)
                this.error = error.message
                throw error
            } finally {
                this.loading = false
            }
        },

        async changeStatus(guideId, newStatus) {
            this.loading = true
            this.error = null
            try {
                const response = await fetch(appConfig.URLShippingGuides, {
                    method: "PATCH",
                    headers: appConfig.headers,
                    body: JSON.stringify({ id: guideId, status: newStatus }),
                })
                if (!response.ok) {
                    const errorData = await response.json()
                    throw new Error(errorData?.error || `Error al cambiar estado (HTTP ${response.status})`)
                }
                const data = await response.json()

                // Actualizar en la lista local
                const index = this.shippingGuides.findIndex(g => g.id === guideId)
                if (index !== -1) {
                    this.shippingGuides[index] = data.data
                }

                return data.data
            } catch (error) {
                console.error("Error changing shipping guide status:", error)
                this.error = error.message
                throw error
            } finally {
                this.loading = false
            }
        },
    },
})
