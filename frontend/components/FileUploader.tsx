'use client'

import { useCallback, useState } from 'react'
import { Upload, FileSpreadsheet, X } from 'lucide-react'
import Button from '@/components/ui/Button'
import Card from '@/components/ui/Card'

interface FileUploaderProps {
  onFileSelect: (file: File) => void
}

export default function FileUploader({ onFileSelect }: FileUploaderProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    const files = e.dataTransfer.files
    if (files.length > 0) {
      const file = files[0]
      if (file.name.match(/\.(csv|xlsx|xls)$/i)) {
        setSelectedFile(file)
      } else {
        alert('Please upload a CSV or Excel file')
      }
    }
  }, [])

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      setSelectedFile(files[0])
    }
  }

  const handleUpload = () => {
    if (selectedFile) {
      onFileSelect(selectedFile)
    }
  }

  const handleRemove = () => {
    setSelectedFile(null)
  }

  return (
    <Card className="bg-white/5 backdrop-blur-sm border-white/10">
      <div
        className={`
          relative border-2 border-dashed rounded-lg p-12 text-center transition-all
          ${isDragging
            ? 'border-primary bg-primary/10'
            : 'border-gray-600 hover:border-gray-500'
          }
        `}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          type="file"
          id="file-upload"
          className="hidden"
          accept=".csv,.xlsx,.xls"
          onChange={handleFileInput}
        />

        {!selectedFile ? (
          <div className="space-y-4">
            <div className="flex justify-center">
              <div className="w-20 h-20 rounded-full bg-primary/20 flex items-center justify-center">
                <Upload className="w-10 h-10 text-primary" />
              </div>
            </div>

            <div>
              <h3 className="text-xl font-semibold text-white mb-2">
                Drop your file here, or browse
              </h3>
              <p className="text-gray-400">
                Supports CSV, Excel (.xlsx, .xls) • Max 10MB
              </p>
            </div>

            <div>
              <label htmlFor="file-upload">
                <Button
                  as="span"
                  size="lg"
                  className="cursor-pointer"
                >
                  Select File
                </Button>
              </label>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-center space-x-4 bg-white/5 rounded-lg p-4">
              <FileSpreadsheet className="w-8 h-8 text-green-400" />
              <div className="flex-1 text-left">
                <p className="font-semibold text-white">{selectedFile.name}</p>
                <p className="text-sm text-gray-400">
                  {(selectedFile.size / 1024).toFixed(2)} KB
                </p>
              </div>
              <button
                onClick={handleRemove}
                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-gray-400" />
              </button>
            </div>

            <Button
              onClick={handleUpload}
              size="lg"
              className="w-full"
            >
              Analyze File
            </Button>
          </div>
        )}
      </div>
    </Card>
  )
}
