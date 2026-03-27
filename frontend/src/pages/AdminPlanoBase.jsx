import { useEffect, useRef, useState } from 'react'
import { listarPlanos, gerarPlano, criarPlano, atualizarPlano, aplicarPlano, deletarPlano, getHierarquiaAdmin } from '../api/adminPlanoBase'

const PERFIL_OPTIONS = ['iniciante', 'intermediario', 'avancado']
const AREA_OPTIONS = ['fiscal', 'eaof_com', 'eaof_svm', 'cfoe_com', 'juridica', 'policial', 'ti', 'saude', 'outro']

// Critérios de avanço fixos — espelho das constantes em gerar_plano_base.py
const CRITERIOS_AVANCO = {
  iniciante:     [65, 70, 75, 80],
  intermediario: [70, 75, 80],
  avancado:      [75, 80],
}

// Parseia fases_json: aceita array legado OU novo objeto {fases, ordem_subtopicos, prerequisitos}
function parseFasesJson(raw) {
  try {
    const parsed = JSON.parse(raw)
    if (Array.isArray(parsed)) {
      return { fases: parsed, ordem_subtopicos: {}, prerequisitos: {} }
    }
    return {
      fases:             parsed.fases             || [],
      ordem_subtopicos:  parsed.ordem_subtopicos  || {},
      prerequisitos:     parsed.prerequisitos     || {},
    }
  } catch {
    return { fases: [], ordem_subtopicos: {}, prerequisitos: {} }
  }
}

// Retorna lista de matérias de uma fase (materias + materias_novas)
function getFaseMaterias(fase) {
  return [...(fase.materias || []), ...(fase.materias_novas || [])]
}

// ── Componente de subtópicos com drag-and-drop ────────────────────────────────
function SubtopicosList({ materiaKey, subtopicos, onChange, subtopicosDisponiveis = [] }) {
  const dragIdx = useRef(null)
  const [dragOver, setDragOver] = useState(null)
  const [pickerOpen, setPickerOpen] = useState(false)
  const [pickerVal, setPickerVal] = useState('')

  function handleDragStart(idx) {
    dragIdx.current = idx
  }

  function handleDragOver(e, idx) {
    e.preventDefault()
    setDragOver(idx)
  }

  function handleDrop(e, targetIdx) {
    e.preventDefault()
    setDragOver(null)
    const src = dragIdx.current
    if (src === null || src === targetIdx) return
    const arr = [...subtopicos]
    const [item] = arr.splice(src, 1)
    arr.splice(targetIdx, 0, item)
    dragIdx.current = null
    onChange(materiaKey, arr)
  }

  function handleDragEnd() {
    setDragOver(null)
    dragIdx.current = null
  }

  function remover(idx) {
    onChange(materiaKey, subtopicos.filter((_, i) => i !== idx))
  }

  function adicionar() {
    setPickerVal('')
    setPickerOpen(true)
  }

  function confirmarPicker() {
    if (pickerVal.trim()) onChange(materiaKey, [...subtopicos, pickerVal.trim()])
    setPickerOpen(false)
  }

  return (
    <div className="mt-2 space-y-1">
      {subtopicos.length === 0 && (
        <p className="text-xs text-brand-muted italic pl-1">Nenhum subtópico cadastrado para esta matéria.</p>
      )}
      {subtopicos.map((s, idx) => (
        <div
          key={idx}
          draggable
          onDragStart={() => handleDragStart(idx)}
          onDragOver={(e) => handleDragOver(e, idx)}
          onDrop={(e) => handleDrop(e, idx)}
          onDragEnd={handleDragEnd}
          className={`flex items-center gap-2 px-2 py-1 rounded text-xs cursor-grab active:cursor-grabbing transition-colors ${
            dragOver === idx
              ? 'bg-indigo-500/20 border border-indigo-500/40'
              : 'bg-brand-bg border border-transparent hover:border-brand-border'
          }`}
        >
          {/* grip */}
          <svg className="w-3 h-3 text-brand-muted shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path d="M7 2a2 2 0 1 0 0 4 2 2 0 0 0 0-4zm6 0a2 2 0 1 0 0 4 2 2 0 0 0 0-4zM7 8a2 2 0 1 0 0 4 2 2 0 0 0 0-4zm6 0a2 2 0 1 0 0 4 2 2 0 0 0 0-4zM7 14a2 2 0 1 0 0 4 2 2 0 0 0 0-4zm6 0a2 2 0 1 0 0 4 2 2 0 0 0 0-4z" />
          </svg>
          <span className="flex-1 text-brand-text">{s}</span>
          <button
            onClick={() => remover(idx)}
            className="text-brand-muted hover:text-red-400 transition-colors"
          >
            ×
          </button>
        </div>
      ))}
      {pickerOpen ? (
        <div className="flex gap-1 mt-1">
          <select
            autoFocus
            value={pickerVal}
            onChange={e => setPickerVal(e.target.value)}
            className="flex-1 bg-brand-surface border border-brand-border rounded px-2 py-1 text-xs text-brand-text focus:outline-none focus:border-indigo-500"
          >
            <option value="">Selecione o subtópico…</option>
            {subtopicosDisponiveis
              .filter(s => !subtopicos.includes(s.nome))
              .map(s => <option key={s.id} value={s.nome}>{s.nome}</option>)}
          </select>
          <button
            onClick={confirmarPicker}
            disabled={!pickerVal}
            className="px-2 py-1 text-xs bg-indigo-500 text-white rounded disabled:opacity-40"
          >+</button>
          <button
            onClick={() => setPickerOpen(false)}
            className="px-2 py-1 text-xs text-brand-muted hover:text-brand-text"
          >×</button>
        </div>
      ) : (
        <button
          onClick={adicionar}
          className="w-full text-left text-xs text-brand-muted hover:text-indigo-400 transition-colors px-2 py-0.5"
        >
          + subtópico
        </button>
      )}
    </div>
  )
}

