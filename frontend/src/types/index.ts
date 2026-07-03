export interface User {
  id: number
  email: string
  full_name: string
  role: 'admin' | 'recruiter' | 'viewer'
  is_active: boolean
  created_at: string
}

export interface Candidate {
  id: number
  name: string
  email: string
  phone?: string
  years_of_experience: number
  skills: string[]
  education?: string
  linkedin_url?: string
  resume_text?: string
  created_at: string
  updated_at: string
}

export interface Job {
  id: number
  title: string
  description: string
  department?: string
  required_skills: string[]
  preferred_skills: string[]
  min_experience_years: number
  max_experience_years?: number
  status: 'draft' | 'active' | 'closed'
  created_at: string
  updated_at: string
}

export interface ScoreBreakdown {
  total_score: number
  required_skills_score: number
  preferred_skills_score: number
  experience_score: number
  keyword_score: number
  matched_required_skills: string[]
  matched_preferred_skills: string[]
  missing_required_skills: string[]
}

export interface Application {
  id: number
  candidate_id: number
  job_id: number
  status: 'pending' | 'reviewed' | 'shortlisted' | 'rejected' | 'hired'
  match_score: number
  score_breakdown: ScoreBreakdown
  notes?: string
  candidate?: Candidate
  job?: Job
  created_at: string
  updated_at: string
}

export interface CandidateListResponse {
  total: number
  page: number
  page_size: number
  candidates: Candidate[]
}

export interface JobListResponse {
  total: number
  page: number
  page_size: number
  jobs: Job[]
}

export interface ApplicationListResponse {
  total: number
  page: number
  page_size: number
  applications: Application[]
}

export interface TokenResponse {
  access_token: string
  token_type: string
}
