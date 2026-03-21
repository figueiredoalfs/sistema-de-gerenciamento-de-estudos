import { useEffect, useState } from 'react'
import { listarPendencias, resolverMateria, resolverBanca } from '../api/adminQuestoes'
import { listarMaterias, listarBancas } from '../api/adminTopicos'

export default function AdminPendencias() {
  const [questoes, setQuestoes] = useState([])
  const [materias, setMaterias] = useState([])
  const [bancas, setBancas] = useState([])
  const [loading, setLoading] = useState(true)
  const [erro, setErro] = useState('')

  // estado por questão: { [id]: { mat: { acao, topico_id, salvando, erro }, ban: { acao, banca_id, salvando, erro } } }
  const [res, setRes] = useState({})

  useEffect(() => {
    Promise.all([listarPendencias(), listarMaterias(), listarBancas(true)])
      .then(([qs, ms, bs]) => { setQuestoes(qs); setMaterias(ms); setBancas(bs) })
      .catch(e => setErro(e.response?.data?.detail || e.message))
      .finally(() => setLoading(false))
  }, [])

  function patchRes(id, tipo, patch) {
    setRes(r => ({ ...r, [id]: { ...r[id], [tipo]: { ...(r[id]?.[tipo] || {}), ...patch } } }))
  }

  // Determina se a matéria está inválida (não cadastrada)
  function materiaInvalida(q) {
    if (!q.materia) return true
    return !materias.some(m => m.nome.toLowerCase() === (q.materia || '').toLowerCase())
  }

  // Determina se a banca está inválida (board preenchido mas não cadastrado)
  function bancaInvalida(q) {
    if (!q.board) return false  // sem banca = ok
    return !bancas.some(b => b.nome.toLowerCase() === (q.board || '').toLowerCase())
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
      // Se ainda pendente (banca também inválida), atualiza a questão; senão remove
      if (updated.materia_pendente) {
        setQuestoes(prev => prev.map(x => x.id === q.id ? updated : x))
      } else {
        setQuestoes(prev => prev.filter(x => x.id !== q.id))
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
      } else {
        setQuestoes(prev => prev.filter(x => x.id !== q.id))
      }
    } catch (e) {
      patchRes(q.id, 'ban', { salvando: false, erro: e.response?.data?.detail || e.message })
    }
  }

  return (
    <div className="p-6 space-y-6 max-w-5xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-brand-text">Pendências de validação</h1>
        <p className="text-sm text-brand-muted mt-1">
          Questões com matéria ou banca não reconhecida. Resolva cada item para remover da fila.
        </p>
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
        <div className="space-y-3">
          {questoes.map(q => {
            const matInv = materiaInvalida(q)
            const banInv = bancaInvalida(q)
            const rMat = res[q.id]?.mat || {}
            const rBan = res[q.id]?.ban || {}
            return (
              <div key={q.id} className="bg-brand-card border border-brand-border rounded-xl p-4 space-y-3">
                {/* Cabeçalho da questão */}
                <div>
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

                {/* Resolução de Matéria */}
                {matInv && (
                  <div className="border-t border-brand-border pt-3 space-y-2">
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
                  <div className="border-t border-brand-border pt-3 space-y-2">
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
      )}
    </div>
  )
}
