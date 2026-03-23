import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { getHierarquia, getBancas, postBateria } from '../api/bateria'

function Campo({ label, children }) {
  return (
    <div className="space-y-1.5">
      <label className="text-xs font-medium text-brand-muted uppercase tracking-wide">{label}</label>
      {children}
    </div>
  )
}

const selectCls =
  'w-full bg-brand-surface border border-brand-border rounded-xl px-3 py-2.5 text-sm text-brand-text focus:outline-none focus:border-indigo-500 transition-colors disabled:opacity-50'

const inputCls =
  'w-full bg-brand-surface border border-brand-border rounded-xl px-3 py-2.5 text-sm text-brand-text focus:outline-none focus:border-indigo-500 transition-colors'

function bancaParaFonte(bancaNome, alunoBanca) {
  if (bancaNome === 'Simulado próprio') return 'simulado'
  if (bancaNome === 'Outra banca') return 'manual'
  if (!bancaNome) return 'manual'
  if (alunoBanca && bancaNome.toLowerCase().includes(alunoBanca.toLowerCase())) {
    return 'prova_anterior_mesma_banca'
  }
  return 'prova_anterior_outra_banca'
}

const ENTRADA_VAZIA = { materia: '', subtopico: '', acertos: '', total: '', banca: '' }

