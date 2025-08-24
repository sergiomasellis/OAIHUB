"use client"

import * as React from "react"
import { defaultFilters, type Filters } from "@/lib/analytics"
import { LogsTable } from "@/components/tables/logs-table"
import { DashboardFilters } from "@/components/dashboard/filters"

export default function LogsPage() {
  const [filters, setFilters] = React.useState<Filters>(defaultFilters)
  return (
    <React.Suspense>
      <div className="flex flex-col gap-4">
        <DashboardFilters filters={filters} onFiltersChange={setFilters} />
        <div className="px-4 lg:px-6 pb-6">
          <LogsTable filters={filters} />
        </div>
      </div>
    </React.Suspense>
  )
}
