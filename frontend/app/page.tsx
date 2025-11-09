'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Download, Trash2, CheckCircle, BarChart3, Eye } from 'lucide-react'
import FileUploader from '@/components/FileUploader'
import BasicAnalysis from '@/components/BasicAnalysis'
import Button from '@/components/ui/Button'
import Card from '@/components/ui/Card'
import { useData } from '@/context/DataContext'

export default function Home() {
  const router = useRouter()
  const data = useData()
  const [loading, setLoading] = useState(false)
  const [cleaningStatus, setCleaningStatus] = useState<'idle' | 'cleaning' | 'done'>('idle')

  const handleFileSelect = async (selectedFile: File) => {
    setLoading(true)

    try {
      // Parse CSV to extract metadata and preview
      const fileContent = await selectedFile.text()
      const lines = fileContent.split('\n').filter(line => line.trim())
      const headers = lines[0].split(',').map(h => h.trim())

      // Parse all rows
      const allRows = lines.slice(1).map(line => {
        const values = line.split(',')
        const obj: any = {}
        headers.forEach((header, idx) => {
          obj[header] = values[idx]?.trim() || null
        })
        return obj
      })

      // Get head (first 5 rows)
      const head = allRows.slice(0, 5)

      // Get tail (last 5 rows)
      const tail = allRows.slice(-5)

      // Calculate basic statistics
      const numericColumns: string[] = []
      const categoricalColumns: string[] = []
      const stats: any = {}

      headers.forEach(col => {
        const values = allRows.map(row => row[col]).filter(v => v !== null && v !== undefined && v !== '')

        // Try to determine if numeric
        const numericValues = values.map(v => parseFloat(v as string)).filter(v => !isNaN(v))

        if (numericValues.length > 0 && numericValues.length / values.length > 0.8) {
          numericColumns.push(col)

          stats[col] = {
            type: 'numeric',
            count: values.length,
            mean: (numericValues.reduce((a, b) => a + b, 0) / numericValues.length).toFixed(2),
            min: Math.min(...numericValues).toFixed(2),
            max: Math.max(...numericValues).toFixed(2),
            std: (Math.sqrt(
              numericValues.reduce((sq, n) => sq + Math.pow(n - (numericValues.reduce((a, b) => a + b, 0) / numericValues.length), 2), 0) / numericValues.length
            )).toFixed(2),
          }
        } else {
          categoricalColumns.push(col)

          const uniqueCount = new Set(values).size
          stats[col] = {
            type: 'categorical',
            count: values.length,
            unique: uniqueCount,
            missing: allRows.length - values.length,
          }
        }
      })

      const parsedData = {
        filename: selectedFile.name,
        fileSize: (selectedFile.size / 1024 / 1024).toFixed(2),
        totalRows: allRows.length,
        totalColumns: headers.length,
        columnNames: headers,
        numericColumns,
        categoricalColumns,
        head,
        tail,
        stats,
        allData: allRows,
      }

      // Get quality analysis from API using smart LLM analyzer
      const formData = new FormData()
      formData.append('file', selectedFile)

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
      // Use smart LLM endpoint for intelligent analysis (if available)
      const response = await fetch(`${apiUrl}/api/local-analysis/smart`, {
        method: 'POST',
        body: formData,
      })

      const analysisData = await response.json()

      // Save to context
      data.setOriginalData(parsedData)
      data.setOriginalAnalysis(analysisData)
    } catch (error) {
      console.error('Error analyzing file:', error)
      alert(`Error analyzing file. Make sure backend is running on port 8001. Error: ${error}`)
    } finally {
      setLoading(false)
    }
  }

  const handleCleanData = async () => {
    if (!data.originalData) return

    setCleaningStatus('cleaning')

    try {
      // Remove duplicates and recalculate statistics
      const cleanedRows = data.originalData.allData.filter((row, idx, arr) => {
        return arr.findIndex(r => JSON.stringify(r) === JSON.stringify(row)) === idx
      })

      // Recalculate statistics for cleaned data
      const numericColumns: string[] = []
      const categoricalColumns: string[] = []
      const stats: any = {}

      data.originalData.columnNames.forEach(col => {
        const values = cleanedRows.map(row => row[col]).filter(v => v !== null && v !== undefined && v !== '')

        const numericValues = values.map(v => parseFloat(v as string)).filter(v => !isNaN(v))

        if (numericValues.length > 0 && numericValues.length / values.length > 0.8) {
          numericColumns.push(col)

          stats[col] = {
            type: 'numeric',
            count: values.length,
            mean: (numericValues.reduce((a, b) => a + b, 0) / numericValues.length).toFixed(2),
            min: Math.min(...numericValues).toFixed(2),
            max: Math.max(...numericValues).toFixed(2),
            std: (Math.sqrt(
              numericValues.reduce((sq, n) => sq + Math.pow(n - (numericValues.reduce((a, b) => a + b, 0) / numericValues.length), 2), 0) / numericValues.length
            )).toFixed(2),
          }
        } else {
          categoricalColumns.push(col)

          const uniqueCount = new Set(values).size
          stats[col] = {
            type: 'categorical',
            count: values.length,
            unique: uniqueCount,
            missing: cleanedRows.length - values.length,
          }
        }
      })

      const cleanedData = {
        ...data.originalData,
        totalRows: cleanedRows.length,
        allData: cleanedRows,
        head: cleanedRows.slice(0, 5),
        tail: cleanedRows.slice(-5),
        numericColumns,
        categoricalColumns,
        stats,
      }

      data.setCleanedData(cleanedData)
      setCleaningStatus('done')
    } catch (error) {
      console.error('Error cleaning data:', error)
      alert('Error cleaning data')
      setCleaningStatus('idle')
    }
  }

  const downloadCleanedData = () => {
    if (!data.cleanedData) return

    const csvContent = [
      data.cleanedData.columnNames.join(','),
      ...data.cleanedData.allData.map(row =>
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

    const element = document.createElement('a')
    element.setAttribute('href', 'data:text/csv;charset=utf-8,' + encodeURIComponent(csvContent))
    element.setAttribute('download', `cleaned_${data.cleanedData.filename}`)
    element.style.display = 'none'
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)
  }

  // No data - show upload
  if (!data.originalData) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        <header className="border-b border-slate-700 backdrop-blur-sm bg-slate-900/50">
          <div className="container mx-auto px-4 py-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
                <BarChart3 className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">Data Cleaner</h1>
                <p className="text-sm text-slate-400">Upload, analyze, clean & visualize your data</p>
              </div>
            </div>
          </div>
        </header>

        <div className="container mx-auto px-4 py-12">
          <div className="max-w-4xl mx-auto">
            <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700">
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold text-white mb-2">Upload Your Dataset</h2>
                <p className="text-slate-400">
                  Upload a CSV or Excel file to start cleaning and analyzing
                </p>
              </div>

              <FileUploader onFileSelect={handleFileSelect} disabled={loading} />

              {/* Info Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-12">
                <div className="bg-slate-700/30 rounded-lg p-4 border border-slate-600">
                  <h3 className="text-white font-semibold mb-2">📊 Analyze</h3>
                  <p className="text-sm text-slate-400">
                    View detailed statistics, head, tail, and describe your data
                  </p>
                </div>
                <div className="bg-slate-700/30 rounded-lg p-4 border border-slate-600">
                  <h3 className="text-white font-semibold mb-2">🎨 Visualize</h3>
                  <p className="text-sm text-slate-400">
                    Create professional charts and dashboards instantly
                  </p>
                </div>
                <div className="bg-slate-700/30 rounded-lg p-4 border border-slate-600">
                  <h3 className="text-white font-semibold mb-2">✨ Clean</h3>
                  <p className="text-sm text-slate-400">
                    Remove duplicates, handle missing values, and validate data
                  </p>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </main>
    )
  }

  // Data uploaded - show quality analysis with navigation buttons
  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header with Navigation */}
      <header className="border-b border-slate-700 backdrop-blur-sm bg-slate-900/50 sticky top-0 z-40">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
                <BarChart3 className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">Data Cleaner</h1>
                <p className="text-xs text-slate-400">
                  {data.isDataCleaned ? '✓ Cleaned Data' : 'Data Quality Analysis'}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <Button
                onClick={() => router.push('/analyze')}
                variant="outline"
                className="text-sm"
              >
                <Eye className="w-4 h-4 mr-2" />
                Analyze
              </Button>
              <Button
                onClick={() => router.push('/visualize')}
                variant="outline"
                className="text-sm"
              >
                <Eye className="w-4 h-4 mr-2" />
                Visualize
              </Button>
              {data.isDataCleaned && (
                <Button
                  onClick={() => router.push('/dashboard')}
                  variant="outline"
                  className="text-sm"
                >
                  Dashboard
                </Button>
              )}
              <Button
                onClick={() => data.reset()}
                variant="outline"
                className="text-sm text-red-400 border-red-400 hover:bg-red-500/10"
              >
                <Trash2 className="w-4 h-4 mr-2" />
                Reset
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-12">
        {!data.isDataCleaned ? (
          // Quality analysis view (uncleaned data)
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-3xl font-bold text-white">Data Quality Analysis Report</h2>
              <Button
                onClick={handleCleanData}
                disabled={cleaningStatus === 'cleaning'}
                className="bg-green-600 hover:bg-green-700"
              >
                {cleaningStatus === 'cleaning' ? 'Cleaning...' : 'Clean Dataset'}
              </Button>
            </div>

            {/* Show quality analysis info */}
            {data.originalAnalysis && (
              <>
                {/* Quality Score Card */}
                <Card className="bg-gradient-to-r from-red-500/10 to-orange-500/10 backdrop-blur-sm border-slate-600 p-8">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-2xl font-bold text-white mb-2">Overall Quality Score</h3>
                      <p className="text-slate-400">
                        Dataset contains {data.originalAnalysis.insights?.length || 0} critical issues
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-6xl font-bold text-red-400">
                        {data.originalAnalysis.quality_score || 0}
                      </p>
                      <p className="text-slate-400 text-sm mt-1">/100</p>
                    </div>
                  </div>
                </Card>

                {/* Issues Found */}
                {data.originalAnalysis.insights && data.originalAnalysis.insights.length > 0 && (
                  <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700">
                    <h3 className="text-2xl font-bold text-white mb-6">Issues Found</h3>
                    <div className="space-y-4">
                      {data.originalAnalysis.insights.map((insight: any, idx: number) => (
                        <div key={idx} className="bg-slate-700/30 border border-slate-600 rounded-lg p-4">
                          <div className="flex items-start justify-between mb-2">
                            <h4 className="text-white font-semibold">{insight.message || insight.issue || `Issue ${idx + 1}`}</h4>
                            <span className="text-xs px-3 py-1 rounded-full bg-red-500/20 text-red-300">
                              {insight.severity || 'High'}
                            </span>
                          </div>
                          {insight.column && (
                            <p className="text-slate-300 text-sm mb-2">
                              <span className="text-slate-400">Column:</span> {insight.column}
                            </p>
                          )}
                          {insight.percent && (
                            <p className="text-slate-300 text-sm mb-2">
                              <span className="text-slate-400">Affected:</span> {insight.percent.toFixed(1)}% of data
                            </p>
                          )}
                          {insight.description && (
                            <p className="text-slate-400 text-sm">{insight.description}</p>
                          )}
                        </div>
                      ))}
                    </div>
                  </Card>
                )}

                {/* Recommendations */}
                {data.originalAnalysis.recommendations && data.originalAnalysis.recommendations.length > 0 && (
                  <Card className="bg-blue-500/10 backdrop-blur-sm border-blue-500/30">
                    <h3 className="text-2xl font-bold text-white mb-6">Recommended Actions</h3>
                    <div className="space-y-4">
                      {data.originalAnalysis.recommendations.map((rec: any, idx: number) => (
                        <div key={idx} className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
                          <div className="flex items-start justify-between mb-2">
                            <h4 className="text-white font-semibold">{rec.action || rec.recommendation || `Action ${idx + 1}`}</h4>
                            <span className="text-xs px-3 py-1 rounded-full bg-blue-500/20 text-blue-300">
                              {rec.priority || 'Medium'}
                            </span>
                          </div>
                          {rec.impact && (
                            <p className="text-slate-300 text-sm mb-2">
                              <span className="text-slate-400">Impact:</span> {rec.impact}
                            </p>
                          )}
                          {rec.description && (
                            <p className="text-slate-400 text-sm">{rec.description}</p>
                          )}
                        </div>
                      ))}
                    </div>
                  </Card>
                )}

                {/* File Info */}
                <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700">
                  <h3 className="text-lg font-bold text-white mb-4">Dataset Information</h3>
                  <div className="grid md:grid-cols-4 gap-4">
                    <div className="bg-slate-700/30 rounded-lg p-4">
                      <p className="text-slate-400 text-sm mb-1">File</p>
                      <p className="text-white font-semibold truncate">{data.originalData?.filename || 'N/A'}</p>
                    </div>
                    <div className="bg-slate-700/30 rounded-lg p-4">
                      <p className="text-slate-400 text-sm mb-1">Total Rows</p>
                      <p className="text-white font-semibold">{data.originalData?.totalRows.toLocaleString() || 0}</p>
                    </div>
                    <div className="bg-slate-700/30 rounded-lg p-4">
                      <p className="text-slate-400 text-sm mb-1">Total Columns</p>
                      <p className="text-white font-semibold">{data.originalData?.totalColumns || 0}</p>
                    </div>
                    <div className="bg-slate-700/30 rounded-lg p-4">
                      <p className="text-slate-400 text-sm mb-1">File Size</p>
                      <p className="text-white font-semibold">{data.originalData?.fileSize} MB</p>
                    </div>
                  </div>
                </Card>
              </>
            )}
          </div>
        ) : (
          // Cleaned data view
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold text-white flex items-center gap-2">
                  <CheckCircle className="w-8 h-8 text-green-500" />
                  Cleaned Dataset
                </h2>
                <p className="text-slate-400 mt-2">
                  Removed {data.originalData!.totalRows - data.cleanedData!.totalRows} duplicates
                </p>
              </div>
              <Button
                onClick={downloadCleanedData}
                className="bg-blue-600 hover:bg-blue-700"
              >
                <Download className="w-4 h-4 mr-2" />
                Download CSV
              </Button>
            </div>

            <BasicAnalysis data={data.cleanedData!} onReset={() => data.reset()} />
          </div>
        )}
      </div>
    </main>
  )
}
