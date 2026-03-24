import { useState, useEffect, useCallback } from 'react'
import api from '../../api/client'

function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('pt-BR')
}

function ModalNovoConvite({ onClose, onCreate }) {
  const [form, setForm] = useState({ codigo: '', descricao: '', usos_maximos: '', expires_at: '' })
  const [loading, setLoading] = useState(false)
  const [erro, setErro] = useState('')

  function set(field, value) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  async function salvar(e) {
    e.preventDefault()
    setErro('')
    setLoading(true)
    try {
      const payload = {
        codigo: form.codigo.trim().toUpperCase(),
        descricao: form.descricao || null,
        usos_maximos: form.usos_maximos ? parseInt(form.usos_maximos) : null,
        expires_at: form.expires_at || null,
      }
      const res = await api.post('/admin/convites', payload)
      onCreate(res.data)
      onClose()
    } catch (err) {
      setErro(err.response?.data?.detail || 'Erro ao criar código.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div className="bg-brand-card border border-brand-border rounded-2xl p-8 w-full max-w-md space-y-6 shadow-2xl">
        <h2 className="text-xl font-bold text-brand-text">Novo Código de Convite</h2>

        <form onSubmit={salvar} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-brand-muted mb-1">Código</label>
            <input
              required
              value={form.codigo}
              onChange={(e) => set('codigo', e.target.value.toUpperCase())}
              placeholder="Ex: TURMA2026"
              className="w-full bg-brand-surface border border-brand-border text-brand-text rounded-xl px-4 py-2.5 outline-none focus:border-brand-primary font-mono tracking-widest"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-brand-muted mb-1">Descrição (opcional)</label>
            <input
              value={form.descricao}
              onChange={(e) => set('descricao', e.target.value)}
              placeholder="Ex: Beta — Turma Março 2026"
              className="w-full bg-brand-surface border border-brand-border text-brand-text rounded-xl px-4 py-2.5 outline-none focus:border-brand-primary"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-brand-muted mb-1">Limite de usos (vazio = ilimitado)</label>
            <input
              type="number"
              min="1"
              value={form.usos_maximos}
              onChange={(e) => set('usos_maximos', e.target.value)}
              placeholder="Ex: 50"
              className="w-full bg-brand-surface border border-brand-border text-brand-text rounded-xl px-4 py-2.5 outline-none focus:border-brand-primary"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-brand-muted mb-1">Expira em (vazio = sem expiração)</label>
            <input
              type="date"
              value={form.expires_at}
              onChange={(e) => set('expires_at', e.target.value)}
              className="w-full bg-brand-surface border border-brand-border text-brand-text rounded-xl px-4 py-2.5 outline-none focus:border-brand-primary"
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
              className="flex-1 py-2.5 text-sm text-brand-muted border border-brand-border rounded-xl hover:text-brand-text transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 py-2.5 text-sm bg-gradient-to-r from-brand-primary to-brand-secondary text-white font-semibold rounded-xl disabled:opacity-50"
            >
              {loading ? 'Criando...' : 'Criar código'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default function AdminConvites() {
  const [convites, setConvites] = useState([])
  const [loading, setLoading] = useState(true)
  const [modal, setModal] = useState(false)
  const [copiado, setCopiado] = useState(null)

  const carregar = useCallback(async () => {
    setLoading(true)
    try {
      const res = await api.get('/admin/convites')
      setConvites(res.data)
    } catch {
      // silencioso
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { carregar() }, [carregar])

  async function toggleAtivo(id, ativo) {
    await api.patch(`/admin/convites/${id}`, { ativo })
    setConvites((prev) => prev.map((c) => c.id === id ? { ...c, ativo } : c))
  }

  async function deletar(id) {
    if (!confirm('Remover este código permanentemente?')) return
    await api.delete(`/admin/convites/${id}`)
    setConvites((prev) => prev.filter((c) => c.id !== id))
  }

  function copiar(codigo) {
    navigator.clipboard.writeText(codigo)
    setCopiado(codigo)
    setTimeout(() => setCopiado(null), 2000)
  }

  return (
    <div className="p-6 md:p-10 max-w-5xl mx-auto space-y-6">
      {modal && (
        <ModalNovoConvite
          onClose={() => setModal(false)}
          onCreate={(novo) => setConvites((prev) => [novo, ...prev])}
        />
      )}

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-brand-text">Códigos de Convite</h1>
          <p className="text-brand-muted text-sm mt-1">Controle quem pode se cadastrar na plataforma.</p>
        </div>
        <button
          onClick={() => setModal(true)}
          className="px-5 py-2.5 bg-gradient-to-r from-brand-primary to-brand-secondary text-white text-sm font-semibold rounded-xl hover:scale-[1.02] transition-all"
        >
          + Novo Código
        </button>
      </div>

      {loading ? (
        <div className="text-brand-muted text-sm">Carregando...</div>
      ) : convites.length === 0 ? (
        <div className="bg-brand-card border border-brand-border rounded-2xl p-8 text-center text-brand-muted">
          Nenhum código cadastrado.
        </div>
      ) : (
        <div className="bg-brand-card border border-brand-border rounded-2xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-brand-border text-brand-muted text-left">
                <th className="px-5 py-3 font-medium">Código</th>
                <th className="px-5 py-3 font-medium">Descrição</th>
                <th className="px-5 py-3 font-medium text-center">Usos</th>
                <th className="px-5 py-3 font-medium text-center">Limite</th>
                <th className="px-5 py-3 font-medium text-center">Expira</th>
                <th className="px-5 py-3 font-medium text-center">Status</th>
                <th className="px-5 py-3 font-medium text-center">Ações</th>
              </tr>
            </thead>
            <tbody>
              {convites.map((c) => (
                <tr key={c.id} className="border-b border-brand-border/50 last:border-0 hover:bg-brand-surface/30 transition-colors">
                  <td className="px-5 py-3">
                    <span className="font-mono font-semibold text-brand-text tracking-wider">{c.codigo}</span>
                  </td>
                  <td className="px-5 py-3 text-brand-muted">{c.descricao || '—'}</td>
                  <td className="px-5 py-3 text-center text-brand-text">{c.usos_atuais}</td>
                  <td className="px-5 py-3 text-center text-brand-muted">{c.usos_maximos ?? '∞'}</td>
                  <td className="px-5 py-3 text-center text-brand-muted">{formatDate(c.expires_at)}</td>
                  <td className="px-5 py-3 text-center">
                    <button
                      onClick={() => toggleAtivo(c.id, !c.ativo)}
                      className={`px-3 py-1 rounded-full text-xs font-semibold transition-colors ${
                        c.ativo
                          ? 'bg-green-500/15 text-green-400 hover:bg-green-500/25'
                          : 'bg-red-500/15 text-red-400 hover:bg-red-500/25'
                      }`}
                    >
                      {c.ativo ? 'Ativo' : 'Inativo'}
                    </button>
                  </td>
                  <td className="px-5 py-3 text-center">
                    <div className="flex items-center justify-center gap-2">
                      <button
                        onClick={() => copiar(c.codigo)}
                        title="Copiar código"
                        className="p-1.5 rounded-lg hover:bg-brand-surface text-brand-muted hover:text-brand-text transition-colors"
                      >
                        {copiado === c.codigo ? (
                          <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        ) : (
                          <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                          </svg>
                        )}
                      </button>
                      <button
                        onClick={() => deletar(c.id)}
                        title="Remover"
                        className="p-1.5 rounded-lg hover:bg-red-500/10 text-brand-muted hover:text-red-400 transition-colors"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
