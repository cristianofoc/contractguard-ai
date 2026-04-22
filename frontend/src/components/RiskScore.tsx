/**
 * RiskScore component: displays the overall risk level as a colour-coded badge.
 * Also shows the numeric score as a percentage.
 */

interface RiskScoreProps {
  level: 'low' | 'medium' | 'high'
  score: number // 0.0 – 1.0
  size?: 'sm' | 'lg'
}

const LEVEL_CONFIG = {
  low: {
    bg: 'bg-green-100',
    text: 'text-green-800',
    border: 'border-green-300',
    label: 'Low Risk',
    icon: '✅',
  },
  medium: {
    bg: 'bg-yellow-100',
    text: 'text-yellow-800',
    border: 'border-yellow-300',
    label: 'Medium Risk',
    icon: '⚠️',
  },
  high: {
    bg: 'bg-red-100',
    text: 'text-red-800',
    border: 'border-red-300',
    label: 'High Risk',
    icon: '🚨',
  },
}

export default function RiskScore({ level, score, size = 'sm' }: RiskScoreProps) {
  const config = LEVEL_CONFIG[level]
  const percentage = Math.round(score * 100)

  if (size === 'lg') {
    return (
      <div
        className={`inline-flex flex-col items-center gap-2 px-8 py-6 rounded-2xl border-2 ${config.bg} ${config.border}`}
      >
        <span className="text-4xl">{config.icon}</span>
        <span className={`text-2xl font-bold ${config.text}`}>{config.label}</span>
        <span className={`text-lg font-semibold ${config.text} opacity-75`}>
          Risk Score: {percentage}%
        </span>
      </div>
    )
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-semibold border ${config.bg} ${config.text} ${config.border}`}
    >
      <span>{config.icon}</span>
      {config.label}
    </span>
  )
}
