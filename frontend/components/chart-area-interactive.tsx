"use client"

import * as React from "react"
import { Area, AreaChart, CartesianGrid, XAxis } from "recharts"

import { useIsMobile } from "@/hooks/use-mobile"
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  ChartConfig,
  ChartContainer,
  ChartLegend,
  ChartLegendContent,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  ToggleGroup,
  ToggleGroupItem,
} from "@/components/ui/toggle-group"

export const description = "An interactive area chart"

import { api } from "@/lib/api"
import { type Filters } from "@/lib/analytics"

interface SeriesPointBase {
  date: string;
  calls: number;
  errors: number;
  visitors: number;
  models: string[];
  model_usage: Record<string, number>;
}

type SeriesPoint = SeriesPointBase & Record<string, number>

// Chart config will be generated dynamically based on available agents
const getChartConfig = (agents: string[]): ChartConfig => {
  const colors = ["var(--chart-1)", "var(--chart-2)", "var(--chart-3)", "var(--chart-4)", "var(--chart-5)"]
  const config: ChartConfig = {}

  agents.forEach((agent, index) => {
    config[agent] = {
      label: agent,
      color: colors[index % colors.length],
    }
  })

  return config
}

interface ChartAreaInteractiveProps {
  filters?: Filters
  onModelsUpdate?: (models: string[]) => void
}

