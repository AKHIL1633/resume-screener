import client from './client'
import type { Job, JobListResponse } from '../types'

export const getJobs = async (page = 1, pageSize = 20): Promise<JobListResponse> => {
  const { data } = await client.get<JobListResponse>('/jobs/', { params: { page, page_size: pageSize } })
  return data
}

export const getActiveJobs = async (): Promise<Job[]> => {
  const { data } = await client.get<Job[]>('/jobs/active')
  return data
}

export const getJob = async (id: number): Promise<Job> => {
  const { data } = await client.get<Job>(`/jobs/${id}`)
  return data
}

export const createJob = async (payload: {
  title: string
  description: string
  department?: string
  required_skills: string[]
  preferred_skills: string[]
  min_experience_years: number
  max_experience_years?: number
  status?: string
}): Promise<Job> => {
  const { data } = await client.post<Job>('/jobs/', payload)
  return data
}

export const updateJob = async (id: number, payload: Partial<Job>): Promise<Job> => {
  const { data } = await client.put<Job>(`/jobs/${id}`, payload)
  return data
}

export const deleteJob = async (id: number): Promise<void> => {
  await client.delete(`/jobs/${id}`)
}
