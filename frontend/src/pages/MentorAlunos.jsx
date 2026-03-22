import { useEffect, useState } from 'react'
import { listarAlunos, resumoAluno } from '../api/mentor'

function Badge({ children, color = 'indigo' }) {
  const colors = {
    emerald: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    yellow:  'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
    red:     'bg-red-500/10 text-red-400 border-red-500/20',
    indigo:  'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
    muted:   'bg-brand-surface text-brand-muted border-brand-border',
  }
  return (
    <span className={`text-xs px-2 py-0.5 rounded border font-medium ${colors[color] || colors.indigo}`}>
      {children}
    </span>
  )
}

function KPI({ label, value, color }) {
  const colorMap = { emerald: 'text-emerald-400', yellow: 'text-yellow-400', red: 'text-red-400', default: 'text-brand-text' }
  return (
    <div className="bg-brand-surface border border-brand-border rounded-lg px-4 py-3 text-center">
      <p className={`text-2xl font-bold ${colorMap[color] || colorMap.default}`}>{value}</p>
      <p className="text-xs text-brand-muted mt-0.5">{label}</p>
    </div>
  )
}

function ModalResumo({ aluno, onClose }) {
  const [dados, setDados] = useState(null)
  const [loading, setLoading] = useState(true)
  const [erro, setErro] = useState('')

  useEffect(() => {
    resumoAluno(aluno.id)
      .then(setDados)
      .catch(() => setErro('Erro ao carregar resumo.'))
      .finally(() => setLoading(false))
  }, [aluno.id])

  const pct = dados?.desempenho?.perc_geral ?? 0
  const acertoColor = pct >= 70 ? 'emerald' : pct >= 50 ? 'yellow' : 'red'

  function formatDate(iso) {
    if (!iso) return '—'
    return new Date(iso).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: '2-digit', hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-brand-card border border-brand-border rounded-xl p-6 w-full max-w-2xl mx-4 shadow-xl max-h-[90vh] overflow-y-auto space-y-5">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-brand-text">{aluno.nome}</h2>
            <p className="text-brand-muted text-sm">{aluno.email}</p>
          </div>
          <button onClick={onClose} className="text-brand-muted hover:text-brand-text">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {loading && <p className="text-brand-muted text-sm">Carregando…</p>}
        {erro && <p className="text-red-400 text-sm">{erro}</p>}

        {dados && (
          <>
            {/* Status geral */}
            <div className="flex flex-wrap gap-2">
              {dados.area && <Badge color="indigo">{dados.area}</Badge>}
              {dados.experiencia && <Badge color="muted">{dados.experiencia}</Badge>}
              {dados.fase_atual != null && <Badge color="indigo">Fase {dados.fase_atual}</Badge>}
              {dados.diagnostico_pendente && <Badge color="yellow">Diagnóstico pendente</Badge>}
              <Badge color={dados.ativo ? 'emerald' : 'red'}>{dados.ativo ? 'Ativo' : 'Inativo'}</Badge>
            </div>

            {/* KPIs */}
            <div className="grid grid-cols-3 gap-3">
              <KPI label="questões respondidas" value={dados.desempenho.total_questoes} />
              <KPI label="de acertos (geral)" value={`${pct}%`} color={acertoColor} />
              <KPI label="última atividade" value={formatDate(dados.ultima_atividade)} />
            </div>

            {/* Meta ativa */}
            {dados.meta_ativa ? (
              <div className="bg-brand-surface border border-brand-border rounded-xl p-4 space-y-2">
                <p className="text-sm font-medium text-brand-text">
                  Meta ativa —{' '}
                  {dados.meta_ativa.numero_semana === 0
                    ? 'Diagnóstico'
                    : `Semana ${String(dados.meta_ativa.numero_semana).padStart(2, '0')}`}
                </p>
                <div className="flex items-center gap-3">
                  <div className="flex-1 h-2 bg-brand-bg rounded-full overflow-hidden">
                    <div
                      className="h-full bg-brand-gradient rounded-full transition-all"
                      style={{ width: `${dados.meta_ativa.progresso_pct}%` }}
                    />
                  </div>
                  <span className="text-sm font-semibold gradient-text">{dados.meta_ativa.progresso_pct}%</span>
                </div>
                <p className="text-xs text-brand-muted">
                  {dados.meta_ativa.tasks_concluidas} de {dados.meta_ativa.tasks_total} tarefas concluídas
                </p>
              </div>
            ) : (
              <p className="text-brand-muted text-sm italic">Sem meta ativa no momento.</p>
            )}

            {/* Pontos fortes e fracos */}
            {(dados.pontos_fortes.length > 0 || dados.pontos_fracos.length > 0) && (
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs font-semibold text-emerald-400 uppercase tracking-wider mb-2">Pontos fortes</p>
                  {dados.pontos_fortes.length === 0 ? (
                    <p className="text-brand-muted text-xs italic">—</p>
                  ) : (
                    <div className="space-y-1">
                      {dados.pontos_fortes.map((m) => (
                        <div key={m.materia} className="flex items-center justify-between">
                          <span className="text-xs text-brand-text truncate max-w-[120px]">{m.materia}</span>
                          <span className="text-xs font-semibold text-emerald-400">{m.perc}%</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
                <div>
                  <p className="text-xs font-semibold text-red-400 uppercase tracking-wider mb-2">Pontos fracos</p>
                  {dados.pontos_fracos.length === 0 ? (
                    <p className="text-brand-muted text-xs italic">—</p>
                  ) : (
                    <div className="space-y-1">
                      {dados.pontos_fracos.map((m) => (
                        <div key={m.materia} className="flex items-center justify-between">
                          <span className="text-xs text-brand-text truncate max-w-[120px]">{m.materia}</span>
                          <span className="text-xs font-semibold text-red-400">{m.perc}%</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Tabela por matéria */}
            {dados.por_materia.length > 0 ? (
              <div className="bg-brand-surface border border-brand-border rounded-xl overflow-hidden">
                <table className="w-full text-sm">
                  <thead className="border-b border-brand-border">
                    <tr>
                      <th className="text-left px-4 py-2 text-brand-muted font-medium text-xs">Matéria</th>
                      <th className="text-right px-4 py-2 text-brand-muted font-medium text-xs">Respondidas</th>
                      <th className="text-right px-4 py-2 text-brand-muted font-medium text-xs">Acertos</th>
                      <th className="text-right px-4 py-2 text-brand-muted font-medium text-xs">%</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-brand-border">
                    {dados.por_materia.map((m) => (
                      <tr key={m.materia}>
                        <td className="px-4 py-2 text-brand-text truncate max-w-xs">{m.materia}</td>
                        <td className="px-4 py-2 text-right text-brand-muted">{m.realizadas}</td>
                        <td className="px-4 py-2 text-right text-brand-muted">{m.acertos}</td>
                        <td className="px-4 py-2 text-right">
                          <span className={`font-semibold ${m.perc >= 70 ? 'text-emerald-400' : m.perc >= 50 ? 'text-yellow-400' : 'text-red-400'}`}>
                            {m.perc}%
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-brand-muted text-sm italic">Nenhuma questão respondida ainda.</p>
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default function MentorAlunos() {
  const [alunos, setAlunos] = useState([])
  const [loading, setLoading] = useState(true)
  const [erro, setErro] = useState('')
  const [busca, setBusca] = useState('')
  const [modalResumo, setModalResumo] = useState(null)

  useEffect(() => {
    listarAlunos()
      .then(setAlunos)
      .catch(() => setErro('Erro ao carregar alunos.'))
      .finally(() => setLoading(false))
  }, [])

  const filtrados = alunos.filter((a) => {
    const q = busca.toLowerCase()
    return !q || a.nome.toLowerCase().includes(q) || (a.email || '').toLowerCase().includes(q)
  })

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      {modalResumo && (
        <ModalResumo aluno={modalResumo} onClose={() => setModalResumo(null)} />
      )}

      <div>
        <h1 className="text-2xl font-bold text-brand-text">Meus Alunos</h1>
        <p className="text-brand-muted text-sm mt-1">{alunos.length} aluno{alunos.length !== 1 ? 's' : ''} sob sua mentoria</p>
      </div>

      {erro && <p className="text-red-400 text-sm">{erro}</p>}

      <input
        type="text"
        placeholder="Buscar por nome ou e-mail…"
        value={busca}
        onChange={(e) => setBusca(e.target.value)}
        className="w-full max-w-sm bg-brand-surface border border-brand-border rounded-lg px-3 py-2 text-brand-text text-sm placeholder-brand-muted focus:outline-none focus:ring-1 focus:ring-indigo-500"
      />

      {filtrados.length === 0 ? (
        <p className="text-brand-muted text-sm">Nenhum aluno encontrado.</p>
      ) : (
        <div className="bg-brand-card border border-brand-border rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead className="border-b border-brand-border">
              <tr>
                <th className="text-left px-4 py-3 text-brand-muted font-medium text-xs uppercase">Aluno</th>
                <th className="text-left px-4 py-3 text-brand-muted font-medium text-xs uppercase hidden md:table-cell">Área</th>
                <th className="text-left px-4 py-3 text-brand-muted font-medium text-xs uppercase hidden md:table-cell">Dedicação</th>
                <th className="text-left px-4 py-3 text-brand-muted font-medium text-xs uppercase">Status</th>
                <th className="text-right px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-brand-border">
              {filtrados.map((a) => (
                <tr key={a.id} className={`hover:bg-brand-surface/50 transition-colors ${!a.ativo ? 'opacity-50' : ''}`}>
                  <td className="px-4 py-3">
                    <div className="font-medium text-brand-text">{a.nome}</div>
                    <div className="text-brand-muted text-xs">{a.email}</div>
                  </td>
                  <td className="px-4 py-3 hidden md:table-cell text-brand-muted capitalize">{a.area ?? '—'}</td>
                  <td className="px-4 py-3 hidden md:table-cell text-brand-muted text-xs">
                    {a.horas_por_dia}h/dia · {a.nivel_desafio}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-0.5 rounded border ${a.ativo ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-red-500/10 text-red-400 border-red-500/20'}`}>
                      {a.ativo ? 'Ativo' : 'Inativo'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => setModalResumo(a)}
                      className="text-brand-muted hover:text-indigo-400 text-xs transition-colors"
                    >
                      Ver resumo
                    </button>
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