export default function LancarBateria() {
  const { user } = useAuth()
  const [hierarquia, setHierarquia] = useState([])
  const [bancas, setBancas] = useState([])
  const [loadingHier, setLoadingHier] = useState(true)

  // Lista de entradas (permite múltiplas matérias)
  const [entradas, setEntradas] = useState([{ ...ENTRADA_VAZIA }])

  const [enviando, setEnviando] = useState(false)
  const [sucesso, setSucesso] = useState(null)
  const [erro, setErro] = useState(null)

  const BANCAS_FALLBACK = [
    'CESPE/CEBRASPE', 'FCC', 'FGV', 'VUNESP', 'AOCP',
    'IDECAN', 'IBFC', 'QUADRIX', 'IADES', 'UPENET',
    'Outra banca', 'Simulado próprio',
  ]

  useEffect(() => {
    Promise.allSettled([getHierarquia(), getBancas()])
      .then(([hierResult, bancsResult]) => {
        if (hierResult.status === 'fulfilled') {
          setHierarquia(Array.isArray(hierResult.value) ? hierResult.value : [])
        } else {
          setErro('Erro ao carregar matérias. Verifique se o servidor está rodando.')
        }
        if (bancsResult.status === 'fulfilled') {
          const bancs = bancsResult.value
          setBancas(Array.isArray(bancs) ? bancs.map(b => b.nome) : BANCAS_FALLBACK)
        } else {
          setBancas(BANCAS_FALLBACK)
        }
      })
      .finally(() => setLoadingHier(false))
  }, [])

  function updateEntrada(idx, campo, valor) {
    setEntradas(prev => {
      const nova = [...prev]
      nova[idx] = { ...nova[idx], [campo]: valor }
      if (campo === 'materia') nova[idx].subtopico = ''
      return nova
    })
  }

  function addEntrada() {
    setEntradas(prev => [...prev, { ...ENTRADA_VAZIA }])
  }

  function removeEntrada(idx) {
    setEntradas(prev => prev.filter((_, i) => i !== idx))
  }

  function resetForm() {
    setEntradas([{ ...ENTRADA_VAZIA }])
    setSucesso(null)
    setErro(null)
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setErro(null)
    setSucesso(null)

    for (let i = 0; i < entradas.length; i++) {
      const en = entradas[i]
      const ac = parseInt(en.acertos, 10)
      const tot = parseInt(en.total, 10)
      const label = entradas.length > 1 ? ` (entrada ${i + 1})` : ''
      if (!en.materia) return setErro(`Selecione a matéria${label}.`)
      if (!en.banca) return setErro(`Selecione a banca${label}.`)
      if (isNaN(ac) || ac < 0) return setErro(`Acertos inválido${label}.`)
      if (isNaN(tot) || tot <= 0) return setErro(`Total deve ser maior que zero${label}.`)
      if (ac > tot) return setErro(`Acertos não pode ser maior que o total${label}.`)
    }

    setEnviando(true)
    try {
      const questoes = entradas.map(en => ({
        materia: en.materia,
        subtopico: en.subtopico || null,
        acertos: parseInt(en.acertos, 10),
        total: parseInt(en.total, 10),
        fonte: bancaParaFonte(en.banca, user?.banca),
      }))
      const res = await postBateria(questoes)
      setSucesso(res.mensagem)
    } catch {
      setErro('Erro ao salvar. Tente novamente.')
    } finally {
      setEnviando(false)
    }
  }

  if (loadingHier) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-8 h-8 rounded-full border-2 border-brand-border border-t-indigo-500 animate-spin" />
      </div>
    )
  }

  return (
    <div className="max-w-lg mx-auto px-4 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-brand-text">Lançar bateria</h1>
        <p className="text-brand-muted text-sm mt-1">
          Registre questões feitas fora do sistema e veja o impacto no seu desempenho.
        </p>
      </div>

      {sucesso ? (
        <div className="bg-brand-card border border-brand-border rounded-2xl p-6 space-y-4">
          <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl px-4 py-3 text-emerald-400 text-sm">
            {sucesso}
          </div>
          <div className="flex gap-3">
            <button
              onClick={resetForm}
              className="flex-1 bg-indigo-500 hover:bg-indigo-600 text-white text-sm font-medium rounded-xl py-2.5 transition-colors"
            >
              Lançar outra
            </button>
            <Link
              to="/desempenho"
              className="flex-1 text-center bg-brand-surface border border-brand-border hover:border-indigo-500/40 text-brand-text text-sm font-medium rounded-xl py-2.5 transition-colors"
            >
              Ver desempenho
            </Link>
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          {erro && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3 text-red-400 text-sm">
              {erro}
            </div>
          )}

          {entradas.map((en, idx) => {
            const subtopicos = hierarquia.find(m => m.nome === en.materia)?.subtopicos ?? []
            const ac = parseInt(en.acertos, 10)
            const tot = parseInt(en.total, 10)
            const perc = !isNaN(ac) && !isNaN(tot) && tot > 0 ? ((ac / tot) * 100).toFixed(1) : null

            return (
              <div key={idx} className="bg-brand-card border border-brand-border rounded-2xl p-5 space-y-4">
                {entradas.length > 1 && (
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-brand-muted uppercase tracking-wide">
                      Matéria {idx + 1}
                    </span>
                    <button
                      type="button"
                      onClick={() => removeEntrada(idx)}
                      className="text-xs text-red-400 hover:text-red-300 transition-colors"
                    >
                      Remover
                    </button>
                  </div>
                )}

                <Campo label="Matéria">
                  <select
                    value={en.materia}
                    onChange={e => updateEntrada(idx, 'materia', e.target.value)}
                    className={selectCls}
                  >
                    <option value="">Selecione a matéria</option>
                    {hierarquia.map(m => (
                      <option key={m.id} value={m.nome}>{m.nome}</option>
                    ))}
                  </select>
                </Campo>

                <Campo label="Subtópico (opcional)">
                  <select
                    value={en.subtopico}
                    onChange={e => updateEntrada(idx, 'subtopico', e.target.value)}
                    disabled={!en.materia || subtopicos.length === 0}
                    className={selectCls}
                  >
                    <option value="">Todos / Geral</option>
                    {subtopicos.map(s => (
                      <option key={s.id} value={s.nome}>{s.nome}</option>
                    ))}
                  </select>
                </Campo>

                <Campo label="Banca">
                  <select
                    value={en.banca}
                    onChange={e => updateEntrada(idx, 'banca', e.target.value)}
                    className={selectCls}
                  >
                    <option value="">Selecione a banca</option>
                    {bancas.map(b => (
                      <option key={b} value={b}>{b}</option>
                    ))}
                  </select>
                </Campo>

                <div className="grid grid-cols-2 gap-4">
                  <Campo label="Acertos">
                    <input
                      type="number"
                      min="0"
                      value={en.acertos}
                      onChange={e => updateEntrada(idx, 'acertos', e.target.value)}
                      placeholder="Ex: 7"
                      className={inputCls}
                    />
                  </Campo>
                  <Campo label="Total de questões">
                    <input
                      type="number"
                      min="1"
                      value={en.total}
                      onChange={e => updateEntrada(idx, 'total', e.target.value)}
                      placeholder="Ex: 10"
                      className={inputCls}
                    />
                  </Campo>
                </div>

                {perc && (
                  <p className="text-xs text-brand-muted text-right">
                    Aproveitamento: <span className="font-semibold text-brand-text">{perc}%</span>
                  </p>
                )}
              </div>
            )
          })}

          <button
            type="button"
            onClick={addEntrada}
            className="w-full py-2.5 rounded-xl border border-dashed border-brand-border text-brand-muted text-sm hover:border-indigo-500/40 hover:text-indigo-400 transition-colors"
          >
            + Adicionar outra matéria
          </button>

          <button
            type="submit"
            disabled={enviando}
            className="w-full bg-indigo-500 hover:bg-indigo-600 disabled:opacity-50 text-white text-sm font-medium rounded-xl py-2.5 transition-colors"
          >
            {enviando ? 'Salvando…' : `Salvar bateria${entradas.length > 1 ? ` (${entradas.length} matérias)` : ''}`}
          </button>
        </form>
      )}
    </div>
  )
}
