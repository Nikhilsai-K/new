'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Grid3x3, Download, ArrowLeft } from 'lucide-react'
import Plot from 'react-plotly.js'
import Button from '@/components/ui/Button'
import Card from '@/components/ui/Card'
import { useData } from '@/context/DataContext'

export default function DashboardPage() {
  const router = useRouter()
  const data = useData()
  const [dashboardData, setDashboardData] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string>('')
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

  // Generate dashboard on mount or when data changes
  useEffect(() => {
    if (!data.cleanedData) return

    const generateDashboard = async () => {
      setLoading(true)
      setError('')

      try {
        // Convert data to CSV format for API
        const csvContent = [
          data.cleanedData!.columnNames.join(','),
          ...data.cleanedData!.allData.map(row =>
            data.cleanedData!.columnNames.map(col => {
              const value = row[col]
              if (value === null || value === undefined) return ''
              if (typeof value === 'string' && value.includes(',')) {
                return `"${value}"`
              }
              return value
            }).join(',')
          ),
        ].join('\n')

        const blob = new Blob([csvContent], { type: 'text/csv' })
        const file = new File([blob], data.cleanedData!.filename, { type: 'text/csv' })

        const formData = new FormData()
        formData.append('file', file)

        const response = await fetch(`${apiUrl}/api/visualize/dashboard`, {
          method: 'POST',
          body: formData
        })

        const dashData = await response.json()
        setDashboardData(dashData)
      } catch (err) {
        setError('Error generating dashboard. Make sure the backend is running.')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    generateDashboard()
  }, [data.cleanedData])

  const renderChart = (chartData: any, index: number) => {
    if (chartData.error) {
      return (
        <div className="text-center py-8 text-red-400">
          <p>{chartData.error}</p>
        </div>
      )
    }

    const plotData = Array.isArray(chartData.data) ? chartData.data : [chartData.data]
    const layout = {
      ...chartData.layout,
      plot_bgcolor: '#1a1a2e',
      paper_bgcolor: '#16213e',
      font: { color: '#ffffff' },
      margin: { l: 50, r: 30, t: 40, b: 50 }
    }

    return (
      <div key={index} className="bg-white/5 rounded-lg overflow-hidden border border-white/10">
        <Plot
          data={plotData}
          layout={layout}
          config={{
            responsive: true,
            displayModeBar: true,
            displaylogo: false
          }}
          style={{ width: '100%', height: '400px' }}
        />
      </div>
    )
  }

  // No cleaned data - show error
  if (!data.cleanedData) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        <header className="border-b border-slate-700 backdrop-blur-sm bg-slate-900/50">
          <div className="container mx-auto px-4 py-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
                  <Grid3x3 className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-white">Data Dashboard</h1>
                  <p className="text-sm text-slate-400">Auto-generated visualizations</p>
                </div>
              </div>
              <Button
                onClick={() => router.push('/')}
                variant="outline"
                className="gap-2"
              >
                <ArrowLeft className="w-4 h-4" />
                Back to Cleaner
              </Button>
            </div>
          </div>
        </header>

        <div className="container mx-auto px-4 py-12">
          <div className="max-w-4xl mx-auto">
            <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700 text-center p-8">
              <h2 className="text-3xl font-bold text-white mb-4">No Cleaned Data</h2>
              <p className="text-slate-400 mb-6">
                Please clean your dataset first to create a dashboard
              </p>
              <Button onClick={() => router.push('/')}>
                Go to Main Page
              </Button>
            </Card>
          </div>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="border-b border-slate-700 backdrop-blur-sm bg-slate-900/50">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
                <Grid3x3 className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">Data Dashboard</h1>
                <p className="text-sm text-slate-400">Auto-generated visualizations</p>
              </div>
            </div>
            <Button
              onClick={() => router.push('/')}
              variant="outline"
              className="gap-2"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Cleaner
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-12">
        <div className="space-y-8">
          {/* Summary Stats */}
          {dashboardData?.summary && (
            <Card className="bg-gradient-to-r from-blue-500/10 to-cyan-500/10 backdrop-blur-sm border border-slate-600 p-8">
              <h2 className="text-xl font-bold text-white mb-6">Data Summary</h2>
              <div className="grid md:grid-cols-4 gap-6">
                <div className="p-4 bg-slate-700/50 rounded-lg border border-slate-600">
                  <p className="text-sm text-slate-400 mb-2">Total Rows</p>
                  <p className="text-3xl font-bold text-white">{dashboardData.summary.total_rows?.toLocaleString()}</p>
                </div>
                <div className="p-4 bg-slate-700/50 rounded-lg border border-slate-600">
                  <p className="text-sm text-slate-400 mb-2">Total Columns</p>
                  <p className="text-3xl font-bold text-white">{dashboardData.summary.total_columns}</p>
                </div>
                <div className="p-4 bg-slate-700/50 rounded-lg border border-slate-600">
                  <p className="text-sm text-slate-400 mb-2">Numeric Columns</p>
                  <p className="text-3xl font-bold text-cyan-400">{dashboardData.summary.numeric_columns}</p>
                </div>
                <div className="p-4 bg-slate-700/50 rounded-lg border border-slate-600">
                  <p className="text-sm text-slate-400 mb-2">Categorical Columns</p>
                  <p className="text-3xl font-bold text-blue-400">{dashboardData.summary.categorical_columns}</p>
                </div>
              </div>
            </Card>
          )}

          {/* Loading State */}
          {loading && (
            <div className="text-center py-12">
              <div className="inline-block">
                <div className="w-12 h-12 border-4 border-slate-600 border-t-blue-500 rounded-full animate-spin"></div>
              </div>
              <p className="text-slate-300 mt-4">Generating dashboard...</p>
            </div>
          )}

          {/* Error State */}
          {error && (
            <Card className="bg-red-500/20 border border-red-500/50 p-4">
              <p className="text-red-300">{error}</p>
            </Card>
          )}

          {/* Charts Grid */}
          {dashboardData?.charts && dashboardData.charts.length > 0 && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-white">Visualizations</h2>
                <div className="text-sm text-slate-400">
                  {dashboardData.charts.length} charts
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                {dashboardData.charts.map((chartData: any, index: number) => (
                  renderChart(chartData, index)
                ))}
              </div>
            </div>
          )}

          {/* File Info */}
          <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700 p-4 text-center">
            <p className="text-sm text-slate-400">
              Analyzing: <span className="text-white font-semibold">{data.cleanedData.filename}</span>
            </p>
          </Card>
        </div>
      </div>
    </main>
  )
}
