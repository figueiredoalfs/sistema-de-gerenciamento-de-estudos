import { useEffect, useState } from 'react'
import { listarPlanos, gerarPlano, aprovarPlano, deletarPlano } from '../api/adminPlanoBase'

const PERFIL_OPTIONS = ['iniciante', 'intermediario', 'avancado']
const AREA_OPTIONS = ['fiscal', 'juridica', 'policial', 'ti', 'saude', 'outro']

function FasesModal({ plano, onClose }) {
  let fases = []
  try { fases = JSON.parse(plano.fases_json) } catch { /* noop */ }

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-brand-card border border-brand-border rounded-xl p-6 w-full max-w-2xl mx-4 space-y-4 shadow-xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-brand-text">Fases do plano</h2>
            <p className="text-brand-muted text-sm">{plano.area} · {plano.perfil}</p>
          </div>
          <button onClick={onClose} className="text-brand-muted hover:text-brand-text">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {fases.length === 0 ? (
          <p className="text-brand-muted text-sm italic">Nenhuma fase definida.</p>
        ) : (
          <div className="space-y-4">
            {fases.map((f) => (
              <div key={f.numero} className="bg-brand-surface border border-brand-border rounded-lg p-4 space-y-2">
                <div className="flex items-center gap-2">
                  <span className="w-7 h-7 rounded-full bg-indigo-500/20 text-indigo-400 text-xs font-bold flex items-center justify-center shrink-0">
                    {f.numero}
                  </span>
                  <span className="font-semibold text-brand-text">{f.nome}</span>
                </div>
                <p className="text-xs text-brand-muted pl-9">
                  <span className="font-medium text-brand-text/70">Critério de avanço:</span> {f.criterio_avanco}
                </p>
                <div className="pl-9 flex flex-wrap gap-1.5">
                  {(f.materias || []).map((m) => (
                    <span key={m} className="text-xs px-2 py-0.5 rounded bg-brand-border text-brand-muted">{m}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default function AdminPlanoBase() {
  const [planos, setPlanos] = useState([])
  const [loading, setLoading] = useState(true)
  const [erro, setErro] = useState('')
  const [gerando, setGerando] = useState(false)
  const [genArea, setGenArea] = useState('fiscal')
  const [genPerfil, setGenPerfil] = useState('iniciante')
  const [verFases, setVerFases] = useState(null)
  const [filtroPendente, setFiltroPendente] = useState(false)

  function carregar() {
    setLoading(true)
    listarPlanos({ pendente_revisao: filtroPendente || undefined })
      .then(setPlanos)
      .catch(() => setErro('Erro ao carregar planos.'))
      .finally(() => setLoading(false))
  }

  useEffect(() => { carregar() }, [filtroPendente]) // eslint-disable-line

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

  async function handleAprovar(id) {
    try {
      const atualizado = await aprovarPlano(id)
      setPlanos((prev) => prev.map((p) => (p.id === atualizado.id ? atualizado : p)))
    } catch {
      setErro('Erro ao aprovar plano.')
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

  const pendentes = planos.filter((p) => p.gerado_por_ia && !p.revisado_admin).length

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      {verFases && <FasesModal plano={verFases} onClose={() => setVerFases(null)} />}

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
          <button onClick={handleGerar} disabled={gerando}
            className="px-4 py-2 text-sm bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors disabled:opacity-50 flex items-center gap-2">
            {gerando ? (
              <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Gerando…</>
            ) : (
              'Gerar via IA'
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
                let fases = []
                try { fases = JSON.parse(p.fases_json) } catch { /* noop */ }
                return (
                  <tr key={p.id} className="hover:bg-brand-surface/50 transition-colors">
                    <td className="px-4 py-3 text-brand-text font-medium capitalize">{p.area}</td>
                    <td className="px-4 py-3 text-brand-muted capitalize">{p.perfil}</td>
                    <td className="px-4 py-3 text-brand-muted">{fases.length} fase{fases.length !== 1 ? 's' : ''}</td>
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
                        <button onClick={() => setVerFases(p)}
                          className="text-brand-muted hover:text-indigo-400 text-xs transition-colors">
                          Ver fases
                        </button>
                        {!p.revisado_admin && (
                          <button onClick={() => handleAprovar(p.id)}
                            className="text-brand-muted hover:text-emerald-400 text-xs transition-colors">
                            Aprovar
                          </button>
                        )}
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
