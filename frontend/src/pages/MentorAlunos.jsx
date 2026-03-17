import { useEffect, useState } from 'react'
import { listarAlunos, progressoAluno } from '../api/mentor'

function ModalProgresso({ aluno, onClose }) {
  const [dados, setDados] = useState(null)
  const [loading, setLoading] = useState(true)
  const [erro, setErro] = useState('')

  useEffect(() => {
    progressoAluno(aluno.id)
      .then(setDados)
      .catch(() => setErro('Erro ao carregar progresso.'))
      .finally(() => setLoading(false))
  }, [aluno.id])

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-brand-card border border-brand-border rounded-xl p-6 w-full max-w-2xl mx-4 space-y-4 shadow-xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-brand-text">Progresso</h2>
            <p className="text-brand-muted text-sm">{aluno.nome} — {aluno.email}</p>
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
            <div className="grid grid-cols-3 gap-3">
              <div className="bg-brand-surface border border-brand-border rounded-lg px-4 py-3 text-center">
                <p className="text-2xl font-bold text-brand-text">{dados.total_questoes}</p>
                <p className="text-xs text-brand-muted mt-0.5">questões respondidas</p>
              </div>
              <div className="bg-brand-surface border border-brand-border rounded-lg px-4 py-3 text-center">
                <p className={`text-2xl font-bold ${dados.perc_geral >= 70 ? 'text-emerald-400' : dados.perc_geral >= 50 ? 'text-yellow-400' : 'text-red-400'}`}>
                  {dados.perc_geral}%
                </p>
                <p className="text-xs text-brand-muted mt-0.5">de acertos (geral)</p>
              </div>
              <div className="bg-brand-surface border border-brand-border rounded-lg px-4 py-3 text-center">
                <p className="text-2xl font-bold text-brand-text">{dados.total_sessoes}</p>
                <p className="text-xs text-brand-muted mt-0.5">sessões de estudo</p>
              </div>
            </div>

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
  const [modalProgresso, setModalProgresso] = useState(null)

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
      {modalProgresso && (
        <ModalProgresso aluno={modalProgresso} onClose={() => setModalProgresso(null)} />
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
                      onClick={() => setModalProgresso(a)}
                      className="text-brand-muted hover:text-indigo-400 text-xs transition-colors"
                    >
                      Ver progresso
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
