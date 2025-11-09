'use client'

import { useState } from 'react'
import { Download, RefreshCw, ChevronDown, ChevronUp } from 'lucide-react'
import Button from '@/components/ui/Button'
import Card from '@/components/ui/Card'

interface BasicAnalysisProps {
  data: {
    filename: string
    fileSize: string
    totalRows: number
    totalColumns: number
    columnNames: string[]
    numericColumns: string[]
    categoricalColumns: string[]
    head: any[]
    tail: any[]
    stats: any
    allData: any[]
  }
  onReset: () => void
}

export default function BasicAnalysis({ data, onReset }: BasicAnalysisProps) {
  const [expandedSections, setExpandedSections] = useState({
    fileInfo: true,
    columns: true,
    head: true,
    tail: true,
    describe: true,
  })

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section],
    }))
  }

  const downloadCSV = () => {
    const csvContent = [
      data.columnNames.join(','),
      ...data.allData.map(row =>
        data.columnNames.map(col => {
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
    element.setAttribute('download', `analyzed_${data.filename}`)
    element.style.display = 'none'
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold text-white">Basic Analysis</h2>
        <div className="flex gap-3">
          <Button onClick={downloadCSV} className="bg-green-600 hover:bg-green-700">
            <Download className="w-4 h-4 mr-2" />
            Download CSV
          </Button>
          <Button onClick={onReset} variant="outline">
            <RefreshCw className="w-4 h-4 mr-2" />
            Analyze Another
          </Button>
        </div>
      </div>

      {/* File Information Section */}
      <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700">
        <button
          onClick={() => toggleSection('fileInfo')}
          className="flex items-center justify-between w-full p-4 hover:bg-slate-700/30 rounded transition"
        >
          <h3 className="text-xl font-semibold text-white">File Information</h3>
          {expandedSections.fileInfo ? (
            <ChevronUp className="w-5 h-5 text-slate-400" />
          ) : (
            <ChevronDown className="w-5 h-5 text-slate-400" />
          )}
        </button>

        {expandedSections.fileInfo && (
          <div className="border-t border-slate-700 p-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-slate-700/30 rounded-lg p-4 border border-slate-600">
                <p className="text-sm text-slate-400 mb-1">Filename</p>
                <p className="text-white font-semibold truncate">{data.filename}</p>
              </div>
              <div className="bg-slate-700/30 rounded-lg p-4 border border-slate-600">
                <p className="text-sm text-slate-400 mb-1">File Size</p>
                <p className="text-white font-semibold">{data.fileSize} MB</p>
              </div>
              <div className="bg-slate-700/30 rounded-lg p-4 border border-slate-600">
                <p className="text-sm text-slate-400 mb-1">Total Rows</p>
                <p className="text-white font-semibold">{data.totalRows.toLocaleString()}</p>
              </div>
              <div className="bg-slate-700/30 rounded-lg p-4 border border-slate-600">
                <p className="text-sm text-slate-400 mb-1">Total Columns</p>
                <p className="text-white font-semibold">{data.totalColumns}</p>
              </div>
            </div>
          </div>
        )}
      </Card>

      {/* Columns Section */}
      <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700">
        <button
          onClick={() => toggleSection('columns')}
          className="flex items-center justify-between w-full p-4 hover:bg-slate-700/30 rounded transition"
        >
          <h3 className="text-xl font-semibold text-white">Column Information</h3>
          {expandedSections.columns ? (
            <ChevronUp className="w-5 h-5 text-slate-400" />
          ) : (
            <ChevronDown className="w-5 h-5 text-slate-400" />
          )}
        </button>

        {expandedSections.columns && (
          <div className="border-t border-slate-700 p-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="text-sm font-semibold text-slate-300 mb-3 uppercase tracking-wide">
                  Numeric Columns ({data.numericColumns.length})
                </h4>
                <div className="space-y-2">
                  {data.numericColumns.length > 0 ? (
                    data.numericColumns.map(col => (
                      <div key={col} className="bg-blue-500/10 border border-blue-500/20 rounded px-3 py-2">
                        <p className="text-sm text-blue-300">{col}</p>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-slate-400 italic">No numeric columns</p>
                  )}
                </div>
              </div>
              <div>
                <h4 className="text-sm font-semibold text-slate-300 mb-3 uppercase tracking-wide">
                  Categorical Columns ({data.categoricalColumns.length})
                </h4>
                <div className="space-y-2">
                  {data.categoricalColumns.length > 0 ? (
                    data.categoricalColumns.map(col => (
                      <div key={col} className="bg-purple-500/10 border border-purple-500/20 rounded px-3 py-2">
                        <p className="text-sm text-purple-300">{col}</p>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-slate-400 italic">No categorical columns</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </Card>

      {/* Head Section */}
      <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700">
        <button
          onClick={() => toggleSection('head')}
          className="flex items-center justify-between w-full p-4 hover:bg-slate-700/30 rounded transition"
        >
          <h3 className="text-xl font-semibold text-white">First 5 Rows (Head)</h3>
          {expandedSections.head ? (
            <ChevronUp className="w-5 h-5 text-slate-400" />
          ) : (
            <ChevronDown className="w-5 h-5 text-slate-400" />
          )}
        </button>

        {expandedSections.head && (
          <div className="border-t border-slate-700 p-4 overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-600">
                  {data.columnNames.map(col => (
                    <th key={col} className="px-4 py-2 text-left text-slate-300 font-semibold whitespace-nowrap">
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.head.map((row, idx) => (
                  <tr key={idx} className="border-b border-slate-700 hover:bg-slate-700/20 transition">
                    {data.columnNames.map(col => (
                      <td key={`${idx}-${col}`} className="px-4 py-2 text-slate-300 whitespace-nowrap text-ellipsis overflow-hidden max-w-xs">
                        {row[col] === null || row[col] === undefined ? (
                          <span className="text-slate-500 italic">null</span>
                        ) : (
                          String(row[col])
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* Tail Section */}
      <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700">
        <button
          onClick={() => toggleSection('tail')}
          className="flex items-center justify-between w-full p-4 hover:bg-slate-700/30 rounded transition"
        >
          <h3 className="text-xl font-semibold text-white">Last 5 Rows (Tail)</h3>
          {expandedSections.tail ? (
            <ChevronUp className="w-5 h-5 text-slate-400" />
          ) : (
            <ChevronDown className="w-5 h-5 text-slate-400" />
          )}
        </button>

        {expandedSections.tail && (
          <div className="border-t border-slate-700 p-4 overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-600">
                  {data.columnNames.map(col => (
                    <th key={col} className="px-4 py-2 text-left text-slate-300 font-semibold whitespace-nowrap">
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.tail.map((row, idx) => (
                  <tr key={idx} className="border-b border-slate-700 hover:bg-slate-700/20 transition">
                    {data.columnNames.map(col => (
                      <td key={`${idx}-${col}`} className="px-4 py-2 text-slate-300 whitespace-nowrap text-ellipsis overflow-hidden max-w-xs">
                        {row[col] === null || row[col] === undefined ? (
                          <span className="text-slate-500 italic">null</span>
                        ) : (
                          String(row[col])
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* Describe/Statistics Section */}
      <Card className="bg-slate-800/50 backdrop-blur-sm border-slate-700">
        <button
          onClick={() => toggleSection('describe')}
          className="flex items-center justify-between w-full p-4 hover:bg-slate-700/30 rounded transition"
        >
          <h3 className="text-xl font-semibold text-white">Describe - Statistics</h3>
          {expandedSections.describe ? (
            <ChevronUp className="w-5 h-5 text-slate-400" />
          ) : (
            <ChevronDown className="w-5 h-5 text-slate-400" />
          )}
        </button>

        {expandedSections.describe && (
          <div className="border-t border-slate-700 p-4 space-y-8">
            {/* Numeric Statistics */}
            {data.numericColumns.length > 0 && (
              <div>
                <h4 className="text-lg font-semibold text-white mb-4">📊 Numeric Columns</h4>
                <div className="space-y-4">
                  {data.numericColumns.map(col => (
                    <div key={col} className="bg-slate-700/30 border border-slate-600 rounded-lg p-4">
                      <h5 className="text-white font-semibold mb-3">{col}</h5>
                      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                        <div className="bg-slate-800/50 rounded p-2">
                          <p className="text-xs text-slate-400">Count</p>
                          <p className="text-white font-semibold">{data.stats[col]?.count || 0}</p>
                        </div>
                        <div className="bg-slate-800/50 rounded p-2">
                          <p className="text-xs text-slate-400">Mean</p>
                          <p className="text-white font-semibold">{data.stats[col]?.mean || 'N/A'}</p>
                        </div>
                        <div className="bg-slate-800/50 rounded p-2">
                          <p className="text-xs text-slate-400">Min</p>
                          <p className="text-white font-semibold">{data.stats[col]?.min || 'N/A'}</p>
                        </div>
                        <div className="bg-slate-800/50 rounded p-2">
                          <p className="text-xs text-slate-400">Max</p>
                          <p className="text-white font-semibold">{data.stats[col]?.max || 'N/A'}</p>
                        </div>
                        <div className="bg-slate-800/50 rounded p-2">
                          <p className="text-xs text-slate-400">Std Dev</p>
                          <p className="text-white font-semibold">{data.stats[col]?.std || 'N/A'}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Categorical Statistics */}
            {data.categoricalColumns.length > 0 && (
              <div>
                <h4 className="text-lg font-semibold text-white mb-4">🏷️ Categorical Columns</h4>
                <div className="space-y-4">
                  {data.categoricalColumns.map(col => (
                    <div key={col} className="bg-slate-700/30 border border-slate-600 rounded-lg p-4">
                      <h5 className="text-white font-semibold mb-3">{col}</h5>
                      <div className="grid grid-cols-3 gap-3">
                        <div className="bg-slate-800/50 rounded p-2">
                          <p className="text-xs text-slate-400">Count</p>
                          <p className="text-white font-semibold">{data.stats[col]?.count || 0}</p>
                        </div>
                        <div className="bg-slate-800/50 rounded p-2">
                          <p className="text-xs text-slate-400">Unique</p>
                          <p className="text-white font-semibold">{data.stats[col]?.unique || 0}</p>
                        </div>
                        <div className="bg-slate-800/50 rounded p-2">
                          <p className="text-xs text-slate-400">Missing</p>
                          <p className="text-white font-semibold">{data.stats[col]?.missing || 0}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </Card>
    </div>
  )
}
