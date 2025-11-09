'use client'

import { useRouter } from 'next/navigation'
import { ArrowLeft, BarChart3 } from 'lucide-react'
import BasicAnalysis from '@/components/BasicAnalysis'
import Button from '@/components/ui/Button'
import Card from '@/components/ui/Card'
import { useData } from '@/context/DataContext'

export default function AnalyzePage() {
  const router = useRouter()
  const data = useData()

  // No data - redirect to home
  if (!data.originalData) {
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
                  <h1 className="text-2xl font-bold text-white">Data Analyzer</h1>
                  <p className="text-sm text-slate-400">Analyze your dataset</p>
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

  // Determine which dataset to show
  const currentData = data.isDataCleaned ? data.cleanedData : data.originalData
  const dataType = data.isDataCleaned ? 'Cleaned' : 'Uncleaned'

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
                <h1 className="text-2xl font-bold text-white">Data Analyzer</h1>
                <p className="text-sm text-slate-400">{dataType} Data Analysis</p>
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
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-3xl font-bold text-white">
              {dataType} Dataset Analysis
            </h2>
          </div>

          {currentData && (
            <BasicAnalysis data={currentData} onReset={() => data.reset()} />
          )}
        </div>
      </div>
    </main>
  )
}
