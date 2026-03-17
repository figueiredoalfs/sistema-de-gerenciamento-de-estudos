import { useEffect, useState } from 'react'
import {
  criarTopico,
  desativarTopico,
  editarTopico,
  listarTodosTopicos,
  questoesPorSubtopico,
} from '../api/adminTopicos'

// ─── Ícones ───────────────────────────────────────────────────────────────────
function IconChevron({ open }) {
  return (
    <svg
      className={`w-3.5 h-3.5 transition-transform duration-200 ${open ? 'rotate-90' : ''}`}
      fill="none" viewBox="0 0 24 24" stroke="currentColor"
    >
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
    </svg>
  )
}

function IconPlus() {
  return (
    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
    </svg>
  )
}

function IconPencil() {
  return (
    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
        d="M15.232 5.232l3.536 3.536M9 13l6.5-6.5a2 2 0 012.828 2.828L11.828 15.828A2 2 0 0111 16.414V18h1.586a2 2 0 001.414-.586L18 14" />
    </svg>
  )
}

function IconEye({ off }) {
  return off ? (
    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
        d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
    </svg>
  ) : (
    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
        d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
        d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
    </svg>
  )
}

// ─── Modal ────────────────────────────────────────────────────────────────────
function Modal({ titulo, form, setForm, onClose, onSave, saving, erro, isEdit }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
      <div className="bg-brand-surface border border-brand-border rounded-xl p-6 w-full max-w-md mx-4 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold text-brand-text">{titulo}</h2>
          <button onClick={onClose} className="text-brand-muted hover:text-brand-text">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="space-y-3">
          <div>
            <label className="text-xs text-brand-muted">Nome <span className="text-red-400">*</span></label>
            <input
              value={form.nome}
              onChange={(e) => setForm((f) => ({ ...f, nome: e.target.value }))}
              className="w-full mt-1 bg-brand-card border border-brand-border rounded-lg px-3 py-2 text-sm text-brand-text focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="text-xs text-brand-muted">Peso no edital</label>
            <input
              type="number"
              step="0.01"
              min="0"
              value={form.peso_edital}
              onChange={(e) => setForm((f) => ({ ...f, peso_edital: e.target.value }))}
              className="w-full mt-1 bg-brand-card border border-brand-border rounded-lg px-3 py-2 text-sm text-brand-text focus:outline-none focus:border-indigo-500"
            />
          </div>

          {isEdit && (
            <label className="flex items-center gap-2 cursor-pointer select-none">
              <div
                onClick={() => setForm((f) => ({ ...f, ativo: !f.ativo }))}
                className={`w-9 h-5 rounded-full transition-colors relative ${form.ativo ? 'bg-indigo-500' : 'bg-brand-border'}`}
              >
                <span className={`absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform ${form.ativo ? 'translate-x-4' : 'translate-x-0.5'}`} />
              </div>
              <span className="text-sm text-brand-muted">{form.ativo ? 'Ativo (visível)' : 'Oculto'}</span>
            </label>
          )}
        </div>

        {erro && <p className="text-red-400 text-xs">{erro}</p>}

        <div className="flex justify-end gap-3 pt-1">
          <button onClick={onClose}
            className="px-4 py-2 text-sm rounded-lg border border-brand-border text-brand-muted hover:text-brand-text transition-colors">
            Cancelar
          </button>
          <button onClick={onSave} disabled={saving || !form.nome.trim()}
            className="px-4 py-2 text-sm rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white disabled:opacity-50 transition-colors">
            {saving ? 'Salvando…' : 'Salvar'}
          </button>
        </div>
      </div>
    </div>
  )
}

// ─── Nível labels ─────────────────────────────────────────────────────────────
const NIVEL_LABEL  = ['Matéria', 'Bloco', 'Subtópico']
const NIVEL_COLORS = ['text-indigo-400', 'text-sky-400', 'text-green-400']
const NIVEL_BG     = ['bg-indigo-500/10', 'bg-sky-500/10', 'bg-green-500/10']

