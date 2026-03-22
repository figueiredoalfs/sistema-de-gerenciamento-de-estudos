import { useEffect, useState } from 'react'
import { listarPlanos, gerarPlano, atualizarPlano, aplicarPlano, deletarPlano } from '../api/adminPlanoBase'

const PERFIL_OPTIONS = ['iniciante', 'intermediario', 'avancado']
const AREA_OPTIONS = ['fiscal', 'eaof_com', 'eaof_svm', 'cfoe_com', 'juridica', 'policial', 'ti', 'saude', 'outro']

// ── Editor visual de fases ───────────────────────────────────────────────────
function FasesEditorModal({ plano, onClose, onSaved }) {
  const [fases, setFases] = useState(() => {
    try { return JSON.parse(plano.fases_json) } catch { return [] }
  })
  const [salvando, setSalvando] = useState(false)
  const [erro, setErro] = useState('')
  const [mostrarAplicar, setMostrarAplicar] = useState(false)
  const [aplicando, setAplicando] = useState(false)
  const [modoAplicar, setModoAplicar] = useState('novos')
  const [resultadoAplicar, setResultadoAplicar] = useState(null)

  function atualizarFase(idx, campo, valor) {
    setFases((prev) => prev.map((f, i) => i === idx ? { ...f, [campo]: valor } : f))
  }

  function adicionarFase() {
    const proximo = fases.length + 1
    setFases((prev) => [...prev, {
      numero: proximo,
      nome: `Fase ${proximo}`,
      criterio_avanco: `${65 + proximo * 5}% de acertos`,
      materias: [],
      subtopicos: [],
      subtopicos_novos: [],
    }])
  }

  function removerFase(idx) {
    setFases((prev) => prev.filter((_, i) => i !== idx).map((f, i) => ({ ...f, numero: i + 1 })))
  }

  async function handleSalvar() {
    setSalvando(true)
    setErro('')
    try {
      const fasesSchema = fases.map((f) => ({
        numero: f.numero,
        nome: f.nome,
        criterio_avanco: f.criterio_avanco,
        materias: f.materias || [],
        subtopicos: f.subtopicos || [],
        subtopicos_novos: f.subtopicos_novos || [],
      }))
      const atualizado = await atualizarPlano(plano.id, { fases: fasesSchema })
      onSaved(atualizado)
    } catch (e) {
      setErro(e.response?.data?.detail || 'Erro ao salvar.')
    } finally {
      setSalvando(false)
    }
  }

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
          <button onClick={onClose} className="text-brand-muted hover:text-brand-text">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Lista de fases */}
        <div className="space-y-3">
          {fases.length === 0 && (
            <p className="text-brand-muted text-sm italic">Nenhuma fase definida.</p>
          )}
          {fases.map((f, idx) => (
            <div key={idx} className="bg-brand-surface border border-brand-border rounded-lg p-4 space-y-3">
              <div className="flex items-center gap-2">
                <span className="w-7 h-7 rounded-full bg-indigo-500/20 text-indigo-400 text-xs font-bold flex items-center justify-center shrink-0">
                  {f.numero}
                </span>
                <input
                  value={f.nome}
                  onChange={(e) => atualizarFase(idx, 'nome', e.target.value)}
                  placeholder="Nome da fase"
                  className="flex-1 bg-brand-bg border border-brand-border rounded-lg px-3 py-1.5 text-brand-text text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
                <button
                  onClick={() => removerFase(idx)}
                  className="text-brand-muted hover:text-red-400 transition-colors"
                  title="Remover fase"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
              <div>
                <label className="text-xs text-brand-muted block mb-1">Critério de avanço</label>
                <input
                  value={f.criterio_avanco}
                  onChange={(e) => atualizarFase(idx, 'criterio_avanco', e.target.value)}
                  placeholder="Ex: 70% de acertos"
                  className="w-full bg-brand-bg border border-brand-border rounded-lg px-3 py-1.5 text-brand-text text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
              </div>
              {f.subtopicos && f.subtopicos.length > 0 && (
                <p className="text-xs text-brand-muted pl-0.5">
                  {f.subtopicos.length} subtópico{f.subtopicos.length !== 1 ? 's' : ''} vinculados (via IA)
                </p>
              )}
            </div>
          ))}
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

export default function AdminPlanoBase() {
  const [planos, setPlanos] = useState([])
  const [loading, setLoading] = useState(true)
  const [erro, setErro] = useState('')
  const [gerando, setGerando] = useState(false)
  const [genArea, setGenArea] = useState('fiscal')
  const [genPerfil, setGenPerfil] = useState('iniciante')
  const [editarPlano, setEditarPlano] = useState(null)
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
