import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const user = await login(email, senha)
      if (user.role === 'administrador' || user.role === 'mentor') {
        navigate('/')
      } else if (!user.area) {
        navigate('/onboarding')
      } else {
        navigate('/')
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Credenciais inválidas')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-brand-bg flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-10">
          <h1 className="text-4xl font-bold gradient-text tracking-tight">Skolai</h1>
          <p className="text-brand-muted mt-2 text-sm">Sua plataforma de estudos inteligente</p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="bg-brand-card border border-brand-border rounded-2xl p-8 space-y-5"
        >
          <div>
            <label className="block text-sm font-medium text-brand-muted mb-1.5">E-mail</label>
            <input
              type="text"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="seu@email.com"
              className="w-full bg-brand-surface border border-brand-border rounded-lg px-4 py-2.5 text-brand-text placeholder:text-brand-muted focus:outline-none focus:border-indigo-500 transition-all duration-300"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-brand-muted mb-1.5">Senha</label>
            <input
              type="password"
              value={senha}
              onChange={(e) => setSenha(e.target.value)}
              required
              placeholder="••••••••"
              className="w-full bg-brand-surface border border-brand-border rounded-lg px-4 py-2.5 text-brand-text placeholder:text-brand-muted focus:outline-none focus:border-indigo-500 transition-all duration-300"
            />
          </div>

          {error && (
            <p className="text-red-400 text-sm bg-red-400/10 border border-red-400/20 rounded-lg px-3 py-2">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-brand-gradient text-white font-semibold rounded-lg py-3 transition-all duration-300 hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Entrando...' : 'Entrar'}
          </button>
        </form>
      </div>
    </div>
  )
}
