import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Logo from '../components/layout/Logo'
import { register } from '../api/auth'

function EyeIcon({ open }) {
  return open ? (
    <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.477 0 8.268 2.943 9.542 7-1.274 4.057-5.065 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
    </svg>
  ) : (
    <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.477 0-8.268-2.943-9.542-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.477 0 8.268 2.943 9.542 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
    </svg>
  )
}

function ModalCadastro({ onClose, onCadastrado }) {
  const [form, setForm] = useState({
    nome: '',
    email: '',
    password: '',
    confirmar_senha: '',
    codigo_convite: '',
  })
  const [showSenha, setShowSenha] = useState(false)
  const [showConfirmar, setShowConfirmar] = useState(false)
  const [loading, setLoading] = useState(false)
  const [erro, setErro] = useState('')

  function set(field, value) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  async function salvar(e) {
    e.preventDefault()
    setErro('')

    if (form.password.length < 8) {
      setErro('A senha deve ter no mínimo 8 caracteres.')
      return
    }
    if (form.password !== form.confirmar_senha) {
      setErro('As senhas não coincidem.')
      return
    }
    if (!form.codigo_convite.trim()) {
      setErro('Código de convite obrigatório.')
      return
    }

    setLoading(true)
    try {
      await register({
        nome: form.nome,
        email: form.email,
        password: form.password,
        codigo_convite: form.codigo_convite.trim(),
        role: 'estudante',
      })
      onCadastrado(form.email, form.password)
    } catch (err) {
      const detail = err.response?.data?.detail
      setErro(Array.isArray(detail) ? 'Dados inválidos.' : detail || 'Erro ao criar conta.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-brand-card border border-brand-border rounded-2xl p-8 w-full max-w-sm space-y-6 shadow-2xl">
        <div>
          <h2 className="text-2xl font-bold text-brand-text">Criar conta</h2>
          <p className="text-brand-muted text-sm mt-1">Preencha os dados para solicitar acesso.</p>
        </div>

        <form onSubmit={salvar} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-brand-muted mb-1.5">Nome</label>
            <input
              required
              value={form.nome}
              onChange={(e) => set('nome', e.target.value)}
              placeholder="Seu nome completo"
              className="w-full bg-brand-surface border border-brand-border text-brand-text rounded-xl px-4 py-3 outline-none transition-all placeholder:text-brand-muted/40 focus:border-brand-primary focus:ring-1 focus:ring-brand-primary"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-brand-muted mb-1.5">E-mail</label>
            <input
              required
              type="email"
              value={form.email}
              onChange={(e) => set('email', e.target.value)}
              placeholder="exemplo@email.com"
              className="w-full bg-brand-surface border border-brand-border text-brand-text rounded-xl px-4 py-3 outline-none transition-all placeholder:text-brand-muted/40 focus:border-brand-primary focus:ring-1 focus:ring-brand-primary"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-brand-muted mb-1.5">Senha</label>
            <div className="relative">
              <input
                required
                type={showSenha ? 'text' : 'password'}
                value={form.password}
                onChange={(e) => set('password', e.target.value)}
                placeholder="Mínimo 8 caracteres"
                className="w-full bg-brand-surface border border-brand-border text-brand-text rounded-xl px-4 py-3 pr-11 outline-none transition-all placeholder:text-brand-muted/40 focus:border-brand-primary focus:ring-1 focus:ring-brand-primary"
              />
              <button
                type="button"
                onClick={() => setShowSenha((v) => !v)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-brand-muted hover:text-brand-text transition-colors"
                tabIndex={-1}
              >
                <EyeIcon open={showSenha} />
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-brand-muted mb-1.5">Confirmar senha</label>
            <div className="relative">
              <input
                required
                type={showConfirmar ? 'text' : 'password'}
                value={form.confirmar_senha}
                onChange={(e) => set('confirmar_senha', e.target.value)}
                placeholder="Repita a senha"
                className="w-full bg-brand-surface border border-brand-border text-brand-text rounded-xl px-4 py-3 pr-11 outline-none transition-all placeholder:text-brand-muted/40 focus:border-brand-primary focus:ring-1 focus:ring-brand-primary"
              />
              <button
                type="button"
                onClick={() => setShowConfirmar((v) => !v)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-brand-muted hover:text-brand-text transition-colors"
                tabIndex={-1}
              >
                <EyeIcon open={showConfirmar} />
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-brand-muted mb-1.5">Código de convite</label>
            <input
              required
              value={form.codigo_convite}
              onChange={(e) => set('codigo_convite', e.target.value.toUpperCase())}
              placeholder="Ex: BETA2026"
              className="w-full bg-brand-surface border border-brand-border text-brand-text rounded-xl px-4 py-3 outline-none transition-all placeholder:text-brand-muted/40 focus:border-brand-primary focus:ring-1 focus:ring-brand-primary font-mono tracking-widest"
            />
          </div>

          {erro && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3 text-red-400 text-sm">
              {erro}
            </div>
          )}

          <div className="flex gap-3 pt-1">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-3 text-sm text-brand-muted hover:text-brand-text border border-brand-border rounded-xl transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 py-3 text-sm bg-gradient-to-r from-brand-primary to-brand-secondary text-white font-semibold rounded-xl transition-all disabled:opacity-50"
            >
              {loading ? 'Criando...' : 'Criar conta'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

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

  const [email, setEmail]         = useState('')
  const [senha, setSenha]         = useState('')
  const [showSenha, setShowSenha] = useState(false)
  const [error, setError]         = useState('')
  const [loading, setLoading]     = useState(false)
  const [slide, setSlide]         = useState(0)
  const [modalCadastro, setModalCadastro] = useState(false)

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

  async function handleCadastrado(emailNovo, senhaNova) {
    setModalCadastro(false)
    setEmail(emailNovo)
    setSenha(senhaNova)
    setError('')
    setLoading(true)
    try {
      const user = await login(emailNovo, senhaNova)
      navigate(user.area ? '/' : '/onboarding')
    } catch {
      setError('Conta criada! Faça login para continuar.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-brand-bg flex flex-col md:flex-row overflow-hidden">
      {modalCadastro && (
        <ModalCadastro
          onClose={() => setModalCadastro(false)}
          onCadastrado={handleCadastrado}
        />
      )}

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
          <span className="ml-3 px-1.5 py-0.5 rounded bg-brand-primary/10 text-brand-primary font-mono">v1.0.0 beta</span>
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
                type="text"
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
              <div className="relative">
                <input
                  type={showSenha ? 'text' : 'password'}
                  value={senha}
                  onChange={(e) => setSenha(e.target.value)}
                  required
                  placeholder="••••••••"
                  className="w-full bg-brand-surface border border-brand-border text-brand-text rounded-xl px-4 py-3.5 pr-11 outline-none transition-all placeholder:text-brand-muted/40 focus:border-brand-primary focus:ring-1 focus:ring-brand-primary"
                />
                <button
                  type="button"
                  onClick={() => setShowSenha((v) => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-brand-muted hover:text-brand-text transition-colors"
                  tabIndex={-1}
                >
                  <EyeIcon open={showSenha} />
                </button>
              </div>
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
            <button
              type="button"
              onClick={() => setModalCadastro(true)}
              className="text-brand-primary font-semibold hover:underline"
            >
              Solicite acesso
            </button>
          </p>

          <p className="text-center text-xs text-brand-muted/40 md:hidden">
            v1.0.0 beta
          </p>
        </div>
      </div>
    </div>
  )
}
