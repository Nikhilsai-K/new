'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import {
  Database, Upload, Download, BarChart3, LineChart, PieChart,
  ArrowLeft, TrendingUp, Users, DollarSign, ShoppingCart,
  Server, Cloud, HardDrive, Plus, Settings, Sparkles, Lightbulb
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

      setDashboardData(data)
      setAiCharts(data.charts || [])
      setConnected(true)

      // Render charts after a short delay to ensure Plotly is loaded
      setTimeout(() => {
        renderAllCharts(data.charts || [])
      }, 500)

    } catch (error: any) {
      console.error('Error:', error)
      alert(error.message || 'Failed to generate AI dashboard')
    } finally {
      setLoading(false)
    }
  }

  const renderAllCharts = (charts: AIChart[]) => {
    if (!plotlyLoaded || !window.Plotly) {
      console.log('Plotly not loaded yet, retrying...')
      setTimeout(() => renderAllCharts(charts), 500)
      return
    }

    charts.forEach((chart, index) => {
      try {
        const elementId = `chart-${index}`
        const element = document.getElementById(elementId)

        if (!element) {
          console.error(`Chart element ${elementId} not found`)
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

        const layout = {
          ...config.layout,
          autosize: true,
          margin: { l: 60, r: 40, t: 40, b: 60 },
          plot_bgcolor: '#1a1a2e',
          paper_bgcolor: '#16213e',
          font: { color: '#ffffff', size: 11 },
          hovermode: 'closest'
        }

        window.Plotly.newPlot(elementId, plotData, layout, {
          responsive: true,
          displayModeBar: false
        })
      } catch (error) {
        console.error(`Error rendering chart ${index}:`, error)
      }
    })
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

  return (
    <>
      {/* Load Plotly.js */}
      <Script
        src="https://cdn.plot.ly/plotly-2.27.0.min.js"
        onLoad={() => {
          console.log('Plotly loaded successfully')
          setPlotlyLoaded(true)
        }}
        onError={(e) => {
          console.error('Failed to load Plotly:', e)
        }}
      />

      <div className="min-h-screen bg-gradient-to-br from-[#1a1a1d] via-[#1f1f23] to-[#25252a] text-white">
        {/* Header */}
        <header className="border-b border-gray-800 bg-[#1f1f23]/80 backdrop-blur-sm">
          <div className="container mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <button
                  onClick={() => router.push('/')}
                  className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
                >
                  <ArrowLeft className="h-5 w-5" />
                </button>
                <BarChart3 className="h-6 w-6 text-purple-500" />
                <h1 className="text-xl font-bold">AI-Powered Business Dashboard</h1>
                {connected && (
                  <span className="px-3 py-1 bg-purple-900/30 border border-purple-700/30 rounded-full text-xs flex items-center gap-1">
                    <Sparkles className="h-3 w-3 text-purple-400" />
                    Llama 3.1 8B
                  </span>
                )}
              </div>
              {connected && (
                <button
                  onClick={() => {
                    setConnected(false)
                    setAiCharts([])
                    setDashboardData(null)
                  }}
                  className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors text-sm"
                >
                  <Settings className="h-4 w-4 inline mr-2" />
                  Change Data Source
                </button>
              )}
            </div>
          </div>
        </header>

        <main className="container mx-auto px-6 py-8">
          {!connected ? (
            !selectedSource ? (
              /* Data Source Selection */
              <div>
                <h2 className="text-2xl font-bold mb-2">Connect Your Data</h2>
                <p className="text-gray-400 mb-6">Choose a data source to create your AI-powered dashboard</p>
                <div className="grid md:grid-cols-3 gap-4">
                  {dataSources.map((source) => (
                    <button
                      key={source.id}
                      onClick={() => setSelectedSource(source.id)}
                      className="p-6 bg-gray-800/50 border border-gray-700 rounded-xl hover:border-purple-500 transition-all text-left group"
                    >
                      <source.icon className={`h-8 w-8 text-${source.color}-400 mb-3`} />
                      <h3 className="font-semibold mb-1">{source.name}</h3>
                      <p className="text-sm text-gray-400">{source.description}</p>
                    </button>
                  ))}
                </div>
              </div>
            ) : selectedSource === 'file' ? (
              /* File Upload */
              <div>
                <button
                  onClick={() => setSelectedSource(null)}
                  className="mb-6 px-4 py-2 bg-gray-800 rounded-lg hover:bg-gray-700 transition-colors"
                >
                  ← Change Source
                </button>

                <div className="bg-gray-800/50 border-2 border-dashed border-gray-700 rounded-xl p-12 text-center">
                  <div className="flex items-center justify-center gap-2 mb-4">
                    <Upload className="h-16 w-16 text-gray-400" />
                    <Sparkles className="h-8 w-8 text-purple-400" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">Upload Your Data File</h3>
                  <p className="text-gray-400 mb-2">AI will analyze your data and create professional visualizations</p>
                  <p className="text-sm text-purple-400 mb-6">Powered by Llama 3.1 8B - Tableau/Power BI-level quality</p>
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
                    className={`inline-block px-6 py-3 bg-purple-600 hover:bg-purple-700 rounded-lg cursor-pointer transition-colors ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    {loading ? 'Generating AI Dashboard...' : 'Choose File'}
                  </label>
                </div>
              </div>
            ) : (
              /* Database Connection Form */
              <div>
                <button
                  onClick={() => setSelectedSource(null)}
                  className="mb-6 px-4 py-2 bg-gray-800 rounded-lg hover:bg-gray-700 transition-colors"
                >
                  ← Change Source
                </button>

                <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-8">
                  <h3 className="text-xl font-semibold mb-6">
                    Connect to {dataSources.find(s => s.id === selectedSource)?.name}
                  </h3>

                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">Host/Server</label>
                      <input
                        type="text"
                        value={dbConfig.host}
                        onChange={(e) => setDbConfig({ ...dbConfig, host: e.target.value })}
                        className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:border-purple-500 outline-none"
                        placeholder="localhost or server address"
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-2">Port</label>
                        <input
                          type="text"
                          value={dbConfig.port}
                          onChange={(e) => setDbConfig({ ...dbConfig, port: e.target.value })}
                          className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:border-purple-500 outline-none"
                          placeholder="5432"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-2">Database</label>
                        <input
                          type="text"
                          value={dbConfig.database}
                          onChange={(e) => setDbConfig({ ...dbConfig, database: e.target.value })}
                          className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:border-purple-500 outline-none"
                          placeholder="database_name"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-2">Username</label>
                        <input
                          type="text"
                          value={dbConfig.username}
                          onChange={(e) => setDbConfig({ ...dbConfig, username: e.target.value })}
                          className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:border-purple-500 outline-none"
                          placeholder="username"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-2">Password</label>
                        <input
                          type="password"
                          value={dbConfig.password}
                          onChange={(e) => setDbConfig({ ...dbConfig, password: e.target.value })}
                          className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:border-purple-500 outline-none"
                          placeholder="••••••••"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium mb-2">SQL Query (Optional)</label>
                      <textarea
                        value={dbConfig.query}
                        onChange={(e) => setDbConfig({ ...dbConfig, query: e.target.value })}
                        className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:border-purple-500 outline-none font-mono text-sm"
                        rows={4}
                        placeholder="SELECT * FROM table_name"
                      />
                      <p className="mt-2 text-xs text-gray-500">Leave empty to browse all tables</p>
                    </div>

                    <button
                      onClick={handleDatabaseConnect}
                      disabled={loading}
                      className="w-full px-6 py-3 bg-purple-600 hover:bg-purple-700 rounded-lg font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {loading ? 'Connecting...' : 'Connect & Create Dashboard'}
                    </button>
                  </div>
                </div>
              </div>
            )
          ) : (
            /* Dashboard View */
            <div>
              {/* Summary Stats */}
              {dashboardData?.summary && (
                <div className="bg-gray-800/30 border border-gray-700 rounded-xl p-6 mb-8">
                  <div className="flex items-center gap-2 mb-4">
                    <Database className="h-5 w-5 text-purple-400" />
                    <h3 className="font-semibold">Dataset Overview</h3>
                  </div>
                  <div className="grid grid-cols-4 gap-6">
                    <div>
                      <p className="text-sm text-gray-400">Total Rows</p>
                      <p className="text-2xl font-bold text-blue-400">{dashboardData.summary.total_rows?.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Total Columns</p>
                      <p className="text-2xl font-bold text-green-400">{dashboardData.summary.total_columns}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Numeric Columns</p>
                      <p className="text-2xl font-bold text-purple-400">{dashboardData.summary.numeric_columns}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">AI Charts Generated</p>
                      <p className="text-2xl font-bold text-orange-400">{dashboardData.summary.chart_count}</p>
                    </div>
                  </div>
                </div>
              )}

              {/* AI-Generated Charts */}
              <div className="mb-6">
                <div className="flex items-center gap-2 mb-4">
                  <h2 className="text-2xl font-bold">AI-Generated Visualizations</h2>
                  <Sparkles className="h-5 w-5 text-purple-400" />
                </div>

                {aiCharts.length === 0 ? (
                  <div className="bg-gray-800/30 border-2 border-dashed border-gray-700 rounded-xl p-12 text-center">
                    <BarChart3 className="h-16 w-16 mx-auto mb-4 text-gray-600" />
                    <p className="text-gray-400">No charts generated. Upload a file to create AI-powered visualizations.</p>
                  </div>
                ) : (
                  <div className="grid md:grid-cols-2 gap-6">
                    {aiCharts.map((chart, index) => (
                      <div key={index} className="bg-gray-800/50 border border-gray-700 rounded-xl p-6 hover:border-purple-500/30 transition-all">
                        <div className="mb-4">
                          <h3 className="font-semibold text-lg mb-2 flex items-center gap-2">
                            {chart.title}
                            <span className="text-xs px-2 py-1 bg-purple-900/30 border border-purple-700/30 rounded text-purple-300">
                              {chart.chart_type}
                            </span>
                          </h3>

                          {/* Story & Insight */}
                          <div className="space-y-2 mb-4">
                            <div className="flex items-start gap-2 text-sm">
                              <BarChart3 className="h-4 w-4 text-blue-400 mt-0.5 flex-shrink-0" />
                              <p className="text-gray-300">{chart.story}</p>
                            </div>
                            <div className="flex items-start gap-2 text-sm">
                              <Lightbulb className="h-4 w-4 text-yellow-400 mt-0.5 flex-shrink-0" />
                              <p className="text-gray-400 italic">{chart.insight}</p>
                            </div>
                          </div>

                          {/* Column Info */}
                          <div className="flex gap-4 text-xs text-gray-500 mb-3">
                            <span>X: {chart.x_column}</span>
                            {chart.y_column && <span>Y: {chart.y_column}</span>}
                          </div>
                        </div>

                        {/* Chart Container */}
                        <div
                          id={`chart-${index}`}
                          className="h-80 bg-gray-900/50 rounded-lg"
                        ></div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {loading && (
            <div className="mt-8 text-center">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
              <p className="mt-4 text-gray-400">AI is analyzing your data and creating visualizations...</p>
              <p className="mt-2 text-sm text-gray-500">This may take 5-10 seconds</p>
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
