'use client'

import { CheckCircle, Download, RotateCcw } from 'lucide-react'
import Button from '@/components/ui/Button'
import Card from '@/components/ui/Card'

interface CleaningResultsProps {
  data: any
  onReset: () => void
}

export default function CleaningResults({ data, onReset }: CleaningResultsProps) {
  return (
    <div className="space-y-6">
      {/* Success Message */}
      <Card className="bg-gradient-to-br from-green-500/20 to-emerald-500/20 backdrop-blur-sm border-green-500/30">
        <div className="flex items-start space-x-4">
          <div className="w-12 h-12 rounded-full bg-green-500/30 flex items-center justify-center flex-shrink-0">
            <CheckCircle className="w-8 h-8 text-green-400" />
          </div>
          <div className="flex-1">
            <h2 className="text-2xl font-bold text-white mb-2">
              Data Cleaned Successfully!
            </h2>
            <p className="text-gray-300">
              Your cleaned file has been downloaded. Check your downloads folder.
            </p>
          </div>
        </div>
      </Card>

      {/* What's Next */}
      <Card className="bg-white/5 backdrop-blur-sm border-white/10">
        <h3 className="text-xl font-semibold text-white mb-4">What's Next?</h3>
        <div className="space-y-4">
          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0 mt-1">
              <span className="text-primary font-bold">1</span>
            </div>
            <div>
              <p className="text-white font-medium">Review Your Cleaned Data</p>
              <p className="text-sm text-gray-400 mt-1">
                Open the downloaded file and verify the changes
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0 mt-1">
              <span className="text-primary font-bold">2</span>
            </div>
            <div>
              <p className="text-white font-medium">Import to Your Systems</p>
              <p className="text-sm text-gray-400 mt-1">
                Use the cleaned data in your CRM, accounting software, or databases
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0 mt-1">
              <span className="text-primary font-bold">3</span>
            </div>
            <div>
              <p className="text-white font-medium">Clean More Files</p>
              <p className="text-sm text-gray-400 mt-1">
                Upload another file to continue cleaning your data
              </p>
            </div>
          </div>
        </div>
      </Card>

      {/* Actions */}
      <div className="flex gap-4">
        <Button
          onClick={onReset}
          size="lg"
          className="flex-1"
        >
          <RotateCcw className="w-5 h-5 mr-2" />
          Clean Another File
        </Button>
      </div>

      {/* Tips */}
      <Card className="bg-blue-500/10 backdrop-blur-sm border-blue-500/30">
        <div className="space-y-2">
          <p className="text-blue-300 font-semibold">💡 Pro Tips:</p>
          <ul className="text-sm text-gray-300 space-y-1 ml-4">
            <li>• Always backup your original data before using cleaned versions</li>
            <li>• Review critical fields manually for important business data</li>
            <li>• Enable AI suggestions for better results (configure API key in backend)</li>
            <li>• Clean data regularly to maintain high data quality</li>
          </ul>
        </div>
      </Card>
    </div>
  )
}
