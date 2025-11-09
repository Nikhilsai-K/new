'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { BarChart3, ArrowLeft } from 'lucide-react'
import Plot from 'react-plotly.js'
import Button from '@/components/ui/Button'
import Card from '@/components/ui/Card'
import { useData } from '@/context/DataContext'

export default function VisualizePage() {
  const router = useRouter()
  const data = useData()
  const [columns, setColumns] = useState<any[]>([])
  const [numeric_columns, setNumericColumns] = useState<string[]>([])
  const [categorical_columns, setCategoricalColumns] = useState<string[]>([])
  const [selectedXColumn, setSelectedXColumn] = useState<string>('')
  const [selectedYColumn, setSelectedYColumn] = useState<string>('')
  const [recommendedCharts, setRecommendedCharts] = useState<any[]>([])
  const [selectedChart, setSelectedChart] = useState<string>('')
  const [chartData, setChartData] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string>('')
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

  // Initialize from context data
  useEffect(() => {
    const currentData = data.isDataCleaned ? data.cleanedData : data.originalData
    if (!currentData) return

    setColumns(
      currentData.columnNames.map(name => ({
        name,
        type: currentData.numericColumns.includes(name) ? 'numeric' : 'categorical'
      }))
    )
    setNumericColumns(currentData.numericColumns)
    setCategoricalColumns(currentData.categoricalColumns)

    // Set default selections
    if (currentData.numericColumns?.length > 0) {
      setSelectedXColumn(currentData.numericColumns[0])
    } else if (currentData.categoricalColumns?.length > 0) {
      setSelectedXColumn(currentData.categoricalColumns[0])
    }

    if (currentData.numericColumns?.length > 1) {
      setSelectedYColumn(currentData.numericColumns[1])
    } else if (currentData.categoricalColumns?.length > 0) {
      setSelectedYColumn(currentData.categoricalColumns[0])
    }
  }, [data.originalData, data.cleanedData, data.isDataCleaned])

  const handleGenerateChart = async () => {
    const currentData = data.isDataCleaned ? data.cleanedData : data.originalData
    if (!currentData || !selectedXColumn) {
      setError('Please select at least X column')
      return
    }

    setLoading(true)
    setError('')

    try {
      // Convert data to CSV format for API
      const csvContent = [
        currentData.columnNames.join(','),
        ...currentData.allData.map(row =>
          currentData.columnNames.map(col => {
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
      const file = new File([blob], currentData.filename, { type: 'text/csv' })

      const formData = new FormData()
      formData.append('file', file)

      const params = new URLSearchParams({
        x_column: selectedXColumn,
        ...(selectedYColumn && { y_column: selectedYColumn }),
        ...(selectedChart && { chart_type: selectedChart })
      })

      const response = await fetch(`${apiUrl}/api/visualize/chart?${params}`, {
        method: 'POST',
        body: formData
      })

      const responseData = await response.json()
      setChartData(responseData)
    } catch (err) {
      setError('Error generating chart. Try again.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const renderChart = () => {
    if (!chartData) return null

    if (chartData.error) {
      return (
        <div className="text-center py-12 text-red-400">
          <p>{chartData.error}</p>
        </div>
      )
    }

    const plotData = Array.isArray(chartData.data) ? chartData.data : [chartData.data]
    const layout = chartData.layout || {
      title: chartData.title,
      hovermode: 'closest',
      plot_bgcolor: '#1a1a2e',
      paper_bgcolor: '#16213e',
      font: { color: '#ffffff' }
    }

    return (
      <div className="w-full bg-slate-700/30 rounded-lg overflow-hidden">
        <Plot
          data={plotData}
          layout={{
            ...layout,
            plot_bgcolor: '#1e293b',
            paper_bgcolor: '#0f172a',
            font: { color: '#ffffff' }
          }}
          config={{
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            toImageButtonOptions: {
              format: 'png',
              filename: `${selectedXColumn}_${selectedYColumn || 'chart'}.png`,
              height: 600,
              width: 1000,
              scale: 2
            }
          }}
          style={{ width: '100%', height: '600px' }}
        />
      </div>
    )
  }

  const currentData = data.isDataCleaned ? data.cleanedData : data.originalData
  const dataType = data.isDataCleaned ? 'Cleaned' : 'Uncleaned'

  // No data - show error state
  if (!currentData) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        <header className="border-b border-slate-700 backdrop-blur-sm bg-slate-900/50">
          <div className="container mx-auto px-4 py-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
                  <BarChart3 className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-white">Data Visualizer</h1>
                  <p className="text-sm text-slate-400">Create interactive charts</p>
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
              <h2 className="text-3xl font-bold text-white mb-4">No Data Loaded</h2>
              <p className="text-slate-400 mb-6">
                Please upload a dataset from the main page first
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
                <BarChart3 className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">Data Visualizer</h1>
                <p className="text-sm text-slate-400">{dataType} Data Visualization</p>
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
          {/* Quick Quality Summary (Llama 3.1 8B Analysis) */}
          {data.originalAnalysis && !data.isDataCleaned && (
            <Card className="bg-gradient-to-r from-blue-500/10 to-cyan-500/10 backdrop-blur-sm border-blue-500/30 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-bold text-white mb-1">Data Quality Score</h3>
                  <p className="text-sm text-slate-400">
                    Analyzed by Llama 3.1 8B - {data.originalAnalysis.insights?.length || 0} issues found
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-4xl font-bold text-blue-400">{data.originalAnalysis.quality_score || 0}/100</p>
                </div>
              </div>
            </Card>
          )}

          {/* Controls */}
          <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700 p-6">
            <div className="space-y-4">
              <div>
                <p className="text-sm text-slate-300 mb-2">
                  File: <span className="text-white font-semibold">{currentData.filename}</span>
                </p>
              </div>

              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">X Column</label>
                  <select
                    value={selectedXColumn}
                    onChange={(e) => setSelectedXColumn(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600 rounded text-white placeholder-slate-400 focus:outline-none focus:border-blue-500"
                  >
                    {columns.map(col => (
                      <option key={col.name} value={col.name}>
                        {col.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Y Column (Optional)</label>
                  <select
                    value={selectedYColumn}
                    onChange={(e) => setSelectedYColumn(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600 rounded text-white placeholder-slate-400 focus:outline-none focus:border-blue-500"
                  >
                    <option value="">None</option>
                    {columns.map(col => (
                      <option key={col.name} value={col.name}>
                        {col.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Chart Type</label>
                  <select
                    value={selectedChart}
                    onChange={(e) => setSelectedChart(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600 rounded text-white placeholder-slate-400 focus:outline-none focus:border-blue-500"
                  >
                    <option value="">Auto</option>
                    {recommendedCharts.map(chart => (
                      <option key={chart.type} value={chart.type}>
                        {chart.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="flex items-end">
                  <Button
                    onClick={handleGenerateChart}
                    disabled={loading}
                    className="w-full bg-blue-600 hover:bg-blue-700"
                  >
                    {loading ? 'Generating...' : 'Generate Chart'}
                  </Button>
                </div>
              </div>

              {error && (
                <div className="p-3 bg-red-500/20 border border-red-500/50 rounded text-red-300">
                  {error}
                </div>
              )}
            </div>
          </Card>

          {/* Chart Display */}
          {chartData && (
            <div className="space-y-4">
              {chartData.stats && (
                <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700 p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">Statistics</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {Object.entries(chartData.stats).map(([key, value]: any) => (
                      <div key={key}>
                        <p className="text-xs text-slate-400 uppercase">{key}</p>
                        {typeof value === 'object' ? (
                          <div className="space-y-1 mt-1">
                            {Object.entries(value).map(([k, v]: any) => (
                              <p key={k} className="text-sm text-slate-300">
                                {k}: {typeof v === 'number' ? v.toFixed(2) : v}
                              </p>
                            ))}
                          </div>
                        ) : (
                          <p className="text-sm text-white font-semibold">
                            {typeof value === 'number' ? value.toFixed(2) : value}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </Card>
              )}

              <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700 p-6 overflow-x-auto">
                {renderChart()}
              </Card>
            </div>
          )}
        </div>
      </div>
    </main>
  )
}
