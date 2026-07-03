import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Search, Trash2, ExternalLink } from 'lucide-react'
import { getCandidates, createCandidate, deleteCandidate } from '../api/candidates'
import Modal from '../components/Modal'
import SkillTag from '../components/SkillTag'
import { useAuth } from '../context/AuthContext'

function AddCandidateForm({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient()
  const [form, setForm] = useState({
    name: '', email: '', phone: '',
    years_of_experience: 0,
    skills: '', education: '',
    resume_text: '', linkedin_url: '',
  })
  const [error, setError] = useState('')

  const mutation = useMutation({
    mutationFn: () => createCandidate({
      name: form.name,
      email: form.email,
      phone: form.phone || undefined,
      years_of_experience: Number(form.years_of_experience),
      skills: form.skills.split(',').map((s) => s.trim()).filter(Boolean),
      education: form.education || undefined,
      resume_text: form.resume_text || undefined,
      linkedin_url: form.linkedin_url || undefined,
    }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['candidates'] }); onClose() },
    onError: () => setError('Failed to add candidate. Email may already exist.'),
  })

  const set = (f: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
    setForm((p) => ({ ...p, [f]: e.target.value }))

  return (
    <form onSubmit={(e) => { e.preventDefault(); mutation.mutate() }} className="space-y-3">
      {error && <p className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg">{error}</p>}

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Full Name *</label>
          <input required value={form.name} onChange={set('name')} placeholder="Alice Johnson"
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Email *</label>
          <input required type="email" value={form.email} onChange={set('email')} placeholder="alice@dev.com"
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Phone</label>
          <input value={form.phone} onChange={set('phone')} placeholder="+91-9876543210"
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Years of Experience</label>
          <input type="number" min={0} value={form.years_of_experience} onChange={set('years_of_experience')}
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div className="col-span-2">
          <label className="block text-sm font-medium text-slate-700 mb-1">Skills (comma-separated) *</label>
          <input required value={form.skills} onChange={set('skills')} placeholder="python, fastapi, sqlalchemy, docker"
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div className="col-span-2">
          <label className="block text-sm font-medium text-slate-700 mb-1">Education</label>
          <input value={form.education} onChange={set('education')} placeholder="B.Tech Computer Science"
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div className="col-span-2">
          <label className="block text-sm font-medium text-slate-700 mb-1">LinkedIn URL</label>
          <input type="url" value={form.linkedin_url} onChange={set('linkedin_url')} placeholder="https://linkedin.com/in/alice"
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div className="col-span-2">
          <label className="block text-sm font-medium text-slate-700 mb-1">Resume Text</label>
          <textarea rows={5} value={form.resume_text} onChange={set('resume_text')}
            placeholder="Paste the candidate's resume text here for keyword scoring..."
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none" />
        </div>
      </div>

      <div className="flex justify-end gap-2 pt-2">
        <button type="button" onClick={onClose} className="px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 rounded-lg">Cancel</button>
        <button type="submit" disabled={mutation.isPending}
          className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-60">
          {mutation.isPending ? 'Adding…' : 'Add Candidate'}
        </button>
      </div>
    </form>
  )
}

export default function Candidates() {
  const { user } = useAuth()
  const qc = useQueryClient()
  const [showAdd, setShowAdd] = useState(false)
  const [search, setSearch] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['candidates'],
    queryFn: () => getCandidates(1, 100),
  })

  const deleteMutation = useMutation({
    mutationFn: deleteCandidate,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['candidates'] }),
  })

  const filtered = data?.candidates.filter((c) =>
    search === '' ||
    c.name.toLowerCase().includes(search.toLowerCase()) ||
    c.email.toLowerCase().includes(search.toLowerCase()) ||
    c.skills.some((s) => s.includes(search.toLowerCase()))
  ) ?? []

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Candidates</h1>
          <p className="text-slate-500 text-sm mt-1">{data?.total ?? 0} candidates in your pipeline</p>
        </div>
        <button onClick={() => setShowAdd(true)}
          className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700">
          <Plus size={16} /> Add Candidate
        </button>
      </div>

      {/* Search */}
      <div className="relative mb-5">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by name, email or skill…"
          className="w-full border border-slate-300 rounded-lg pl-9 pr-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {isLoading ? (
        <div className="text-slate-400 text-sm">Loading…</div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
          <table className="w-full">
            <thead className="bg-slate-50 border-b border-slate-100">
              <tr>
                {['Candidate', 'Contact', 'Skills', 'Experience', 'Education', ''].map((h) => (
                  <th key={h} className="text-left text-xs font-semibold text-slate-500 px-4 py-3">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {filtered.map((c) => (
                <tr key={c.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-4 py-4">
                    <p className="text-sm font-semibold text-slate-800">{c.name}</p>
                    <p className="text-xs text-slate-400">{c.email}</p>
                  </td>
                  <td className="px-4 py-4 text-xs text-slate-500">{c.phone ?? '—'}</td>
                  <td className="px-4 py-4">
                    <div className="flex flex-wrap gap-1 max-w-[200px]">
                      {c.skills.slice(0, 4).map((s) => <SkillTag key={s} skill={s} />)}
                      {c.skills.length > 4 && <span className="text-xs text-slate-400">+{c.skills.length - 4}</span>}
                    </div>
                  </td>
                  <td className="px-4 py-4 text-sm text-slate-600 whitespace-nowrap">{c.years_of_experience} yrs</td>
                  <td className="px-4 py-4 text-xs text-slate-500 max-w-[160px] truncate">{c.education ?? '—'}</td>
                  <td className="px-4 py-4">
                    <div className="flex items-center gap-2">
                      {c.linkedin_url && (
                        <a href={c.linkedin_url} target="_blank" rel="noopener noreferrer"
                          className="text-slate-300 hover:text-blue-500 transition-colors">
                          <ExternalLink size={15} />
                        </a>
                      )}
                      {user?.role === 'admin' && (
                        <button onClick={() => deleteMutation.mutate(c.id)}
                          className="text-slate-300 hover:text-red-500 transition-colors">
                          <Trash2 size={15} />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {filtered.length === 0 && (
            <p className="text-center text-slate-400 text-sm py-10">
              {search ? 'No candidates match your search.' : 'No candidates yet. Add your first one!'}
            </p>
          )}
        </div>
      )}

      {showAdd && <Modal title="Add Candidate" onClose={() => setShowAdd(false)}><AddCandidateForm onClose={() => setShowAdd(false)} /></Modal>}
    </div>
  )
}
