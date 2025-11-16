'use client'

import { useRouter } from 'next/navigation'
import { Database, BarChart3, Sparkles, TrendingUp } from 'lucide-react'

export default function LandingPage() {
  const router = useRouter()

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#1a1a1d] via-[#1f1f23] to-[#25252a] text-white">
      {/* Header */}
      <header className="border-b border-gray-800 bg-[#1f1f23]/80 backdrop-blur-sm">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center gap-3">
            <Sparkles className="h-8 w-8 text-blue-500" />
            <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              AI Data Platform
            </h1>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-16">
        <div className="text-center mb-16">
          <h2 className="text-5xl font-bold mb-4 bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
            Welcome to Your Data Platform
          </h2>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Choose your workspace based on your role and needs
          </p>
        </div>

        {/* Two Service Cards */}
        <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">

          {/* Clean & Analyze Card */}
          <button
            onClick={() => router.push('/clean')}
            className="group relative bg-gradient-to-br from-blue-900/30 to-blue-800/20 border border-blue-700/30 rounded-2xl p-8 hover:border-blue-500/50 hover:shadow-2xl hover:shadow-blue-500/20 transition-all duration-300 text-left"
          >
            <div className="absolute top-4 right-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <Database className="h-32 w-32" />
            </div>

            <div className="relative z-10">
              <div className="bg-blue-500/20 w-16 h-16 rounded-xl flex items-center justify-center mb-6 group-hover:bg-blue-500/30 transition-colors">
                <Database className="h-8 w-8 text-blue-400" />
              </div>

              <h3 className="text-3xl font-bold mb-3 group-hover:text-blue-400 transition-colors">
                Clean & Analyze
              </h3>

              <p className="text-gray-400 mb-6 text-lg">
                For Data Analysts & Engineers
              </p>

              <ul className="space-y-3 mb-8">
                <li className="flex items-start gap-2 text-gray-300">
                  <span className="text-blue-400 mt-1">✓</span>
                  <span>Connect to databases (BigQuery, PostgreSQL, MySQL, etc.)</span>
                </li>
                <li className="flex items-start gap-2 text-gray-300">
                  <span className="text-blue-400 mt-1">✓</span>
                  <span>Clean and analyze data with AI assistance</span>
                </li>
                <li className="flex items-start gap-2 text-gray-300">
                  <span className="text-blue-400 mt-1">✓</span>
                  <span>Basic EDA (head, describe, info, null analysis)</span>
                </li>
                <li className="flex items-start gap-2 text-gray-300">
                  <span className="text-blue-400 mt-1">✓</span>
                  <span>Export to Jupyter Notebook or Google Colab</span>
                </li>
              </ul>

              <div className="flex items-center gap-2 text-blue-400 font-semibold group-hover:gap-4 transition-all">
                <span>Get Started</span>
                <span>→</span>
              </div>
            </div>
          </button>

          {/* Dashboard Card */}
          <button
            onClick={() => router.push('/dashboard')}
            className="group relative bg-gradient-to-br from-purple-900/30 to-purple-800/20 border border-purple-700/30 rounded-2xl p-8 hover:border-purple-500/50 hover:shadow-2xl hover:shadow-purple-500/20 transition-all duration-300 text-left"
          >
            <div className="absolute top-4 right-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <BarChart3 className="h-32 w-32" />
            </div>

            <div className="relative z-10">
              <div className="bg-purple-500/20 w-16 h-16 rounded-xl flex items-center justify-center mb-6 group-hover:bg-purple-500/30 transition-colors">
                <BarChart3 className="h-8 w-8 text-purple-400" />
              </div>

              <h3 className="text-3xl font-bold mb-3 group-hover:text-purple-400 transition-colors">
                Business Dashboard
              </h3>

              <p className="text-gray-400 mb-6 text-lg">
                For Business Users & Stakeholders
              </p>

              <ul className="space-y-3 mb-8">
                <li className="flex items-start gap-2 text-gray-300">
                  <span className="text-purple-400 mt-1">✓</span>
                  <span>Connect to your data sources (no code required)</span>
                </li>
                <li className="flex items-start gap-2 text-gray-300">
                  <span className="text-purple-400 mt-1">✓</span>
                  <span>Visualize data with drag-and-drop interface</span>
                </li>
                <li className="flex items-start gap-2 text-gray-300">
                  <span className="text-purple-400 mt-1">✓</span>
                  <span>Pre-built charts and insights</span>
                </li>
                <li className="flex items-start gap-2 text-gray-300">
                  <span className="text-purple-400 mt-1">✓</span>
                  <span>Share reports with your team</span>
                </li>
              </ul>

              <div className="flex items-center gap-2 text-purple-400 font-semibold group-hover:gap-4 transition-all">
                <span>Get Started</span>
                <span>→</span>
              </div>
            </div>
          </button>
        </div>

        {/* Features Section */}
        <div className="mt-24 grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
          <div className="bg-gray-800/30 border border-gray-700/50 rounded-xl p-6 text-center">
            <div className="bg-green-500/20 w-12 h-12 rounded-lg flex items-center justify-center mx-auto mb-4">
              <Sparkles className="h-6 w-6 text-green-400" />
            </div>
            <h4 className="font-semibold mb-2 text-lg">AI-Powered</h4>
            <p className="text-gray-400 text-sm">
              Llama 3.1 8B for intelligent data analysis and cleaning
            </p>
          </div>

          <div className="bg-gray-800/30 border border-gray-700/50 rounded-xl p-6 text-center">
            <div className="bg-blue-500/20 w-12 h-12 rounded-lg flex items-center justify-center mx-auto mb-4">
              <Database className="h-6 w-6 text-blue-400" />
            </div>
            <h4 className="font-semibold mb-2 text-lg">Multiple Sources</h4>
            <p className="text-gray-400 text-sm">
              Connect to BigQuery, SQL databases, data warehouses, and data lakes
            </p>
          </div>

          <div className="bg-gray-800/30 border border-gray-700/50 rounded-xl p-6 text-center">
            <div className="bg-purple-500/20 w-12 h-12 rounded-lg flex items-center justify-center mx-auto mb-4">
              <TrendingUp className="h-6 w-6 text-purple-400" />
            </div>
            <h4 className="font-semibold mb-2 text-lg">Enterprise Ready</h4>
            <p className="text-gray-400 text-sm">
              Secure, scalable, and built for teams of all sizes
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-800 mt-24 py-8">
        <div className="container mx-auto px-6 text-center text-gray-500">
          <p>© 2025 AI Data Platform. Built with Next.js, FastAPI, and Llama 3.1</p>
        </div>
      </footer>
    </div>
  )
}
