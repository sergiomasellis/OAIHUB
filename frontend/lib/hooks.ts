"use client"

import * as React from "react"
import { api } from "@/lib/api"

// Mock data types based on backend models
export interface AgentEvent {
  agent_id: string
  timestamp: string
  message_type: string
  content?: string
  metadata?: Record<string, any>
  error_details?: string
  response_time_ms?: number
  token_count?: number
  model_used?: string
  user_feedback?: number
}

export interface AgentMetrics {
  agent_id: string
  date: string
  total_messages: number
  total_responses: number
  total_errors: number
  average_response_time: number
  total_tokens_used: number
  average_feedback_score: number
  unique_users: number
}

// Hook for fetching agents
export function useAgents() {
  const [agents, setAgents] = React.useState<string[]>([])
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState<Error | null>(null)

  React.useEffect(() => {
    const fetchAgents = async () => {
      try {
        setLoading(true)
        const data = await api.getAgents()
        setAgents(data)
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to fetch agents'))
      } finally {
        setLoading(false)
      }
    }

    fetchAgents()
  }, [])

  return { agents, loading, error }
}

// Hook for fetching agent metrics
export function useAgentMetrics(agentId: string, options?: { 
  days?: number; 
  startDate?: string; 
  endDate?: string 
}) {
  const [metrics, setMetrics] = React.useState<AgentMetrics | null>(null)
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState<Error | null>(null)

  React.useEffect(() => {
    if (!agentId) return

    const fetchMetrics = async () => {
      try {
        setLoading(true)
        const data = await api.getAgentMetrics(agentId, options)
        setMetrics(data.metrics)
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to fetch metrics'))
      } finally {
        setLoading(false)
      }
    }

    fetchMetrics()
  }, [agentId, options?.days, options?.startDate, options?.endDate])

  return { metrics, loading, error }
}

// Hook for recording agent events
export function useRecordAgentEvent() {
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState<Error | null>(null)

  const recordEvent = React.useCallback(async (agentId: string, event: Partial<AgentEvent>) => {
    try {
      setLoading(true)
      setError(null)
      await api.recordAgentEvent(agentId, event)
      return true
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to record event'))
      return false
    } finally {
      setLoading(false)
    }
  }, [])

  return { recordEvent, loading, error }
}