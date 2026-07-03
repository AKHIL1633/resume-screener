import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Briefcase, Users, FileText, TrendingUp, ChevronRight } from 'lucide-react'
import StatCard from '../components/StatCard'
import ScoreBar from '../components/ScoreBar'
import StatusBadge from '../components/StatusBadge'
import { getCandidates } from '../api/candidates'
import { getJobs } from '../api/jobs'
import { getRankedCandidates } from '../api/applications'
import type { Application, Job } from '../types'

export default function Dashboard() {
  const [stats, setStats] = useState({ candidates: 0, jobs: 0, applications: 0, avgScore: 0 })
  const [activeJobs, setActiveJobs] = useState<Job[]>([])
  const [recentApps, setRecentApps] = useState<Application[]>([])

  useEffect(() => {
    Promise.all([getCandidates(1, 1), getJobs(1, 100)]).then(async ([cRes, jRes]) => {
      const jobs = jRes.jobs.filter((j) => j.status === 'active')
      setActiveJobs(jobs.slice(0, 4))

      let totalApps = 0
      let totalScore = 0
      const latest: Application[] = []

      await Promise.all(
        jobs.slice(0, 3).map(async (job) => {
          const res = await getRankedCandidates(job.id, 0, 1, 5)
          totalApps += res.total
          res.applications.forEach((a) => { totalScore += a.match_score })
          latest.push(...res.applications)
        })
      )

      setStats({
        candidates: cRes.total,
        jobs: jRes.total,
        applications: totalApps,
        avgScore: latest.length ? Math.round(totalScore / latest.length) : 0,
      })
      setRecentApps(latest.slice(0, 5))
    })
  }, [])

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-800">Dashboard</h1>
        <p className="text-slate-500 text-sm mt-1">Overview of your hiring pipeline</p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 mb-8">
        <StatCard label="Total Candidates" value={stats.candidates} icon={Users} color="bg-blue-500" />
        <StatCard label="Job Postings" value={stats.jobs} icon={Briefcase} color="bg-indigo-500" />
        <StatCard label="Applications" value={stats.applications} icon={FileText} color="bg-violet-500" />
        <StatCard label="Avg Match Score" value={`${stats.avgScore}%`} icon={TrendingUp} color="bg-emerald-500" />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* Active jobs */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-slate-800">Active Jobs</h2>
            <Link to="/jobs" className="text-xs text-blue-600 hover:underline flex items-center gap-1">
              View all <ChevronRight size={12} />
            </Link>
          </div>
          {activeJobs.length === 0 ? (
            <p className="text-sm text-slate-400 py-4 text-center">No active jobs yet.</p>
          ) : (
            <ul className="space-y-3">
              {activeJobs.map((job) => (
                <li key={job.id}>
                  <Link
                    to={`/jobs/${job.id}/rankings`}
                    className="flex items-center justify-between p-3 rounded-lg hover:bg-slate-50 transition-colors"
                  >
                    <div>
                      <p className="text-sm font-medium text-slate-700">{job.title}</p>
                      <p className="text-xs text-slate-400">{job.department ?? 'No department'}</p>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-slate-400">
                      <span className="bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-medium">Active</span>
                      <ChevronRight size={14} />
                    </div>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Recent applications */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-5">
          <h2 className="font-semibold text-slate-800 mb-4">Recent Applications</h2>
          {recentApps.length === 0 ? (
            <p className="text-sm text-slate-400 py-4 text-center">No applications yet.</p>
          ) : (
            <ul className="space-y-3">
              {recentApps.map((app) => (
                <li key={app.id} className="flex items-center gap-3">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-slate-700 truncate">
                      {app.candidate?.name ?? `Candidate #${app.candidate_id}`}
                    </p>
                    <p className="text-xs text-slate-400 truncate">
                      {app.job?.title ?? `Job #${app.job_id}`}
                    </p>
                  </div>
                  <div className="w-24">
                    <ScoreBar score={app.match_score} />
                  </div>
                  <StatusBadge status={app.status} />
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  )
}
