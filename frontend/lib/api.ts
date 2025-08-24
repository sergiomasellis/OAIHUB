"use client"

// Get the API base URL from environment variables
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  // Fallback for docker-compose env naming
  (process.env as any).REACT_APP_API_URL ||
  'http://localhost:8001/api/v1'

// Helper function for API calls
async function apiCall<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`
  
  const config: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  }

  try {
    const response = await fetch(url, config)
    
    if (!response.ok) {
      throw new Error(`API call failed: ${response.status} ${response.statusText}`)
    }
    
    return await response.json()
  } catch (error) {
    console.error(`API call failed for ${url}:`, error)
    throw error
  }
}

// API functions
export const api = {
  // Get list of all agents
  getAgents: () => apiCall<string[]>('/agents'),
  
  // Record an agent event
  recordAgentEvent: (agentId: string, event: any) => 
    apiCall<any>(`/agents/${agentId}/events`, {
      method: 'POST',
      body: JSON.stringify(event),
    }),
  
  // Get agent metrics
  getAgentMetrics: (agentId: string, params?: { days?: number; startDate?: string; endDate?: string }) => {
    const searchParams = new URLSearchParams()
    if (params?.days) searchParams.append('days', params.days.toString())
    if (params?.startDate) searchParams.append('start_date', params.startDate)
    if (params?.endDate) searchParams.append('end_date', params.endDate)
    
    const queryString = searchParams.toString()
    const endpoint = `/agents/${agentId}/metrics${queryString ? '?' + queryString : ''}`
    
    return apiCall<any>(endpoint)
  },

  // Get dashboard KPIs
  getKPIs: (params?: { startDate?: string; endDate?: string; agents?: string[] }) => {
    const sp = new URLSearchParams()
    if (params?.startDate) sp.append('start_date', params.startDate)
    if (params?.endDate) sp.append('end_date', params.endDate)
    if (params?.agents && params.agents.length) sp.append('agents', params.agents.join(','))
    const qs = sp.toString()
    return apiCall<any>(`/dashboard/kpis${qs ? '?' + qs : ''}`)
  },

  // List events with optional filters
  getEvents: (params?: { agentId?: string; messageType?: string; startDate?: string; endDate?: string; limit?: number }) => {
    const sp = new URLSearchParams()
    if (params?.agentId) sp.append('agent_id', params.agentId)
    if (params?.messageType) sp.append('message_type', params.messageType)
    if (params?.startDate) sp.append('start_date', params.startDate)
    if (params?.endDate) sp.append('end_date', params.endDate)
    if (params?.limit) sp.append('limit', String(params.limit))
    const qs = sp.toString()
    return apiCall<any>(`/events${qs ? '?' + qs : ''}`)
  },

  // Time-series metrics (daily calls/errors)
  getSeries: (params?: { startDate?: string; endDate?: string; agents?: string[] }) => {
    const sp = new URLSearchParams()
    if (params?.startDate) sp.append('start_date', params.startDate)
    if (params?.endDate) sp.append('end_date', params.endDate)
    if (params?.agents && params.agents.length) sp.append('agents', params.agents.join(','))
    const qs = sp.toString()
    return apiCall<any>(`/metrics/series${qs ? '?' + qs : ''}`)
  },

  // Conversations summary
  getConversations: (params?: { startDate?: string; endDate?: string; agentId?: string; limit?: number }) => {
    const sp = new URLSearchParams()
    if (params?.startDate) sp.append('start_date', params.startDate)
    if (params?.endDate) sp.append('end_date', params.endDate)
    if (params?.agentId) sp.append('agent_id', params.agentId)
    if (params?.limit) sp.append('limit', String(params.limit))
    const qs = sp.toString()
    return apiCall<any>(`/conversations${qs ? '?' + qs : ''}`)
  },

  // Trace detail
  getTrace: (traceId: string) => apiCall<any>(`/traces/${encodeURIComponent(traceId)}`),
}
