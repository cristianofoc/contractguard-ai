/**
 * Analysis page: displays full AI analysis results for a single contract.
 * Polls the API every 3 seconds while status is pending/processing.
 */

import { useEffect, useRef, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { contractsApi, type Analysis } from '../services/api'
import RiskScore from '../components/RiskScore'
import ClauseCard from '../components/ClauseCard'

export default function AnalysisPage() {
  const { id } = useParams<{ id: string }>()
  const [analysis, setAnalysis] = useState<Analysis | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const fetchAnalysis = async () => {
    if (!id) return
    try {
      const { data } = await contractsApi.get(id)
      setAnalysis(data)

      // Stop polling once in a terminal state
      if (data.status === 'completed' || data.status === 'failed') {
        if (pollRef.current) clearInterval(pollRef.current)
      }
    } catch {
      setError('Failed to load analysis.')
      if (pollRef.current) clearInterval(pollRef.current)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAnalysis()
    // Poll every 3 seconds while processing
    pollRef.current = setInterval(fetchAnalysis, 3000)
    return () => {
      if (pollRef.current) clearInterval(pollRef.current)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id])

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen gap-4">
        <div className="animate-spin text-5xl">⏳</div>
        <p className="text-gray-500">Loading analysis…</p>
      </div>
    )
  }

  if (error || !analysis) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-20 text-center">
        <div className="text-5xl mb-4">❌</div>
        <h2 className="text-xl font-semibold text-gray-700 mb-2">{error || 'Analysis not found'}</h2>
        <Link to="/dashboard" className="text-brand-500 hover:underline text-sm">
          ← Back to dashboard
        </Link>
      </div>
    )
  }

  // Processing state
  if (analysis.status === 'pending' || analysis.status === 'processing') {
    return (
      <div className="max-w-2xl mx-auto px-4 py-20 text-center">
        <div className="animate-pulse text-5xl mb-4">🤖</div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Analysing your contract…</h2>
        <p className="text-gray-500 mb-2">
          Our AI is reviewing <strong>{analysis.filename}</strong> clause by clause.
        </p>
        <p className="text-sm text-gray-400">This usually takes 30–60 seconds.</p>
        <div className="mt-8 flex justify-center">
          <div className="flex gap-1">
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                className="w-2.5 h-2.5 bg-brand-500 rounded-full animate-bounce"
                style={{ animationDelay: `${i * 0.15}s` }}
              />
            ))}
          </div>
        </div>
      </div>
    )
  }

  // Failed state
  if (analysis.status === 'failed') {
    return (
      <div className="max-w-2xl mx-auto px-4 py-20 text-center">
        <div className="text-5xl mb-4">😕</div>
        <h2 className="text-xl font-semibold text-gray-700 mb-2">Analysis failed</h2>
        <p className="text-gray-500 mb-6">
          We couldn't analyse <strong>{analysis.filename}</strong>. This may be due to an
          unreadable file or a temporary error.
        </p>
        <Link to="/" className="bg-brand-500 text-white px-6 py-3 rounded-lg font-semibold text-sm hover:bg-brand-600 transition-colors">
          Try again with another file
        </Link>
      </div>
    )
  }

  // Completed state
  const clauses = analysis.clauses ?? []
  const highCount = clauses.filter((c) => c.risk_level === 'high').length
  const mediumCount = clauses.filter((c) => c.risk_level === 'medium').length
  const lowCount = clauses.filter((c) => c.risk_level === 'low').length

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Breadcrumb */}
      <nav className="text-sm text-gray-500">
        <Link to="/dashboard" className="hover:text-brand-500 transition-colors">
          ← Dashboard
        </Link>
        <span className="mx-2">/</span>
        <span className="text-gray-700 font-medium truncate">{analysis.filename}</span>
      </nav>

      {/* Header card */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 sm:p-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-1 break-words">{analysis.filename}</h1>
        <p className="text-sm text-gray-400 mb-6">
          Analysed on {new Date(analysis.updated_at).toLocaleString()}
        </p>

        {/* Overall risk */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-6">
          {analysis.overall_risk_level && analysis.overall_risk_score !== null && (
            <RiskScore
              level={analysis.overall_risk_level}
              score={analysis.overall_risk_score}
              size="lg"
            />
          )}
          <div className="flex gap-4 text-sm">
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">{highCount}</div>
              <div className="text-gray-500">High risk</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-600">{mediumCount}</div>
              <div className="text-gray-500">Medium risk</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{lowCount}</div>
              <div className="text-gray-500">Low risk</div>
            </div>
          </div>
        </div>
      </div>

      {/* Executive summary */}
      {analysis.summary && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-3">📋 Executive Summary</h2>
          <p className="text-gray-700 leading-relaxed">{analysis.summary}</p>
        </div>
      )}

      {/* Clause breakdown */}
      {clauses.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            🔍 Clause-by-Clause Breakdown
            <span className="ml-2 text-sm font-normal text-gray-400">({clauses.length} clauses)</span>
          </h2>
          <div className="space-y-4">
            {clauses.map((clause, i) => (
              <ClauseCard key={clause.id} clause={clause} index={i + 1} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
