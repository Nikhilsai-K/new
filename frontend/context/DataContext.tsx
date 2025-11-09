'use client'

import React, { createContext, useContext, useState, ReactNode } from 'react'

interface ParsedData {
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

interface AnalysisData {
  quality_score?: number
  insights?: any[]
  recommendations?: any[]
  detailed_metrics?: any
}

interface DataContextType {
  // Original file data
  originalData: ParsedData | null
  originalAnalysis: AnalysisData | null
  setOriginalData: (data: ParsedData | null) => void
  setOriginalAnalysis: (data: AnalysisData | null) => void

  // Cleaned file data
  cleanedData: ParsedData | null
  cleanedAnalysis: AnalysisData | null
  setCleanedData: (data: ParsedData | null) => void
  setCleanedAnalysis: (data: AnalysisData | null) => void

  // State tracking
  isDataCleaned: boolean
  reset: () => void
}

const DataContext = createContext<DataContextType | undefined>(undefined)

export function DataProvider({ children }: { children: ReactNode }) {
  const [originalData, setOriginalData] = useState<ParsedData | null>(null)
  const [originalAnalysis, setOriginalAnalysis] = useState<AnalysisData | null>(null)
  const [cleanedData, setCleanedData] = useState<ParsedData | null>(null)
  const [cleanedAnalysis, setCleanedAnalysis] = useState<AnalysisData | null>(null)

  const isDataCleaned = cleanedData !== null

  const reset = () => {
    setOriginalData(null)
    setOriginalAnalysis(null)
    setCleanedData(null)
    setCleanedAnalysis(null)
  }

  return (
    <DataContext.Provider
      value={{
        originalData,
        originalAnalysis,
        setOriginalData,
        setOriginalAnalysis,
        cleanedData,
        cleanedAnalysis,
        setCleanedData,
        setCleanedAnalysis,
        isDataCleaned,
        reset,
      }}
    >
      {children}
    </DataContext.Provider>
  )
}

export function useData() {
  const context = useContext(DataContext)
  if (context === undefined) {
    throw new Error('useData must be used within a DataProvider')
  }
  return context
}