// ─── Componente principal ─────────────────────────────────────────────────────
export default function AdminTopicos() {
  const [topicos, setTopicos]     = useState([])
  const [contagens, setContagens] = useState({})
  const [loading, setLoading]     = useState(true)
  const [erro, setErro]           = useState('')

  const [abertos, setAbertos]     = useState({}) // {id: bool}

  // Modal state
  const [modal, setModal]         = useState(null)  // {tipo: 'criar'|'editar', topico?, parentId?, nivel?}
  const [formModal, setFormModal] = useState({ nome: '', peso_edital: '1.0', ativo: true })
  const [erroModal, setErroModal] = useState('')
  const [saving, setSaving]       = useState(false)

  function carregar() {
    setLoading(true)
    Promise.all([listarTodosTopicos(), questoesPorSubtopico()])
      .then(([ts, cnts]) => { setTopicos(ts); setContagens(cnts) })
      .catch((e) => setErro(e.response?.data?.detail || e.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => { carregar() }, [])

  // Estrutura em árvore
  const materias = topicos.filter((t) => t.nivel === 0).sort((a, b) => a.nome.localeCompare(b.nome))
  const blocosDe  = (midId) => topicos.filter((t) => t.nivel === 1 && t.parent_id === midId).sort((a, b) => a.nome.localeCompare(b.nome))
  const subsDe    = (bId)   => topicos.filter((t) => t.nivel === 2 && t.parent_id === bId).sort((a, b) => a.nome.localeCompare(b.nome))

  function toggleAberto(id) {
    setAbertos((prev) => ({ ...prev, [id]: !prev[id] }))
  }

  // Modal handlers
  function abrirCriar(nivel, parentId = null) {
    setFormModal({ nome: '', peso_edital: '1.0', ativo: true })
    setErroModal('')
    setModal({ tipo: 'criar', nivel, parentId })
  }

  function abrirEditar(topico) {
    setFormModal({ nome: topico.nome, peso_edital: String(topico.peso_edital), ativo: topico.ativo })
    setErroModal('')
    setModal({ tipo: 'editar', topico })
  }

  async function salvarModal() {
    setSaving(true)
    setErroModal('')
    try {
      if (modal.tipo === 'criar') {
        const criado = await criarTopico({
          nome: formModal.nome.trim(),
          nivel: modal.nivel,
          parent_id: modal.parentId || null,
          peso_edital: parseFloat(formModal.peso_edital) || 1.0,
        })
        setTopicos((prev) => [...prev, criado])
        // Expandir o pai automaticamente
        if (modal.parentId) setAbertos((prev) => ({ ...prev, [modal.parentId]: true }))
      } else {
        const updated = await editarTopico(modal.topico.id, {
          nome: formModal.nome.trim(),
          peso_edital: parseFloat(formModal.peso_edital) || 1.0,
          ativo: formModal.ativo,
        })
        setTopicos((prev) => prev.map((t) => (t.id === updated.id ? updated : t)))
      }
      setModal(null)
    } catch (e) {
      setErroModal(e.response?.data?.detail || e.message)
    } finally {
      setSaving(false)
    }
  }

  async function toggleAtivo(topico) {
    try {
      if (topico.ativo) {
        await desativarTopico(topico.id)
        setTopicos((prev) => prev.map((t) => (t.id === topico.id ? { ...t, ativo: false } : t)))
      } else {
        const updated = await editarTopico(topico.id, { ativo: true })
        setTopicos((prev) => prev.map((t) => (t.id === updated.id ? updated : t)))
      }
    } catch (e) {
      setErro(e.response?.data?.detail || e.message)
    }
  }

  // ─── Row ────────────────────────────────────────────────────────────────────
  function Row({ topico, indent = 0, expandable = false, children }) {
    const isOpen   = abertos[topico.id]
    const inativo  = !topico.ativo
    const nivel    = topico.nivel
    const countQ   = nivel === 2 ? (contagens[topico.id] || 0) : null

    return (
      <div>
        <div
          className={`group flex items-center gap-2 px-3 py-2 rounded-lg transition-colors hover:bg-brand-surface ${inativo ? 'opacity-50' : ''}`}
          style={{ paddingLeft: `${12 + indent * 20}px` }}
        >
          {/* Chevron / spacer */}
          {expandable ? (
            <button onClick={() => toggleAberto(topico.id)} className="text-brand-muted hover:text-brand-text flex-shrink-0">
              <IconChevron open={isOpen} />
            </button>
          ) : (
            <span className="w-3.5 flex-shrink-0" />
          )}

          {/* Badge nível */}
          <span className={`text-xs px-1.5 py-0.5 rounded font-medium flex-shrink-0 ${NIVEL_COLORS[nivel]} ${NIVEL_BG[nivel]}`}>
            {NIVEL_LABEL[nivel]}
          </span>

          {/* Nome */}
          <span className={`flex-1 text-sm text-brand-text truncate ${inativo ? 'line-through' : ''}`}>
            {topico.nome}
          </span>

          {/* Peso edital */}
          <span className="text-xs text-brand-muted flex-shrink-0 hidden sm:block">
            peso {topico.peso_edital}
          </span>

          {/* Contador de questões */}
          {countQ !== null && (
            <span className={`text-xs px-2 py-0.5 rounded-full flex-shrink-0 ${
              countQ > 0 ? 'bg-indigo-500/15 text-indigo-400' : 'bg-brand-border/50 text-brand-muted'
            }`}>
              {countQ} q
            </span>
          )}

          {/* Ações */}
          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0">
            {/* Adicionar filho (matéria → bloco, bloco → subtópico) */}
            {nivel < 2 && (
              <button
                onClick={() => abrirCriar(nivel + 1, topico.id)}
                title={`Adicionar ${NIVEL_LABEL[nivel + 1]}`}
                className="p-1 rounded text-brand-muted hover:text-indigo-400 hover:bg-indigo-500/10 transition-colors"
              >
                <IconPlus />
              </button>
            )}
            {/* Editar */}
            <button
              onClick={() => abrirEditar(topico)}
              title="Editar"
              className="p-1 rounded text-brand-muted hover:text-sky-400 hover:bg-sky-500/10 transition-colors"
            >
              <IconPencil />
            </button>
            {/* Ocultar/Mostrar */}
            <button
              onClick={() => toggleAtivo(topico)}
              title={topico.ativo ? 'Ocultar' : 'Mostrar'}
              className="p-1 rounded text-brand-muted hover:text-yellow-400 hover:bg-yellow-500/10 transition-colors"
            >
              <IconEye off={!topico.ativo} />
            </button>
          </div>
        </div>

        {/* Filhos */}
        {expandable && isOpen && (
          <div>{children}</div>
        )}
      </div>
    )
  }

  // ─── Render ─────────────────────────────────────────────────────────────────
  if (loading) return (
    <div className="p-6 flex items-center gap-2 text-brand-muted text-sm">
      <span className="w-4 h-4 rounded-full border-2 border-brand-muted/30 border-t-brand-muted animate-spin" />
      Carregando…
    </div>
  )

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-brand-text">Tópicos e Subtópicos</h1>
          <p className="text-xs text-brand-muted mt-0.5">
            {materias.filter(m => m.ativo).length} matéria{materias.filter(m => m.ativo).length !== 1 ? 's' : ''} ativas
          </p>
        </div>
        <button
          onClick={() => abrirCriar(0)}
          className="flex items-center gap-2 px-4 py-2 text-sm rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white transition-colors"
        >
          <IconPlus />
          Nova Matéria
        </button>
      </div>

      {erro && <p className="text-red-400 text-sm">{erro}</p>}

      {/* Legenda */}
      <div className="flex items-center gap-4 text-xs text-brand-muted">
        {NIVEL_LABEL.map((l, i) => (
          <span key={i} className={`px-2 py-0.5 rounded ${NIVEL_COLORS[i]} ${NIVEL_BG[i]}`}>{l}</span>
        ))}
        <span className="ml-2">· Passe o mouse para ver ações · <span className="text-brand-muted/60">q = questões no banco</span></span>
      </div>

      {/* Árvore */}
      <div className="bg-brand-card border border-brand-border rounded-xl overflow-hidden divide-y divide-brand-border/40">
        {materias.length === 0 ? (
          <p className="px-4 py-6 text-sm text-brand-muted text-center">Nenhuma matéria cadastrada.</p>
        ) : (
          materias.map((mat) => {
            const blocos = blocosDe(mat.id)
            return (
              <Row key={mat.id} topico={mat} indent={0} expandable={blocos.length > 0}>
                {blocos.map((bloco) => {
                  const subs = subsDe(bloco.id)
                  return (
                    <Row key={bloco.id} topico={bloco} indent={1} expandable={subs.length > 0}>
                      {subs.map((sub) => (
                        <Row key={sub.id} topico={sub} indent={2} expandable={false} />
                      ))}
                    </Row>
                  )
                })}
              </Row>
            )
          })
        )}
      </div>

      {/* Modal */}
      {modal && (
        <Modal
          titulo={
            modal.tipo === 'criar'
              ? `Novo ${NIVEL_LABEL[modal.nivel]}`
              : `Editar ${NIVEL_LABEL[modal.topico.nivel]}`
          }
          form={formModal}
          setForm={setFormModal}
          onClose={() => setModal(null)}
          onSave={salvarModal}
          saving={saving}
          erro={erroModal}
          isEdit={modal.tipo === 'editar'}
        />
      )}
    </div>
  )
}
