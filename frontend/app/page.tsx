'use client'

import { useState } from 'react'
import { Upload, Sparkles, Download, CheckCircle, XCircle, AlertCircle } from 'lucide-react'
import FileUploader from '@/components/FileUploader'
import DataPreview from '@/components/DataPreview'
import CleaningResults from '@/components/CleaningResults'
import Button from '@/components/ui/Button'
import Card from '@/components/ui/Card'

export default function Home() {
  const [file, setFile] = useState<File | null>(null)
  const [analysisData, setAnalysisData] = useState<any>(null)
  const [cleanedData, setCleanedData] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [step, setStep] = useState<'upload' | 'analyze' | 'clean'>('upload')

  const handleFileSelect = async (selectedFile: File) => {
    setFile(selectedFile)
    setStep('analyze')
    setLoading(true)

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

      const response = await fetch('http://localhost:8000/api/analyze', {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()
      setAnalysisData(data)
    } catch (error) {
      console.error('Error analyzing file:', error)
      alert('Error analyzing file. Make sure the backend is running on port 8000.')
    } finally {
      setLoading(false)
    }
  }

  const handleClean = async (options: any) => {
    setLoading(true)
    setStep('clean')

    try {
      const formData = new FormData()
      formData.append('file', file!)

      const queryParams = new URLSearchParams({
        remove_duplicates: options.removeDuplicates.toString(),
        fill_missing: options.fillMissing.toString(),
        standardize_formats: options.standardizeFormats.toString(),
        use_ai: options.useAI.toString(),
      })

      const response = await fetch(`http://localhost:8000/api/clean?${queryParams}`, {
        method: 'POST',
        body: formData,
      })

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = file!.name.replace(/\.(csv|xlsx)$/, '_cleaned.$1')
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      // Get cleaning report from headers
      const report = response.headers.get('X-Cleaning-Report')
      setCleanedData({ success: true, report })

    } catch (error) {
      console.error('Error cleaning file:', error)
      alert('Error cleaning file. Make sure the backend is running.')
    } finally {
      setLoading(false)
    }
  }

  const resetApp = () => {
    setFile(null)
    setAnalysisData(null)
    setCleanedData(null)
    setStep('upload')
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900">
      {/* Header */}
      <header className="border-b border-white/10 backdrop-blur-sm bg-white/5">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">AI Data Cleaner</h1>
                <p className="text-sm text-gray-300">Clean your data with AI power</p>
              </div>
            </div>
            {file && (
              <Button onClick={resetApp} variant="secondary">
                Upload New File
              </Button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-12">
        {step === 'upload' && (
          <div className="max-w-4xl mx-auto">
            {/* Hero Section */}
            <div className="text-center mb-12">
              <h2 className="text-5xl font-bold text-white mb-4">
                Clean Your Data in <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">Seconds</span>
              </h2>
              <p className="text-xl text-gray-300 mb-8">
                Upload your CSV or Excel file and let AI handle the rest
              </p>
            </div>

            {/* Features Grid */}
            <div className="grid md:grid-cols-3 gap-6 mb-12">
              <Card className="bg-white/5 backdrop-blur-sm border-white/10">
                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 rounded-lg bg-green-500/20 flex items-center justify-center flex-shrink-0">
                    <CheckCircle className="w-6 h-6 text-green-400" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-white mb-2">Remove Duplicates</h3>
                    <p className="text-gray-400 text-sm">Automatically detect and remove duplicate rows</p>
                  </div>
                </div>
              </Card>

              <Card className="bg-white/5 backdrop-blur-sm border-white/10">
                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 rounded-lg bg-blue-500/20 flex items-center justify-center flex-shrink-0">
                    <AlertCircle className="w-6 h-6 text-blue-400" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-white mb-2">Fill Missing Values</h3>
                    <p className="text-gray-400 text-sm">Smart filling based on data patterns</p>
                  </div>
                </div>
              </Card>

              <Card className="bg-white/5 backdrop-blur-sm border-white/10">
                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 rounded-lg bg-purple-500/20 flex items-center justify-center flex-shrink-0">
                    <Sparkles className="w-6 h-6 text-purple-400" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-white mb-2">Standardize Formats</h3>
                    <p className="text-gray-400 text-sm">Normalize dates, emails, phone numbers</p>
                  </div>
                </div>
              </Card>
            </div>

            {/* Upload Section */}
            <FileUploader onFileSelect={handleFileSelect} />
          </div>
        )}

        {step === 'analyze' && analysisData && (
          <div className="max-w-6xl mx-auto">
            <DataPreview
              data={analysisData}
              onClean={handleClean}
              loading={loading}
            />
          </div>
        )}

        {step === 'clean' && cleanedData && (
          <div className="max-w-4xl mx-auto">
            <CleaningResults
              data={cleanedData}
              onReset={resetApp}
            />
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="border-t border-white/10 backdrop-blur-sm bg-white/5 mt-20">
        <div className="container mx-auto px-4 py-6 text-center text-gray-400">
          <p>Built with Next.js, FastAPI, and LangChain • Free for SMEs 🚀</p>
        </div>
      </footer>
    </main>
  )
}
