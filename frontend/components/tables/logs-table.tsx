"use client"

import * as React from "react"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { type Filters } from "@/lib/analytics"
import { api } from "@/lib/api"
import Link from "next/link"

type EventRow = {
  id: string
  timestamp: string
  level: 'info' | 'warn' | 'error'
  message: string
  agentId: string
  model?: string
  traceId?: string
}

function deriveDates(filters: Filters): { startDate: string; endDate: string } {
  const now = new Date()
  let start = new Date(now)
  switch (filters.timeRange) {
    case '1h': start = new Date(now.getTime() - 60 * 60 * 1000); break
    case '7d': start = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000); break
    case '30d': start = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000); break
    default: start = new Date(now.getTime() - 24 * 60 * 60 * 1000)
  }
  return {
    startDate: (filters.startDate ?? start.toISOString().slice(0, 10)),
    endDate: (filters.endDate ?? now.toISOString().slice(0, 10))
  }
}

export function LogsTable({ filters }: { filters: Filters }) {
  const [rows, setRows] = React.useState<EventRow[]>([])
  const [loading, setLoading] = React.useState(true)

  React.useEffect(() => {
    const { startDate, endDate } = deriveDates(filters)
    const agentId = filters.agents?.[0] // simple: first selected agent if any
    setLoading(true)
    api.getEvents({ agentId, startDate, endDate, limit: 100 }).then((res) => {
      const mapped: EventRow[] = (res.items || []).map((e: any, idx: number) => ({
        id: `${e.agent_id}-${e.timestamp}-${idx}`,
        timestamp: e.timestamp,
        level: e.message_type === 'error' ? 'error' : 'info',
        message: e.error_details || e.content || e.message_type,
        agentId: e.agent_id,
        model: e.model_used,
        traceId: e.metadata?.trace_id,
      }))
      setRows(mapped)
    }).finally(() => setLoading(false))
  }, [filters.timeRange, filters.startDate, filters.endDate, filters.agents?.join(',')])

  return (
    <div className="overflow-hidden rounded-lg border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Time</TableHead>
            <TableHead>Level</TableHead>
            <TableHead>Message</TableHead>
            <TableHead>Agent</TableHead>
            <TableHead>Model</TableHead>
            <TableHead>Trace</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {loading ? (
            <TableRow>
              <TableCell colSpan={6} className="text-sm text-muted-foreground">Loading events…</TableCell>
            </TableRow>
          ) : (
            rows.map((r) => (
              <TableRow key={r.id}>
                <TableCell className="whitespace-nowrap">{new Date(r.timestamp).toLocaleTimeString()}</TableCell>
                <TableCell>
                  <Badge variant="outline" className="uppercase">{r.level}</Badge>
                </TableCell>
                <TableCell className="max-w-[420px] truncate">{r.message}</TableCell>
                <TableCell>{r.agentId}</TableCell>
                <TableCell>{r.model}</TableCell>
                <TableCell className="font-mono text-xs">
                  {r.traceId ? (
                    <Link href={`/traces/${r.traceId}`} className="underline underline-offset-2">
                      {r.traceId}
                    </Link>
                  ) : null}
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  )
}