export function ChartAreaInteractive({ filters, onModelsUpdate }: ChartAreaInteractiveProps = {}) {
  const isMobile = useIsMobile()
  const [timeRange, setTimeRange] = React.useState("90d")
  const [data, setData] = React.useState<SeriesPoint[]>([])
  const [loading, setLoading] = React.useState(true)
  const [availableAgents, setAvailableAgents] = React.useState<string[]>([])
  const [availableModels, setAvailableModels] = React.useState<string[]>([])
  const [hasLoadedData, setHasLoadedData] = React.useState(false)

  React.useEffect(() => {
    if (isMobile) {
      setTimeRange("7d")
    }
  }, [isMobile])

  React.useEffect(() => {
    const now = new Date()

    // Use filters if provided, otherwise fall back to local timeRange
    let startDate: string
    let endDate: string

    if (filters) {
      // Use filter dates if custom range is selected
      if (filters.timeRange === 'custom' && filters.startDate && filters.endDate) {
        startDate = filters.startDate
        endDate = filters.endDate
      } else {
        // Calculate dates based on timeRange
        let days = 90
        if (filters.timeRange === '30d') days = 30
        if (filters.timeRange === '7d') days = 7
        if (filters.timeRange === '1h') days = 1/24
        if (filters.timeRange === '24h') days = 1
        const start = new Date(now.getTime() - days * 24 * 60 * 60 * 1000)
        startDate = start.toISOString().slice(0, 10)
        endDate = now.toISOString().slice(0, 10)
      }
    } else {
      // Fallback to local timeRange
      let days = 90
      if (timeRange === '30d') days = 30
      if (timeRange === '7d') days = 7
      const start = new Date(now.getTime() - days * 24 * 60 * 60 * 1000)
      startDate = start.toISOString().slice(0, 10)
      endDate = now.toISOString().slice(0, 10)
    }

    setLoading(true)

    // First fetch available agents
    api.getAgents().then((agents) => {
      setAvailableAgents(agents)

      // Fetch data for all agents to show individual lines
      const agentPromises = agents.map(agent =>
        api.getSeries({ startDate, endDate, agents: [agent] }).then((res) => ({
          agent,
          data: res.items || []
        }))
      )

      return Promise.all(agentPromises)
    }).then((results) => {
      // Transform data into format suitable for multi-line chart
      const dateMap = new Map<string, SeriesPoint>()

      results.forEach(({ agent, data: agentData }) => {
        agentData.forEach((point: any) => {
          const date = point.date
          if (!dateMap.has(date)) {
            dateMap.set(date, {
              date,
              calls: 0,
              errors: 0,
              visitors: 0,
              models: [],
              model_usage: {},
              // Initialize with empty agent values
            } as unknown as SeriesPoint)
          }
          const totalUsage = Number(point.calls || 0) + Number(point.visitors || 0)
          dateMap.get(date)![agent] = totalUsage
        })
      })

      // Convert map to array and sort by date
      const chartData = Array.from(dateMap.values()).sort((a, b) =>
        new Date(a.date).getTime() - new Date(b.date).getTime()
      )

      setData(chartData)
      setAvailableAgents(results.map(r => r.agent))

      // Extract all available models from the data
      const allModels = new Set<string>()
      chartData.forEach(point => {
        point.models.forEach(model => allModels.add(model))
      })
      const modelsArray = Array.from(allModels).sort()
      console.log('Chart: Extracted models from data:', modelsArray)
      setAvailableModels(modelsArray)
      setHasLoadedData(true)

      // Only notify parent if we have actual models and this is after initial load
      if (modelsArray.length > 0 && onModelsUpdate && hasLoadedData) {
        console.log('Chart: Calling onModelsUpdate with:', modelsArray)
        onModelsUpdate(modelsArray)
      } else if (modelsArray.length === 0) {
        console.log('Chart: No models found, not calling onModelsUpdate')
      } else {
        console.log('Chart: onModelsUpdate callback not provided or first load')
      }
    }).catch((error) => {
      console.error('Error fetching chart data:', error)
      setData([])
      setAvailableAgents([])
      setAvailableModels([])
    }).finally(() => setLoading(false))
  }, [filters, timeRange])

  // Separate effect to call onModelsUpdate after data is loaded
  React.useEffect(() => {
    if (hasLoadedData && availableModels.length > 0 && onModelsUpdate) {
      console.log('Chart: Calling onModelsUpdate after data load:', availableModels)
      onModelsUpdate(availableModels)
    }
  }, [hasLoadedData, availableModels, onModelsUpdate])

  return (
    <Card className="@container/card">
      <CardHeader>
        <CardTitle>Agent Usage Comparison</CardTitle>
        <CardDescription>
          <span className="hidden @[540px]/card:block">
            Individual agent performance showing calls + visitors over time
          </span>
          <span className="@[540px]/card:hidden">Agent usage comparison</span>
        </CardDescription>
        <CardAction>
          <ToggleGroup
            type="single"
            value={timeRange}
            onValueChange={setTimeRange}
            variant="outline"
            className="hidden *:data-[slot=toggle-group-item]:!px-4 @[767px]/card:flex"
          >
            <ToggleGroupItem value="90d">Last 3 months</ToggleGroupItem>
            <ToggleGroupItem value="30d">Last 30 days</ToggleGroupItem>
            <ToggleGroupItem value="7d">Last 7 days</ToggleGroupItem>
          </ToggleGroup>
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger
              className="flex w-40 **:data-[slot=select-value]:block **:data-[slot=select-value]:truncate @[767px]/card:hidden"
              size="sm"
              aria-label="Select a value"
            >
              <SelectValue placeholder="Last 3 months" />
            </SelectTrigger>
            <SelectContent className="rounded-xl">
              <SelectItem value="90d" className="rounded-lg">
                Last 3 months
              </SelectItem>
              <SelectItem value="30d" className="rounded-lg">
                Last 30 days
              </SelectItem>
              <SelectItem value="7d" className="rounded-lg">
                Last 7 days
              </SelectItem>
            </SelectContent>
          </Select>
        </CardAction>
      </CardHeader>
      <CardContent className="px-2 pt-4 sm:px-6 sm:pt-6">
        <ChartContainer
          config={getChartConfig(availableAgents)}
          className="aspect-auto h-[250px] w-full"
        >
          <AreaChart data={data}>
            <defs>
              {availableAgents.map((agent, index) => {
                const colors = ["var(--chart-1)", "var(--chart-2)", "var(--chart-3)", "var(--chart-4)", "var(--chart-5)"]
                const color = colors[index % colors.length]
                return (
                  <linearGradient key={agent} id={`fill${agent}`} x1="0" y1="0" x2="0" y2="1">
                    <stop
                      offset="5%"
                      stopColor={color}
                      stopOpacity={0.8}
                    />
                    <stop
                      offset="95%"
                      stopColor={color}
                      stopOpacity={0.1}
                    />
                  </linearGradient>
                )
              })}
            </defs>
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="date"
              tickLine={false}
              axisLine={false}
              tickMargin={8}
              minTickGap={32}
              tickFormatter={(value) => {
                const date = new Date(value)
                return date.toLocaleDateString("en-US", {
                  month: "short",
                  day: "numeric",
                })
              }}
            />
            <ChartTooltip
              cursor={false}
              content={
                <ChartTooltipContent
                  labelFormatter={(value) => {
                    return new Date(value).toLocaleDateString("en-US", {
                      month: "short",
                      day: "numeric",
                    })
                  }}
                  indicator="dot"
                />
              }
            />
            {availableAgents.map((agent, index) => {
              const colors = ["var(--chart-1)", "var(--chart-2)", "var(--chart-3)", "var(--chart-4)", "var(--chart-5)"]
              const color = colors[index % colors.length]
              return (
                <Area
                  key={agent}
                  dataKey={agent}
                  type="natural"
                  fill={`url(#fill${agent})`}
                  stroke={color}
                  stackId="a"
                />
              )
            })}
            <ChartLegend content={<ChartLegendContent />} />
          </AreaChart>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}
