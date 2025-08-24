"use client"

import * as React from "react"
import { ChartAreaInteractive } from "@/components/chart-area-interactive"
import { DataTable } from "@/components/data-table"
import { DashboardFilters } from "@/components/dashboard/filters"
import { KPICards } from "@/components/kpi-cards"
import data from "./data.json"
import { defaultFilters, type Filters } from "@/lib/analytics"

export default function Page() {
  const [filters, setFilters] = React.useState<Filters>(defaultFilters)
  const [availableModels, setAvailableModels] = React.useState<string[]>([])

  const handleModelsUpdate = (models: string[]) => {
    console.log('Dashboard: Received models update:', models)
    setAvailableModels(models)
  }

  return (
    <>
      <DashboardFilters
        filters={filters}
        onFiltersChange={setFilters}
        availableModels={availableModels}
      />
      <KPICards filters={filters} />
       <div className="px-4 lg:px-6">
         <ChartAreaInteractive
           filters={filters}
           onModelsUpdate={handleModelsUpdate}
         />
       </div>
      <DataTable data={data} />
    </>
  )
}
