'use client'

import { useState } from 'react'
import { AlertCircle, CheckCircle, XCircle, Sparkles } from 'lucide-react'
import Button from '@/components/ui/Button'
import Card from '@/components/ui/Card'

interface DataPreviewProps {
  data: any
  onClean: (options: any) => void
  loading: boolean
}

export default function DataPreview({ data, onClean, loading }: DataPreviewProps) {
  const [options, setOptions] = useState({
    removeDuplicates: true,
    fillMissing: true,
    standardizeFormats: true,
    useAI: false,
  })

  const qualityScore = data.quality_score || data.analysis?.quality_score || 0
  const insights = data.insights || data.analysis?.insights || []
  const recommendations = data.recommendations || data.analysis?.recommendations || []
  const detailedMetrics = data.detailed_metrics || data.analysis?.detailed_metrics || {}

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-400'
    if (score >= 50) return 'text-yellow-400'
    return 'text-red-400'
  }

  const getScoreBg = (score: number) => {
    if (score >= 80) return 'bg-green-500/20'
    if (score >= 50) return 'bg-yellow-500/20'
    return 'bg-red-500/20'
  }

  return (
    <div className="space-y-6">
      {/* File Info & Quality Score */}
      <Card className="bg-white/5 backdrop-blur-sm border-white/10">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-white mb-2">Data Analysis</h2>
            <p className="text-gray-400">
              {data.filename} • {data.rows.toLocaleString()} rows • {data.columns} columns
            </p>
          </div>
          <div className={`${getScoreBg(qualityScore)} px-6 py-4 rounded-lg`}>
            <p className="text-sm text-gray-300 mb-1">Quality Score</p>
            <p className={`text-4xl font-bold ${getScoreColor(qualityScore)}`}>
              {qualityScore}
            </p>
          </div>
        </div>
      </Card>

      {/* Issues Found - Insights */}
      {insights && insights.length > 0 && (
        <Card className="bg-white/5 backdrop-blur-sm border-white/10">
          <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
            <AlertCircle className="w-5 h-5 mr-2 text-yellow-400" />
            Issues Found ({insights.length})
          </h3>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {insights.map((insight: any, idx: number) => (
              <div
                key={idx}
                className="flex items-start space-x-3 bg-white/5 rounded-lg p-4"
              >
                <XCircle className="w-5 h-5 text-red-400 mt-0.5" />
                <div className="flex-1">
                  <p className="text-white font-medium">
                    {insight.message || insight.issue || JSON.stringify(insight)}
                  </p>
                  {insight.column && (
                    <p className="text-sm text-gray-400 mt-1">
                      Column: <span className="text-gray-300">{insight.column}</span>
                      {insight.percent && ` • ${insight.percent.toFixed(1)}% affected`}
                    </p>
                  )}
                  {insight.severity && (
                    <p className="text-sm text-gray-400 mt-1">
                      Severity: <span className="capitalize text-yellow-400">{insight.severity}</span>
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Recommendations */}
      {recommendations && recommendations.length > 0 && (
        <Card className="bg-blue-500/10 backdrop-blur-sm border-blue-500/30">
          <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
            <Sparkles className="w-5 h-5 mr-2 text-blue-400" />
            Recommendations ({recommendations.length})
          </h3>
          <div className="space-y-3">
            {recommendations.map((rec: any, idx: number) => (
              <div
                key={idx}
                className="flex items-start space-x-3 bg-blue-500/10 rounded-lg p-4"
              >
                <CheckCircle className="w-5 h-5 text-blue-400 mt-0.5" />
                <div className="flex-1">
                  <p className="text-white font-medium">{rec.action}</p>
                  <p className="text-sm text-gray-400 mt-1">
                    Priority: <span className="capitalize text-blue-400">{rec.priority}</span>
                    {rec.impact && ` • Impact: ${rec.impact}`}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Data Preview */}
      <Card className="bg-white/5 backdrop-blur-sm border-white/10">
        <h3 className="text-xl font-semibold text-white mb-4">Data Preview</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-700">
                {data.column_names.map((col: string) => (
                  <th key={col} className="px-4 py-3 text-left text-gray-300 font-semibold">
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.preview.map((row: any, idx: number) => (
                <tr key={idx} className="border-b border-gray-800 hover:bg-white/5">
                  {data.column_names.map((col: string) => (
                    <td key={col} className="px-4 py-3 text-gray-400">
                      {row[col] !== null && row[col] !== undefined ? String(row[col]) : '—'}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Cleaning Options */}
      <Card className="bg-white/5 backdrop-blur-sm border-white/10">
        <h3 className="text-xl font-semibold text-white mb-4">Cleaning Options</h3>
        <div className="space-y-3">
          <label className="flex items-center space-x-3 cursor-pointer group">
            <input
              type="checkbox"
              checked={options.removeDuplicates}
              onChange={(e) => setOptions({ ...options, removeDuplicates: e.target.checked })}
              className="w-5 h-5 rounded border-gray-600 bg-gray-800 text-primary focus:ring-primary focus:ring-offset-gray-900"
            />
            <span className="text-white group-hover:text-primary transition-colors">
              Remove duplicate rows
            </span>
          </label>

          <label className="flex items-center space-x-3 cursor-pointer group">
            <input
              type="checkbox"
              checked={options.fillMissing}
              onChange={(e) => setOptions({ ...options, fillMissing: e.target.checked })}
              className="w-5 h-5 rounded border-gray-600 bg-gray-800 text-primary focus:ring-primary focus:ring-offset-gray-900"
            />
            <span className="text-white group-hover:text-primary transition-colors">
              Fill missing values (smart fill)
            </span>
          </label>

          <label className="flex items-center space-x-3 cursor-pointer group">
            <input
              type="checkbox"
              checked={options.standardizeFormats}
              onChange={(e) => setOptions({ ...options, standardizeFormats: e.target.checked })}
              className="w-5 h-5 rounded border-gray-600 bg-gray-800 text-primary focus:ring-primary focus:ring-offset-gray-900"
            />
            <span className="text-white group-hover:text-primary transition-colors">
              Standardize formats (dates, emails, phones)
            </span>
          </label>

          <label className="flex items-center space-x-3 cursor-pointer group">
            <input
              type="checkbox"
              checked={options.useAI}
              onChange={(e) => setOptions({ ...options, useAI: e.target.checked })}
              className="w-5 h-5 rounded border-gray-600 bg-gray-800 text-primary focus:ring-primary focus:ring-offset-gray-900"
            />
            <span className="text-white group-hover:text-primary transition-colors flex items-center">
              <Sparkles className="w-4 h-4 mr-2 text-purple-400" />
              Use AI for smart suggestions (requires API key)
            </span>
          </label>
        </div>

        <div className="mt-6">
          <Button
            onClick={() => onClean(options)}
            disabled={loading}
            size="lg"
            className="w-full"
          >
            {loading ? 'Cleaning...' : 'Clean & Download'}
          </Button>
        </div>
      </Card>
    </div>
  )
}
