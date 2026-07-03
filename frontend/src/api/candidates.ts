import client from './client'
import type { Candidate, CandidateListResponse } from '../types'

export const getCandidates = async (
  page = 1,
  pageSize = 20,
  skills?: string[],
  minExperience?: number
): Promise<CandidateListResponse> => {
  const params: Record<string, unknown> = { page, page_size: pageSize }
  if (skills?.length) params.skills = skills
  if (minExperience !== undefined) params.min_experience = minExperience
  const { data } = await client.get<CandidateListResponse>('/candidates/', { params })
  return data
}

export const getCandidate = async (id: number): Promise<Candidate> => {
  const { data } = await client.get<Candidate>(`/candidates/${id}`)
  return data
}

export const createCandidate = async (payload: {
  name: string
  email: string
  phone?: string
  years_of_experience: number
  skills: string[]
  education?: string
  resume_text?: string
  linkedin_url?: string
}): Promise<Candidate> => {
  const { data } = await client.post<Candidate>('/candidates/', payload)
  return data
}

export const updateCandidate = async (id: number, payload: Partial<Candidate>): Promise<Candidate> => {
  const { data } = await client.put<Candidate>(`/candidates/${id}`, payload)
  return data
}

export const deleteCandidate = async (id: number): Promise<void> => {
  await client.delete(`/candidates/${id}`)
}
