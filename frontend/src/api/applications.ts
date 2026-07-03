import client from './client'
import type { Application, ApplicationListResponse } from '../types'

export const getRankedCandidates = async (
  jobId: number,
  minScore = 0,
  page = 1,
  pageSize = 50
): Promise<ApplicationListResponse> => {
  const { data } = await client.get<ApplicationListResponse>(`/applications/job/${jobId}`, {
    params: { min_score: minScore, page, page_size: pageSize },
  })
  return data
}

export const createApplication = async (candidateId: number, jobId: number): Promise<Application> => {
  const { data } = await client.post<Application>('/applications/', {
    candidate_id: candidateId,
    job_id: jobId,
  })
  return data
}

export const updateApplicationStatus = async (
  id: number,
  status: Application['status']
): Promise<Application> => {
  const { data } = await client.patch<Application>(`/applications/${id}`, { status })
  return data
}

export const bulkScore = async (jobId: number): Promise<void> => {
  await client.post('/applications/bulk-score', { job_id: jobId })
}
