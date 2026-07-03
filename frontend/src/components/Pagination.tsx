import { ChevronLeft, ChevronRight } from 'lucide-react'

interface PaginationProps {
  page: number
  total: number
  pageSize: number
  onPageChange: (page: number) => void
}

export default function Pagination({ page, total, pageSize, onPageChange }: PaginationProps) {
  const totalPages = Math.ceil(total / pageSize)
  if (totalPages <= 1) return null

  return (
    <div className="flex items-center justify-between mt-4 text-sm text-slate-600">
      <span>
        Showing {(page - 1) * pageSize + 1}–{Math.min(page * pageSize, total)} of {total}
      </span>
      <div className="flex items-center gap-1">
        <button
          onClick={() => onPageChange(page - 1)}
          disabled={page <= 1}
          className="p-1.5 rounded-lg hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <ChevronLeft size={16} />
        </button>
        {Array.from({ length: totalPages }, (_, i) => i + 1)
          .filter((p) => Math.abs(p - page) <= 2 || p === 1 || p === totalPages)
          .reduce<(number | '…')[]>((acc, p, idx, arr) => {
            if (idx > 0 && (arr[idx - 1] as number) + 1 < p) acc.push('…')
            acc.push(p)
            return acc
          }, [])
          .map((p, idx) =>
            p === '…' ? (
              <span key={`ellipsis-${idx}`} className="px-2">…</span>
            ) : (
              <button
                key={p}
                onClick={() => onPageChange(p as number)}
                className={`w-8 h-8 rounded-lg text-sm ${
                  p === page ? 'bg-blue-600 text-white font-medium' : 'hover:bg-slate-100'
                }`}
              >
                {p}
              </button>
            )
          )}
        <button
          onClick={() => onPageChange(page + 1)}
          disabled={page >= totalPages}
          className="p-1.5 rounded-lg hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <ChevronRight size={16} />
        </button>
      </div>
    </div>
  )
}
