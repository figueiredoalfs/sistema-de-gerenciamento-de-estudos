import { useEffect, useState } from 'react'
import {
  listarPendencias, resolverMateria, resolverBanca,
  reclassificarPendencias, resolverMateriaLote, resolverBancaLote,
} from '../api/adminQuestoes'
import { listarMaterias, listarBancas } from '../api/adminTopicos'

export default function AdminPendencias() {
  const [questoes, setQuestoes] = useState([])
  const [materias, setMaterias] = useState([])
  const [bancas, setBancas] = useState([])
  const [loading, setLoading] = useState(true)
  const [erro, setErro] = useState('')

  // estado por questão: { [id]: { mat: { acao, topico_id, salvando, erro }, ban: { acao, banca_id, salvando, erro } } }
  const [res, setRes] = useState({})
  const [reclassificando, setReclassificando] = useState(false)

  // seleção para lote
  const [selecionadas, setSelecionadas] = useState(new Set())
  const [lote, setLote] = useState({
    mat: { acao: 'vincular', topico_id: '', salvando: false, erro: '' },
    ban: { acao: 'vincular', banca_id: '', salvando: false, erro: '' },
  })

  useEffect(() => {
    Promise.all([listarPendencias(), listarMaterias(), listarBancas(true)])
      .then(([qs, ms, bs]) => { setQuestoes(qs); setMaterias(ms); setBancas(bs) })
      .catch(e => setErro(e.response?.data?.detail || e.message))
      .finally(() => setLoading(false))
  }, [])

  function patchRes(id, tipo, patch) {
    setRes(r => ({ ...r, [id]: { ...r[id], [tipo]: { ...(r[id]?.[tipo] || {}), ...patch } } }))
  }

  function patchLote(tipo, patch) {
    setLote(l => ({ ...l, [tipo]: { ...l[tipo], ...patch } }))
  }

  function materiaInvalida(q) {
    if (!q.materia) return true
    return !materias.some(m => m.nome.toLowerCase() === (q.materia || '').toLowerCase())
  }

  function bancaInvalida(q) {
    if (!q.board) return false
    return !bancas.some(b => b.nome.toLowerCase() === (q.board || '').toLowerCase())
  }

  function toggleSelecionada(id) {
    setSelecionadas(prev => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id); else next.add(id)
      return next
    })
  }

  function toggleTodas() {
    if (selecionadas.size === questoes.length) {
      setSelecionadas(new Set())
    } else {
      setSelecionadas(new Set(questoes.map(q => q.id)))
    }
  }

  function aplicarLoteResult(data) {
    setQuestoes(data.pendentes)
    setSelecionadas(new Set())
    setRes({})
  }

  async function handleResolverMateria(q) {
    const r = res[q.id]?.mat || {}
    if (!r.acao) return
    if (r.acao === 'vincular' && !r.topico_id) return
    patchRes(q.id, 'mat', { salvando: true, erro: '' })
    try {
      const updated = await resolverMateria(q.id, {
        acao: r.acao,
        topico_id: r.acao === 'vincular' ? r.topico_id : undefined,
        nova_materia: r.acao === 'criar' ? q.materia : undefined,
      })
      if (updated.materia_pendente) {
        setQuestoes(prev => prev.map(x => x.id === q.id ? updated : x))
        patchRes(q.id, 'mat', { salvando: false, acao: '', topico_id: '' })
      } else {
        setQuestoes(prev => prev.filter(x => x.id !== q.id))
        setSelecionadas(prev => { const next = new Set(prev); next.delete(q.id); return next })
      }
    } catch (e) {
      patchRes(q.id, 'mat', { salvando: false, erro: e.response?.data?.detail || e.message })
    }
  }

  async function handleResolverBanca(q) {
    const r = res[q.id]?.ban || {}
    if (!r.acao) return
    if (r.acao === 'vincular' && !r.banca_id) return
    patchRes(q.id, 'ban', { salvando: true, erro: '' })
    try {
      const updated = await resolverBanca(q.id, {
        acao: r.acao,
        banca_id: r.acao === 'vincular' ? r.banca_id : undefined,
        nova_banca: r.acao === 'criar' ? q.board : undefined,
      })
      if (updated.materia_pendente) {
        setQuestoes(prev => prev.map(x => x.id === q.id ? updated : x))
        patchRes(q.id, 'ban', { salvando: false, acao: '', banca_id: '' })
      } else {
        setQuestoes(prev => prev.filter(x => x.id !== q.id))
        setSelecionadas(prev => { const next = new Set(prev); next.delete(q.id); return next })
      }
    } catch (e) {
      patchRes(q.id, 'ban', { salvando: false, erro: e.response?.data?.detail || e.message })
    }
  }

  async function handleReclassificar() {
    setReclassificando(true)
    try {
      await reclassificarPendencias()
      const [qs, ms, bs] = await Promise.all([listarPendencias(), listarMaterias(), listarBancas(true)])
      setQuestoes(qs); setMaterias(ms); setBancas(bs)
      setSelecionadas(new Set()); setRes({})
    } catch (e) {
      setErro(e.response?.data?.detail || e.message)
    } finally {
      setReclassificando(false)
    }
  }

  async function handleLoteMateria() {
    const ids = Array.from(selecionadas)
    if (!ids.length) return
    const l = lote.mat
    if (l.acao === 'vincular' && !l.topico_id) return
    patchLote('mat', { salvando: true, erro: '' })
    try {
      const data = await resolverMateriaLote({
        question_ids: ids,
        acao: l.acao,
        topico_id: l.acao === 'vincular' ? l.topico_id : undefined,
        nova_materia: l.acao === 'criar' ? l.nova_materia : undefined,
      })
      aplicarLoteResult(data)
      patchLote('mat', { salvando: false, acao: 'vincular', topico_id: '', nova_materia: '' })
      const [ms, bs] = await Promise.all([listarMaterias(), listarBancas(true)])
      setMaterias(ms); setBancas(bs)
    } catch (e) {
      patchLote('mat', { salvando: false, erro: e.response?.data?.detail || e.message })
    }
  }

  async function handleLoteBanca() {
    const ids = Array.from(selecionadas)
    if (!ids.length) return
    const l = lote.ban
    if (l.acao === 'vincular' && !l.banca_id) return
    patchLote('ban', { salvando: true, erro: '' })
    try {
      const data = await resolverBancaLote({
        question_ids: ids,
        acao: l.acao,
        banca_id: l.acao === 'vincular' ? l.banca_id : undefined,
        nova_banca: l.acao === 'criar' ? l.nova_banca : undefined,
      })
      aplicarLoteResult(data)
      patchLote('ban', { salvando: false, acao: 'vincular', banca_id: '', nova_banca: '' })
      const [ms, bs] = await Promise.all([listarMaterias(), listarBancas(true)])
      setMaterias(ms); setBancas(bs)
    } catch (e) {
      patchLote('ban', { salvando: false, erro: e.response?.data?.detail || e.message })
    }
  }

  const temMateriaSelecionada = questoes.some(q => selecionadas.has(q.id) && materiaInvalida(q))
  const temBancaSelecionada = questoes.some(q => selecionadas.has(q.id) && bancaInvalida(q))

  return (
    <div className="p-6 space-y-6 max-w-5xl mx-auto">
      {/* Cabeçalho */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-brand-text">Pendências de validação</h1>
          <p className="text-sm text-brand-muted mt-1">
            Questões com matéria ou banca não reconhecida. Resolva cada item para remover da fila.
          </p>
        </div>
        <button
          onClick={handleReclassificar}
          disabled={reclassificando}
          className="flex-shrink-0 px-4 py-2 text-sm rounded-lg bg-brand-card border border-brand-border text-brand-muted hover:text-brand-text hover:border-indigo-500 disabled:opacity-40 transition-colors"
        >
          {reclassificando ? 'Reclassificando…' : 'Reclassificar tudo'}
        </button>
      </div>

      {erro && <p className="text-red-400 text-sm">{erro}</p>}

      {loading ? (
        <p className="text-brand-muted text-sm">Carregando…</p>
      ) : questoes.length === 0 ? (
        <div className="bg-brand-card border border-brand-border rounded-xl p-8 text-center">
          <p className="text-green-400 font-medium">Nenhuma pendência</p>
          <p className="text-brand-muted text-sm mt-1">Todas as matérias e bancas estão validadas.</p>
        </div>
      ) : (
        <>
          {/* Barra de lote */}
          {selecionadas.size > 0 && (
            <div className="bg-indigo-950/60 border border-indigo-500/30 rounded-xl p-4 space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-semibold text-indigo-300">
                  {selecionadas.size} questão(ões) selecionada(s)
                </span>
                <button
                  onClick={() => setSelecionadas(new Set())}
                  className="text-xs text-brand-muted hover:text-brand-text transition-colors"
                >
                  Limpar seleção
                </button>
              </div>

              {/* Lote matéria */}
              {temMateriaSelecionada && (
                <div className="space-y-2 border-t border-indigo-500/20 pt-3">
                  <p className="text-xs font-semibold text-yellow-400">Resolver matéria em lote</p>
                  <div className="flex flex-wrap gap-4 items-end">
                    <div className="flex items-center gap-3">
                      <label className="flex items-center gap-1.5 cursor-pointer text-sm text-brand-text">
                        <input type="radio" name="lote-mat-acao" value="vincular"
                          checked={lote.mat.acao === 'vincular'}
                          onChange={() => patchLote('mat', { acao: 'vincular', topico_id: '' })}
                          className="accent-indigo-500" />
                        Vincular existente
                      </label>
                      <label className="flex items-center gap-1.5 cursor-pointer text-sm text-brand-text">
                        <input type="radio" name="lote-mat-acao" value="criar"
                          checked={lote.mat.acao === 'criar'}
                          onChange={() => patchLote('mat', { acao: 'criar', topico_id: '' })}
                          className="accent-indigo-500" />
                        Criar nova
                      </label>
                    </div>
                    {lote.mat.acao === 'vincular' ? (
                      <select
                        value={lote.mat.topico_id || ''}
                        onChange={e => patchLote('mat', { topico_id: e.target.value })}
                        className="flex-1 min-w-[200px] bg-brand-surface border border-brand-border rounded-lg px-3 py-1.5 text-sm text-brand-text focus:outline-none focus:border-indigo-500"
                      >
                        <option value="">Selecione a matéria…</option>
                        {materias.map(m => <option key={m.id} value={String(m.id)}>{m.nome}</option>)}
                      </select>
                    ) : (
                      <input
                        type="text"
                        placeholder="Nome da nova matéria"
                        value={lote.mat.nova_materia || ''}
                        onChange={e => patchLote('mat', { nova_materia: e.target.value })}
                        className="flex-1 min-w-[200px] bg-brand-surface border border-brand-border rounded-lg px-3 py-1.5 text-sm text-brand-text focus:outline-none focus:border-indigo-500"
                      />
                    )}
                    <button
                      onClick={handleLoteMateria}
                      disabled={
                        lote.mat.salvando ||
                        (lote.mat.acao === 'vincular' && !lote.mat.topico_id) ||
                        (lote.mat.acao === 'criar' && !lote.mat.nova_materia?.trim())
                      }
                      className="px-4 py-1.5 text-sm rounded-lg bg-yellow-600 hover:bg-yellow-500 text-white font-medium disabled:opacity-40 transition-colors whitespace-nowrap"
                    >
                      {lote.mat.salvando ? 'Aplicando…' : 'Aplicar matéria'}
                    </button>
                  </div>
                  {lote.mat.erro && <p className="text-red-400 text-xs">{lote.mat.erro}</p>}
                </div>
              )}

              {/* Lote banca */}
              {temBancaSelecionada && (
                <div className="space-y-2 border-t border-indigo-500/20 pt-3">
                  <p className="text-xs font-semibold text-orange-400">Resolver banca em lote</p>
                  <div className="flex flex-wrap gap-4 items-end">
                    <div className="flex items-center gap-3">
                      <label className="flex items-center gap-1.5 cursor-pointer text-sm text-brand-text">
                        <input type="radio" name="lote-ban-acao" value="vincular"
                          checked={lote.ban.acao === 'vincular'}
                          onChange={() => patchLote('ban', { acao: 'vincular', banca_id: '' })}
                          className="accent-indigo-500" />
                        Vincular existente
                      </label>
                      <label className="flex items-center gap-1.5 cursor-pointer text-sm text-brand-text">
                        <input type="radio" name="lote-ban-acao" value="criar"
                          checked={lote.ban.acao === 'criar'}
                          onChange={() => patchLote('ban', { acao: 'criar', banca_id: '' })}
                          className="accent-indigo-500" />
                        Criar nova
                      </label>
                    </div>
                    {lote.ban.acao === 'vincular' ? (
                      <select
                        value={lote.ban.banca_id || ''}
                        onChange={e => patchLote('ban', { banca_id: e.target.value })}
                        className="flex-1 min-w-[200px] bg-brand-surface border border-brand-border rounded-lg px-3 py-1.5 text-sm text-brand-text focus:outline-none focus:border-indigo-500"
                      >
                        <option value="">Selecione a banca…</option>
                        {bancas.map(b => <option key={b.id} value={b.id}>{b.nome}</option>)}
                      </select>
                    ) : (
                      <input
                        type="text"
                        placeholder="Nome da nova banca"
                        value={lote.ban.nova_banca || ''}
                        onChange={e => patchLote('ban', { nova_banca: e.target.value })}
                        className="flex-1 min-w-[200px] bg-brand-surface border border-brand-border rounded-lg px-3 py-1.5 text-sm text-brand-text focus:outline-none focus:border-indigo-500"
                      />
                    )}
                    <button
                      onClick={handleLoteBanca}
                      disabled={
                        lote.ban.salvando ||
                        (lote.ban.acao === 'vincular' && !lote.ban.banca_id) ||
                        (lote.ban.acao === 'criar' && !lote.ban.nova_banca?.trim())
                      }
                      className="px-4 py-1.5 text-sm rounded-lg bg-orange-600 hover:bg-orange-500 text-white font-medium disabled:opacity-40 transition-colors whitespace-nowrap"
                    >
                      {lote.ban.salvando ? 'Aplicando…' : 'Aplicar banca'}
                    </button>
                  </div>
                  {lote.ban.erro && <p className="text-red-400 text-xs">{lote.ban.erro}</p>}
                </div>
              )}
            </div>
          )}

          {/* Cabeçalho da lista com select-all */}
          <div className="flex items-center gap-3 px-1">
            <input
              type="checkbox"
              checked={selecionadas.size === questoes.length && questoes.length > 0}
              ref={el => { if (el) el.indeterminate = selecionadas.size > 0 && selecionadas.size < questoes.length }}
              onChange={toggleTodas}
              className="accent-indigo-500 w-4 h-4 cursor-pointer"
            />
            <span className="text-xs text-brand-muted">
              Selecionar todas ({questoes.length})
            </span>
          </div>

          <div className="space-y-3">
            {questoes.map(q => {
              const matInv = materiaInvalida(q)
              const banInv = bancaInvalida(q)
              const rMat = res[q.id]?.mat || {}
              const rBan = res[q.id]?.ban || {}
              const sel = selecionadas.has(q.id)
              return (
                <div
                  key={q.id}
                  className={`bg-brand-card border rounded-xl p-4 space-y-3 transition-colors ${sel ? 'border-indigo-500/50' : 'border-brand-border'}`}
                >
                  {/* Cabeçalho da questão */}
                  <div className="flex items-start gap-3">
                    <input
                      type="checkbox"
                      checked={sel}
                      onChange={() => toggleSelecionada(q.id)}
                      className="accent-indigo-500 w-4 h-4 mt-1 cursor-pointer flex-shrink-0"
                    />
                    <div className="flex-1 min-w-0">
                      <p className="font-mono text-xs text-brand-muted">{q.question_code}</p>
                      <div className="flex flex-wrap gap-3 mt-1">
                        {matInv && (
                          <span className="text-sm text-yellow-400">
                            Matéria: <strong>"{q.materia || '(vazia)'}"</strong>
                          </span>
                        )}
                        {banInv && (
                          <span className="text-sm text-orange-400">
                            Banca: <strong>"{q.board}"</strong>
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-brand-muted mt-1 line-clamp-2">{q.statement}</p>
                    </div>
                  </div>

                  {/* Resolução de Matéria */}
                  {matInv && (
                    <div className="border-t border-brand-border pt-3 space-y-2 ml-7">
                      <p className="text-xs font-semibold text-yellow-400">Resolver matéria</p>
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input type="radio" name={`mat-${q.id}`} value="vincular"
                          checked={rMat.acao === 'vincular'}
                          onChange={() => patchRes(q.id, 'mat', { acao: 'vincular', topico_id: '' })}
                          className="accent-indigo-500" />
                        <span className="text-sm text-brand-text">Vincular a matéria existente</span>
                      </label>
                      {rMat.acao === 'vincular' && (
                        <select
                          value={rMat.topico_id || ''}
                          onChange={e => patchRes(q.id, 'mat', { topico_id: e.target.value })}
                          className="w-full bg-brand-surface border border-brand-border rounded-lg px-3 py-1.5 text-sm text-brand-text focus:outline-none focus:border-indigo-500 ml-5"
                        >
                          <option value="">Selecione a matéria…</option>
                          {materias.map(m => <option key={m.id} value={String(m.id)}>{m.nome}</option>)}
                        </select>
                      )}
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input type="radio" name={`mat-${q.id}`} value="criar"
                          checked={rMat.acao === 'criar'}
                          onChange={() => patchRes(q.id, 'mat', { acao: 'criar' })}
                          className="accent-indigo-500" />
                        <span className="text-sm text-brand-text">
                          Criar nova matéria <span className="text-yellow-400 font-semibold">"{q.materia}"</span>
                        </span>
                      </label>
                      {rMat.erro && <p className="text-red-400 text-xs ml-5">{rMat.erro}</p>}
                      <div className="flex justify-end">
                        <button
                          onClick={() => handleResolverMateria(q)}
                          disabled={!rMat.acao || (rMat.acao === 'vincular' && !rMat.topico_id) || rMat.salvando}
                          className="px-4 py-1.5 text-sm rounded-lg bg-yellow-600 hover:bg-yellow-500 text-white font-medium disabled:opacity-40 transition-colors"
                        >
                          {rMat.salvando ? 'Salvando…' : 'Confirmar matéria'}
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Resolução de Banca */}
                  {banInv && (
                    <div className="border-t border-brand-border pt-3 space-y-2 ml-7">
                      <p className="text-xs font-semibold text-orange-400">Resolver banca</p>
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input type="radio" name={`ban-${q.id}`} value="vincular"
                          checked={rBan.acao === 'vincular'}
                          onChange={() => patchRes(q.id, 'ban', { acao: 'vincular', banca_id: '' })}
                          className="accent-indigo-500" />
                        <span className="text-sm text-brand-text">Vincular a banca existente</span>
                      </label>
                      {rBan.acao === 'vincular' && (
                        <select
                          value={rBan.banca_id || ''}
                          onChange={e => patchRes(q.id, 'ban', { banca_id: e.target.value })}
                          className="w-full bg-brand-surface border border-brand-border rounded-lg px-3 py-1.5 text-sm text-brand-text focus:outline-none focus:border-indigo-500 ml-5"
                        >
                          <option value="">Selecione a banca…</option>
                          {bancas.map(b => <option key={b.id} value={b.id}>{b.nome}</option>)}
                        </select>
                      )}
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input type="radio" name={`ban-${q.id}`} value="criar"
                          checked={rBan.acao === 'criar'}
                          onChange={() => patchRes(q.id, 'ban', { acao: 'criar' })}
                          className="accent-indigo-500" />
                        <span className="text-sm text-brand-text">
                          Criar nova banca <span className="text-orange-400 font-semibold">"{q.board}"</span>
                        </span>
                      </label>
                      {rBan.erro && <p className="text-red-400 text-xs ml-5">{rBan.erro}</p>}
                      <div className="flex justify-end">
                        <button
                          onClick={() => handleResolverBanca(q)}
                          disabled={!rBan.acao || (rBan.acao === 'vincular' && !rBan.banca_id) || rBan.salvando}
                          className="px-4 py-1.5 text-sm rounded-lg bg-orange-600 hover:bg-orange-500 text-white font-medium disabled:opacity-40 transition-colors"
                        >
                          {rBan.salvando ? 'Salvando…' : 'Confirmar banca'}
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </>
      )}
    </div>
  )
}
