import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Logo from '../components/layout/Logo'

const SLIDES = [
  {
    title: 'Estudo Inteligente',
    desc: 'Cronogramas gerados por IA baseados no seu desempenho real.',
  },
  {
    title: 'Diagnóstico Preciso',
    desc: 'Identifique suas fraquezas antes mesmo de começar a prova.',
  },
  {
    title: 'Gestão de Tempo',
    desc: 'Maximize cada hora de estudo com nossa trilha otimizada.',
  },
]

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()

  const [email, setEmail]     = useState('')
  const [senha, setSenha]     = useState('')
  const [error, setError]     = useState('')
  const [loading, setLoading] = useState(false)
  const [slide, setSlide]     = useState(0)

  useEffect(() => {
    const t = setInterval(() => setSlide((s) => (s + 1) % SLIDES.length), 5000)
    return () => clearInterval(t)
  }, [])

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const user = await login(email, senha)
      navigate(user.area ? '/' : '/onboarding')
    } catch (err) {
      setError(err.response?.data?.detail || 'Credenciais inválidas')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-brand-bg flex flex-col md:flex-row overflow-hidden">

      {/* Painel esquerdo */}
      <div className="hidden md:flex md:w-1/2 lg:w-3/5 bg-brand-surface relative p-12 flex-col justify-between border-r border-brand-border overflow-hidden">
        <div className="absolute top-[-10%] right-[-10%] w-[500px] h-[500px] bg-brand-primary/5 blur-[120px] rounded-full pointer-events-none" />
        <div className="absolute bottom-[-10%] left-[-10%] w-[400px] h-[400px] bg-brand-secondary/5 blur-[120px] rounded-full pointer-events-none" />

        <Logo className="h-10 relative z-10" />

        <div className="relative z-10 max-w-xl">
          <div className="w-full aspect-video bg-brand-bg/60 rounded-2xl border border-brand-border flex items-center justify-center mb-8 shadow-2xl">
            <span className="text-brand-muted text-sm">Preview do Sistema</span>
          </div>

          <div className="space-y-2 min-h-[72px]">
            <h2 className="text-3xl font-bold text-brand-text transition-all duration-500">
              {SLIDES[slide].title}
            </h2>
            <p className="text-lg text-brand-muted transition-all duration-500">
              {SLIDES[slide].desc}
            </p>
          </div>

          <div className="flex gap-2 mt-6">
            {SLIDES.map((_, i) => (
              <button
                key={i}
                onClick={() => setSlide(i)}
                className={`h-1.5 rounded-full transition-all duration-300 ${
                  slide === i
                    ? 'w-8 bg-brand-primary'
                    : 'w-2 bg-brand-border hover:bg-brand-muted'
                }`}
              />
            ))}
          </div>
        </div>

        <p className="text-xs text-brand-muted relative z-10">
          © 2026 Skolai — Todos os direitos reservados
        </p>
      </div>

      {/* Painel direito — formulário */}
      <div className="flex-1 flex flex-col items-center justify-center p-6 md:p-12 lg:p-24">
        <div className="w-full max-w-sm space-y-8">

          <div className="md:hidden flex justify-center">
            <Logo className="h-10" />
          </div>

          <div className="space-y-1">
            <h1 className="text-3xl font-bold text-brand-text tracking-tight">Entrar</h1>
            <p className="text-brand-muted">Bem-vindo de volta! Digite seus dados.</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-brand-muted mb-1.5">E-mail</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="exemplo@email.com"
                className="w-full bg-brand-surface border border-brand-border text-brand-text rounded-xl px-4 py-3.5 outline-none transition-all placeholder:text-brand-muted/40 focus:border-brand-primary focus:ring-1 focus:ring-brand-primary"
              />
            </div>

            <div>
              <div className="flex justify-between items-center mb-1.5">
                <label className="block text-sm font-medium text-brand-muted">Senha</label>
                <a href="#" className="text-xs text-brand-primary hover:underline" onClick={(e) => e.preventDefault()}>
                  Esqueceu a senha?
                </a>
              </div>
              <input
                type="password"
                value={senha}
                onChange={(e) => setSenha(e.target.value)}
                required
                placeholder="••••••••"
                className="w-full bg-brand-surface border border-brand-border text-brand-text rounded-xl px-4 py-3.5 outline-none transition-all placeholder:text-brand-muted/40 focus:border-brand-primary focus:ring-1 focus:ring-brand-primary"
              />
            </div>

            {error && (
              <div className="bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3 text-red-400 text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-brand-primary to-brand-secondary text-white font-bold py-4 rounded-xl shadow-lg shadow-brand-primary/20 hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="w-4 h-4 rounded-full border-2 border-white/30 border-t-white animate-spin" />
                  Entrando...
                </span>
              ) : (
                'Acessar Plataforma'
              )}
            </button>
          </form>

          <p className="text-center text-sm text-brand-muted">
            Ainda não tem uma conta?{' '}
            <a href="#" className="text-brand-primary font-semibold hover:underline">
              Solicite acesso
            </a>
          </p>
        </div>
      </div>
    </div>
  )
}
