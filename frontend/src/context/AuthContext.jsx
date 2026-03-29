import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { getMe, login as apiLogin } from '../api/auth'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(() => sessionStorage.getItem('token'))
  const [loading, setLoading] = useState(true)

  function _saveTokens(accessToken, refreshToken) {
    sessionStorage.setItem('token', accessToken)
    if (refreshToken) sessionStorage.setItem('refresh_token', refreshToken)
    setToken(accessToken)
  }

  useEffect(() => {
    if (!token) {
      setLoading(false)
      return
    }
    setLoading(true)
    getMe()
      .then(setUser)
      .catch(() => {
        sessionStorage.removeItem('token')
        sessionStorage.removeItem('refresh_token')
        setToken(null)
      })
      .finally(() => setLoading(false))
  }, [token])

  const login = useCallback(async (email, senha) => {
    const data = await apiLogin(email, senha)
    _saveTokens(data.access_token, data.refresh_token)
    const me = await getMe()
    setUser(me)
    return me
  }, []) // eslint-disable-line

  const logout = useCallback(() => {
    sessionStorage.removeItem('token')
    sessionStorage.removeItem('refresh_token')
    setToken(null)
    setUser(null)
  }, [])

  const refreshUser = useCallback(async () => {
    const me = await getMe()
    setUser(me)
    return me
  }, [])

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
