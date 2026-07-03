import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import { getMe, login as apiLogin, logoutApi } from '../api/auth'
import type { User } from '../types'

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) { setLoading(false); return }
    getMe()
      .then(setUser)
      .catch(() => {
        localStorage.removeItem('token')
        localStorage.removeItem('refresh_token')
      })
      .finally(() => setLoading(false))
  }, [])

  const login = async (email: string, password: string) => {
    const { access_token, refresh_token } = await apiLogin(email, password)
    localStorage.setItem('token', access_token)
    localStorage.setItem('refresh_token', refresh_token)
    const me = await getMe()
    setUser(me)
  }

  const logout = () => {
    const rt = localStorage.getItem('refresh_token')
    if (rt) logoutApi(rt).catch(() => {})  // fire-and-forget; revoke on server
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
