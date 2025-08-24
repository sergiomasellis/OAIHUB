"use client"

import * as React from "react"
import { defaultFilters, type Filters } from "@/lib/analytics"
import { ConversationsTable } from "@/components/tables/conversations-table"
import { DashboardFilters } from "@/components/dashboard/filters"

export default function ConversationsPage() {
  const [filters, setFilters] = React.useState<Filters>(defaultFilters)
  return (
    <React.Suspense>
      <div className="flex flex-col gap-4">
        <DashboardFilters filters={filters} onFiltersChange={setFilters} />
        <div className="px-4 lg:px-6 pb-6">
          <ConversationsTable filters={filters} />
        </div>
      </div>
    </React.Suspense>
  )
}
