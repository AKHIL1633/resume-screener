import client from './client'
import type { TokenResponse, User } from '../types'

export const login = async (email: string, password: string): Promise<TokenResponse> => {
  const { data } = await client.post<TokenResponse>('/auth/login', { email, password })
  return data
}

export const register = async (
  email: string,
  full_name: string,
  password: string,
  role = 'recruiter'
): Promise<User> => {
  const { data } = await client.post<User>('/auth/register', { email, full_name, password, role })
  return data
}

export const getMe = async (): Promise<User> => {
  const { data } = await client.get<User>('/auth/me')
  return data
}

export const refreshToken = async (refresh_token: string): Promise<TokenResponse> => {
  const { data } = await client.post<TokenResponse>('/auth/refresh', { refresh_token })
  return data
}

export const logoutApi = async (refresh_token: string): Promise<void> => {
  await client.post('/auth/logout', { refresh_token })
}
