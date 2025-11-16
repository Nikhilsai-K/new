'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import {
  Database, Upload, Download, BarChart3, LineChart, PieChart,
  ArrowLeft, TrendingUp, Users, DollarSign, ShoppingCart,
  Server, Cloud, HardDrive, Plus, Settings
} from 'lucide-react'

type DataSource = 'file' | 'bigquery' | 'postgresql' | 'mysql' | 'sqlserver' | 'snowflake' | 'redshift' | 's3' | 'azure'

interface ChartConfig {
  id: string
  type: 'bar' | 'line' | 'pie' | 'area'
  title: string
  xColumn?: string
  yColumn?: string
  groupBy?: string
}

export default function BusinessDashboardPage() {
  const router = useRouter()
  const [selectedSource, setSelectedSource] = useState<DataSource | null>(null)
  const [connected, setConnected] = useState(false)
  const [loading, setLoading] = useState(false)
  const [dashboardData, setDashboardData] = useState<any>(null)
  const [charts, setCharts] = useState<ChartConfig[]>([])

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

      const response = await fetch('http://localhost:8001/api/dashboard/upload', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) throw new Error('Failed to upload file')

      const data = await response.json()
      setDashboardData(data)
      setConnected(true)
    } catch (error) {
      console.error('Error:', error)
      alert('Failed to upload file')
    } finally {
      setLoading(false)
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

  const addChart = (chartType: 'bar' | 'line' | 'pie' | 'area') => {
    const newChart: ChartConfig = {
      id: Date.now().toString(),
      type: chartType,
      title: `New ${chartType.charAt(0).toUpperCase() + chartType.slice(1)} Chart`,
    }
    setCharts([...charts, newChart])
  }

  return (
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
              <h1 className="text-xl font-bold">Business Dashboard</h1>
            </div>
            {connected && (
              <button
                onClick={() => setConnected(false)}
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
              <p className="text-gray-400 mb-6">Choose a data source to create your dashboard</p>
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
                <Upload className="h-16 w-16 mx-auto mb-4 text-gray-400" />
                <h3 className="text-xl font-semibold mb-2">Upload Your Data File</h3>
                <p className="text-gray-400 mb-6">Supports CSV, Excel (.xlsx, .xls)</p>
                <input
                  type="file"
                  accept=".csv,.xlsx,.xls"
                  onChange={handleFileUpload}
                  className="hidden"
                  id="dashboard-file-upload"
                />
                <label
                  htmlFor="dashboard-file-upload"
                  className="inline-block px-6 py-3 bg-purple-600 hover:bg-purple-700 rounded-lg cursor-pointer transition-colors"
                >
                  Choose File
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
            {/* Key Metrics */}
            <div className="grid md:grid-cols-4 gap-6 mb-8">
              <div className="bg-gradient-to-br from-blue-900/30 to-blue-800/20 border border-blue-700/30 rounded-xl p-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-400 text-sm">Total Records</span>
                  <Database className="h-5 w-5 text-blue-400" />
                </div>
                <p className="text-3xl font-bold text-blue-400">
                  {dashboardData?.total_records?.toLocaleString() || '0'}
                </p>
                <p className="text-xs text-gray-500 mt-2">↑ 12% from last month</p>
              </div>

              <div className="bg-gradient-to-br from-green-900/30 to-green-800/20 border border-green-700/30 rounded-xl p-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-400 text-sm">Revenue</span>
                  <DollarSign className="h-5 w-5 text-green-400" />
                </div>
                <p className="text-3xl font-bold text-green-400">
                  ${dashboardData?.total_revenue?.toLocaleString() || '0'}
                </p>
                <p className="text-xs text-gray-500 mt-2">↑ 8% from last month</p>
              </div>

              <div className="bg-gradient-to-br from-purple-900/30 to-purple-800/20 border border-purple-700/30 rounded-xl p-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-400 text-sm">Active Users</span>
                  <Users className="h-5 w-5 text-purple-400" />
                </div>
                <p className="text-3xl font-bold text-purple-400">
                  {dashboardData?.active_users?.toLocaleString() || '0'}
                </p>
                <p className="text-xs text-gray-500 mt-2">↑ 23% from last month</p>
              </div>

              <div className="bg-gradient-to-br from-orange-900/30 to-orange-800/20 border border-orange-700/30 rounded-xl p-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-400 text-sm">Conversion</span>
                  <TrendingUp className="h-5 w-5 text-orange-400" />
                </div>
                <p className="text-3xl font-bold text-orange-400">
                  {dashboardData?.conversion_rate || '0'}%
                </p>
                <p className="text-xs text-gray-500 mt-2">↑ 5% from last month</p>
              </div>
            </div>

            {/* Add Chart Button */}
            <div className="mb-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold">Visualizations</h2>
                <div className="flex gap-2">
                  <button
                    onClick={() => addChart('bar')}
                    className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors text-sm"
                  >
                    <Plus className="h-4 w-4 inline mr-1" />
                    Bar Chart
                  </button>
                  <button
                    onClick={() => addChart('line')}
                    className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors text-sm"
                  >
                    <Plus className="h-4 w-4 inline mr-1" />
                    Line Chart
                  </button>
                  <button
                    onClick={() => addChart('pie')}
                    className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors text-sm"
                  >
                    <Plus className="h-4 w-4 inline mr-1" />
                    Pie Chart
                  </button>
                </div>
              </div>

              {charts.length === 0 ? (
                <div className="bg-gray-800/30 border-2 border-dashed border-gray-700 rounded-xl p-12 text-center">
                  <BarChart3 className="h-16 w-16 mx-auto mb-4 text-gray-600" />
                  <p className="text-gray-400">No charts yet. Click the buttons above to add visualizations.</p>
                </div>
              ) : (
                <div className="grid md:grid-cols-2 gap-6">
                  {charts.map((chart) => (
                    <div key={chart.id} className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
                      <h3 className="font-semibold mb-4">{chart.title}</h3>
                      <div className="h-64 bg-gray-900/50 rounded-lg flex items-center justify-center">
                        <p className="text-gray-500">Chart placeholder - {chart.type}</p>
                      </div>
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
            <p className="mt-4 text-gray-400">Loading your dashboard...</p>
          </div>
        )}
      </main>
    </div>
  )
}
