interface ScoreBarProps {
  score: number
  label?: string
  showValue?: boolean
}

function scoreColor(score: number) {
  if (score >= 75) return { bar: 'bg-green-500', text: 'text-green-700', bg: 'bg-green-50' }
  if (score >= 50) return { bar: 'bg-yellow-400', text: 'text-yellow-700', bg: 'bg-yellow-50' }
  return { bar: 'bg-red-400', text: 'text-red-700', bg: 'bg-red-50' }
}

export default function ScoreBar({ score, label, showValue = true }: ScoreBarProps) {
  const { bar, text, bg } = scoreColor(score)

  return (
    <div className="w-full">
      {label && <p className="text-xs text-slate-500 mb-1">{label}</p>}
      <div className="flex items-center gap-2">
        <div className="flex-1 bg-slate-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all duration-500 ${bar}`}
            style={{ width: `${Math.min(score, 100)}%` }}
          />
        </div>
        {showValue && (
          <span className={`text-xs font-semibold px-1.5 py-0.5 rounded ${bg} ${text} min-w-[42px] text-right`}>
            {score.toFixed(0)}%
          </span>
        )}
      </div>
    </div>
  )
}
