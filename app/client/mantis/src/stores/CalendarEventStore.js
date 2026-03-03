import { defineStore } from "pinia"
import { appConfig } from "@/AppConfig"

export const UseCalendarEventStore = defineStore("calendarEventStore", {
    state: () => ({
        events: [],
        selectedEvent: null,
        loading: false,
        error: null,
    }),
    getters: {
        eventsByDate(state) {
            const byDate = {}
            state.events.forEach(event => {
                const dateStr = event.start_date
                if (!byDate[dateStr]) {
                    byDate[dateStr] = []
                }
                byDate[dateStr].push(event)
            })
            return byDate
        },
    },
    actions: {
        async fetchEventsByMonth(projectId, year, month) {
            this.loading = true
            this.error = null
            try {
                const url = appConfig.URLCalendarEvents + `?project_id=${projectId}&year=${year}&month=${month}`
                const response = await fetch(url, {
                    method: "GET",
                    headers: appConfig.headers,
                })
                if (!response.ok) {
                    throw new Error("Error al obtener los eventos del calendario")
                }
                const data = await response.json()
                this.events = data.data || []
                return this.events
            } catch (error) {
                console.error("Error fetching calendar events:", error)
                this.error = error.message
                this.events = []
                throw error
            } finally {
                this.loading = false
            }
        },

        async fetchEventDetail(eventId) {
            this.loading = true
            this.error = null
            try {
                const url = appConfig.URLCalendarEventDetail.replace("${id}", eventId)
                const response = await fetch(url, {
                    method: "GET",
                    headers: appConfig.headers,
                })
                if (!response.ok) {
                    throw new Error("Error al obtener el detalle del evento")
                }
                const data = await response.json()
                this.selectedEvent = data.data
                return data.data
            } catch (error) {
                console.error("Error fetching event detail:", error)
                this.error = error.message
                throw error
            } finally {
                this.loading = false
            }
        },

        async createEvent(eventData) {
            this.loading = true
            this.error = null
            try {
                const response = await fetch(appConfig.URLCalendarEvents, {
                    method: "POST",
                    headers: appConfig.headers,
                    body: JSON.stringify(eventData),
                })
                if (!response.ok) {
                    const errorData = await response.json()
                    throw new Error(errorData?.error || `Error al crear el evento (HTTP ${response.status})`)
                }
                const data = await response.json()
                this.events.push(data.data)
                return data.data
            } catch (error) {
                console.error("Error creating calendar event:", error)
                this.error = error.message
                throw error
            } finally {
                this.loading = false
            }
        },

        async updateEvent(eventData) {
            this.loading = true
            this.error = null
            try {
                const url = appConfig.URLCalendarEventDetail.replace("${id}", eventData.id)
                const response = await fetch(url, {
                    method: "PUT",
                    headers: appConfig.headers,
                    body: JSON.stringify(eventData),
                })
                if (!response.ok) {
                    const errorData = await response.json()
                    throw new Error(errorData?.error || `Error al actualizar el evento (HTTP ${response.status})`)
                }
                const data = await response.json()
                const index = this.events.findIndex(e => e.id === eventData.id)
                if (index !== -1) {
                    this.events[index] = data.data
                }
                return data.data
            } catch (error) {
                console.error("Error updating calendar event:", error)
                this.error = error.message
                throw error
            } finally {
                this.loading = false
            }
        },

        async moveEvent(eventId, newStartDate, newEndDate = null) {
            this.error = null
            try {
                const url = appConfig.URLCalendarEventMove.replace("${id}", eventId)
                const body = { start_date: newStartDate }
                if (newEndDate) {
                    body.end_date = newEndDate
                }
                const response = await fetch(url, {
                    method: "PATCH",
                    headers: appConfig.headers,
                    body: JSON.stringify(body),
                })
                if (!response.ok) {
                    const errorData = await response.json()
                    throw new Error(errorData?.error || `Error al mover el evento (HTTP ${response.status})`)
                }
                const data = await response.json()
                const index = this.events.findIndex(e => e.id === eventId)
                if (index !== -1) {
                    this.events[index] = data.data
                }
                return data.data
            } catch (error) {
                console.error("Error moving calendar event:", error)
                this.error = error.message
                throw error
            }
        },

        async deleteEvent(eventId) {
            this.loading = true
            this.error = null
            try {
                const url = appConfig.URLCalendarEventDelete.replace("${id}", eventId)
                const response = await fetch(url, {
                    method: "DELETE",
                    headers: appConfig.headers,
                })
                if (!response.ok) {
                    const errorData = await response.json()
                    throw new Error(errorData?.error || `Error al eliminar el evento (HTTP ${response.status})`)
                }
                this.events = this.events.filter(e => e.id !== eventId)
                return true
            } catch (error) {
                console.error("Error deleting calendar event:", error)
                this.error = error.message
                throw error
            } finally {
                this.loading = false
            }
        },
    },
})
