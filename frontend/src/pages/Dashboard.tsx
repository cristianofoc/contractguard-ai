/**
 * Dashboard page: shows paginated list of past contract analyses.
 */

import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { contractsApi, type AnalysisSummary } from '../services/api'
import RiskScore from '../components/RiskScore'

function StatusBadge({ status }: { status: AnalysisSummary['status'] }) {
  const map = {
    pending: 'bg-gray-100 text-gray-600',
    processing: 'bg-blue-100 text-blue-700 animate-pulse',
    completed: 'bg-green-100 text-green-700',
    failed: 'bg-red-100 text-red-700',
  }
  return (
    <span className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-semibold ${map[status]}`}>
      {status}
    </span>
  )
}

export default function Dashboard() {
  const [analyses, setAnalyses] = useState<AnalysisSummary[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()
  const PER_PAGE = 20

  const fetchAnalyses = async (p: number) => {
    setLoading(true)
    setError(null)
    try {
      const { data } = await contractsApi.list(p, PER_PAGE)
      setAnalyses(data.items)
      setTotal(data.total)
    } catch {
      setError('Failed to load analyses.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAnalyses(page)
  }, [page])

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this analysis? This cannot be undone.')) return
    try {
      await contractsApi.delete(id)
      fetchAnalyses(page)
    } catch {
      alert('Failed to delete analysis.')
    }
  }

  const totalPages = Math.ceil(total / PER_PAGE)

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">My Contracts</h1>
          <p className="text-gray-500 mt-1 text-sm">
            {total} {total === 1 ? 'analysis' : 'analyses'} total
          </p>
        </div>
        <Link
          to="/"
          className="bg-brand-500 hover:bg-brand-600 text-white font-semibold px-5 py-2.5 rounded-lg transition-colors text-sm"
        >
          + Analyse new contract
        </Link>
      </div>

      {/* States */}
      {loading && (
        <div className="flex justify-center py-20 text-gray-400">
          <span className="animate-spin text-3xl">⏳</span>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl p-6 text-center">
          {error}
        </div>
      )}

      {!loading && !error && analyses.length === 0 && (
        <div className="text-center py-20">
          <div className="text-5xl mb-4">📂</div>
          <h2 className="text-xl font-semibold text-gray-700 mb-2">No analyses yet</h2>
          <p className="text-gray-500 mb-6">Upload your first contract to get started.</p>
          <Link to="/" className="bg-brand-500 hover:bg-brand-600 text-white px-6 py-3 rounded-lg font-semibold transition-colors">
            Upload a contract
          </Link>
        </div>
      )}

      {/* Table */}
      {!loading && analyses.length > 0 && (
        <>
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-100">
                <tr>
                  <th className="text-left px-5 py-3 font-semibold text-gray-600">Filename</th>
                  <th className="text-left px-5 py-3 font-semibold text-gray-600">Status</th>
                  <th className="text-left px-5 py-3 font-semibold text-gray-600">Risk</th>
                  <th className="text-left px-5 py-3 font-semibold text-gray-600">Date</th>
                  <th className="px-5 py-3" />
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {analyses.map((a) => (
                  <tr
                    key={a.id}
                    className="hover:bg-gray-50 transition-colors cursor-pointer"
                    onClick={() => a.status === 'completed' && navigate(`/analysis/${a.id}`)}
                  >
                    <td className="px-5 py-4 font-medium text-gray-900 max-w-xs truncate">
                      📄 {a.filename}
                    </td>
                    <td className="px-5 py-4">
                      <StatusBadge status={a.status} />
                    </td>
                    <td className="px-5 py-4">
                      {a.overall_risk_level ? (
                        <RiskScore level={a.overall_risk_level} score={a.overall_risk_score ?? 0} />
                      ) : (
                        <span className="text-gray-400 text-xs">—</span>
                      )}
                    </td>
                    <td className="px-5 py-4 text-gray-500">
                      {new Date(a.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-5 py-4 text-right">
                      <button
                        onClick={(e) => { e.stopPropagation(); handleDelete(a.id) }}
                        className="text-gray-400 hover:text-red-500 transition-colors text-xs"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex justify-center gap-2 mt-6">
              <button
                onClick={() => setPage((p) => Math.max(p - 1, 1))}
                disabled={page === 1}
                className="px-4 py-2 text-sm rounded-lg border border-gray-200 disabled:opacity-40 hover:bg-gray-50 transition-colors"
              >
                ← Previous
              </button>
              <span className="px-4 py-2 text-sm text-gray-600">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(p + 1, totalPages))}
                disabled={page === totalPages}
                className="px-4 py-2 text-sm rounded-lg border border-gray-200 disabled:opacity-40 hover:bg-gray-50 transition-colors"
              >
                Next →
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
