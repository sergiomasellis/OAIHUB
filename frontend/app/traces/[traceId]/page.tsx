"use client"

import * as React from "react"
import { api } from "@/lib/api"

export default function TracePage({ params }: { params: { traceId: string } }) {
  const { traceId } = params
  const [data, setData] = React.useState<any>(null)
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState<string | null>(null)

  React.useEffect(() => {
    setLoading(true)
    api.getTrace(traceId)
      .then(setData)
      .catch((e) => setError(e?.message || 'Failed to load trace'))
      .finally(() => setLoading(false))
  }, [traceId])

  if (loading) return <div className="p-6 text-sm text-muted-foreground">Loading trace…</div>
  if (error) return <div className="p-6 text-sm text-destructive">{error}</div>
  if (!data) return <div className="p-6">No data</div>

  return (
    <div className="p-6 space-y-4">
      <div>
        <div className="text-xs text-muted-foreground">Trace ID</div>
        <div className="font-mono text-sm">{data.trace_id}</div>
      </div>
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <div className="text-xs text-muted-foreground">Start</div>
          <div>{data.start_time}</div>
        </div>
        <div>
          <div className="text-xs text-muted-foreground">End</div>
          <div>{data.end_time}</div>
        </div>
        <div>
          <div className="text-xs text-muted-foreground">Duration</div>
          <div>{data.duration_ms ?? '-'} ms</div>
        </div>
      </div>
      <div>
        <div className="text-sm font-medium mb-2">Spans</div>
        <div className="border rounded-md overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-muted/50">
              <tr>
                <th className="text-left px-3 py-2">Name</th>
                <th className="text-left px-3 py-2">Span</th>
                <th className="text-left px-3 py-2">Parent</th>
                <th className="text-left px-3 py-2">Service</th>
                <th className="text-left px-3 py-2">Start</th>
                <th className="text-left px-3 py-2">End</th>
                <th className="text-left px-3 py-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {(data.spans || []).map((s: any) => (
                <tr key={s.span_id} className="border-t">
                  <td className="px-3 py-2">{s.name}</td>
                  <td className="px-3 py-2 font-mono text-xs">{s.span_id}</td>
                  <td className="px-3 py-2 font-mono text-xs">{s.parent_span_id || '-'}</td>
                  <td className="px-3 py-2">{s.service_name || '-'}</td>
                  <td className="px-3 py-2">{s.start_time || '-'}</td>
                  <td className="px-3 py-2">{s.end_time || '-'}</td>
                  <td className="px-3 py-2">{s.status || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

