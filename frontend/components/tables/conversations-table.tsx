"use client"

import * as React from "react"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { type Filters } from "@/lib/analytics"
import { api } from "@/lib/api"

type Row = {
  id: string
  agentId: string
  startedAt: string
  duration: number
  messageCount: number
  status: 'completed' | 'active' | 'error'
}

function deriveDates(filters: Filters): { startDate: string; endDate: string } {
  const now = new Date()
  let start = new Date(now)
  switch (filters.timeRange) {
    case '7d': start = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000); break
    case '30d': start = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000); break
    default: start = new Date(now.getTime() - 24 * 60 * 60 * 1000)
  }
  return { startDate: (filters.startDate ?? start.toISOString().slice(0,10)), endDate: (filters.endDate ?? now.toISOString().slice(0,10)) }
}

export function ConversationsTable({ filters }: { filters: Filters }) {
  const [rows, setRows] = React.useState<Row[]>([])
  const [loading, setLoading] = React.useState(true)

  React.useEffect(() => {
    const { startDate, endDate } = deriveDates(filters)
    const agentId = filters.agents?.[0]
    setLoading(true)
    api.getConversations({ startDate, endDate, agentId, limit: 100 }).then((res) => {
      const mapped: Row[] = (res.items || []).map((c: any) => ({
        id: c.id,
        agentId: c.agent_id,
        startedAt: c.startedAt,
        duration: c.duration,
        messageCount: c.messageCount,
        status: c.status,
      }))
      setRows(mapped)
    }).finally(() => setLoading(false))
  }, [filters.timeRange, filters.startDate, filters.endDate, filters.agents?.join(',')])

  return (
    <div className="overflow-hidden rounded-lg border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Conversation</TableHead>
            <TableHead>Agent</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Started</TableHead>
            <TableHead className="text-right">Messages</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {loading ? (
            <TableRow>
              <TableCell colSpan={5} className="text-sm text-muted-foreground">Loading conversations…</TableCell>
            </TableRow>
          ) : rows.map((r) => (
            <TableRow key={r.id}>
              <TableCell className="font-medium">{r.id}</TableCell>
              <TableCell>{r.agentId}</TableCell>
              <TableCell>
                <Badge variant="outline" className="capitalize">{r.status}</Badge>
              </TableCell>
              <TableCell>{new Date(r.startedAt).toLocaleString()}</TableCell>
              <TableCell className="text-right tabular-nums">{r.messageCount}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}
