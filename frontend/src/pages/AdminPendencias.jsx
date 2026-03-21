import { useEffect, useState } from 'react'
import { listarPendencias, resolverPendencia } from '../api/adminQuestoes'
import { listarMaterias } from '../api/adminTopicos'

export default function AdminPendencias() {
  const [questoes, setQuestoes] = useState([])
  const [materias, setMaterias] = useState([])
  const [loading, setLoading] = useState(true)
  const [erro, setErro] = useState('')

  // estado por questão: { [id]: { acao: 'vincular'|'criar'|null, topico_id: '', salvando: bool } }
  const [resolucoes, setResolucoes] = useState({})

  useEffect(() => {
    Promise.all([listarPendencias(), listarMaterias()])
      .then(([qs, ms]) => { setQuestoes(qs); setMaterias(ms) })
      .catch(e => setErro(e.response?.data?.detail || e.message))
      .finally(() => setLoading(false))
  }, [])

  function setRes(id, patch) {
    setResolucoes(r => ({ ...r, [id]: { ...r[id], ...patch } }))
  }

  async function handleResolver(q) {
    const res = resolucoes[q.id] || {}
    if (!res.acao) return
    if (res.acao === 'vincular' && !res.topico_id) return
    setRes(q.id, { salvando: true })
    try {
      await resolverPendencia(q.id, {
        acao: res.acao,
        topico_id: res.acao === 'vincular' ? res.topico_id : undefined,
        nova_materia: res.acao === 'criar' ? q.subject : undefined,
      })
      setQuestoes(prev => prev.filter(x => x.id !== q.id))
    } catch (e) {
      setRes(q.id, { salvando: false, erro: e.response?.data?.detail || e.message })
    }
  }

  return (
    <div className="p-6 space-y-6 max-w-5xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-brand-text">Matérias pendentes de validação</h1>
        <p className="text-sm text-brand-muted mt-1">
          Questões importadas com matérias não reconhecidas. Vincule a uma matéria existente ou crie uma nova.
        </p>
      </div>

      {erro && <p className="text-red-400 text-sm">{erro}</p>}

      {loading ? (
        <p className="text-brand-muted text-sm">Carregando…</p>
      ) : questoes.length === 0 ? (
        <div className="bg-brand-card border border-brand-border rounded-xl p-8 text-center">
          <p className="text-green-400 font-medium">Nenhuma pendência</p>
          <p className="text-brand-muted text-sm mt-1">Todas as matérias estão validadas.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {questoes.map(q => {
            const res = resolucoes[q.id] || {}
            return (
              <div key={q.id} className="bg-brand-card border border-brand-border rounded-xl p-4 space-y-3">
                <div className="flex items-start justify-between gap-4">
                  <div className="min-w-0">
                    <p className="font-mono text-xs text-brand-muted">{q.question_code}</p>
                    <p className="text-sm font-semibold text-yellow-400 mt-0.5">
                      Matéria informada: <span className="font-bold">"{q.subject}"</span>
                    </p>
                    <p className="text-xs text-brand-muted mt-1 line-clamp-2">{q.statement}</p>
                  </div>
                </div>

                <div className="border-t border-brand-border pt-3 space-y-2">
                  {/* Opção A: vincular */}
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name={`acao-${q.id}`}
                      value="vincular"
                      checked={res.acao === 'vincular'}
                      onChange={() => setRes(q.id, { acao: 'vincular', topico_id: '' })}
                      className="accent-indigo-500"
                    />
                    <span className="text-sm text-brand-text">Vincular a matéria existente</span>
                  </label>
                  {res.acao === 'vincular' && (
                    <select
                      value={res.topico_id || ''}
                      onChange={e => setRes(q.id, { topico_id: e.target.value })}
                      className="w-full bg-brand-surface border border-brand-border rounded-lg px-3 py-1.5 text-sm text-brand-text focus:outline-none focus:border-indigo-500 ml-5"
                    >
                      <option value="">Selecione a matéria…</option>
                      {materias.map(m => (
                        <option key={m.id} value={String(m.id)}>{m.nome}</option>
                      ))}
                    </select>
                  )}

                  {/* Opção B: criar */}
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name={`acao-${q.id}`}
                      value="criar"
                      checked={res.acao === 'criar'}
                      onChange={() => setRes(q.id, { acao: 'criar' })}
                      className="accent-indigo-500"
                    />
                    <span className="text-sm text-brand-text">
                      Criar nova matéria <span className="text-yellow-400 font-semibold">"{q.subject}"</span>
                    </span>
                  </label>

                  {res.erro && <p className="text-red-400 text-xs ml-5">{res.erro}</p>}

                  <div className="flex justify-end pt-1">
                    <button
                      onClick={() => handleResolver(q)}
                      disabled={!res.acao || (res.acao === 'vincular' && !res.topico_id) || res.salvando}
                      className="px-4 py-1.5 text-sm rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium disabled:opacity-40 transition-colors"
                    >
                      {res.salvando ? 'Salvando…' : 'Confirmar'}
                    </button>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
