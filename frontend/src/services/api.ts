import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Event Monitor API
export const eventApi = {
  getEvents: (params: any) => api.post('/analytics/events', params),
  getEventTrends: (params: any) => api.get('/analytics/events/trends', { params }),
  getTopActors: (params: any) => api.get('/analytics/events/top-actors', { params }),
  getEventEvidence: (eventId: string) => api.get(`/analytics/events/${eventId}/evidence`),
  detectSpikes: (params: any) => api.get('/analytics/events/spikes', { params }),
}

// Entity Intelligence API
export const entityApi = {
  searchEntities: (data: any) => api.post('/analytics/entities/search', data),
  getEntityOverview: (entityId: string) => api.get(`/analytics/entities/${entityId}/overview`),
  getEntityTimeline: (entityId: string, params: any) => 
    api.get(`/analytics/entities/${entityId}/timeline`, { params }),
  getEntityNetwork: (entityId: string, params: any) => 
    api.get(`/analytics/entities/${entityId}/network`, { params }),
  getEntitySources: (entityId: string, params: any) => 
    api.get(`/analytics/entities/${entityId}/sources`, { params }),
}

// Storyline Explorer API
export const storylineApi = {
  findStorylines: (data: any) => api.post('/analytics/storylines/find', data),
  getBridgeActors: (params: any) => api.get('/analytics/bridge-actors', { params }),
  getEntityChains: (entityId: string, params: any) => 
    api.get(`/analytics/storylines/entity/${entityId}/chains`, { params }),
  analyzeTransitions: (params: any) => api.get('/analytics/storylines/transitions', { params }),
}

// Alerts API
export const alertsApi = {
  getAlerts: (params: any) => api.get('/analytics/alerts', { params }),
  configureAlerts: (data: any) => api.post('/analytics/alerts/config', data),
}

// QA API
export const qaApi = {
  askQuestion: (data: any) => api.post('/analytics/qa', data),
}

// Statistics API
export const statsApi = {
  getOverview: () => api.get('/analytics/stats/overview'),
  getEventTypeDistribution: () => api.get('/analytics/stats/event-types'),
}

export default api

