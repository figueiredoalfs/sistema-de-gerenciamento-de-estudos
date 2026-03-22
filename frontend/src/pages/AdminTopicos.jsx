import { useEffect, useState } from 'react'
import {
  criarTopico,
  desativarTopico,
  editarTopico,
  listarTodosTopicos,
  questoesPorSubtopico,
  hierarquiaTopicos,
  salvarAreaSubtopico,
  listarBancas,
  criarBanca,
  editarBanca,
  desativarBanca,
} from '../api/adminTopicos'

// ─── Ícones ───────────────────────────────────────────────────────────────────
function IconChevron({ open }) {
  return (
    <svg className={`w-3.5 h-3.5 transition-transform duration-200 ${open ? 'rotate-90' : ''}`}
      fill="none" viewBox="0 0 24 24" stroke="currentColor">
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
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
        d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
    </svg>
  )
}

// ─── Modal criar/editar tópico ─────────────────────────────────────────────────
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
              type="number" step="0.01" min="0"
              value={form.peso_edital}
              onChange={(e) => setForm((f) => ({ ...f, peso_edital: e.target.value }))}
              className="w-full mt-1 bg-brand-card border border-brand-border rounded-lg px-3 py-2 text-sm text-brand-text focus:outline-none focus:border-indigo-500"
            />
          </div>
          {isEdit && (
            <label className="flex items-center gap-2 cursor-pointer select-none">
              <div onClick={() => setForm((f) => ({ ...f, ativo: !f.ativo }))}
                className={`w-9 h-5 rounded-full transition-colors relative ${form.ativo ? 'bg-indigo-500' : 'bg-brand-border'}`}>
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

// ─── Modal configurar SubtopicoArea ──────────────────────────────────────────
const AREAS_OPCOES = [
  { value: 'fiscal',    label: 'Fiscal' },
  { value: 'eaof_com',  label: 'EAOF-COM' },
  { value: 'eaof_svm',  label: 'EAOF-SVM' },
  { value: 'cfoe_com',  label: 'CFOE-COM' },
]
const COMPLEXIDADE_OPCOES = [
  { value: 'baixa', label: 'Baixa (70%)' },
  { value: 'media', label: 'Média (75%)' },
  { value: 'alta',  label: 'Alta (80%)' },
]
const COMPLEXIDADE_CORES = { baixa: 'text-green-400', media: 'text-yellow-400', alta: 'text-red-400' }

function ModalAreaSubtopico({ subtopico, areaAtiva, areasConfig, onClose, onSaved }) {
  const cfg = areasConfig?.find((a) => a.area === areaAtiva)
  const [peso, setPeso] = useState(String(cfg?.peso ?? '1.0'))
  const [complexidade, setComplexidade] = useState(cfg?.complexidade ?? 'media')
  const [saving, setSaving] = useState(false)
  const [erro, setErro] = useState('')

  async function salvar() {
    setSaving(true)
    setErro('')
    try {
      await salvarAreaSubtopico(subtopico.id, {
        area: areaAtiva,
        peso: parseFloat(peso) || 1.0,
        complexidade,
      })
      onSaved()
    } catch (e) {
      setErro(e.response?.data?.detail || e.message)
    } finally {
      setSaving(false)
    }
  }

  const areaLabel = AREAS_OPCOES.find((a) => a.value === areaAtiva)?.label ?? areaAtiva

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
      <div className="bg-brand-surface border border-brand-border rounded-xl p-6 w-full max-w-sm mx-4 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-brand-text">Configurar para {areaLabel}</h2>
            <p className="text-xs text-brand-muted mt-0.5">{subtopico.nome}</p>
          </div>
          <button onClick={onClose} className="text-brand-muted hover:text-brand-text">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="space-y-3">
          <div>
            <label className="text-xs text-brand-muted">Peso na área</label>
            <input
              type="number" step="0.01" min="0" max="1"
              value={peso}
              onChange={(e) => setPeso(e.target.value)}
              className="w-full mt-1 bg-brand-card border border-brand-border rounded-lg px-3 py-2 text-sm text-brand-text focus:outline-none focus:border-indigo-500"
            />
          </div>
          <div>
            <label className="text-xs text-brand-muted">Complexidade</label>
            <div className="flex gap-2 mt-1">
              {COMPLEXIDADE_OPCOES.map((op) => (
                <button
                  key={op.value}
                  onClick={() => setComplexidade(op.value)}
                  className={`flex-1 py-1.5 text-xs rounded-lg border transition-colors ${
                    complexidade === op.value
                      ? 'border-indigo-500 bg-indigo-500/15 text-indigo-300'
                      : 'border-brand-border text-brand-muted hover:text-brand-text'
                  }`}
                >
                  {op.label}
                </button>
              ))}
            </div>
            <p className="text-xs text-brand-muted mt-1.5">
              Define o limiar de domínio e o nível das questões selecionadas para esta área.
            </p>
          </div>
        </div>

        {erro && <p className="text-red-400 text-xs">{erro}</p>}

        <div className="flex justify-end gap-3 pt-1">
          <button onClick={onClose}
            className="px-4 py-2 text-sm rounded-lg border border-brand-border text-brand-muted hover:text-brand-text transition-colors">
            Cancelar
          </button>
          <button onClick={salvar} disabled={saving}
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

// ─── Aba Matérias ─────────────────────────────────────────────────────────────
function TabMaterias() {
  const [hierarquia, setHierarquia] = useState([])
  const [topicos, setTopicos]       = useState([])   // para criar/editar via modal
  const [contagens, setContagens]   = useState({})
  const [loading, setLoading]       = useState(true)
  const [erro, setErro]             = useState('')
  const [abertos, setAbertos]       = useState({})
  const [areaAtiva, setAreaAtiva]   = useState('fiscal')

  const [modal, setModal]           = useState(null)
  const [formModal, setFormModal]   = useState({ nome: '', peso_edital: '1.0', ativo: true })
  const [erroModal, setErroModal]   = useState('')
  const [saving, setSaving]         = useState(false)

  const [modalArea, setModalArea]   = useState(null)  // { subtopico, areasConfig }

  function carregar() {
    setLoading(true)
    Promise.all([hierarquiaTopicos(), listarTodosTopicos(), questoesPorSubtopico()])
      .then(([hier, ts, cnts]) => {
        setHierarquia(hier)
        setTopicos(ts)
        setContagens(cnts)
      })
      .catch((e) => setErro(e.response?.data?.detail || e.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => { carregar() }, [])

  function toggleAberto(id) { setAbertos((p) => ({ ...p, [id]: !p[id] })) }

  // Para criar usamos ainda o endpoint simples (listarTodosTopicos já tem os dados)
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
        await criarTopico({
          nome: formModal.nome.trim(),
          nivel: modal.nivel,
          parent_id: modal.parentId || null,
          peso_edital: parseFloat(formModal.peso_edital) || 1.0,
        })
        if (modal.parentId) setAbertos((prev) => ({ ...prev, [modal.parentId]: true }))
      } else {
        await editarTopico(modal.topico.id, {
          nome: formModal.nome.trim(),
          peso_edital: parseFloat(formModal.peso_edital) || 1.0,
          ativo: formModal.ativo,
        })
      }
      setModal(null)
      carregar()
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
      } else {
        await editarTopico(topico.id, { ativo: true })
      }
      carregar()
    } catch (e) {
      setErro(e.response?.data?.detail || e.message)
    }
  }

  function abrirConfigArea(subtopico, areasConfig) {
    setModalArea({ subtopico, areasConfig })
  }

  // ─── Row subtópico ──────────────────────────────────────────────────────────
  function RowSubtopico({ sub, indent = 2 }) {
    const inativo  = !sub.ativo
    const countQ   = contagens[sub.id] ?? sub.num_questoes ?? 0
    const cfgArea  = sub.areas?.find((a) => a.area === areaAtiva)
    const temConfig = !!cfgArea

    return (
      <div
        className={`group flex items-center gap-2 px-3 py-2 rounded-lg transition-colors hover:bg-brand-surface ${inativo ? 'opacity-50' : ''}`}
        style={{ paddingLeft: `${12 + indent * 20}px` }}
      >
        <span className="w-3.5 flex-shrink-0" />
        <span className={`text-xs px-1.5 py-0.5 rounded font-medium flex-shrink-0 ${NIVEL_COLORS[2]} ${NIVEL_BG[2]}`}>
          Subtópico
        </span>
        <span className={`flex-1 text-sm text-brand-text truncate ${inativo ? 'line-through' : ''}`}>
          {sub.nome}
        </span>

        {/* Configuração da área ativa */}
        <button
          onClick={() => abrirConfigArea(sub, sub.areas ?? [])}
          title={`Configurar para ${AREAS_OPCOES.find(a => a.value === areaAtiva)?.label}`}
          className={`flex-shrink-0 flex items-center gap-1 px-2 py-0.5 rounded text-xs transition-colors ${
            temConfig
              ? `${COMPLEXIDADE_CORES[cfgArea.complexidade]} bg-current/10 hover:opacity-80`
              : 'text-brand-muted border border-brand-border/50 hover:border-indigo-400 hover:text-indigo-400'
          }`}
        >
          {temConfig ? (
            <>
              <span>{cfgArea.complexidade}</span>
              <span className="text-brand-muted">·</span>
              <span>p{cfgArea.peso.toFixed(2)}</span>
            </>
          ) : (
            <span>+ config</span>
          )}
        </button>

        {/* Contador de questões */}
        <span className={`text-xs px-2 py-0.5 rounded-full flex-shrink-0 ${countQ > 0 ? 'bg-indigo-500/15 text-indigo-400' : 'bg-brand-border/50 text-brand-muted'}`}>
          {countQ} q
        </span>

        {/* Ações (hover) */}
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0">
          <button onClick={() => abrirEditar({ id: sub.id, nome: sub.nome, peso_edital: sub.peso_edital, ativo: sub.ativo, nivel: 2 })}
            title="Editar"
            className="p-1 rounded text-brand-muted hover:text-sky-400 hover:bg-sky-500/10 transition-colors">
            <IconPencil />
          </button>
          <button
            onClick={() => toggleAtivo({ id: sub.id, ativo: sub.ativo })}
            title={sub.ativo ? (countQ > 0 ? 'Possui questões — não pode desativar' : 'Ocultar') : 'Mostrar'}
            disabled={sub.ativo && countQ > 0}
            className={`p-1 rounded transition-colors ${
              sub.ativo && countQ > 0
                ? 'text-brand-border cursor-not-allowed'
                : 'text-brand-muted hover:text-yellow-400 hover:bg-yellow-500/10'
            }`}>
            <IconEye off={!sub.ativo} />
          </button>
        </div>
      </div>
    )
  }

  // ─── Row genérico (matéria / bloco) ────────────────────────────────────────
  function Row({ topico, indent = 0, expandable = false, children }) {
    const isOpen  = abertos[topico.id]
    const inativo = !topico.ativo
    const nivel   = topico.nivel
    return (
      <div>
        <div
          className={`group flex items-center gap-2 px-3 py-2 rounded-lg transition-colors hover:bg-brand-surface ${inativo ? 'opacity-50' : ''}`}
          style={{ paddingLeft: `${12 + indent * 20}px` }}
        >
          {expandable ? (
            <button onClick={() => toggleAberto(topico.id)} className="text-brand-muted hover:text-brand-text flex-shrink-0">
              <IconChevron open={isOpen} />
            </button>
          ) : (
            <span className="w-3.5 flex-shrink-0" />
          )}
          <span className={`text-xs px-1.5 py-0.5 rounded font-medium flex-shrink-0 ${NIVEL_COLORS[nivel]} ${NIVEL_BG[nivel]}`}>
            {NIVEL_LABEL[nivel]}
          </span>
          <span className={`flex-1 text-sm text-brand-text truncate ${inativo ? 'line-through' : ''}`}>
            {topico.nome}
          </span>
          <span className="text-xs text-brand-muted flex-shrink-0 hidden sm:block">peso {topico.peso_edital}</span>
          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0">
            {nivel < 2 && (
              <button onClick={() => abrirCriar(nivel + 1, topico.id)} title={`Adicionar ${NIVEL_LABEL[nivel + 1]}`}
                className="p-1 rounded text-brand-muted hover:text-indigo-400 hover:bg-indigo-500/10 transition-colors">
                <IconPlus />
              </button>
            )}
            <button onClick={() => abrirEditar(topico)} title="Editar"
              className="p-1 rounded text-brand-muted hover:text-sky-400 hover:bg-sky-500/10 transition-colors">
              <IconPencil />
            </button>
            <button onClick={() => toggleAtivo(topico)} title={topico.ativo ? 'Ocultar' : 'Mostrar'}
              className="p-1 rounded text-brand-muted hover:text-yellow-400 hover:bg-yellow-500/10 transition-colors">
              <IconEye off={!topico.ativo} />
            </button>
          </div>
        </div>
        {expandable && isOpen && <div>{children}</div>}
      </div>
    )
  }

  if (loading) return <p className="text-brand-muted text-sm">Carregando…</p>

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <p className="text-xs text-brand-muted">
          {hierarquia.filter((m) => m.ativo).length} matéria{hierarquia.filter((m) => m.ativo).length !== 1 ? 's' : ''} ativas
        </p>
        <div className="flex items-center gap-2 flex-wrap">
          {/* Selector de área */}
          <div className="flex items-center gap-1 bg-brand-card border border-brand-border rounded-lg p-0.5">
            {AREAS_OPCOES.map((a) => (
              <button
                key={a.value}
                onClick={() => setAreaAtiva(a.value)}
                className={`px-2.5 py-1 text-xs rounded-md transition-colors ${
                  areaAtiva === a.value
                    ? 'bg-indigo-600 text-white'
                    : 'text-brand-muted hover:text-brand-text'
                }`}
              >
                {a.label}
              </button>
            ))}
          </div>
          <button onClick={() => abrirCriar(0)}
            className="flex items-center gap-2 px-4 py-2 text-sm rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white transition-colors">
            <IconPlus />
            Nova Matéria
          </button>
        </div>
      </div>

      {erro && <p className="text-red-400 text-sm">{erro}</p>}

      <div className="flex items-center gap-4 text-xs text-brand-muted flex-wrap">
        {NIVEL_LABEL.map((l, i) => (
          <span key={i} className={`px-2 py-0.5 rounded ${NIVEL_COLORS[i]} ${NIVEL_BG[i]}`}>{l}</span>
        ))}
        <span className="ml-1">· Subtópico: clique em <span className="text-brand-text">complexidade · peso</span> para configurar por área</span>
      </div>

      <div className="bg-brand-card border border-brand-border rounded-xl overflow-hidden divide-y divide-brand-border/40">
        {hierarquia.length === 0 ? (
          <p className="px-4 py-6 text-sm text-brand-muted text-center">Nenhuma matéria cadastrada.</p>
        ) : (
          hierarquia.map((mat) => (
            <Row key={mat.id} topico={mat} indent={0} expandable={mat.blocos.length > 0}>
              {mat.blocos.map((bloco) => (
                <Row key={bloco.id} topico={bloco} indent={1} expandable={bloco.subtopicos.length > 0}>
                  {bloco.subtopicos.map((sub) => (
                    <RowSubtopico key={sub.id} sub={sub} indent={2} />
                  ))}
                  {/* Botão adicionar subtópico dentro do bloco */}
                  <div style={{ paddingLeft: `${12 + 2 * 20}px` }} className="py-1">
                    <button
                      onClick={() => abrirCriar(2, bloco.id)}
                      className="flex items-center gap-1 text-xs text-brand-muted hover:text-indigo-400 transition-colors"
                    >
                      <IconPlus />
                      Novo Subtópico
                    </button>
                  </div>
                </Row>
              ))}
            </Row>
          ))
        )}
      </div>

      {modal && (
        <Modal
          titulo={modal.tipo === 'criar' ? `Novo ${NIVEL_LABEL[modal.nivel]}` : `Editar ${NIVEL_LABEL[modal.topico.nivel]}`}
          form={formModal}
          setForm={setFormModal}
          onClose={() => setModal(null)}
          onSave={salvarModal}
          saving={saving}
          erro={erroModal}
          isEdit={modal.tipo === 'editar'}
        />
      )}

      {modalArea && (
        <ModalAreaSubtopico
          subtopico={modalArea.subtopico}
          areaAtiva={areaAtiva}
          areasConfig={modalArea.areasConfig}
          onClose={() => setModalArea(null)}
          onSaved={() => { setModalArea(null); carregar() }}
        />
      )}
    </div>
  )
}

