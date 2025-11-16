'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import {
  Database, Upload, Download, BarChart3, LineChart, PieChart,
  ArrowLeft, TrendingUp, Users, DollarSign, ShoppingCart,
  Server, Cloud, HardDrive, Plus, Settings, Sparkles, Lightbulb,
  Grid3x3, Maximize2, Filter, RefreshCw, FileDown, Share2
} from 'lucide-react'
import Script from 'next/script'

type DataSource = 'file' | 'bigquery' | 'postgresql' | 'mysql' | 'sqlserver' | 'snowflake' | 'redshift' | 's3' | 'azure'

interface AIChart {
  title: string
  chart_type: string
  x_column: string
  y_column: string | null
  story: string
  insight: string
  config: {
    data: any
    layout: any
  }
}

export default function BusinessDashboardPage() {
  const router = useRouter()
  const [selectedSource, setSelectedSource] = useState<DataSource | null>(null)
  const [connected, setConnected] = useState(false)
  const [loading, setLoading] = useState(false)
  const [dashboardData, setDashboardData] = useState<any>(null)
  const [aiCharts, setAiCharts] = useState<AIChart[]>([])
  const [plotlyLoaded, setPlotlyLoaded] = useState(false)
  const [renderAttempts, setRenderAttempts] = useState<Map<number, number>>(new Map())

  // Database connection states
  const [dbConfig, setDbConfig] = useState({
    host: '',
    port: '',
    database: '',
    username: '',
    password: '',
    query: 'SELECT * FROM table_name'
  })

  const dataSources = [
    { id: 'file' as DataSource, name: 'Local File', icon: Upload, color: 'blue', description: 'Upload CSV, Excel files' },
    { id: 'bigquery' as DataSource, name: 'BigQuery', icon: Cloud, color: 'green', description: 'Google Cloud BigQuery' },
    { id: 'postgresql' as DataSource, name: 'PostgreSQL', icon: Database, color: 'indigo', description: 'PostgreSQL database' },
    { id: 'mysql' as DataSource, name: 'MySQL', icon: Database, color: 'orange', description: 'MySQL database' },
    { id: 'sqlserver' as DataSource, name: 'SQL Server', icon: Server, color: 'red', description: 'Microsoft SQL Server' },
    { id: 'snowflake' as DataSource, name: 'Snowflake', icon: Cloud, color: 'cyan', description: 'Snowflake Data Warehouse' },
    { id: 'redshift' as DataSource, name: 'Redshift', icon: Cloud, color: 'purple', description: 'Amazon Redshift' },
    { id: 's3' as DataSource, name: 'Amazon S3', icon: HardDrive, color: 'yellow', description: 'AWS S3 Data Lake' },
    { id: 'azure' as DataSource, name: 'Azure Data Lake', icon: HardDrive, color: 'blue', description: 'Azure Data Lake Storage' },
  ]

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setLoading(true)

    try {
      const formData = new FormData()
      formData.append('file', file)

      // Call AI-powered dashboard generation endpoint
      const response = await fetch('http://localhost:8001/api/dashboard/ai-generate', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to generate dashboard')
      }

      const data = await response.json()

      if (data.error) {
        alert(`AI Dashboard Error: ${data.error}\n\nPlease ensure Ollama is running with Llama 3.1 8B:\nollama pull llama3.1:8b`)
        return
      }

      console.log('Dashboard data received:', data)
      console.log('Charts count:', data.charts?.length || 0)

      setDashboardData(data)
      setAiCharts(data.charts || [])
      setConnected(true)
      setRenderAttempts(new Map())

      // Render charts with multiple retries to ensure all render
      setTimeout(() => {
        console.log('Starting chart rendering...')
        renderAllChartsWithRetry(data.charts || [])
      }, 1000)

    } catch (error: any) {
      console.error('Error:', error)
      alert(error.message || 'Failed to generate AI dashboard')
    } finally {
      setLoading(false)
    }
  }

  const renderAllChartsWithRetry = (charts: AIChart[], attempt: number = 1) => {
    if (!plotlyLoaded || !window.Plotly) {
      console.log(`Plotly not loaded yet, retry attempt ${attempt}...`)
      if (attempt < 10) {
        setTimeout(() => renderAllChartsWithRetry(charts, attempt + 1), 500)
      }
      return
    }

    console.log(`Rendering ${charts.length} charts (attempt ${attempt})...`)
    let successCount = 0
    let failedIndices: number[] = []

    charts.forEach((chart, index) => {
      try {
        const elementId = `chart-${index}`
        const element = document.getElementById(elementId)

        if (!element) {
          console.error(`Chart element ${elementId} not found in DOM`)
          failedIndices.push(index)
          return
        }

        const config = chart.config

        // Handle different data formats
        let plotData
        if (Array.isArray(config.data)) {
          plotData = config.data
        } else {
          plotData = [config.data]
        }

        // Enhanced layout for professional appearance
        const layout = {
          ...config.layout,
          autosize: true,
          margin: { l: 60, r: 30, t: 30, b: 60 },
          plot_bgcolor: 'rgba(15, 23, 42, 0.8)',
          paper_bgcolor: 'transparent',
          font: {
            color: '#e2e8f0',
            size: 12,
            family: 'Inter, system-ui, sans-serif'
          },
          hovermode: 'closest',
          hoverlabel: {
            bgcolor: '#1e293b',
            bordercolor: '#475569',
            font: { color: '#f1f5f9', size: 13 }
          },
          xaxis: {
            ...config.layout?.xaxis,
            gridcolor: 'rgba(148, 163, 184, 0.1)',
            color: '#cbd5e1',
            tickfont: { size: 11 }
          },
          yaxis: {
            ...config.layout?.yaxis,
            gridcolor: 'rgba(148, 163, 184, 0.1)',
            color: '#cbd5e1',
            tickfont: { size: 11 }
          }
        }

        console.log(`Rendering chart ${index}: ${chart.title} (${chart.chart_type})`)

        window.Plotly.newPlot(elementId, plotData, layout, {
          responsive: true,
          displayModeBar: true,
          displaylogo: false,
          modeBarButtonsToRemove: ['lasso2d', 'select2d']
        })

        successCount++
        console.log(`✓ Chart ${index} rendered successfully`)

      } catch (error) {
        console.error(`✗ Error rendering chart ${index} (${chart.title}):`, error)
        failedIndices.push(index)
      }
    })

    console.log(`Rendered ${successCount}/${charts.length} charts successfully`)

    // Retry failed charts
    if (failedIndices.length > 0 && attempt < 5) {
      console.log(`Retrying ${failedIndices.length} failed charts in 1 second...`)
      setTimeout(() => {
        failedIndices.forEach(index => {
          const chart = charts[index]
          const elementId = `chart-${index}`
          const element = document.getElementById(elementId)

          if (element && window.Plotly) {
            try {
              const config = chart.config
              let plotData = Array.isArray(config.data) ? config.data : [config.data]

              const layout = {
                ...config.layout,
                autosize: true,
                margin: { l: 60, r: 30, t: 30, b: 60 },
                plot_bgcolor: 'rgba(15, 23, 42, 0.8)',
                paper_bgcolor: 'transparent',
                font: { color: '#e2e8f0', size: 12 }
              }

              window.Plotly.newPlot(elementId, plotData, layout, {
                responsive: true,
                displayModeBar: true,
                displaylogo: false
              })

              console.log(`✓ Retry successful for chart ${index}`)
            } catch (error) {
              console.error(`✗ Retry failed for chart ${index}:`, error)
            }
          }
        })
      }, 1000)
    }
  }

  const handleDatabaseConnect = async () => {
    if (!selectedSource || selectedSource === 'file') return

    setLoading(true)

    try {
      const response = await fetch('http://localhost:8001/api/dashboard/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source_type: selectedSource,
          config: dbConfig
        }),
      })

      if (!response.ok) throw new Error('Failed to connect to database')

      const data = await response.json()
      setDashboardData(data)
      setConnected(true)
    } catch (error) {
      console.error('Error:', error)
      alert('Failed to connect to database')
    } finally {
      setLoading(false)
    }
  }

  const handleExportDashboard = () => {
    alert('Export functionality - Coming soon!')
  }

  const handleRefreshData = () => {
    if (aiCharts.length > 0) {
      renderAllChartsWithRetry(aiCharts)
    }
  }

  return (
    <>
      {/* Load Plotly.js */}
      <Script
        src="https://cdn.plot.ly/plotly-2.27.0.min.js"
        onLoad={() => {
          console.log('✓ Plotly.js loaded successfully')
          setPlotlyLoaded(true)
        }}
        onError={(e) => {
          console.error('✗ Failed to load Plotly.js:', e)
        }}
      />

      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
        {/* Professional Header with Tableau-style toolbar */}
        <header className="border-b border-slate-700/50 bg-slate-900/95 backdrop-blur-md shadow-xl sticky top-0 z-50">
          <div className="container mx-auto px-6 py-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-6">
                <button
                  onClick={() => router.push('/')}
                  className="p-2 hover:bg-slate-800 rounded-lg transition-all duration-200 group"
                >
                  <ArrowLeft className="h-5 w-5 text-slate-400 group-hover:text-white" />
                </button>
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-gradient-to-br from-violet-600 to-purple-600 rounded-lg shadow-lg shadow-violet-500/30">
                    <BarChart3 className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h1 className="text-xl font-bold text-white tracking-tight">Executive Dashboard</h1>
                    <p className="text-xs text-slate-400">AI-Powered Analytics Platform</p>
                  </div>
                </div>
                {connected && (
                  <div className="flex items-center gap-2">
                    <span className="px-3 py-1.5 bg-gradient-to-r from-violet-600/20 to-purple-600/20 border border-violet-500/30 rounded-lg text-xs flex items-center gap-1.5 shadow-lg">
                      <Sparkles className="h-3.5 w-3.5 text-violet-400 animate-pulse" />
                      <span className="text-violet-300 font-medium">Llama 3.1 8B</span>
                    </span>
                  </div>
                )}
              </div>

              {connected && (
                <div className="flex items-center gap-2">
                  <button
                    onClick={handleRefreshData}
                    className="px-3 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg transition-all duration-200 text-sm flex items-center gap-2 group"
                  >
                    <RefreshCw className="h-4 w-4 text-slate-400 group-hover:text-white group-hover:rotate-180 transition-all duration-500" />
                    <span className="text-slate-300 group-hover:text-white">Refresh</span>
                  </button>
                  <button
                    onClick={handleExportDashboard}
                    className="px-3 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg transition-all duration-200 text-sm flex items-center gap-2 group"
                  >
                    <FileDown className="h-4 w-4 text-slate-400 group-hover:text-white" />
                    <span className="text-slate-300 group-hover:text-white">Export</span>
                  </button>
                  <button
                    onClick={() => {
                      setConnected(false)
                      setAiCharts([])
                      setDashboardData(null)
                    }}
                    className="px-3 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg transition-all duration-200 text-sm flex items-center gap-2 group"
                  >
                    <Settings className="h-4 w-4 text-slate-400 group-hover:text-white" />
                    <span className="text-slate-300 group-hover:text-white">Change Source</span>
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        <main className="container mx-auto px-6 py-8">
          {!connected ? (
            !selectedSource ? (
              /* Data Source Selection - Professional Cards */
              <div className="max-w-7xl mx-auto">
                <div className="mb-8">
                  <h2 className="text-3xl font-bold text-white mb-3 tracking-tight">Connect Your Data Source</h2>
                  <p className="text-slate-400 text-lg">Choose a data source to generate AI-powered insights and visualizations</p>
                </div>
                <div className="grid md:grid-cols-3 lg:grid-cols-3 gap-5">
                  {dataSources.map((source) => (
                    <button
                      key={source.id}
                      onClick={() => setSelectedSource(source.id)}
                      className="group relative p-6 bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-slate-700/50 rounded-2xl hover:border-violet-500/50 hover:shadow-2xl hover:shadow-violet-500/10 transition-all duration-300 text-left overflow-hidden"
                    >
                      <div className="absolute inset-0 bg-gradient-to-br from-violet-600/5 to-purple-600/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                      <div className="relative">
                        <div className="mb-4 inline-block p-3 bg-slate-800 rounded-xl group-hover:bg-violet-600/20 transition-colors duration-300">
                          <source.icon className="h-8 w-8 text-slate-400 group-hover:text-violet-400 transition-colors duration-300" />
                        </div>
                        <h3 className="font-semibold text-lg text-white mb-2 group-hover:text-violet-300 transition-colors">{source.name}</h3>
                        <p className="text-sm text-slate-400 group-hover:text-slate-300 transition-colors">{source.description}</p>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            ) : selectedSource === 'file' ? (
              /* File Upload - Professional */
              <div className="max-w-3xl mx-auto">
                <button
                  onClick={() => setSelectedSource(null)}
                  className="mb-6 px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg hover:bg-slate-700 transition-all duration-200 text-slate-300 hover:text-white flex items-center gap-2"
                >
                  <ArrowLeft className="h-4 w-4" />
                  Change Source
                </button>

                <div className="bg-gradient-to-br from-slate-800/40 to-slate-900/40 border-2 border-dashed border-slate-600/50 rounded-2xl p-16 text-center backdrop-blur-sm shadow-2xl">
                  <div className="flex items-center justify-center gap-3 mb-6">
                    <div className="p-4 bg-slate-800 rounded-2xl">
                      <Upload className="h-16 w-16 text-slate-400" />
                    </div>
                    <div className="p-3 bg-gradient-to-br from-violet-600/20 to-purple-600/20 rounded-2xl">
                      <Sparkles className="h-12 w-12 text-violet-400" />
                    </div>
                  </div>
                  <h3 className="text-2xl font-bold text-white mb-3 tracking-tight">Upload Your Dataset</h3>
                  <p className="text-slate-400 mb-2 text-lg">AI will analyze and create professional visualizations</p>
                  <p className="text-sm text-violet-400 mb-8 font-medium">Powered by Llama 3.1 8B • Tableau/Power BI Quality</p>
                  <input
                    type="file"
                    accept=".csv,.xlsx,.xls"
                    onChange={handleFileUpload}
                    className="hidden"
                    id="dashboard-file-upload"
                    disabled={loading}
                  />
                  <label
                    htmlFor="dashboard-file-upload"
                    className={`inline-block px-8 py-4 bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-500 hover:to-purple-500 rounded-xl cursor-pointer transition-all duration-200 shadow-lg shadow-violet-500/30 hover:shadow-xl hover:shadow-violet-500/40 font-semibold text-white ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    {loading ? (
                      <span className="flex items-center gap-2">
                        <RefreshCw className="h-5 w-5 animate-spin" />
                        Generating AI Dashboard...
                      </span>
                    ) : (
                      'Choose File'
                    )}
                  </label>
                  <p className="mt-4 text-xs text-slate-500">Supports CSV, Excel (.xlsx, .xls)</p>
                </div>
              </div>
            ) : (
              /* Database Connection Form - Professional */
              <div className="max-w-3xl mx-auto">
                <button
                  onClick={() => setSelectedSource(null)}
                  className="mb-6 px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg hover:bg-slate-700 transition-all text-slate-300 hover:text-white flex items-center gap-2"
                >
                  <ArrowLeft className="h-4 w-4" />
                  Change Source
                </button>

                <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-8 shadow-2xl backdrop-blur-sm">
                  <h3 className="text-2xl font-bold text-white mb-6 tracking-tight">
                    Connect to {dataSources.find(s => s.id === selectedSource)?.name}
                  </h3>

                  <div className="space-y-5">
                    <div>
                      <label className="block text-sm font-medium mb-2 text-slate-300">Host/Server</label>
                      <input
                        type="text"
                        value={dbConfig.host}
                        onChange={(e) => setDbConfig({ ...dbConfig, host: e.target.value })}
                        className="w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-lg focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none transition-all text-white"
                        placeholder="localhost or server address"
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-2 text-slate-300">Port</label>
                        <input
                          type="text"
                          value={dbConfig.port}
                          onChange={(e) => setDbConfig({ ...dbConfig, port: e.target.value })}
                          className="w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-lg focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none transition-all text-white"
                          placeholder="5432"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-2 text-slate-300">Database</label>
                        <input
                          type="text"
                          value={dbConfig.database}
                          onChange={(e) => setDbConfig({ ...dbConfig, database: e.target.value })}
                          className="w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-lg focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none transition-all text-white"
                          placeholder="database_name"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-2 text-slate-300">Username</label>
                        <input
                          type="text"
                          value={dbConfig.username}
                          onChange={(e) => setDbConfig({ ...dbConfig, username: e.target.value })}
                          className="w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-lg focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none transition-all text-white"
                          placeholder="username"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-2 text-slate-300">Password</label>
                        <input
                          type="password"
                          value={dbConfig.password}
                          onChange={(e) => setDbConfig({ ...dbConfig, password: e.target.value })}
                          className="w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-lg focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none transition-all text-white"
                          placeholder="••••••••"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium mb-2 text-slate-300">SQL Query (Optional)</label>
                      <textarea
                        value={dbConfig.query}
                        onChange={(e) => setDbConfig({ ...dbConfig, query: e.target.value })}
                        className="w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-lg focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 outline-none font-mono text-sm text-white"
                        rows={4}
                        placeholder="SELECT * FROM table_name"
                      />
                      <p className="mt-2 text-xs text-slate-500">Leave empty to browse all tables</p>
                    </div>

                    <button
                      onClick={handleDatabaseConnect}
                      disabled={loading}
                      className="w-full px-6 py-4 bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-500 hover:to-purple-500 rounded-lg font-semibold transition-all shadow-lg shadow-violet-500/30 hover:shadow-xl hover:shadow-violet-500/40 disabled:opacity-50 disabled:cursor-not-allowed text-white"
                    >
                      {loading ? 'Connecting...' : 'Connect & Generate Dashboard'}
                    </button>
                  </div>
                </div>
              </div>
            )
          ) : (
            /* Tableau/Power BI-Style Dashboard View */
            <div className="space-y-6">
              {/* Professional KPI Cards */}
              {dashboardData?.summary && (
                <div className="grid grid-cols-4 gap-5">
                  <div className="bg-gradient-to-br from-blue-600/10 to-blue-800/10 border border-blue-500/30 rounded-xl p-6 shadow-xl backdrop-blur-sm group hover:shadow-2xl hover:shadow-blue-500/20 transition-all duration-300">
                    <div className="flex items-center justify-between mb-3">
                      <div className="p-2.5 bg-blue-600/20 rounded-lg group-hover:bg-blue-600/30 transition-colors">
                        <Database className="h-5 w-5 text-blue-400" />
                      </div>
                      <TrendingUp className="h-4 w-4 text-blue-400 opacity-50" />
                    </div>
                    <p className="text-sm text-slate-400 mb-1 font-medium">Total Rows</p>
                    <p className="text-3xl font-bold text-white tracking-tight">{dashboardData.summary.total_rows?.toLocaleString()}</p>
                  </div>
                  <div className="bg-gradient-to-br from-green-600/10 to-green-800/10 border border-green-500/30 rounded-xl p-6 shadow-xl backdrop-blur-sm group hover:shadow-2xl hover:shadow-green-500/20 transition-all duration-300">
                    <div className="flex items-center justify-between mb-3">
                      <div className="p-2.5 bg-green-600/20 rounded-lg group-hover:bg-green-600/30 transition-colors">
                        <Grid3x3 className="h-5 w-5 text-green-400" />
                      </div>
                      <TrendingUp className="h-4 w-4 text-green-400 opacity-50" />
                    </div>
                    <p className="text-sm text-slate-400 mb-1 font-medium">Total Columns</p>
                    <p className="text-3xl font-bold text-white tracking-tight">{dashboardData.summary.total_columns}</p>
                  </div>
                  <div className="bg-gradient-to-br from-purple-600/10 to-purple-800/10 border border-purple-500/30 rounded-xl p-6 shadow-xl backdrop-blur-sm group hover:shadow-2xl hover:shadow-purple-500/20 transition-all duration-300">
                    <div className="flex items-center justify-between mb-3">
                      <div className="p-2.5 bg-purple-600/20 rounded-lg group-hover:bg-purple-600/30 transition-colors">
                        <BarChart3 className="h-5 w-5 text-purple-400" />
                      </div>
                      <TrendingUp className="h-4 w-4 text-purple-400 opacity-50" />
                    </div>
                    <p className="text-sm text-slate-400 mb-1 font-medium">Numeric Columns</p>
                    <p className="text-3xl font-bold text-white tracking-tight">{dashboardData.summary.numeric_columns}</p>
                  </div>
                  <div className="bg-gradient-to-br from-orange-600/10 to-orange-800/10 border border-orange-500/30 rounded-xl p-6 shadow-xl backdrop-blur-sm group hover:shadow-2xl hover:shadow-orange-500/20 transition-all duration-300">
                    <div className="flex items-center justify-between mb-3">
                      <div className="p-2.5 bg-orange-600/20 rounded-lg group-hover:bg-orange-600/30 transition-colors">
                        <Sparkles className="h-5 w-5 text-orange-400" />
                      </div>
                      <TrendingUp className="h-4 w-4 text-orange-400 opacity-50" />
                    </div>
                    <p className="text-sm text-slate-400 mb-1 font-medium">AI Visualizations</p>
                    <p className="text-3xl font-bold text-white tracking-tight">{dashboardData.summary.chart_count}</p>
                  </div>
                </div>
              )}

              {/* Professional Chart Grid - Tableau Style */}
              <div>
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-3">
                    <h2 className="text-2xl font-bold text-white tracking-tight">AI-Generated Insights</h2>
                    <Sparkles className="h-6 w-6 text-violet-400" />
                  </div>
                  <span className="text-sm text-slate-400">{aiCharts.length} visualizations</span>
                </div>

                {aiCharts.length === 0 ? (
                  <div className="bg-slate-800/30 border-2 border-dashed border-slate-700 rounded-2xl p-16 text-center">
                    <BarChart3 className="h-20 w-20 mx-auto mb-4 text-slate-700" />
                    <p className="text-slate-400 text-lg">No charts generated. Upload data to create AI-powered visualizations.</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {aiCharts.map((chart, index) => (
                      <div
                        key={index}
                        className="group bg-gradient-to-br from-slate-800/60 to-slate-900/60 border border-slate-700/50 rounded-2xl p-6 hover:border-violet-500/50 hover:shadow-2xl hover:shadow-violet-500/10 transition-all duration-300 backdrop-blur-sm"
                      >
                        {/* Chart Header */}
                        <div className="mb-5">
                          <div className="flex items-start justify-between mb-3">
                            <h3 className="font-bold text-lg text-white group-hover:text-violet-300 transition-colors leading-tight">
                              {chart.title}
                            </h3>
                            <span className="text-xs px-2.5 py-1 bg-gradient-to-r from-violet-600/20 to-purple-600/20 border border-violet-500/30 rounded-lg text-violet-300 font-medium uppercase tracking-wide whitespace-nowrap ml-2">
                              {chart.chart_type}
                            </span>
                          </div>

                          {/* Story & Insight - Professional Layout */}
                          <div className="space-y-2.5 mb-4">
                            <div className="flex items-start gap-2.5 p-3 bg-slate-900/40 rounded-lg border border-slate-700/30">
                              <BarChart3 className="h-4 w-4 text-blue-400 mt-0.5 flex-shrink-0" />
                              <p className="text-sm text-slate-300 leading-relaxed">{chart.story}</p>
                            </div>
                            <div className="flex items-start gap-2.5 p-3 bg-slate-900/40 rounded-lg border border-slate-700/30">
                              <Lightbulb className="h-4 w-4 text-amber-400 mt-0.5 flex-shrink-0" />
                              <p className="text-sm text-slate-400 italic leading-relaxed">{chart.insight}</p>
                            </div>
                          </div>

                          {/* Column Metadata */}
                          <div className="flex gap-3 text-xs">
                            <span className="px-2 py-1 bg-slate-800/60 border border-slate-700/40 rounded text-slate-400">
                              <span className="text-slate-500 font-medium">X:</span> {chart.x_column}
                            </span>
                            {chart.y_column && (
                              <span className="px-2 py-1 bg-slate-800/60 border border-slate-700/40 rounded text-slate-400">
                                <span className="text-slate-500 font-medium">Y:</span> {chart.y_column}
                              </span>
                            )}
                          </div>
                        </div>

                        {/* Chart Container - Professional Styling */}
                        <div className="relative">
                          <div
                            id={`chart-${index}`}
                            className="h-96 bg-gradient-to-br from-slate-900/70 to-slate-950/70 rounded-xl border border-slate-800/50 shadow-inner overflow-hidden"
                            style={{ minHeight: '384px' }}
                          ></div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {loading && (
            <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center z-50">
              <div className="bg-slate-800/90 border border-slate-700 rounded-2xl p-8 text-center max-w-md shadow-2xl">
                <div className="inline-block animate-spin rounded-full h-16 w-16 border-4 border-slate-700 border-t-violet-500 mb-4"></div>
                <p className="text-white text-lg font-semibold mb-2">AI is analyzing your data...</p>
                <p className="text-slate-400 text-sm mb-1">Generating professional visualizations</p>
                <p className="text-xs text-slate-500">This may take 5-10 seconds</p>
              </div>
            </div>
          )}
        </main>
      </div>
    </>
  )
}

// Add type declaration for Plotly
declare global {
  interface Window {
    Plotly: any
  }
}
