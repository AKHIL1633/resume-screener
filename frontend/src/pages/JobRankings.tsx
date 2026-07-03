import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, Zap, ChevronDown, ChevronUp } from 'lucide-react'
import toast from 'react-hot-toast'
import { getJob } from '../api/jobs'
import { getRankedCandidates, updateApplicationStatus, bulkScore } from '../api/applications'
import ScoreBar from '../components/ScoreBar'
import SkillTag from '../components/SkillTag'
import StatusBadge from '../components/StatusBadge'
import type { Application } from '../types'

function ScoreBreakdownRow({ app }: { app: Application }) {
  const [open, setOpen] = useState(false)
  const bd = app.score_breakdown

  return (
    <>
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-1 text-xs text-slate-400 hover:text-blue-600 mt-1"
      >
        Score breakdown {open ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
      </button>
      {open && (
        <div className="mt-2 space-y-1.5 bg-slate-50 rounded-lg p-3">
          <ScoreBar score={bd.required_skills_score} label="Required skills" />
          <ScoreBar score={bd.experience_score} label="Experience" />
          <ScoreBar score={bd.preferred_skills_score} label="Preferred skills" />
          <ScoreBar score={bd.keyword_score} label="Keyword match" />
          {bd.missing_required_skills.length > 0 && (
            <div className="pt-1">
              <p className="text-xs text-slate-500 mb-1">Missing required skills:</p>
              <div className="flex flex-wrap gap-1">
                {bd.missing_required_skills.map((s) => <SkillTag key={s} skill={s} variant="missing" />)}
              </div>
            </div>
          )}
          {bd.matched_preferred_skills.length > 0 && (
            <div>
              <p className="text-xs text-slate-500 mb-1">Matched preferred:</p>
              <div className="flex flex-wrap gap-1">
                {bd.matched_preferred_skills.map((s) => <SkillTag key={s} skill={s} variant="preferred" />)}
              </div>
            </div>
          )}
        </div>
      )}
    </>
  )
}

export default function JobRankings() {
  const { jobId } = useParams<{ jobId: string }>()
  const id = Number(jobId)
  const qc = useQueryClient()
  const [minScore, setMinScore] = useState(0)

  const { data: job } = useQuery({ queryKey: ['job', id], queryFn: () => getJob(id) })
  const { data, isLoading } = useQuery({
    queryKey: ['rankings', id, minScore],
    queryFn: () => getRankedCandidates(id, minScore),
  })

  const statusMutation = useMutation({
    mutationFn: ({ appId, status }: { appId: number; status: Application['status'] }) =>
      updateApplicationStatus(appId, status),
    onSuccess: (_, { status }) => { qc.invalidateQueries({ queryKey: ['rankings', id] }); toast.success(`Status updated to ${status}`) },
    onError: () => toast.error('Failed to update status'),
  })

  const bulkMutation = useMutation({
    mutationFn: () => bulkScore(id),
    onSuccess: () => { toast.success('Re-scoring started in background'); setTimeout(() => qc.invalidateQueries({ queryKey: ['rankings', id] }), 1500) },
    onError: () => toast.error('Failed to trigger re-score'),
  })

  return (
    <div>
      <Link to="/jobs" className="flex items-center gap-1 text-sm text-slate-500 hover:text-slate-700 mb-6">
        <ArrowLeft size={16} /> Back to Jobs
      </Link>

      {/* Job header */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-6 mb-6">
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
          <div>
            <h1 className="text-xl font-bold text-slate-800">{job?.title}</h1>
            <p className="text-sm text-slate-500 mt-1">
              {job?.department} · {job?.min_experience_years}+ yrs experience
            </p>
            <div className="flex flex-wrap gap-1 mt-3">
              {job?.required_skills.map((s) => <SkillTag key={s} skill={s} variant="matched" />)}
              {job?.preferred_skills.map((s) => <SkillTag key={s} skill={s} variant="preferred" />)}
            </div>
          </div>
          <button
            onClick={() => bulkMutation.mutate()}
            disabled={bulkMutation.isPending}
            className="flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-60 whitespace-nowrap"
          >
            <Zap size={15} />
            {bulkMutation.isPending ? 'Scoring…' : 'Bulk Score All'}
          </button>
        </div>
      </div>

      {/* Filter */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-4 mb-4 flex items-center gap-4">
        <label className="text-sm font-medium text-slate-700 whitespace-nowrap">
          Min Score: <span className="text-blue-600 font-bold">{minScore}%</span>
        </label>
        <input
          type="range" min={0} max={90} step={5} value={minScore}
          onChange={(e) => setMinScore(Number(e.target.value))}
          className="flex-1 accent-blue-600"
        />
        <span className="text-sm text-slate-500 whitespace-nowrap">{data?.total ?? 0} candidates</span>
      </div>

      {/* Rankings table */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-slate-400 text-sm">Loading rankings…</div>
        ) : data?.applications.length === 0 ? (
          <div className="p-8 text-center">
            <p className="text-slate-400 text-sm">No applications found.</p>
            <p className="text-slate-400 text-xs mt-1">Use "Bulk Score All" to auto-score every candidate.</p>
          </div>
        ) : (
          <table className="w-full">
            <thead className="bg-slate-50 border-b border-slate-100">
              <tr>
                {['Rank', 'Candidate', 'Skills', 'Exp', 'Match Score', 'Status', 'Action'].map((h) => (
                  <th key={h} className="text-left text-xs font-semibold text-slate-500 px-4 py-3">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {data?.applications.map((app, idx) => (
                <tr key={app.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-4 py-4">
                    <span className={`font-bold text-sm ${idx === 0 ? 'text-yellow-500' : idx === 1 ? 'text-slate-400' : idx === 2 ? 'text-amber-600' : 'text-slate-300'}`}>
                      #{idx + 1}
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    <p className="text-sm font-medium text-slate-800">{app.candidate?.name}</p>
                    <p className="text-xs text-slate-400">{app.candidate?.email}</p>
                  </td>
                  <td className="px-4 py-4">
                    <div className="flex flex-wrap gap-1 max-w-[180px]">
                      {app.candidate?.skills.slice(0, 3).map((s) => <SkillTag key={s} skill={s} />)}
                      {(app.candidate?.skills.length ?? 0) > 3 && (
                        <span className="text-xs text-slate-400">+{(app.candidate?.skills.length ?? 0) - 3}</span>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-4 text-sm text-slate-600 whitespace-nowrap">
                    {app.candidate?.years_of_experience} yrs
                  </td>
                  <td className="px-4 py-4 w-48">
                    <ScoreBar score={app.match_score} />
                    <ScoreBreakdownRow app={app} />
                  </td>
                  <td className="px-4 py-4"><StatusBadge status={app.status} /></td>
                  <td className="px-4 py-4">
                    <div className="flex flex-col gap-1">
                      {app.status !== 'shortlisted' && app.status !== 'hired' && (
                        <button
                          onClick={() => statusMutation.mutate({ appId: app.id, status: 'shortlisted' })}
                          className="text-xs bg-green-50 text-green-700 hover:bg-green-100 px-2 py-1 rounded font-medium transition-colors"
                        >Shortlist</button>
                      )}
                      {app.status !== 'rejected' && app.status !== 'hired' && (
                        <button
                          onClick={() => statusMutation.mutate({ appId: app.id, status: 'rejected' })}
                          className="text-xs bg-red-50 text-red-600 hover:bg-red-100 px-2 py-1 rounded font-medium transition-colors"
                        >Reject</button>
                      )}
                      {app.status === 'shortlisted' && (
                        <button
                          onClick={() => statusMutation.mutate({ appId: app.id, status: 'hired' })}
                          className="text-xs bg-purple-50 text-purple-700 hover:bg-purple-100 px-2 py-1 rounded font-medium transition-colors"
                        >Hire</button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
