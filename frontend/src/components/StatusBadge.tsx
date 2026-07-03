import type { Application } from '../types'

type Status = Application['status']

const styles: Record<Status, string> = {
  pending:     'bg-slate-100 text-slate-600',
  reviewed:    'bg-blue-100 text-blue-700',
  shortlisted: 'bg-green-100 text-green-700',
  rejected:    'bg-red-100 text-red-600',
  hired:       'bg-purple-100 text-purple-700',
}

export default function StatusBadge({ status }: { status: Status }) {
  return (
    <span className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-semibold capitalize ${styles[status]}`}>
      {status}
    </span>
  )
}