// ── Editor visual de fases ────────────────────────────────────────────────────
function FasesEditorModal({ plano, onClose, onSaved }) {
  const [conteudo, setConteudo] = useState(() => parseFasesJson(plano.fases_json))
  const [expandedFase, setExpandedFase]     = useState(null)
  const [expandedMateria, setExpandedMateria] = useState(null)
  const [salvando, setSalvando]   = useState(false)
  const [regenerando, setRegenerando] = useState(false)
  const [erro, setErro]           = useState('')
  const [mostrarAplicar, setMostrarAplicar] = useState(false)
  const [aplicando, setAplicando] = useState(false)
  const [modoAplicar, setModoAplicar]       = useState('novos')
  const [resultadoAplicar, setResultadoAplicar] = useState(null)
  const [hierarquia, setHierarquia] = useState([])
  const [pickerFase, setPickerFase] = useState(null)  // faseIdx ou null
  const [pickerMateria, setPickerMateria] = useState('')

  useEffect(() => {
    getHierarquiaAdmin().then(h => {
      const arr = Array.isArray(h) ? h : []
      setHierarquia(arr.filter((m, i, a) => a.findIndex(x => x.nome === m.nome) === i))
    }).catch(() => {})
  }, [])

  const criteriosPerfil = CRITERIOS_AVANCO[plano.perfil] || [70, 75, 80]

  // ── mutações de conteúdo ──────────────────────────────────────────────────
  function atualizarFaseNome(idx, nome) {
    setConteudo((prev) => ({
      ...prev,
      fases: prev.fases.map((f, i) => i === idx ? { ...f, nome } : f),
    }))
  }

  function removerFase(idx) {
    setConteudo((prev) => ({
      ...prev,
      fases: prev.fases
        .filter((_, i) => i !== idx)
        .map((f, i) => ({ ...f, numero: i + 1 })),
    }))
  }

  function adicionarFase() {
    setConteudo((prev) => {
      const proximo = prev.fases.length + 1
      return {
        ...prev,
        fases: [...prev.fases, {
          numero: proximo,
          nome: `Fase ${proximo}`,
          materias: proximo === 1 ? [] : undefined,
          materias_novas: proximo > 1 ? [] : undefined,
        }],
      }
    })
  }

  function adicionarMateria(faseIdx) {
    setPickerMateria('')
    setPickerFase(faseIdx)
  }

  function confirmarPickerMateria() {
    const nome = pickerMateria.trim()
    if (!nome) return
    const subtopicosInicial = hierarquia.find(m => m.nome === nome)?.blocos?.flatMap(b => b.subtopicos.map(s => s.nome)) ?? []
    setConteudo((prev) => {
      const fases = prev.fases.map((f, i) => {
        if (i !== pickerFase) return f
        if (f.numero === 1) {
          return { ...f, materias: [...(f.materias || []), nome] }
        }
        return { ...f, materias_novas: [...(f.materias_novas || []), nome] }
      })
      return {
        ...prev,
        fases,
        ordem_subtopicos: { ...prev.ordem_subtopicos, [nome]: subtopicosInicial },
      }
    })
    setPickerFase(null)
  }

  function removerMateria(faseIdx, materiaIdx) {
    setConteudo((prev) => {
      const fases = prev.fases.map((f, i) => {
        if (i !== faseIdx) return f
        const all = getFaseMaterias(f)
        all.splice(materiaIdx, 1)
        if (f.numero === 1) return { ...f, materias: all, materias_novas: [] }
        return { ...f, materias: [], materias_novas: all }
      })
      return { ...prev, fases }
    })
  }

  function atualizarOrdemSubtopicos(materiaKey, novaOrdem) {
    setConteudo((prev) => ({
      ...prev,
      ordem_subtopicos: { ...prev.ordem_subtopicos, [materiaKey]: novaOrdem },
    }))
  }

  // ── Regenerar ─────────────────────────────────────────────────────────────
  async function handleRegerar() {
    if (!confirm('Isso substituirá o conteúdo atual pelo novo resultado da IA. Continuar?')) return
    setRegenerando(true)
    setErro('')
    try {
      const novo = await gerarPlano({ area: plano.area, perfil: plano.perfil })
      const parsed = parseFasesJson(novo.fases_json)
      setConteudo(parsed)
      setExpandedFase(null)
      setExpandedMateria(null)
    } catch (e) {
      setErro(e.response?.data?.detail || 'Erro ao regenerar via IA.')
    } finally {
      setRegenerando(false)
    }
  }

  // ── Salvar ────────────────────────────────────────────────────────────────
  async function handleSalvar() {
    setSalvando(true)
    setErro('')
    try {
      const atualizado = await atualizarPlano(plano.id, { conteudo })
      onSaved(atualizado)
    } catch (e) {
      setErro(e.response?.data?.detail || 'Erro ao salvar.')
    } finally {
      setSalvando(false)
    }
  }

  // ── Aplicar ───────────────────────────────────────────────────────────────
  async function handleAplicar() {
    setAplicando(true)
    setErro('')
    try {
      const res = await aplicarPlano(plano.id, modoAplicar)
      setResultadoAplicar(res)
      onSaved({ ...plano, revisado_admin: true })
    } catch (e) {
      setErro(e.response?.data?.detail || 'Erro ao aplicar.')
    } finally {
      setAplicando(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-brand-card border border-brand-border rounded-xl p-6 w-full max-w-2xl mx-4 shadow-xl max-h-[90vh] overflow-y-auto space-y-5">

        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-brand-text">Editor de Fases</h2>
            <p className="text-brand-muted text-sm capitalize">{plano.area} · {plano.perfil}</p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleRegerar}
              disabled={regenerando}
              title="Regenerar tudo via IA"
              className="px-3 py-1.5 text-xs border border-purple-500/40 text-purple-400 rounded-lg hover:bg-purple-500/10 transition-colors disabled:opacity-50 flex items-center gap-1.5"
            >
              {regenerando
                ? <><div className="w-3 h-3 border-2 border-purple-400/30 border-t-purple-400 rounded-full animate-spin" /> Regenerando…</>
                : <>↺ Regenerar IA</>
              }
            </button>
            <button onClick={onClose} className="text-brand-muted hover:text-brand-text ml-1">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Critérios do sistema (read-only) */}
        <div className="bg-brand-surface border border-brand-border rounded-lg px-4 py-3">
          <p className="text-xs font-medium text-brand-muted mb-2">Critérios de avanço do sistema (fixos)</p>
          <div className="flex flex-wrap gap-2">
            {criteriosPerfil.map((pct, i) => (
              <span key={i} className="text-xs px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                Fase {i + 1}: {pct}% de acertos
              </span>
            ))}
          </div>
        </div>

        {/* Lista de fases */}
        <div className="space-y-3">
          {conteudo.fases.length === 0 && (
            <p className="text-brand-muted text-sm italic">Nenhuma fase definida.</p>
          )}
          {conteudo.fases.map((f, faseIdx) => {
            const materias = getFaseMaterias(f)
            const isExpanded = expandedFase === faseIdx

            return (
              <div key={faseIdx} className="bg-brand-surface border border-brand-border rounded-lg overflow-hidden">
                {/* Cabeçalho da fase */}
                <div className="flex items-center gap-2 p-3">
                  <span className="w-7 h-7 rounded-full bg-indigo-500/20 text-indigo-400 text-xs font-bold flex items-center justify-center shrink-0">
                    {f.numero}
                  </span>
                  <input
                    value={f.nome}
                    onChange={(e) => atualizarFaseNome(faseIdx, e.target.value)}
                    placeholder="Nome da fase"
                    className="flex-1 bg-brand-bg border border-brand-border rounded-lg px-3 py-1.5 text-brand-text text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  />
                  <span className="text-xs text-brand-muted shrink-0">{materias.length} matéria{materias.length !== 1 ? 's' : ''}</span>
                  <button
                    onClick={() => setExpandedFase(isExpanded ? null : faseIdx)}
                    className="text-brand-muted hover:text-indigo-400 transition-colors"
                    title={isExpanded ? 'Recolher' : 'Expandir matérias'}
                  >
                    <svg className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                  <button
                    onClick={() => removerFase(faseIdx)}
                    className="text-brand-muted hover:text-red-400 transition-colors"
                    title="Remover fase"
                  >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>

                {/* Matérias expandidas */}
                {isExpanded && (
                  <div className="border-t border-brand-border px-3 pb-3 pt-2 space-y-1">
                    {materias.length === 0 && (
                      <p className="text-xs text-brand-muted italic">Nenhuma matéria nesta fase.</p>
                    )}
                    {materias.map((mat, matIdx) => {
                      const subKey = mat
                      const subs = conteudo.ordem_subtopicos[subKey] || []
                      const matExpanded = expandedMateria === `${faseIdx}-${matIdx}`

                      return (
                        <div key={matIdx} className="rounded border border-brand-border bg-brand-bg">
                          <div className="flex items-center gap-2 px-3 py-1.5">
                            <span className="flex-1 text-sm text-brand-text">{mat}</span>
                            <span className="text-xs text-brand-muted">{subs.length} subtóp.</span>
                            <button
                              onClick={() => setExpandedMateria(matExpanded ? null : `${faseIdx}-${matIdx}`)}
                              className="text-brand-muted hover:text-indigo-400 transition-colors"
                              title={matExpanded ? 'Recolher subtópicos' : 'Ver/editar subtópicos'}
                            >
                              <svg className={`w-3.5 h-3.5 transition-transform ${matExpanded ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                              </svg>
                            </button>
                            <button
                              onClick={() => removerMateria(faseIdx, matIdx)}
                              className="text-brand-muted hover:text-red-400 transition-colors"
                              title="Remover matéria"
                            >
                              ×
                            </button>
                          </div>

                          {matExpanded && (
                            <div className="border-t border-brand-border px-3 pb-2">
                              <SubtopicosList
                                materiaKey={subKey}
                                subtopicos={subs}
                                onChange={atualizarOrdemSubtopicos}
                                subtopicosDisponiveis={hierarquia.find(m => m.nome === subKey)?.blocos?.flatMap(b => b.subtopicos) ?? []}
                              />
                            </div>
                          )}
                        </div>
                      )
                    })}
                    {pickerFase === faseIdx ? (
                      <div className="flex gap-1 mt-1">
                        <select
                          autoFocus
                          value={pickerMateria}
                          onChange={e => setPickerMateria(e.target.value)}
                          className="flex-1 bg-brand-surface border border-brand-border rounded px-2 py-1 text-xs text-brand-text focus:outline-none focus:border-indigo-500"
                        >
                          <option value="">Selecione a matéria…</option>
                          {hierarquia
                            .filter(m => !conteudo.fases.flatMap(getFaseMaterias).includes(m.nome))
                            .map(m => <option key={m.id} value={m.nome}>{m.nome}</option>)}
                        </select>
                        <button
                          onClick={confirmarPickerMateria}
                          disabled={!pickerMateria}
                          className="px-2 py-1 text-xs bg-indigo-500 text-white rounded disabled:opacity-40"
                        >+</button>
                        <button
                          onClick={() => setPickerFase(null)}
                          className="px-2 py-1 text-xs text-brand-muted hover:text-brand-text"
                        >×</button>
                      </div>
                    ) : (
                      <button
                        onClick={() => adicionarMateria(faseIdx)}
                        className="w-full text-left text-xs text-brand-muted hover:text-indigo-400 transition-colors px-1 py-1"
                      >
                        + matéria
                      </button>
                    )}
                  </div>
                )}
              </div>
            )
          })}
        </div>

        <button
          onClick={adicionarFase}
          className="w-full border border-dashed border-brand-border rounded-lg py-2 text-brand-muted text-sm hover:border-indigo-500 hover:text-indigo-400 transition-colors"
        >
          + Adicionar fase
        </button>

        {erro && <p className="text-red-400 text-sm">{erro}</p>}

        {/* Modal de aplicar */}
        {mostrarAplicar && !resultadoAplicar && (
          <div className="border border-brand-border rounded-xl p-4 bg-brand-surface/50 space-y-3">
            <p className="text-sm font-medium text-brand-text">Aplicar plano a alunos</p>
            <div className="space-y-2">
              {[
                { value: 'novos', label: 'Somente novos alunos', desc: 'Aprova o plano — será usado nos próximos onboardings' },
                { value: 'todos', label: 'Todos os alunos da área', desc: `Redefine o plano para todos com área "${plano.area}"` },
              ].map((op) => (
                <button
                  key={op.value}
                  onClick={() => setModoAplicar(op.value)}
                  className={`w-full text-left border rounded-lg p-3 transition-all ${
                    modoAplicar === op.value
                      ? 'border-indigo-500 bg-indigo-500/10'
                      : 'border-brand-border hover:border-indigo-400'
                  }`}
                >
                  <p className={`text-sm font-medium ${modoAplicar === op.value ? 'text-indigo-300' : 'text-brand-text'}`}>{op.label}</p>
                  <p className="text-xs text-brand-muted mt-0.5">{op.desc}</p>
                </button>
              ))}
            </div>
            <div className="flex gap-2 justify-end">
              <button onClick={() => setMostrarAplicar(false)} className="px-3 py-1.5 text-sm text-brand-muted hover:text-brand-text transition-colors">
                Cancelar
              </button>
              <button
                onClick={handleAplicar}
                disabled={aplicando}
                className="px-4 py-1.5 text-sm bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg transition-colors disabled:opacity-50"
              >
                {aplicando ? 'Aplicando…' : 'Confirmar'}
              </button>
            </div>
          </div>
        )}

        {resultadoAplicar && (
          <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-3 text-emerald-400 text-sm">
            Plano aprovado e aplicado.
            {resultadoAplicar.perfis_atualizados > 0 && ` ${resultadoAplicar.perfis_atualizados} perfil(is) atualizado(s).`}
          </div>
        )}

        {/* Ações */}
        <div className="flex items-center justify-between pt-2 border-t border-brand-border">
          <button
            onClick={() => setMostrarAplicar((v) => !v)}
            className="px-4 py-2 text-sm border border-emerald-500/40 text-emerald-400 rounded-lg hover:bg-emerald-500/10 transition-colors"
          >
            Aprovar & Aplicar
          </button>
          <div className="flex gap-2">
            <button onClick={onClose} className="px-4 py-2 text-sm text-brand-muted hover:text-brand-text transition-colors">
              Cancelar
            </button>
            <button
              onClick={handleSalvar}
              disabled={salvando}
              className="px-4 py-2 text-sm bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors disabled:opacity-50"
            >
              {salvando ? 'Salvando…' : 'Salvar'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

// ── Página principal ──────────────────────────────────────────────────────────
export default function AdminPlanoBase() {
  const [planos, setPlanos]     = useState([])
  const [loading, setLoading]   = useState(true)
  const [erro, setErro]         = useState('')
  const [gerando, setGerando]   = useState(false)
  const [criando, setCriando]   = useState(false)
  const [genArea, setGenArea]   = useState('fiscal')
  const [genPerfil, setGenPerfil] = useState('iniciante')
  const [editarPlano, setEditarPlano]   = useState(null)
  const [filtroPendente, setFiltroPendente] = useState(false)

  function carregar() {
    setLoading(true)
    listarPlanos({ pendente_revisao: filtroPendente || undefined })
      .then(data => setPlanos(data.filter((p, i, a) => a.findIndex(x => x.id === p.id) === i)))
      .catch(() => setErro('Erro ao carregar planos.'))
      .finally(() => setLoading(false))
  }

  useEffect(() => { carregar() }, [filtroPendente]) // eslint-disable-line

  async function handleCriar() {
    setCriando(true)
    setErro('')
    try {
      const novo = await criarPlano({ area: genArea, perfil: genPerfil })
      setPlanos((prev) => [novo, ...prev])
      setEditarPlano(novo)
    } catch (e) {
      setErro(e.response?.data?.detail || 'Erro ao criar plano.')
    } finally {
      setCriando(false)
    }
  }

  async function handleGerar() {
    setGerando(true)
    setErro('')
    try {
      const novo = await gerarPlano({ area: genArea, perfil: genPerfil })
      setPlanos((prev) => [novo, ...prev])
    } catch (e) {
      setErro(e.response?.data?.detail || 'Erro ao gerar plano via IA.')
    } finally {
      setGerando(false)
    }
  }

  async function handleDeletar(id) {
    try {
      await deletarPlano(id)
      setPlanos((prev) => prev.filter((p) => p.id !== id))
    } catch {
      setErro('Erro ao deletar plano.')
    }
  }

  function handleSaved(atualizado) {
    setPlanos((prev) => prev.map((p) => (p.id === atualizado.id ? atualizado : p)))
  }

  const pendentes = planos.filter((p) => p.gerado_por_ia && !p.revisado_admin).length

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      {editarPlano && (
        <FasesEditorModal
          plano={editarPlano}
          onClose={() => setEditarPlano(null)}
          onSaved={(atualizado) => { handleSaved(atualizado); setEditarPlano(null) }}
        />
      )}

      <div className="flex items-start justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-brand-text">Planos Base</h1>
          <p className="text-brand-muted text-sm mt-1">
            {planos.length} plano{planos.length !== 1 ? 's' : ''}
            {pendentes > 0 && (
              <span className="ml-2 px-2 py-0.5 rounded bg-yellow-500/15 text-yellow-400 text-xs font-medium border border-yellow-500/20">
                {pendentes} pendente{pendentes !== 1 ? 's' : ''} de revisão
              </span>
            )}
          </p>
        </div>

        {/* Gerador IA */}
        <div className="flex flex-wrap gap-2 items-end">
          <div>
            <label className="text-xs text-brand-muted block mb-1">Área</label>
            <select value={genArea} onChange={(e) => setGenArea(e.target.value)}
              className="bg-brand-surface border border-brand-border rounded-lg px-3 py-2 text-brand-text text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500">
              {AREA_OPTIONS.map((a) => <option key={a}>{a}</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs text-brand-muted block mb-1">Perfil</label>
            <select value={genPerfil} onChange={(e) => setGenPerfil(e.target.value)}
              className="bg-brand-surface border border-brand-border rounded-lg px-3 py-2 text-brand-text text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500">
              {PERFIL_OPTIONS.map((p) => <option key={p}>{p}</option>)}
            </select>
          </div>
          <button onClick={handleGerar} disabled={gerando || criando}
            className="px-4 py-2 text-sm bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors disabled:opacity-50 flex items-center gap-2">
            {gerando ? (
              <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Gerando…</>
            ) : (
              'Gerar via IA'
            )}
          </button>
          <button onClick={handleCriar} disabled={criando || gerando}
            className="px-4 py-2 text-sm bg-brand-surface border border-brand-border hover:border-indigo-500 text-brand-text rounded-lg transition-colors disabled:opacity-50 flex items-center gap-2">
            {criando ? (
              <><div className="w-4 h-4 border-2 border-brand-border border-t-indigo-400 rounded-full animate-spin" /> Criando…</>
            ) : (
              'Criar manualmente'
            )}
          </button>
        </div>
      </div>

      <label className="flex items-center gap-2 text-sm text-brand-muted cursor-pointer w-fit">
        <input type="checkbox" checked={filtroPendente} onChange={(e) => setFiltroPendente(e.target.checked)}
          className="w-4 h-4 rounded border-brand-border accent-indigo-500" />
        Mostrar apenas pendentes de revisão
      </label>

      {erro && <p className="text-red-400 text-sm">{erro}</p>}

      {loading ? (
        <p className="text-brand-muted text-sm">Carregando…</p>
      ) : planos.length === 0 ? (
        <p className="text-brand-muted text-sm">Nenhum plano encontrado.</p>
      ) : (
        <div className="bg-brand-card border border-brand-border rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead className="border-b border-brand-border">
              <tr>
                <th className="text-left px-4 py-3 text-brand-muted font-medium text-xs uppercase">Área</th>
                <th className="text-left px-4 py-3 text-brand-muted font-medium text-xs uppercase">Perfil</th>
                <th className="text-left px-4 py-3 text-brand-muted font-medium text-xs uppercase">Fases</th>
                <th className="text-left px-4 py-3 text-brand-muted font-medium text-xs uppercase">Origem</th>
                <th className="text-left px-4 py-3 text-brand-muted font-medium text-xs uppercase">Status</th>
                <th className="text-right px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-brand-border">
              {planos.map((p) => {
                const conteudo = parseFasesJson(p.fases_json)
                return (
                  <tr key={p.id} className="hover:bg-brand-surface/50 transition-colors">
                    <td className="px-4 py-3 text-brand-text font-medium capitalize">{p.area}</td>
                    <td className="px-4 py-3 text-brand-muted capitalize">{p.perfil}</td>
                    <td className="px-4 py-3 text-brand-muted">
                      {conteudo.fases.length} fase{conteudo.fases.length !== 1 ? 's' : ''}
                    </td>
                    <td className="px-4 py-3">
                      {p.gerado_por_ia
                        ? <span className="text-xs px-2 py-0.5 rounded bg-purple-500/10 text-purple-300 border border-purple-500/20">IA</span>
                        : <span className="text-xs px-2 py-0.5 rounded bg-brand-surface text-brand-muted border border-brand-border">Manual</span>}
                    </td>
                    <td className="px-4 py-3">
                      {p.revisado_admin
                        ? <span className="text-xs px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">Aprovado</span>
                        : <span className="text-xs px-2 py-0.5 rounded bg-yellow-500/10 text-yellow-400 border border-yellow-500/20">Pendente</span>}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center justify-end gap-3">
                        <button onClick={() => setEditarPlano(p)}
                          className="text-brand-muted hover:text-indigo-400 text-xs transition-colors">
                          Editar fases
                        </button>
                        <button onClick={() => handleDeletar(p.id)}
                          className="text-brand-muted hover:text-red-400 text-xs transition-colors">
                          Deletar
                        </button>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