// ─── Aba Bancas ───────────────────────────────────────────────────────────────
function TabBancas() {
  const [bancas, setBancas] = useState([])
  const [loading, setLoading] = useState(true)
  const [erro, setErro] = useState('')
  const [novoNome, setNovoNome] = useState('')
  const [criando, setCriando] = useState(false)
  const [erroCriar, setErroCriar] = useState('')
  const [editandoId, setEditandoId] = useState(null)
  const [editNome, setEditNome] = useState('')

  function carregar() {
    setLoading(true)
    listarBancas(false)
      .then(setBancas)
      .catch((e) => setErro(e.response?.data?.detail || e.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => { carregar() }, [])

  async function handleCriar() {
    if (!novoNome.trim() || criando) return
    setCriando(true)
    setErroCriar('')
    try {
      const nova = await criarBanca(novoNome.trim())
      setBancas((prev) => [...prev, nova].sort((a, b) => a.nome.localeCompare(b.nome)))
      setNovoNome('')
    } catch (e) {
      setErroCriar(e.response?.data?.detail || e.message)
    } finally {
      setCriando(false)
    }
  }

  async function handleSalvarEdit(id) {
    if (!editNome.trim()) return
    try {
      const updated = await editarBanca(id, { nome: editNome.trim() })
      setBancas((prev) => prev.map((b) => (b.id === id ? updated : b)))
      setEditandoId(null)
    } catch (e) {
      setErro(e.response?.data?.detail || e.message)
    }
  }

  async function handleToggle(banca) {
    try {
      if (banca.ativo) {
        await desativarBanca(banca.id)
        setBancas((prev) => prev.map((b) => (b.id === banca.id ? { ...b, ativo: false } : b)))
      } else {
        const updated = await editarBanca(banca.id, { ativo: true })
        setBancas((prev) => prev.map((b) => (b.id === updated.id ? updated : b)))
      }
    } catch (e) {
      setErro(e.response?.data?.detail || e.message)
    }
  }

  if (loading) return <p className="text-brand-muted text-sm">Carregando…</p>

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <input
          value={novoNome}
          onChange={(e) => setNovoNome(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter') handleCriar() }}
          placeholder="Nome da banca (ex: CESPE, FGV, VUNESP)"
          className="flex-1 bg-brand-card border border-brand-border rounded-lg px-3 py-2 text-sm text-brand-text focus:outline-none focus:border-indigo-500"
        />
        <button type="button" onClick={handleCriar} disabled={criando || !novoNome.trim()}
          className="px-4 py-2 text-sm rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium disabled:opacity-50 transition-colors">
          {criando ? 'Salvando…' : 'Adicionar'}
        </button>
      </div>
      {erroCriar && <p className="text-red-400 text-xs">{erroCriar}</p>}
      {erro && <p className="text-red-400 text-sm">{erro}</p>}

      <div className="bg-brand-card border border-brand-border rounded-xl overflow-hidden divide-y divide-brand-border/40">
        {bancas.length === 0 ? (
          <p className="px-4 py-6 text-sm text-brand-muted text-center">Nenhuma banca cadastrada.</p>
        ) : (
          bancas.map((b) => (
            <div key={b.id} className={`group flex items-center gap-3 px-4 py-2.5 hover:bg-brand-surface transition-colors ${!b.ativo ? 'opacity-50' : ''}`}>
              {editandoId === b.id ? (
                <>
                  <input
                    value={editNome}
                    onChange={(e) => setEditNome(e.target.value)}
                    className="flex-1 bg-brand-surface border border-indigo-500 rounded-lg px-2 py-1 text-sm text-brand-text focus:outline-none"
                    autoFocus
                  />
                  <button onClick={() => handleSalvarEdit(b.id)}
                    className="text-xs px-3 py-1 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white transition-colors">
                    Salvar
                  </button>
                  <button onClick={() => setEditandoId(null)}
                    className="text-xs px-3 py-1 rounded-lg border border-brand-border text-brand-muted hover:text-brand-text transition-colors">
                    Cancelar
                  </button>
                </>
              ) : (
                <>
                  <span className={`flex-1 text-sm text-brand-text ${!b.ativo ? 'line-through' : ''}`}>{b.nome}</span>
                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button onClick={() => { setEditandoId(b.id); setEditNome(b.nome) }}
                      className="p-1 rounded text-brand-muted hover:text-sky-400 hover:bg-sky-500/10 transition-colors">
                      <IconPencil />
                    </button>
                    <button onClick={() => handleToggle(b)} title={b.ativo ? 'Desativar' : 'Ativar'}
                      className="p-1 rounded text-brand-muted hover:text-yellow-400 hover:bg-yellow-500/10 transition-colors">
                      <IconEye off={!b.ativo} />
                    </button>
                  </div>
                </>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
}

// ─── Componente principal ─────────────────────────────────────────────────────
export default function AdminTopicos() {
  const [aba, setAba] = useState('materias')

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-5">
      <div>
        <h1 className="text-xl font-bold text-brand-text">Matérias e Bancas</h1>
        <p className="text-xs text-brand-muted mt-0.5">
          Gerencie a hierarquia de tópicos, configure peso e complexidade por área, e gerencie bancas.
        </p>
      </div>

      <div className="flex gap-1 border-b border-brand-border">
        {[
          { key: 'materias', label: 'Matérias / Tópicos' },
          { key: 'bancas', label: 'Bancas' },
        ].map((t) => (
          <button
            key={t.key}
            onClick={() => setAba(t.key)}
            className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors ${
              aba === t.key
                ? 'border-indigo-500 text-indigo-400'
                : 'border-transparent text-brand-muted hover:text-brand-text'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {aba === 'materias' ? <TabMaterias /> : <TabBancas />}
    </div>
  )
}
