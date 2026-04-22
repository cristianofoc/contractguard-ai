/**
 * ClauseCard component: displays a single contract clause analysis.
 * Shows the title, risk badge, plain-English explanation, red flags, and recommendation.
 */

import type { ClauseAnalysis } from '../services/api'
import RiskScore from './RiskScore'

interface ClauseCardProps {
  clause: ClauseAnalysis
  index: number
}

export default function ClauseCard({ clause, index }: ClauseCardProps) {
  const borderColor =
    clause.risk_level === 'high'
      ? 'border-red-300'
      : clause.risk_level === 'medium'
        ? 'border-yellow-300'
        : 'border-green-300'

  return (
    <div className={`bg-white rounded-xl border-l-4 ${borderColor} shadow-sm p-5 space-y-3`}>
      {/* Header row */}
      <div className="flex items-start justify-between gap-3">
        <h3 className="font-semibold text-gray-900 text-base">
          <span className="text-gray-400 mr-2 text-sm">#{index}</span>
          {clause.title}
        </h3>
        <RiskScore level={clause.risk_level} score={clause.risk_score} />
      </div>

      {/* Plain-English explanation */}
      <p className="text-gray-700 text-sm leading-relaxed">{clause.plain_english}</p>

      {/* Red flags */}
      {clause.red_flags.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-red-600 uppercase tracking-wide mb-1.5">
            ⚠ Red Flags
          </p>
          <ul className="space-y-1">
            {clause.red_flags.map((flag, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-red-700">
                <span className="mt-0.5 text-red-400">•</span>
                {flag}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Recommendation */}
      {clause.recommendation && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg px-4 py-3">
          <p className="text-xs font-semibold text-blue-600 uppercase tracking-wide mb-1">
            💡 Recommendation
          </p>
          <p className="text-sm text-blue-800">{clause.recommendation}</p>
        </div>
      )}

      {/* Original text — collapsed by default */}
      <details className="group">
        <summary className="cursor-pointer text-xs text-gray-400 hover:text-gray-600 select-none">
          View original clause text ▸
        </summary>
        <pre className="mt-2 text-xs text-gray-600 bg-gray-50 rounded p-3 overflow-auto whitespace-pre-wrap max-h-48 font-mono leading-relaxed">
          {clause.original_text}
        </pre>
      </details>
    </div>
  )
}
