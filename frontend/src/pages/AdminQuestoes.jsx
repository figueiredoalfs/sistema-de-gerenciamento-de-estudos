import { useEffect, useState } from 'react'
import { listarQuestoes, editarQuestao, deletarQuestao, sugerirSubtopico, associarSubtopicos, removerSubtopico } from '../api/adminQuestoes'
import { listarTodosTopicos, listarMaterias, listarBancas } from '../api/adminTopicos'

const LETRAS = ['A', 'B', 'C', 'D', 'E']

function parseAlts(json) {
  try { return JSON.parse(json || '{}') } catch { return {} }
}

function RowExpandida({ questao }) {
  const alts = parseAlts(questao.alternatives_json)
  const temAlts = LETRAS.some(k => alts[k])
  return (
    <tr>
      <td colSpan={6} className="px-5 pb-4 pt-1 bg-brand-surface/60">
        <p className="text-sm text-brand-text leading-relaxed mb-3">{questao.statement}</p>
        {temAlts ? (
          <div className="space-y-1">
            {LETRAS.filter(k => alts[k]).map(k => (
              <div key={k} className={`flex gap-2 text-sm ${questao.correct_answer === k ? 'text-green-400 font-semibold' : 'text-brand-muted'}`}>
                <span className="w-5 shrink-0 font-bold">{k})</span>
                <span>{alts[k]}</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-xs text-brand-muted italic">
            Questão Certo / Errado — gabarito: <span className="font-bold text-indigo-400">{questao.correct_answer === 'C' ? 'CERTO' : 'ERRADO'}</span>
          </p>
        )}
      </td>
    </tr>
  )
}

function ModalEditar({ questao, onClose, onSaved }) {
  const [form, setForm] = useState({
    materia: questao.materia || questao.subject || '',
    statement: questao.statement,
    correct_answer: questao.correct_answer,
    board: questao.board || '',
    year: questao.year || '',
  })
  const [saving, setSaving] = useState(false)
  const [erro, setErro] = useState('')

  // matéria — seletor hierárquico
  const [materias, setMaterias] = useState([])
  const [bancasModal, setBancasModal] = useState([])
  const [todosTopicos, setTodosTopicos] = useState([])
  const [materiaSel, setMateriaSel] = useState('') // id do Topico nivel=0 ou 'outra'

  // seletor manual de subtópico
  const [addMateriaSel, setAddMateriaSel] = useState('')
  const [addTopicoSel, setAddTopicoSel] = useState('')
  const [addSubtopicoSel, setAddSubtopicoSel] = useState('')
  const [adicionando, setAdicionando] = useState(false)

  // subtópicos
  const [subtopicos, setSubtopicos] = useState(questao.subtopicos || [])
  const [sugerindo, setSugerindo] = useState(false)
  const [sugestoes, setSugestoes] = useState([])
  const [erroSugestao, setErroSugestao] = useState('')

  useEffect(() => {
    listarMaterias().then(data => {
      setMaterias(data)
      const matNome = questao.materia || questao.subject || ''
      const match = data.find(m => m.nome.toLowerCase() === matNome.toLowerCase())
      setMateriaSel(match ? String(match.id) : (matNome ? 'outra' : ''))
    })
    listarTodosTopicos().then(setTodosTopicos)
    listarBancas(true).then(setBancasModal)
  }, [])

  function handle(e) {
    setForm(f => ({ ...f, [e.target.name]: e.target.value }))
  }

  function handleMateria(e) {
    const val = e.target.value
    setMateriaSel(val)
    if (val !== 'outra') {
      const m = materias.find(m => String(m.id) === val)
      if (m) setForm(f => ({ ...f, materia: m.nome }))
    }
  }

  // cascata para adicionar subtópico manualmente
  const topicosFiltrados = todosTopicos.filter(t => t.nivel === 1 && String(t.parent_id) === addMateriaSel)
  const subtopicosDisponiveis = todosTopicos.filter(t => t.nivel === 2 && String(t.parent_id) === addTopicoSel)

  async function handleAdicionarSubtopico() {
    if (!addSubtopicoSel) return
    setAdicionando(true)
    try {
      const atualizados = await associarSubtopicos(questao.id, [addSubtopicoSel])
      setSubtopicos(atualizados)
      setAddMateriaSel('')
      setAddTopicoSel('')
      setAddSubtopicoSel('')
    } catch (e) {
      setErroSugestao(e.response?.data?.detail || e.message)
    } finally {
      setAdicionando(false)
    }
  }

  async function salvar() {
    setSaving(true)
    setErro('')
    try {
      const payload = {
        materia: form.materia,
        statement: form.statement,
        correct_answer: form.correct_answer,
        board: form.board || null,
        year: form.year ? Number(form.year) : null,
      }
      const updated = await editarQuestao(questao.id, payload)
      onSaved({ ...updated, subtopicos })
    } catch (e) {
      setErro(e.response?.data?.detail || e.message)
    } finally {
      setSaving(false)
    }
  }

  async function handleSugerir() {
    setSugerindo(true)
    setErroSugestao('')
    setSugestoes([])
    try {
      const resultado = await sugerirSubtopico(questao.id)
      const existingIds = new Set(subtopicos.map(s => s.id))
      setSugestoes(resultado.filter(s => !existingIds.has(s.id)))
    } catch (e) {
      setErroSugestao(e.response?.data?.detail || e.message)
    } finally {
      setSugerindo(false)
    }
  }

  async function handleConfirmarSugestao(sug) {
    try {
      const atualizados = await associarSubtopicos(questao.id, [sug.id])
      setSubtopicos(atualizados)
      setSugestoes(s => s.filter(x => x.id !== sug.id))
    } catch (e) {
      setErroSugestao(e.response?.data?.detail || e.message)
    }
  }

  async function handleRemoverSubtopico(subtopicId) {
    try {
      await removerSubtopico(questao.id, subtopicId)
      setSubtopicos(s => s.filter(x => x.id !== subtopicId))
    } catch (e) {
      setErro(e.response?.data?.detail || e.message)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
      <div className="bg-brand-surface border border-brand-border rounded-xl p-6 w-full max-w-2xl mx-4 space-y-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-brand-text">Editar questão</h2>
          <button onClick={onClose} className="text-brand-muted hover:text-brand-text">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="space-y-3">
          <div>
            <label className="text-xs text-brand-muted">Matéria</label>
            <select
              value={materiaSel}
              onChange={handleMateria}
              className="w-full mt-1 bg-brand-card border border-brand-border rounded-lg px-3 py-2 text-sm text-brand-text focus:outline-none focus:border-indigo-500"
            >
              <option value="" disabled>Selecione uma matéria…</option>
              {materias.map(m => (
                <option key={m.id} value={String(m.id)}>{m.nome}</option>
              ))}
              <option value="outra">Outra (nova matéria)</option>
            </select>
            {materiaSel === 'outra' && (
              <input
                name="materia"
                value={form.materia}
                onChange={handle}
                placeholder="Digite o nome da nova matéria"
                className="w-full mt-2 bg-brand-card border border-yellow-500/40 rounded-lg px-3 py-2 text-sm text-brand-text focus:outline-none focus:border-yellow-500"
              />
            )}
          </div>
          <div>
            <label className="text-xs text-brand-muted">Enunciado</label>
            <textarea name="statement" value={form.statement} onChange={handle} rows={5}
              className="w-full mt-1 bg-brand-card border border-brand-border rounded-lg px-3 py-2 text-sm text-brand-text focus:outline-none focus:border-indigo-500 resize-none" />
          </div>
          <div className="flex gap-3">
            <div className="flex-1">
              <label className="text-xs text-brand-muted">Gabarito</label>
              <select name="correct_answer" value={form.correct_answer} onChange={handle}
                className="w-full mt-1 bg-brand-card border border-brand-border rounded-lg px-3 py-2 text-sm text-brand-text focus:outline-none focus:border-indigo-500">
                {['A', 'B', 'C', 'D', 'E'].map(l => <option key={l}>{l}</option>)}
              </select>
            </div>
            <div className="flex-1">
              <label className="text-xs text-brand-muted">Banca</label>
              <select name="board" value={form.board} onChange={handle}
                className="w-full mt-1 bg-brand-card border border-brand-border rounded-lg px-3 py-2 text-sm text-brand-text focus:outline-none focus:border-indigo-500">
                <option value="">Sem banca</option>
                {bancasModal.map(b => <option key={b.id} value={b.nome}>{b.nome}</option>)}
              </select>
            </div>
            <div className="w-24">
              <label className="text-xs text-brand-muted">Ano</label>
              <input name="year" type="number" value={form.year} onChange={handle}
                className="w-full mt-1 bg-brand-card border border-brand-border rounded-lg px-3 py-2 text-sm text-brand-text focus:outline-none focus:border-indigo-500" />
            </div>
          </div>

          {/* Subtópicos */}
          <div className="border border-brand-border rounded-lg p-3 space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-xs text-brand-muted font-medium">Subtópicos vinculados</label>
              <button
                type="button"
                onClick={handleSugerir}
                disabled={sugerindo}
                className="flex items-center gap-1.5 px-3 py-1 text-xs rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-400 border border-indigo-500/30 disabled:opacity-50 transition-colors"
              >
                {sugerindo ? (
                  <>
                    <svg className="w-3 h-3 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                    </svg>
                    Consultando IA…
                  </>
                ) : 'Sugerir Subtópico'}
              </button>
            </div>

            {subtopicos.length === 0 ? (
              <p className="text-xs text-yellow-500/70 italic">Nenhum subtópico vinculado</p>
            ) : (
              <div className="flex flex-wrap gap-1.5">
                {subtopicos.map(s => (
                  <span key={s.id} className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-brand-card border border-brand-border text-xs text-brand-text">
                    {s.nome}
                    {s.fonte === 'ia' && <span className="text-indigo-400/70 ml-0.5">IA</span>}
                    <button
                      type="button"
                      onClick={() => handleRemoverSubtopico(s.id)}
                      className="ml-0.5 text-brand-muted hover:text-red-400 transition-colors"
                    >×</button>
                  </span>
                ))}
              </div>
            )}

            {erroSugestao && <p className="text-red-400 text-xs">{erroSugestao}</p>}

            {sugestoes.length > 0 && (
              <div className="mt-2 pt-2 border-t border-brand-border space-y-1">
                <p className="text-xs text-indigo-400 font-medium">Sugestões da IA — clique para confirmar:</p>
                <div className="flex flex-wrap gap-1.5">
                  {sugestoes.map(s => (
                    <button
                      key={s.id}
                      type="button"
                      onClick={() => handleConfirmarSugestao(s)}
                      className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-xs text-indigo-300 hover:bg-indigo-500/20 transition-colors"
                    >
                      + {s.nome}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {!sugerindo && sugestoes.length === 0 && erroSugestao === '' && subtopicos.length > 0 && (
              <p className="text-xs text-brand-muted/50 italic hidden" />
            )}

            {/* Seletor manual de subtópico */}
            <div className="mt-3 pt-3 border-t border-brand-border space-y-2">
              <p className="text-xs text-brand-muted font-medium">Adicionar subtópico manualmente</p>
              <div className="flex flex-col gap-1.5">
                <select
                  value={addMateriaSel}
                  onChange={e => { setAddMateriaSel(e.target.value); setAddTopicoSel(''); setAddSubtopicoSel('') }}
                  className="w-full bg-brand-card border border-brand-border rounded-lg px-2 py-1.5 text-xs text-brand-text focus:outline-none focus:border-indigo-500"
                >
                  <option value="">Matéria…</option>
                  {todosTopicos.filter(t => t.nivel === 0).map(m => (
                    <option key={m.id} value={String(m.id)}>{m.nome}</option>
                  ))}
                </select>
                {addMateriaSel && (
                  <select
                    value={addTopicoSel}
                    onChange={e => { setAddTopicoSel(e.target.value); setAddSubtopicoSel('') }}
                    className="w-full bg-brand-card border border-brand-border rounded-lg px-2 py-1.5 text-xs text-brand-text focus:outline-none focus:border-indigo-500"
                  >
                    <option value="">Tópico…</option>
                    {topicosFiltrados.map(t => (
                      <option key={t.id} value={String(t.id)}>{t.nome}</option>
                    ))}
                  </select>
                )}
                {addTopicoSel && (
                  <select
                    value={addSubtopicoSel}
                    onChange={e => setAddSubtopicoSel(e.target.value)}
                    className="w-full bg-brand-card border border-brand-border rounded-lg px-2 py-1.5 text-xs text-brand-text focus:outline-none focus:border-indigo-500"
                  >
                    <option value="">Subtópico…</option>
                    {subtopicosDisponiveis.map(s => (
                      <option key={s.id} value={String(s.id)}>{s.nome}</option>
                    ))}
                  </select>
                )}
                {addSubtopicoSel && (
                  <button
                    type="button"
                    onClick={handleAdicionarSubtopico}
                    disabled={adicionando}
                    className="self-start px-3 py-1 text-xs rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-400 border border-indigo-500/30 disabled:opacity-50 transition-colors"
                  >
                    {adicionando ? 'Adicionando…' : 'Adicionar'}
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>

        {erro && <p className="text-red-400 text-sm">{erro}</p>}

        <div className="flex justify-end gap-3 pt-2">
          <button onClick={onClose}
            className="px-4 py-2 text-sm rounded-lg border border-brand-border text-brand-muted hover:text-brand-text transition-colors">
            Cancelar
          </button>
          <button onClick={salvar} disabled={saving}
            className="px-4 py-2 text-sm rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium disabled:opacity-50 transition-colors">
            {saving ? 'Salvando…' : 'Salvar'}
          </button>
        </div>
      </div>
    </div>
  )
}

function ModalConfirmarDelete({ questao, onClose, onConfirm, deleting }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
      <div className="bg-brand-surface border border-brand-border rounded-xl p-6 w-full max-w-md mx-4 space-y-4">
        <h2 className="text-lg font-bold text-brand-text">Confirmar exclusão</h2>
        <p className="text-brand-muted text-sm">
          Tem certeza que deseja deletar a questão <span className="text-brand-text font-mono">{questao.question_code}</span>?
          Esta ação não pode ser desfeita.
        </p>
        <div className="flex justify-end gap-3 pt-2">
          <button onClick={onClose}
            className="px-4 py-2 text-sm rounded-lg border border-brand-border text-brand-muted hover:text-brand-text transition-colors">
            Cancelar
          </button>
          <button onClick={onConfirm} disabled={deleting}
            className="px-4 py-2 text-sm rounded-lg bg-red-600 hover:bg-red-500 text-white font-medium disabled:opacity-50 transition-colors">
            {deleting ? 'Deletando…' : 'Deletar'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default function AdminQuestoes() {
  const [questoes, setQuestoes] = useState([])
  const [loading, setLoading] = useState(true)
  const [erro, setErro] = useState('')

  const [filtroMateria, setFiltroMateria] = useState('')
  const [filtroSubtopico, setFiltroSubtopico] = useState('')
  const [filtroBanca, setFiltroBanca] = useState('')
  const [filtroAno, setFiltroAno] = useState('')
  const [page, setPage] = useState(1)
  const [totalBanco, setTotalBanco] = useState(0)
  const [totalFiltro, setTotalFiltro] = useState(0)

  const [topicos, setTopicos] = useState([])
  const [bancasLista, setBancasLista] = useState([])
  useEffect(() => {
    listarTodosTopicos().then(setTopicos).catch(() => {})
    listarBancas(true).then(setBancasLista).catch(() => {})
  }, [])

  const materias = topicos.filter(t => t.nivel === 0).sort((a, b) => a.nome.localeCompare(b.nome))
  const subtopicosDisponiveis = (() => {
    const subs = topicos.filter(t => t.nivel === 2)
    if (!filtroMateria) return subs.sort((a, b) => a.nome.localeCompare(b.nome))
    const materia = materias.find(m => m.nome === filtroMateria)
    if (!materia) return []
    const blocoIds = new Set(topicos.filter(t => t.nivel === 1 && t.parent_id === materia.id).map(t => t.id))
    return subs.filter(s => blocoIds.has(s.parent_id)).sort((a, b) => a.nome.localeCompare(b.nome))
  })()
  const PER_PAGE = 20

  const [expandedId, setExpandedId] = useState(null)
  const [editando, setEditando] = useState(null)
  const [deletando, setDeletando] = useState(null)
  const [deletandoId, setDeletandoId] = useState(false)

  function buscar(pg = 1, overrides = {}) {
    const materia = 'materia' in overrides ? overrides.materia : filtroMateria
    const subtopico = 'subtopico' in overrides ? overrides.subtopico : filtroSubtopico
    const banca = 'banca' in overrides ? overrides.banca : filtroBanca
    const ano = 'ano' in overrides ? overrides.ano : filtroAno
    setLoading(true)
    setErro('')
    setExpandedId(null)
    listarQuestoes({ materia, subtopico, banca, ano: ano ? Number(ano) : undefined, page: pg, per_page: PER_PAGE })
      .then(({ questoes: data, totalFiltro: tf, totalBanco: tb }) => {
        setQuestoes(data)
        setTotalFiltro(tf)
        setTotalBanco(tb)
        setPage(pg)
      })
      .catch(e => setErro(e.response?.data?.detail || e.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => { buscar(1) }, []) // eslint-disable-line

  function handleFiltrar(e) {
    e.preventDefault()
    buscar(1)
  }

  function handleSaved(updated) {
    setQuestoes(qs => qs.map(q => q.id === updated.id ? updated : q))
    setEditando(null)
  }

  async function handleDelete() {
    setDeletandoId(true)
    try {
      await deletarQuestao(deletando.id)
      setQuestoes(qs => qs.filter(q => q.id !== deletando.id))
      setDeletando(null)
    } catch (e) {
      setErro(e.response?.data?.detail || e.message)
      setDeletando(null)
    } finally {
      setDeletandoId(false)
    }
  }

  const temProxima = questoes.length === PER_PAGE
  const temAnterior = page > 1

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-brand-text">Questões</h1>
        <div className="flex items-center gap-3 text-sm text-brand-muted">
          <span>Banco: <span className="text-brand-text font-medium">{totalBanco}</span></span>
          {(filtroMateria || filtroSubtopico || filtroBanca || filtroAno) && (
            <span>· Filtro: <span className="text-indigo-400 font-medium">{totalFiltro}</span></span>
          )}
          <span className="text-brand-border">|</span>
          <span>pág. {page}</span>
        </div>
      </div>

      {/* Filtros */}
      <form onSubmit={handleFiltrar} className="flex flex-wrap gap-3 items-end">
        <div>
          <label className="text-xs text-brand-muted block mb-1">Matéria</label>
          <select
            value={filtroMateria}
            onChange={e => { setFiltroMateria(e.target.value); setFiltroSubtopico('') }}
            className="bg-brand-card border border-brand-border rounded-lg px-3 py-2 text-sm text-brand-text focus:outline-none focus:border-indigo-500 w-48"
          >
            <option value="">Todas</option>
            {materias.map(m => <option key={m.id} value={m.nome}>{m.nome}</option>)}
          </select>
        </div>
        <div>
          <label className="text-xs text-brand-muted block mb-1">Subtópico</label>
          <select
            value={filtroSubtopico}
            onChange={e => setFiltroSubtopico(e.target.value)}
            className="bg-brand-card border border-brand-border rounded-lg px-3 py-2 text-sm text-brand-text focus:outline-none focus:border-indigo-500 w-48"
          >
            <option value="">Todos</option>
            {subtopicosDisponiveis.map(s => <option key={s.id} value={s.nome}>{s.nome}</option>)}
          </select>
        </div>
        <div>
          <label className="text-xs text-brand-muted block mb-1">Banca</label>
          <select
            value={filtroBanca}
            onChange={e => setFiltroBanca(e.target.value)}
            className="bg-brand-card border border-brand-border rounded-lg px-3 py-2 text-sm text-brand-text focus:outline-none focus:border-indigo-500 w-36"
          >
            <option value="">Todas</option>
            {bancasLista.map(b => <option key={b.id} value={b.nome}>{b.nome}</option>)}
          </select>
        </div>
        <div>
          <label className="text-xs text-brand-muted block mb-1">Ano</label>
          <input
            type="number"
            value={filtroAno}
            onChange={e => setFiltroAno(e.target.value)}
            placeholder="ex: 2023"
            className="bg-brand-card border border-brand-border rounded-lg px-3 py-2 text-sm text-brand-text focus:outline-none focus:border-indigo-500 w-28"
          />
        </div>
        <button type="submit"
          className="px-4 py-2 text-sm rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium transition-colors">
          Filtrar
        </button>
        <button type="button" onClick={() => {
          setFiltroMateria(''); setFiltroSubtopico(''); setFiltroBanca(''); setFiltroAno('')
          buscar(1, { materia: '', subtopico: '', banca: '', ano: '' })
        }}
          className="px-4 py-2 text-sm rounded-lg border border-brand-border text-brand-muted hover:text-brand-text transition-colors">
          Limpar
        </button>
      </form>

      {erro && <p className="text-red-400 text-sm">{erro}</p>}

      {loading ? (
        <p className="text-brand-muted text-sm">Carregando…</p>
      ) : questoes.length === 0 && page === 1 ? (
        <p className="text-brand-muted text-sm">Nenhuma questão encontrada.</p>
      ) : questoes.length === 0 ? null : (
        <div className="bg-brand-card border border-brand-border rounded-xl overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="border-b border-brand-border">
              <tr>
                <th className="text-left px-4 py-3 text-brand-muted font-medium">Código</th>
                <th className="text-left px-4 py-3 text-brand-muted font-medium">Matéria</th>
                <th className="text-left px-4 py-3 text-brand-muted font-medium">Banca / Ano</th>
                <th className="text-left px-4 py-3 text-brand-muted font-medium">Subtópicos</th>
                <th className="text-left px-4 py-3 text-brand-muted font-medium">Gabarito</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-brand-border">
              {questoes.map(q => {
                const expanded = expandedId === q.id
                return (
                  <>
                    <tr
                      key={q.id}
                      onClick={() => setExpandedId(expanded ? null : q.id)}
                      className="hover:bg-brand-surface transition-colors cursor-pointer select-none"
                    >
                      <td className="px-4 py-3 font-mono text-xs text-brand-muted whitespace-nowrap">{q.question_code}</td>
                      <td className="px-4 py-3 max-w-xs truncate">
                        <span className="text-brand-text">{q.materia || q.subject}</span>
                        {q.materia_pendente && (
                          <span className="ml-1.5 text-xs text-yellow-400/80">⚠</span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-brand-muted whitespace-nowrap">{q.board || '—'} {q.year || ''}</td>
                      <td className="px-4 py-3 text-brand-muted max-w-xs truncate">
                        {q.subtopicos?.length > 0
                          ? q.subtopicos.map(s => s.nome).join(', ')
                          : <span className="text-xs text-yellow-500/70">sem subtópico</span>}
                      </td>
                      <td className="px-4 py-3">
                        <span className="px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 font-bold text-xs">{q.correct_answer}</span>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap" onClick={e => e.stopPropagation()}>
                        <button onClick={() => setEditando(q)}
                          className="text-brand-muted hover:text-indigo-400 transition-colors mr-3 text-xs">
                          Editar
                        </button>
                        <button onClick={() => setDeletando(q)}
                          className="text-brand-muted hover:text-red-400 transition-colors text-xs">
                          Deletar
                        </button>
                      </td>
                    </tr>
                    {expanded && <RowExpandida key={`exp-${q.id}`} questao={q} />}
                  </>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Paginação — sempre visível se há navegação possível */}
      {!loading && (temAnterior || temProxima) && (
        <div className="flex gap-3 items-center">
          <button
            onClick={() => buscar(page - 1)}
            disabled={!temAnterior}
            className="px-3 py-1.5 text-sm rounded-lg border border-brand-border text-brand-muted hover:text-brand-text disabled:opacity-40 transition-colors">
            ← Anterior
          </button>
          <span className="text-brand-muted text-sm">Página {page}</span>
          <button
            onClick={() => buscar(page + 1)}
            disabled={!temProxima}
            className="px-3 py-1.5 text-sm rounded-lg border border-brand-border text-brand-muted hover:text-brand-text disabled:opacity-40 transition-colors">
            Próxima →
          </button>
        </div>
      )}

      {editando && (
        <ModalEditar questao={editando} onClose={() => setEditando(null)} onSaved={handleSaved} />
      )}
      {deletando && (
        <ModalConfirmarDelete
          questao={deletando}
          onClose={() => setDeletando(null)}
          onConfirm={handleDelete}
          deleting={deletandoId}
        />
      )}
    </div>
  )
}
