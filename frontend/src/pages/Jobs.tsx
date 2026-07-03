import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, ChevronRight, Briefcase, Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { getJobs, createJob, deleteJob } from '../api/jobs'
import Modal from '../components/Modal'
import SkillTag from '../components/SkillTag'
import type { Job } from '../types'
import { useAuth } from '../context/AuthContext'

const STATUS_COLORS: Record<Job['status'], string> = {
  active: 'bg-green-100 text-green-700',
  draft: 'bg-slate-100 text-slate-600',
  closed: 'bg-red-100 text-red-600',
}

function JobForm({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient()
  const [form, setForm] = useState({
    title: '', description: '', department: '',
    required_skills: '', preferred_skills: '',
    min_experience_years: 0, max_experience_years: '',
    status: 'active',
  })
  const [error, setError] = useState('')

  const mutation = useMutation({
    mutationFn: () => createJob({
      title: form.title,
      description: form.description,
      department: form.department || undefined,
      required_skills: form.required_skills.split(',').map((s) => s.trim()).filter(Boolean),
      preferred_skills: form.preferred_skills.split(',').map((s) => s.trim()).filter(Boolean),
      min_experience_years: Number(form.min_experience_years),
      max_experience_years: form.max_experience_years ? Number(form.max_experience_years) : undefined,
      status: form.status,
    }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['jobs'] }); toast.success('Job created!'); onClose() },
    onError: () => { setError('Failed to create job. Check all fields.'); toast.error('Failed to create job') },
  })

  const set = (f: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) =>
    setForm((p) => ({ ...p, [f]: e.target.value }))

  return (
    <form onSubmit={(e) => { e.preventDefault(); mutation.mutate() }} className="space-y-4">
      {error && <p className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg">{error}</p>}

      <div className="grid grid-cols-2 gap-3">
        <div className="col-span-2">
          <label className="block text-sm font-medium text-slate-700 mb-1">Job Title *</label>
          <input required value={form.title} onChange={set('title')} placeholder="Python Backend Developer"
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Department</label>
          <input value={form.department} onChange={set('department')} placeholder="Engineering"
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Status</label>
          <select value={form.status} onChange={set('status')}
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="active">Active</option>
            <option value="draft">Draft</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Min Experience (yrs)</label>
          <input type="number" min={0} value={form.min_experience_years} onChange={set('min_experience_years')}
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Max Experience (yrs)</label>
          <input type="number" min={0} value={form.max_experience_years} onChange={set('max_experience_years')} placeholder="optional"
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div className="col-span-2">
          <label className="block text-sm font-medium text-slate-700 mb-1">Required Skills (comma-separated) *</label>
          <input required value={form.required_skills} onChange={set('required_skills')} placeholder="python, fastapi, sqlalchemy"
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div className="col-span-2">
          <label className="block text-sm font-medium text-slate-700 mb-1">Preferred Skills (comma-separated)</label>
          <input value={form.preferred_skills} onChange={set('preferred_skills')} placeholder="oracle, docker, redis"
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div className="col-span-2">
          <label className="block text-sm font-medium text-slate-700 mb-1">Description *</label>
          <textarea required rows={4} value={form.description} onChange={set('description')} placeholder="Describe the role..."
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none" />
        </div>
      </div>

      <div className="flex justify-end gap-2 pt-2">
        <button type="button" onClick={onClose} className="px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 rounded-lg">Cancel</button>
        <button type="submit" disabled={mutation.isPending}
          className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-60">
          {mutation.isPending ? 'Creating…' : 'Create Job'}
        </button>
      </div>
    </form>
  )
}

export default function Jobs() {
  const { user } = useAuth()
  const qc = useQueryClient()
  const [showCreate, setShowCreate] = useState(false)

  const { data, isLoading } = useQuery({
    queryKey: ['jobs'],
    queryFn: () => getJobs(1, 100),
  })

  const deleteMutation = useMutation({
    mutationFn: deleteJob,
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['jobs'] }); toast.success('Job deleted') },
    onError: () => toast.error('Failed to delete job'),
  })

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Job Postings</h1>
          <p className="text-slate-500 text-sm mt-1">{data?.total ?? 0} jobs total</p>
        </div>
        <button onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors">
          <Plus size={16} /> New Job
        </button>
      </div>

      {isLoading ? (
        <div className="text-slate-400 text-sm">Loading…</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {data?.jobs.map((job) => (
            <div key={job.id} className="bg-white rounded-xl shadow-sm border border-slate-100 p-5 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-3">
                <div className="p-2 bg-blue-50 rounded-lg"><Briefcase size={18} className="text-blue-600" /></div>
                <span className={`text-xs font-semibold px-2.5 py-0.5 rounded-full capitalize ${STATUS_COLORS[job.status]}`}>
                  {job.status}
                </span>
              </div>
              <h3 className="font-semibold text-slate-800 mb-1">{job.title}</h3>
              <p className="text-xs text-slate-400 mb-3">{job.department ?? 'No department'} · {job.min_experience_years}+ yrs</p>
              <div className="flex flex-wrap gap-1 mb-4">
                {job.required_skills.slice(0, 4).map((s) => <SkillTag key={s} skill={s} />)}
                {job.required_skills.length > 4 && (
                  <span className="text-xs text-slate-400">+{job.required_skills.length - 4} more</span>
                )}
              </div>
              <div className="flex items-center justify-between pt-3 border-t border-slate-100">
                <Link to={`/jobs/${job.id}/rankings`}
                  className="flex items-center gap-1 text-sm text-blue-600 font-medium hover:underline">
                  View Rankings <ChevronRight size={14} />
                </Link>
                {user?.role === 'admin' && (
                  <button onClick={() => deleteMutation.mutate(job.id)}
                    className="text-slate-300 hover:text-red-500 transition-colors">
                    <Trash2 size={15} />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {showCreate && <Modal title="Create Job Posting" onClose={() => setShowCreate(false)}><JobForm onClose={() => setShowCreate(false)} /></Modal>}
    </div>
  )
}
