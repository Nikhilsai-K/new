'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import {
  Database, Upload, Download, FileText, Code,
  ArrowLeft, Play, Table, BarChart,
  Server, Cloud, HardDrive
} from 'lucide-react'

type DataSource = 'file' | 'bigquery' | 'postgresql' | 'mysql' | 'sqlserver' | 'snowflake' | 'redshift' | 's3' | 'azure'

interface EdaResult {
  head: any[]
  tail: any[]
  info: any
  describe: any
  nullCounts: any
  shape: { rows: number, columns: number }
  dtypes: any
  correlations?: any
}

interface TableInfo {
  name: string
  schema: string
  type: string
  full_name?: string
}

interface ColumnInfo {
  name: string
  type: string
  nullable: boolean
}

export default function CleanAnalyzePage() {
  const router = useRouter()
  const [selectedSource, setSelectedSource] = useState<DataSource | null>(null)
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [edaResults, setEdaResults] = useState<EdaResult | null>(null)
  const [analysisData, setAnalysisData] = useState<any>(null)
  const [rowLimit, setRowLimit] = useState<string>('all')

  // Data quality analysis states
  const [qualityAnalysis, setQualityAnalysis] = useState<any>(null)
  const [loadingQuality, setLoadingQuality] = useState(false)
  const [cleanedData, setCleanedData] = useState<any>(null)
  const [cleaningReport, setCleaningReport] = useState<any>(null)

  // Database connection states
  const [dbConfig, setDbConfig] = useState({
    host: '',
    port: '',
    database: '',
    username: '',
    password: '',
    query: 'SELECT * FROM table_name'
  })

  // Table browser states
  const [queryMode, setQueryMode] = useState<'browse' | 'custom'>('browse')
  const [tables, setTables] = useState<TableInfo[]>([])
  const [selectedTable, setSelectedTable] = useState<string | null>(null)
  const [tableColumns, setTableColumns] = useState<ColumnInfo[]>([])
  const [selectedColumns, setSelectedColumns] = useState<string[]>([])
  const [loadingTables, setLoadingTables] = useState(false)
  const [loadingColumns, setLoadingColumns] = useState(false)

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
    const selectedFile = e.target.files?.[0]
    if (!selectedFile) return

    setFile(selectedFile)
    setLoading(true)

    try {
      // Upload file and run EDA
      const formData = new FormData()
      formData.append('file', selectedFile)

      const response = await fetch('http://localhost:8001/api/eda/analyze', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) throw new Error('Failed to analyze file')

      const data = await response.json()
      setEdaResults(data.eda)
      setAnalysisData(data)

      // Also run smart quality analysis
      analyzeDataQuality(selectedFile)
    } catch (error) {
      console.error('Error:', error)
      alert('Failed to analyze file')
    } finally {
      setLoading(false)
    }
  }

  const analyzeDataQuality = async (fileToAnalyze: File) => {
    setLoadingQuality(true)

    try {
      const formData = new FormData()
      formData.append('file', fileToAnalyze)

      const response = await fetch('http://localhost:8001/api/local-analysis/smart', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) throw new Error('Failed to analyze data quality')

      const data = await response.json()
      setQualityAnalysis(data)
    } catch (error) {
      console.error('Error:', error)
      alert('Failed to analyze data quality. Make sure Ollama with Llama 3.1 8B is running.')
    } finally {
      setLoadingQuality(false)
    }
  }

  const cleanData = async () => {
    if (!file || !qualityAnalysis) return

    setLoading(true)

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('analysis', JSON.stringify(qualityAnalysis))

      const response = await fetch('http://localhost:8001/api/clean-data-smart', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) throw new Error('Failed to clean data')

      const data = await response.json()
      setCleanedData(data.cleaned_csv)
      setCleaningReport(data.report)

      // Download cleaned file
      const blob = new Blob([data.cleaned_csv], { type: 'text/csv' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = file.name.replace(/\.(csv|xlsx)$/i, '_cleaned.csv')
      a.click()

      alert('Data cleaned successfully! File downloaded.')
    } catch (error) {
      console.error('Error:', error)
      alert('Failed to clean data')
    } finally {
      setLoading(false)
    }
  }

  const handleDatabaseConnect = async () => {
    if (!selectedSource || selectedSource === 'file') return

    setLoading(true)

    try {
      // Apply row limit to query if not already specified
      let finalQuery = dbConfig.query.trim()

      // Check if query already has a LIMIT clause
      const hasLimit = /LIMIT\s+\d+/i.test(finalQuery)

      // Add LIMIT if user selected a limit and query doesn't have one
      if (rowLimit !== 'all' && !hasLimit) {
        finalQuery = `${finalQuery} LIMIT ${rowLimit}`
      }

      const response = await fetch('http://localhost:8001/api/database/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source_type: selectedSource,
          config: {
            ...dbConfig,
            query: finalQuery
          }
        }),
      })

      if (!response.ok) throw new Error('Failed to connect to database')

      const data = await response.json()
      setEdaResults(data.eda)
      setAnalysisData(data)
    } catch (error) {
      console.error('Error:', error)
      alert('Failed to connect to database')
    } finally {
      setLoading(false)
    }
  }

  const exportToJupyter = async () => {
    if (!analysisData) return

    try {
      const response = await fetch('http://localhost:8001/api/export/jupyter', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ analysis_data: analysisData }),
      })

      if (!response.ok) throw new Error('Failed to export')

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'analysis.ipynb'
      a.click()
    } catch (error) {
      console.error('Error:', error)
      alert('Failed to export to Jupyter Notebook')
    }
  }

  const exportToColab = async () => {
    if (!analysisData) return

    try {
      const response = await fetch('http://localhost:8001/api/export/colab', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ analysis_data: analysisData }),
      })

      if (!response.ok) throw new Error('Failed to export')

      const data = await response.json()
      // Open Colab with the generated notebook
      window.open(data.colab_url, '_blank')
    } catch (error) {
      console.error('Error:', error)
      alert('Failed to export to Google Colab')
    }
  }

  // Table browser functions
  const fetchTables = async () => {
    if (!selectedSource || selectedSource === 'file' || selectedSource === 's3' || selectedSource === 'azure') return

    setLoadingTables(true)

    try {
      const response = await fetch('http://localhost:8001/api/database/list-tables', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source_type: selectedSource,
          config: dbConfig
        }),
      })

      if (!response.ok) throw new Error('Failed to fetch tables')

      const data = await response.json()
      setTables(data.tables)
    } catch (error) {
      console.error('Error:', error)
      alert('Failed to fetch tables. Make sure your connection details are correct.')
    } finally {
      setLoadingTables(false)
    }
  }

  const fetchTableSchema = async (tableName: string) => {
    if (!selectedSource || selectedSource === 'file') return

    setLoadingColumns(true)
    setSelectedTable(tableName)

    try {
      const response = await fetch('http://localhost:8001/api/database/table-schema', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source_type: selectedSource,
          config: dbConfig,
          table_name: tableName
        }),
      })

      if (!response.ok) throw new Error('Failed to fetch table schema')

      const data = await response.json()
      setTableColumns(data.schema.columns)
      setSelectedColumns([]) // Reset selected columns
    } catch (error) {
      console.error('Error:', error)
      alert('Failed to fetch table schema')
    } finally {
      setLoadingColumns(false)
    }
  }

  const toggleColumn = (columnName: string) => {
    if (selectedColumns.includes(columnName)) {
      setSelectedColumns(selectedColumns.filter(c => c !== columnName))
    } else {
      setSelectedColumns([...selectedColumns, columnName])
    }
  }

  const selectAllColumns = () => {
    setSelectedColumns(tableColumns.map(col => col.name))
  }

  const deselectAllColumns = () => {
    setSelectedColumns([])
  }

  const generateSQLFromSelection = () => {
    if (!selectedTable) return ''

    const columns = selectedColumns.length > 0
      ? selectedColumns.join(', ')
      : '*'

    const limitClause = rowLimit !== 'all' ? ` LIMIT ${rowLimit}` : ''

    if (selectedSource === 'bigquery' && selectedTable.includes('.')) {
      // BigQuery format: `project.dataset.table`
      return `SELECT ${columns} FROM \`${selectedTable}\`${limitClause}`
    } else {
      return `SELECT ${columns} FROM ${selectedTable}${limitClause}`
    }
  }

  const applyGeneratedSQL = () => {
    const sql = generateSQLFromSelection()
    setDbConfig({ ...dbConfig, query: sql })
    // Optionally switch to custom mode to show the generated SQL
    // setQueryMode('custom')
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
              <Database className="h-6 w-6 text-blue-500" />
              <h1 className="text-xl font-bold">Clean & Analyze Data</h1>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8">
        {!selectedSource ? (
          /* Data Source Selection */
          <div>
            <h2 className="text-2xl font-bold mb-6">Select Data Source</h2>
            <div className="grid md:grid-cols-3 gap-4">
              {dataSources.map((source) => (
                <button
                  key={source.id}
                  onClick={() => setSelectedSource(source.id)}
                  className="p-6 bg-gray-800/50 border border-gray-700 rounded-xl hover:border-blue-500 transition-all text-left group"
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
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className="inline-block px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg cursor-pointer transition-colors"
              >
                Choose File
              </label>
              {file && (
                <p className="mt-4 text-sm text-gray-400">
                  Selected: {file.name}
                </p>
              )}
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
                {/* BigQuery specific fields */}
                {selectedSource === 'bigquery' ? (
                  <>
                    <div>
                      <label className="block text-sm font-medium mb-2">Project ID</label>
                      <input
                        type="text"
                        value={dbConfig.database}
                        onChange={(e) => setDbConfig({ ...dbConfig, database: e.target.value })}
                        className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:border-blue-500 outline-none"
                        placeholder="your-gcp-project-id"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium mb-2">Service Account JSON (Credentials)</label>
                      <textarea
                        value={dbConfig.password}
                        onChange={(e) => setDbConfig({ ...dbConfig, password: e.target.value })}
                        className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:border-blue-500 outline-none font-mono text-xs"
                        rows={6}
                        placeholder='{"type": "service_account", "project_id": "...", "private_key": "..."}'
                      />
                      <p className="mt-2 text-xs text-gray-500">
                        Paste your service account JSON credentials here. Get it from Google Cloud Console → IAM & Admin → Service Accounts
                      </p>
                    </div>
                  </>
                ) : selectedSource === 's3' ? (
                  /* S3 specific fields */
                  <>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-2">AWS Access Key ID</label>
                        <input
                          type="text"
                          value={dbConfig.username}
                          onChange={(e) => setDbConfig({ ...dbConfig, username: e.target.value })}
                          className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:border-blue-500 outline-none"
                          placeholder="AKIA..."
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-2">AWS Secret Access Key</label>
                        <input
                          type="password"
                          value={dbConfig.password}
                          onChange={(e) => setDbConfig({ ...dbConfig, password: e.target.value })}
                          className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:border-blue-500 outline-none"
                          placeholder="••••••••"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-2">Bucket Name</label>
                        <input
                          type="text"
                          value={dbConfig.database}
                          onChange={(e) => setDbConfig({ ...dbConfig, database: e.target.value })}
                          className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:border-blue-500 outline-none"
                          placeholder="my-bucket"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-2">Region</label>
                        <input
                          type="text"
                          value={dbConfig.host}
                          onChange={(e) => setDbConfig({ ...dbConfig, host: e.target.value })}
                          className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:border-blue-500 outline-none"
                          placeholder="us-east-1"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium mb-2">File Path in S3</label>
                      <input
                        type="text"
                        value={dbConfig.query}
                        onChange={(e) => setDbConfig({ ...dbConfig, query: e.target.value })}
                        className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:border-blue-500 outline-none"
                        placeholder="path/to/file.csv"
                      />
                    </div>
                  </>
                ) : selectedSource === 'snowflake' ? (
                  /* Snowflake specific fields */
                  <>
                    <div>
                      <label className="block text-sm font-medium mb-2">Account</label>
                      <input
                        type="text"
                        value={dbConfig.host}
                        onChange={(e) => setDbConfig({ ...dbConfig, host: e.target.value })}
                        className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:border-blue-500 outline-none"
                        placeholder="xy12345.us-east-1"
                      />
                      <p className="mt-1 text-xs text-gray-500">Format: account_name.region</p>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-2">Username</label>
                        <input
                          type="text"
                          value={dbConfig.username}
                          onChange={(e) => setDbConfig({ ...dbConfig, username: e.target.value })}
                          className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:border-blue-500 outline-none"
                          placeholder="username"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-2">Password</label>
                        <input
                          type="password"
                          value={dbConfig.password}
                          onChange={(e) => setDbConfig({ ...dbConfig, password: e.target.value })}
                          className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:border-blue-500 outline-none"
                          placeholder="••••••••"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-2">Warehouse</label>
                        <input
                          type="text"
                          value={dbConfig.port}
                          onChange={(e) => setDbConfig({ ...dbConfig, port: e.target.value })}
                          className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:border-blue-500 outline-none"
                          placeholder="COMPUTE_WH"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-2">Database</label>
                        <input
                          type="text"
                          value={dbConfig.database}
                          onChange={(e) => setDbConfig({ ...dbConfig, database: e.target.value })}
                          className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:border-blue-500 outline-none"
                          placeholder="database_name"
                        />
                      </div>
                    </div>
                  </>
                ) : (
                  /* Standard SQL database fields (PostgreSQL, MySQL, SQL Server, Redshift) */
                  <>
                    <div>
                      <label className="block text-sm font-medium mb-2">Host/Server</label>
                      <input
                        type="text"
                        value={dbConfig.host}
                        onChange={(e) => setDbConfig({ ...dbConfig, host: e.target.value })}
                        className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:border-blue-500 outline-none"
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
                          className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:border-blue-500 outline-none"
                          placeholder={
                            selectedSource === 'postgresql' ? '5432' :
                            selectedSource === 'mysql' ? '3306' :
                            selectedSource === 'sqlserver' ? '1433' :
                            selectedSource === 'redshift' ? '5439' : '5432'
                          }
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-2">Database</label>
                        <input
                          type="text"
                          value={dbConfig.database}
                          onChange={(e) => setDbConfig({ ...dbConfig, database: e.target.value })}
                          className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:border-blue-500 outline-none"
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
                          className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:border-blue-500 outline-none"
                          placeholder="username"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-2">Password</label>
                        <input
                          type="password"
                          value={dbConfig.password}
                          onChange={(e) => setDbConfig({ ...dbConfig, password: e.target.value })}
                          className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:border-blue-500 outline-none"
                          placeholder="••••••••"
                        />
                      </div>
                    </div>
                  </>
                )}

                {/* Row Limit Selector (for all databases) */}
                {selectedSource !== 's3' && selectedSource !== 'azure' && (
                  <div>
                    <label className="block text-sm font-medium mb-2">Row Limit</label>
                    <select
                      value={rowLimit}
                      onChange={(e) => setRowLimit(e.target.value)}
                      className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:border-blue-500 outline-none"
                    >
                      <option value="1000">1,000 rows (Quick test)</option>
                      <option value="10000">10,000 rows (Small dataset)</option>
                      <option value="100000">100,000 rows (Medium dataset)</option>
                      <option value="500000">500,000 rows (Large dataset)</option>
                      <option value="1000000">1,000,000 rows (Very large)</option>
                      <option value="all">All rows (No limit - Full dataset)</option>
                    </select>
                    <p className="mt-2 text-xs text-gray-500">
                      {rowLimit === 'all'
                        ? '⚠️ Loading entire dataset. This may take time and cost money (BigQuery).'
                        : `Will fetch ${parseInt(rowLimit).toLocaleString()} rows for analysis.`
                      }
                    </p>
                  </div>
                )}

                {/* Query Mode Toggle */}
                {selectedSource !== 's3' && selectedSource !== 'azure' && (
                  <div>
                    <label className="block text-sm font-medium mb-3">Query Mode</label>
                    <div className="flex gap-2 mb-4">
                      <button
                        onClick={() => setQueryMode('browse')}
                        className={`flex-1 px-4 py-2 rounded-lg font-medium transition-colors ${
                          queryMode === 'browse'
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                        }`}
                      >
                        Browse Tables (Visual)
                      </button>
                      <button
                        onClick={() => setQueryMode('custom')}
                        className={`flex-1 px-4 py-2 rounded-lg font-medium transition-colors ${
                          queryMode === 'custom'
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                        }`}
                      >
                        Custom SQL
                      </button>
                    </div>
                  </div>
                )}

                {/* Browse Tables Mode */}
                {queryMode === 'browse' && selectedSource !== 's3' && selectedSource !== 'azure' && (
                  <div className="space-y-4">
                    {/* Fetch Tables Button */}
                    {tables.length === 0 && (
                      <button
                        onClick={fetchTables}
                        disabled={loadingTables}
                        className="w-full px-4 py-3 bg-purple-600 hover:bg-purple-700 rounded-lg font-medium transition-colors disabled:opacity-50"
                      >
                        {loadingTables ? 'Loading Tables...' : 'Browse Available Tables'}
                      </button>
                    )}

                    {/* Tables List */}
                    {tables.length > 0 && !selectedTable && (
                      <div>
                        <div className="flex items-center justify-between mb-3">
                          <label className="block text-sm font-medium">Select a Table</label>
                          <button
                            onClick={() => {
                              setTables([])
                              setSelectedTable(null)
                              setTableColumns([])
                              setSelectedColumns([])
                            }}
                            className="text-xs text-gray-400 hover:text-white"
                          >
                            Refresh Tables
                          </button>
                        </div>
                        <div className="max-h-64 overflow-y-auto bg-gray-900 border border-gray-700 rounded-lg">
                          {tables.map((table) => (
                            <button
                              key={table.name}
                              onClick={() => fetchTableSchema(table.name)}
                              className="w-full text-left px-4 py-3 hover:bg-gray-800 border-b border-gray-800 last:border-b-0 transition-colors"
                            >
                              <div className="flex items-center justify-between">
                                <div>
                                  <p className="font-medium text-blue-400">{table.name}</p>
                                  <p className="text-xs text-gray-500">Schema: {table.schema}</p>
                                </div>
                                <span className="text-xs bg-gray-800 px-2 py-1 rounded">{table.type}</span>
                              </div>
                            </button>
                          ))}
                        </div>
                        <p className="mt-2 text-xs text-gray-500">
                          Found {tables.length} table{tables.length !== 1 ? 's' : ''}. Click on a table to select columns.
                        </p>
                      </div>
                    )}

                    {/* Column Selector */}
                    {selectedTable && tableColumns.length > 0 && (
                      <div>
                        <div className="flex items-center justify-between mb-3">
                          <label className="block text-sm font-medium">
                            Select Columns from <span className="text-blue-400">{selectedTable}</span>
                          </label>
                          <button
                            onClick={() => {
                              setSelectedTable(null)
                              setTableColumns([])
                              setSelectedColumns([])
                            }}
                            className="text-xs text-gray-400 hover:text-white"
                          >
                            ← Back to Tables
                          </button>
                        </div>

                        {/* Select All / Deselect All */}
                        <div className="flex gap-2 mb-3">
                          <button
                            onClick={selectAllColumns}
                            className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-xs"
                          >
                            Select All
                          </button>
                          <button
                            onClick={deselectAllColumns}
                            className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-xs"
                          >
                            Deselect All
                          </button>
                        </div>

                        {/* Columns with Checkboxes */}
                        <div className="max-h-64 overflow-y-auto bg-gray-900 border border-gray-700 rounded-lg p-3">
                          {tableColumns.map((column) => (
                            <label
                              key={column.name}
                              className="flex items-center gap-3 px-3 py-2 hover:bg-gray-800 rounded cursor-pointer"
                            >
                              <input
                                type="checkbox"
                                checked={selectedColumns.includes(column.name)}
                                onChange={() => toggleColumn(column.name)}
                                className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500"
                              />
                              <div className="flex-1">
                                <span className="font-medium text-white">{column.name}</span>
                                <span className="ml-2 text-xs text-gray-400">{column.type}</span>
                                {column.nullable && <span className="ml-2 text-xs text-yellow-400">nullable</span>}
                              </div>
                            </label>
                          ))}
                        </div>

                        <p className="mt-2 text-xs text-gray-500">
                          {selectedColumns.length} column{selectedColumns.length !== 1 ? 's' : ''} selected
                          {selectedColumns.length === 0 && ' (all columns will be selected with *)'}
                        </p>

                        {/* Generated SQL Preview */}
                        <div className="mt-4">
                          <label className="block text-sm font-medium mb-2">Generated SQL Query</label>
                          <div className="bg-gray-900 border border-gray-700 rounded-lg p-4 font-mono text-sm text-green-400">
                            {generateSQLFromSelection()}
                          </div>
                        </div>

                        {/* Apply and Run Button */}
                        <button
                          onClick={() => {
                            applyGeneratedSQL()
                            handleDatabaseConnect()
                          }}
                          className="w-full mt-3 px-4 py-3 bg-green-600 hover:bg-green-700 rounded-lg font-medium transition-colors"
                        >
                          Run Query & Analyze
                        </button>
                      </div>
                    )}

                    {loadingColumns && (
                      <div className="text-center py-4">
                        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                        <p className="mt-2 text-sm text-gray-400">Loading columns...</p>
                      </div>
                    )}
                  </div>
                )}

                {/* Custom SQL Mode */}
                {queryMode === 'custom' && selectedSource !== 's3' && selectedSource !== 'azure' && (
                  <div>
                    <label className="block text-sm font-medium mb-2">SQL Query</label>
                    <textarea
                      value={dbConfig.query}
                      onChange={(e) => setDbConfig({ ...dbConfig, query: e.target.value })}
                      className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:border-blue-500 outline-none font-mono text-sm"
                      rows={4}
                      placeholder={
                        selectedSource === 'bigquery'
                          ? `SELECT * FROM \`project.dataset.table\`${rowLimit !== 'all' ? ` LIMIT ${rowLimit}` : ''}`
                          : `SELECT * FROM table_name${rowLimit !== 'all' ? ` LIMIT ${rowLimit}` : ''}`
                      }
                    />
                    <p className="mt-2 text-xs text-gray-500">
                      💡 Tip: Your query will automatically use the row limit selected above unless you specify a different LIMIT in the query.
                    </p>
                  </div>
                )}

                {/* Connect & Analyze button (only show in custom SQL mode) */}
                {queryMode === 'custom' && (
                  <button
                    onClick={handleDatabaseConnect}
                    disabled={loading}
                    className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? 'Connecting...' : 'Connect & Analyze'}
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* EDA Results */}
        {loading && (
          <div className="mt-8 text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            <p className="mt-4 text-gray-400">Analyzing your data...</p>
          </div>
        )}

        {edaResults && !loading && (
          <div className="mt-8 space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">Exploratory Data Analysis</h2>
              <div className="flex gap-3">
                <button
                  onClick={exportToJupyter}
                  className="flex items-center gap-2 px-4 py-2 bg-orange-600 hover:bg-orange-700 rounded-lg transition-colors"
                >
                  <FileText className="h-4 w-4" />
                  Export to Jupyter
                </button>
                <button
                  onClick={exportToColab}
                  className="flex items-center gap-2 px-4 py-2 bg-yellow-600 hover:bg-yellow-700 rounded-lg transition-colors"
                >
                  <Code className="h-4 w-4" />
                  Open in Colab
                </button>
              </div>
            </div>

            {/* Dataset Shape */}
            <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Table className="h-5 w-5 text-blue-400" />
                Dataset Shape
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-900/50 p-4 rounded-lg">
                  <p className="text-gray-400 text-sm">Rows</p>
                  <p className="text-2xl font-bold text-blue-400">{edaResults.shape.rows.toLocaleString()}</p>
                </div>
                <div className="bg-gray-900/50 p-4 rounded-lg">
                  <p className="text-gray-400 text-sm">Columns</p>
                  <p className="text-2xl font-bold text-purple-400">{edaResults.shape.columns}</p>
                </div>
              </div>
            </div>

            {/* Data Quality Analysis (LLM-Powered) */}
            {loadingQuality && (
              <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-8 text-center">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mb-4"></div>
                <p className="text-gray-400">Analyzing data quality with Llama 3.1 8B...</p>
                <p className="text-sm text-gray-500 mt-2">This usually takes 2-5 seconds</p>
              </div>
            )}

            {qualityAnalysis && !loadingQuality && (
              <div className="bg-gradient-to-br from-blue-900/20 to-purple-900/20 border border-blue-700/50 rounded-xl p-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <BarChart className="h-5 w-5 text-blue-400" />
                  AI Data Quality Analysis (Llama 3.1 8B)
                </h3>

                {/* Quality Score */}
                <div className="bg-gray-900/50 p-6 rounded-lg mb-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-400">Overall Quality Score</span>
                    <span className={`text-3xl font-bold ${
                      qualityAnalysis.overall_quality_score >= 80 ? 'text-green-400' :
                      qualityAnalysis.overall_quality_score >= 60 ? 'text-yellow-400' :
                      'text-red-400'
                    }`}>
                      {qualityAnalysis.overall_quality_score?.toFixed(1) || 'N/A'}/100
                    </span>
                  </div>
                  <div className="w-full bg-gray-800 rounded-full h-3">
                    <div
                      className={`h-3 rounded-full ${
                        qualityAnalysis.overall_quality_score >= 80 ? 'bg-green-500' :
                        qualityAnalysis.overall_quality_score >= 60 ? 'bg-yellow-500' :
                        'bg-red-500'
                      }`}
                      style={{ width: `${qualityAnalysis.overall_quality_score || 0}%` }}
                    ></div>
                  </div>
                </div>

                {/* Issues Found */}
                {qualityAnalysis.issues && qualityAnalysis.issues.length > 0 && (
                  <div className="bg-gray-900/50 p-6 rounded-lg mb-4">
                    <h4 className="font-semibold mb-3 text-red-400">Issues Found ({qualityAnalysis.issues.length})</h4>
                    <div className="space-y-3">
                      {qualityAnalysis.issues.map((issue: any, idx: number) => (
                        <div key={idx} className="flex gap-3 items-start">
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            issue.severity === 'high' ? 'bg-red-500/20 text-red-400' :
                            issue.severity === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                            'bg-blue-500/20 text-blue-400'
                          }`}>
                            {issue.severity}
                          </span>
                          <div className="flex-1">
                            <p className="text-white">{issue.type}: {issue.message}</p>
                            {issue.affected_columns && (
                              <p className="text-xs text-gray-500 mt-1">
                                Columns: {issue.affected_columns.join(', ')}
                              </p>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Cleaning Strategies */}
                {qualityAnalysis.cleaning_strategies && qualityAnalysis.cleaning_strategies.length > 0 && (
                  <div className="bg-gray-900/50 p-6 rounded-lg mb-4">
                    <h4 className="font-semibold mb-3 text-green-400">Recommended Cleaning Strategies</h4>
                    <div className="space-y-3">
                      {qualityAnalysis.cleaning_strategies.map((strategy: any, idx: number) => (
                        <div key={idx} className="bg-gray-800/50 p-4 rounded">
                          <div className="flex items-start gap-3">
                            <span className="text-green-400 text-lg">✓</span>
                            <div className="flex-1">
                              <p className="font-medium text-white">{strategy.column}</p>
                              <p className="text-sm text-gray-400 mt-1">{strategy.strategy}</p>
                              {strategy.reason && (
                                <p className="text-xs text-gray-500 mt-2">Reason: {strategy.reason}</p>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Recommendations */}
                {qualityAnalysis.recommendations && qualityAnalysis.recommendations.length > 0 && (
                  <div className="bg-gray-900/50 p-6 rounded-lg mb-4">
                    <h4 className="font-semibold mb-3 text-purple-400">AI Recommendations</h4>
                    <ul className="space-y-2">
                      {qualityAnalysis.recommendations.map((rec: any, idx: number) => (
                        <li key={idx} className="flex gap-2 text-gray-300">
                          <span className="text-purple-400">•</span>
                          <span>{typeof rec === 'string' ? rec : rec.action || JSON.stringify(rec)}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Clean Data Button */}
                <button
                  onClick={cleanData}
                  disabled={loading}
                  className="w-full px-6 py-4 bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 rounded-lg font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {loading ? 'Cleaning...' : 'Clean Data Now with AI Recommendations'}
                </button>

                {cleaningReport && (
                  <div className="mt-4 bg-green-900/30 border border-green-700 rounded-lg p-4">
                    <h4 className="font-semibold text-green-400 mb-2">Cleaning Complete!</h4>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-gray-400">Rows Before:</p>
                        <p className="text-white font-semibold">{cleaningReport.original_rows?.toLocaleString()}</p>
                      </div>
                      <div>
                        <p className="text-gray-400">Rows After:</p>
                        <p className="text-white font-semibold">{cleaningReport.cleaned_rows?.toLocaleString()}</p>
                      </div>
                      <div>
                        <p className="text-gray-400">Rows Removed:</p>
                        <p className="text-red-400 font-semibold">{cleaningReport.rows_removed?.toLocaleString()}</p>
                      </div>
                      <div>
                        <p className="text-gray-400">Missing Values Remaining:</p>
                        <p className="text-yellow-400 font-semibold">{cleaningReport.missing_values_remaining?.toLocaleString()}</p>
                      </div>
                    </div>
                    <p className="text-xs text-gray-500 mt-3">File downloaded automatically</p>
                  </div>
                )}
              </div>
            )}

            {/* Head - First Rows */}
            <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
              <h3 className="text-lg font-semibold mb-4">df.head() - First 10 Rows</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm border-collapse">
                  <thead>
                    <tr className="border-b border-gray-700">
                      <th className="px-4 py-2 text-left bg-gray-900 font-semibold text-gray-400"></th>
                      {edaResults.head.length > 0 && Object.keys(edaResults.head[0]).map((col) => (
                        <th key={col} className="px-4 py-2 text-left bg-gray-900 font-semibold text-blue-400">{col}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {edaResults.head.map((row: any, idx: number) => (
                      <tr key={idx} className="border-b border-gray-800 hover:bg-gray-900/30">
                        <td className="px-4 py-2 font-mono text-gray-500">{idx}</td>
                        {Object.values(row).map((val: any, colIdx: number) => (
                          <td key={colIdx} className="px-4 py-2 text-gray-300">
                            {val === null || val === undefined ? <span className="text-gray-600 italic">NaN</span> : String(val)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Describe - Statistical Summary */}
            <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
              <h3 className="text-lg font-semibold mb-4">df.describe() - Statistical Summary</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm border-collapse">
                  <thead>
                    <tr className="border-b border-gray-700">
                      <th className="px-4 py-2 text-left bg-gray-900 font-semibold text-gray-400"></th>
                      {Object.keys(edaResults.describe).map((col) => (
                        <th key={col} className="px-4 py-2 text-left bg-gray-900 font-semibold text-blue-400">{col}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max', 'unique', 'top', 'freq'].map((stat) => {
                      const hasData = Object.values(edaResults.describe).some((col: any) => col[stat] !== null && col[stat] !== undefined);
                      if (!hasData) return null;
                      return (
                        <tr key={stat} className="border-b border-gray-800 hover:bg-gray-900/30">
                          <td className="px-4 py-2 font-mono text-gray-400 font-semibold">{stat}</td>
                          {Object.values(edaResults.describe).map((col: any, idx: number) => (
                            <td key={idx} className="px-4 py-2 text-gray-300">
                              {col[stat] !== null && col[stat] !== undefined
                                ? (typeof col[stat] === 'number' ? col[stat].toFixed(2) : String(col[stat]))
                                : <span className="text-gray-600 italic">NaN</span>
                              }
                            </td>
                          ))}
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Null Counts */}
            <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
              <h3 className="text-lg font-semibold mb-4">df.isnull().sum() - Missing Values</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm border-collapse">
                  <thead>
                    <tr className="border-b border-gray-700">
                      <th className="px-4 py-2 text-left bg-gray-900 font-semibold text-blue-400">Column</th>
                      <th className="px-4 py-2 text-right bg-gray-900 font-semibold text-blue-400">Missing Count</th>
                      <th className="px-4 py-2 text-right bg-gray-900 font-semibold text-blue-400">Percentage</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(edaResults.nullCounts).map(([col, data]: [string, any]) => (
                      <tr key={col} className="border-b border-gray-800 hover:bg-gray-900/30">
                        <td className="px-4 py-2 text-gray-300">{col}</td>
                        <td className="px-4 py-2 text-right font-mono text-gray-300">{data.count}</td>
                        <td className="px-4 py-2 text-right font-mono">
                          <span className={data.percentage > 0 ? 'text-red-400' : 'text-green-400'}>
                            {data.percentage.toFixed(2)}%
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Data Types */}
            <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
              <h3 className="text-lg font-semibold mb-4">df.dtypes - Column Data Types</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm border-collapse">
                  <thead>
                    <tr className="border-b border-gray-700">
                      <th className="px-4 py-2 text-left bg-gray-900 font-semibold text-blue-400">Column</th>
                      <th className="px-4 py-2 text-left bg-gray-900 font-semibold text-blue-400">Dtype</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(edaResults.dtypes).map(([col, dtype]: [string, any]) => (
                      <tr key={col} className="border-b border-gray-800 hover:bg-gray-900/30">
                        <td className="px-4 py-2 text-gray-300">{col}</td>
                        <td className="px-4 py-2 font-mono text-purple-400">{dtype}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Info */}
            <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
              <h3 className="text-lg font-semibold mb-4">df.info() - Dataset Information</h3>
              <div className="bg-gray-900 p-4 rounded-lg">
                <pre className="text-sm text-gray-300 font-mono whitespace-pre-wrap">
                  {edaResults.info.summary}
                </pre>
              </div>
              <div className="mt-4">
                <p className="text-sm text-gray-400 mb-2">
                  <span className="font-semibold">Memory Usage:</span> {(edaResults.info.memory_usage / 1024).toFixed(2)} KB
                </p>
                <p className="text-sm text-gray-400">
                  <span className="font-semibold">Total Rows:</span> {edaResults.info.total_rows.toLocaleString()} |
                  <span className="font-semibold ml-4">Total Columns:</span> {edaResults.info.total_columns}
                </p>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
