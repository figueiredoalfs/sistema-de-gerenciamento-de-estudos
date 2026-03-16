import { useEffect, useState } from 'react'
import { getTaskQuestoes } from '../../api/tasks'

const LETRAS = ['A', 'B', 'C', 'D', 'E']

export default function QuestionFlow({ taskId, onConcluir }) {
  const [questoes, setQuestoes] = useState([])
  const [loading, setLoading] = useState(true)
  const [idx, setIdx] = useState(0)
  const [selecionada, setSelecionada] = useState(null)
  const [acertos, setAcertos] = useState(0)
  const [done, setDone] = useState(false)

  useEffect(() => {
    getTaskQuestoes(taskId)
      .then(setQuestoes)
      .finally(() => setLoading(false))
  }, [taskId])

  if (loading) return (
    <div className="flex items-center justify-center py-16">
      <div className="w-7 h-7 rounded-full border-2 border-brand-border border-t-indigo-500 animate-spin" />
    </div>
  )

  if (!questoes.length) return (
    <div className="bg-brand-card border border-brand-border rounded-xl p-8 text-center space-y-3">
      <p className="text-brand-text font-medium">Nenhuma questão atribuída</p>
      <p className="text-brand-muted text-sm">Esta tarefa não possui questões vinculadas.</p>
      <button
        onClick={() => onConcluir({ acertos: 0, total: 0, pct: 100 })}
        className="mt-2 px-5 py-2.5 bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 font-semibold rounded-xl text-sm hover:bg-emerald-500/30 transition-all duration-300"
      >
        ✓ Concluir tarefa
      </button>
    </div>
  )

  if (done) {
    const pct = Math.round((acertos / questoes.length) * 100)
    return (
      <div className="bg-brand-card border border-brand-border rounded-2xl p-8 text-center space-y-4">
        <div className="w-16 h-16 rounded-2xl bg-brand-gradient/10 border border-indigo-500/20 flex items-center justify-center mx-auto">
          <span className="text-2xl">{pct >= 60 ? '🎯' : '📚'}</span>
        </div>
        <div>
          <p className="text-2xl font-bold text-brand-text">{acertos}/{questoes.length}</p>
          <p className="text-brand-muted text-sm mt-1">{pct}% de aproveitamento</p>
        </div>
        <div className="w-full h-2 bg-brand-border rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-500"
            style={{
              width: `${pct}%`,
              background: pct >= 60 ? 'linear-gradient(90deg, #10b981, #34d399)' : 'linear-gradient(90deg, #f59e0b, #fbbf24)',
            }}
          />
        </div>
        <button
          onClick={() => onConcluir({ acertos, total: questoes.length, pct })}
          className="w-full py-3 bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 font-semibold rounded-xl text-sm hover:bg-emerald-500/30 transition-all duration-300"
        >
          ✓ Concluir tarefa
        </button>
      </div>
    )
  }

  const questao = questoes[idx]
  const alternativas = (() => {
    try { return JSON.parse(questao.alternativas_json) } catch { return {} }
  })()
  const correta = questao.resposta_correta

  function handleSelecionar(letra) {
    if (selecionada) return
    setSelecionada(letra)
    if (letra === correta) setAcertos(a => a + 1)
  }

  function handleProxima() {
    if (idx + 1 >= questoes.length) {
      setDone(true)
    } else {
      setIdx(i => i + 1)
      setSelecionada(null)
    }
  }

  return (
    <div className="space-y-4">
      {/* Progresso */}
      <div className="flex items-center justify-between text-xs text-brand-muted">
        <span>Questão {idx + 1} de {questoes.length}</span>
        <span>{acertos} acerto{acertos !== 1 ? 's' : ''}</span>
      </div>
      <div className="w-full h-1.5 bg-brand-border rounded-full overflow-hidden">
        <div
          className="h-full bg-brand-gradient rounded-full transition-all duration-300"
          style={{ width: `${(idx / questoes.length) * 100}%` }}
        />
      </div>

      {/* Enunciado */}
      <div className="bg-brand-card border border-brand-border rounded-xl p-5">
        {questao.banca && questao.ano && (
          <p className="text-xs text-brand-muted mb-3 font-medium">{questao.banca} — {questao.ano}</p>
        )}
        <p className="text-brand-text text-sm leading-relaxed">{questao.enunciado}</p>
      </div>

      {/* Alternativas */}
      <div className="space-y-2">
        {LETRAS.filter(l => alternativas[l]).map(letra => {
          let btnClass = 'border-brand-border hover:border-slate-600 text-brand-text cursor-pointer'
          if (selecionada) {
            if (letra === correta) btnClass = 'border-emerald-500/50 bg-emerald-500/10 text-emerald-300 cursor-default'
            else if (letra === selecionada) btnClass = 'border-red-500/50 bg-red-500/10 text-red-300 cursor-default'
            else btnClass = 'border-brand-border text-brand-muted opacity-50 cursor-default'
          }
          return (
            <button
              key={letra}
              onClick={() => handleSelecionar(letra)}
              className={`w-full text-left px-4 py-3 rounded-xl border bg-brand-card text-sm transition-all duration-200 ${btnClass}`}
            >
              <span className="font-semibold mr-2">{letra}.</span>
              {alternativas[letra]}
            </button>
          )
        })}
      </div>

      {/* Feedback + próxima */}
      {selecionada && (
        <div className="space-y-3">
          <p className={`text-sm font-medium text-center ${selecionada === correta ? 'text-emerald-400' : 'text-red-400'}`}>
            {selecionada === correta ? '✓ Correto!' : `✗ Incorreto — resposta: ${correta}`}
          </p>
          <button
            onClick={handleProxima}
            className="w-full py-2.5 bg-indigo-500/20 border border-indigo-500/30 text-indigo-400 font-semibold rounded-xl text-sm hover:bg-indigo-500/30 transition-all duration-300"
          >
            {idx + 1 < questoes.length ? 'Próxima questão →' : 'Ver resultado'}
          </button>
        </div>
      )}
    </div>
  )
}
