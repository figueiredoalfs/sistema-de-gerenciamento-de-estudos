import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { getResumo, getSugestoesRevisao } from '../api/desempenho'
import { listarBaterias } from '../api/bateria'

function Spinner() {
  return (
    <div className="flex items-center justify-center py-20">
      <div className="w-8 h-8 rounded-full border-2 border-brand-border border-t-indigo-500 animate-spin" />
    </div>
  )
}

function AdminHub() {
  const { user } = useAuth()
  return (
    <div className="max-w-2xl mx-auto px-4 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-brand-text">
          Olá, <span className="gradient-text">{user?.nome?.split(' ')[0]}</span>
        </h1>
        <p className="text-brand-muted text-sm mt-1">Painel de administração — use o menu lateral para navegar.</p>
      </div>
    </div>
  )
}

function KpiCard({ label, value, sub, color = 'indigo' }) {
  const colors = {
    indigo: 'bg-indigo-500/10 border-indigo-500/20 text-indigo-400',
    emerald: 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400',
    amber: 'bg-amber-500/10 border-amber-500/20 text-amber-400',
    red: 'bg-red-500/10 border-red-500/20 text-red-400',
  }
  return (
    <div className={`rounded-2xl border p-5 ${colors[color]}`}>
      <p className="text-xs font-medium opacity-70 uppercase tracking-wide mb-1">{label}</p>
      <p className="text-2xl font-bold">{value}</p>
      {sub && <p className="text-xs opacity-60 mt-1">{sub}</p>}
    </div>
  )
}

function PercBar({ perc }) {
  const color = perc >= 70 ? 'bg-emerald-500' : perc >= 50 ? 'bg-amber-500' : 'bg-red-500'
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 bg-brand-border rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${Math.min(perc, 100)}%` }} />
      </div>
      <span className="text-xs text-brand-muted w-10 text-right">{perc.toFixed(1)}%</span>
    </div>
  )
}

function PrioridadeBadge({ p }) {
  if (p === 'critico') return <span className="text-xs px-2 py-0.5 rounded-full bg-red-500/20 text-red-400 font-medium">Crítico</span>
  if (p === 'urgente') return <span className="text-xs px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-400 font-medium">Urgente</span>
  return <span className="text-xs px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-400 font-medium">Revisar</span>
}

export default function Dashboard() {
  const { user } = useAuth()
  const [resumo, setResumo] = useState(null)
  const [sugestoes, setSugestoes] = useState([])
  const [baterias, setBaterias] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    Promise.all([getResumo(), getSugestoesRevisao(), listarBaterias({ pagina: 1, por_pagina: 5 })])
      .then(([r, s, b]) => {
        setResumo(r)
        setSugestoes(Array.isArray(s) ? s : [])
        setBaterias(Array.isArray(b) ? b : [])
      })
      .catch(() => setError('Erro ao carregar dados.'))
      .finally(() => setLoading(false))
  }, [])

  if (user?.role === 'administrador' || user?.role === 'mentor') return <AdminHub />
  if (loading) return <Spinner />

  const semDados = !resumo || resumo.total_questoes === 0

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 space-y-8">
      {/* Saudação */}
      <div>
        <h1 className="text-2xl font-bold text-brand-text">
          Olá, <span className="gradient-text">{user?.nome?.split(' ')[0]}</span>
        </h1>
        <p className="text-brand-muted text-sm mt-1">Central de análise do seu desempenho</p>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3 text-red-400 text-sm">{error}</div>
      )}

      {semDados ? (
        <div className="bg-brand-card border border-brand-border rounded-2xl p-8 text-center space-y-4">
          <div className="w-14 h-14 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center mx-auto">
            <svg className="w-7 h-7 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <div>
            <p className="text-brand-text font-semibold">Nenhum dado ainda</p>
            <p className="text-brand-muted text-sm mt-1">Lance seu primeiro caderno de questões para ver seu desempenho aqui.</p>
          </div>
          <Link
            to="/caderno-questoes"
            className="inline-block px-6 py-2.5 bg-brand-gradient text-white rounded-xl font-semibold text-sm hover:opacity-90 transition-all duration-300"
          >
            Lançar questões
          </Link>
        </div>
      ) : (
        <>
          {/* KPIs */}
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <KpiCard
              label="Aproveitamento"
              value={`${(resumo.taxa_acerto_geral ?? 0).toFixed(1)}%`}
              color={resumo.taxa_acerto_geral >= 70 ? 'emerald' : resumo.taxa_acerto_geral >= 50 ? 'amber' : 'red'}
            />
            <KpiCard label="Questões feitas" value={(resumo.total_questoes ?? 0).toLocaleString()} color="indigo" />
            <KpiCard label="Streak" value={`${resumo.streak_dias ?? 0}d`} sub="dias consecutivos" color="amber" />
            <KpiCard label="Dias este mês" value={resumo.dias_estudados_30d ?? 0} sub="últimos 30 dias" color="indigo" />
          </div>

          {/* Matérias */}
          {resumo.materias?.length > 0 && (
            <div className="bg-brand-card border border-brand-border rounded-2xl overflow-hidden">
              <div className="px-5 py-4 border-b border-brand-border flex items-center justify-between">
                <div>
                  <h2 className="text-sm font-semibold text-brand-text">Desempenho por matéria</h2>
                  <p className="text-xs text-brand-muted mt-0.5">Ordenado por aproveitamento</p>
                </div>
                <Link to="/desempenho" className="text-xs text-indigo-400 hover:text-indigo-300">Ver detalhes</Link>
              </div>
              <div className="divide-y divide-brand-border">
                {resumo.materias.map((m) => (
                  <div key={m.nome} className="px-5 py-3">
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-sm text-brand-text truncate pr-2">{m.nome}</span>
                      <span className="text-xs text-brand-muted shrink-0">{m.total_questoes} questões</span>
                    </div>
                    <PercBar perc={m.taxa_acerto} />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Revisão sugerida */}
          {sugestoes.length > 0 && (
            <div className="bg-brand-card border border-brand-border rounded-2xl overflow-hidden">
              <div className="px-5 py-4 border-b border-brand-border">
                <h2 className="text-sm font-semibold text-brand-text">Revisão sugerida</h2>
                <p className="text-xs text-brand-muted mt-0.5">Subtópicos que precisam de atenção</p>
              </div>
              <div className="divide-y divide-brand-border">
                {sugestoes.slice(0, 5).map((s, i) => (
                  <div key={i} className="px-5 py-3 flex items-center gap-3">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-brand-text truncate">{s.subtopico || s.materia}</p>
                      <p className="text-xs text-brand-muted">{s.materia} · {s.taxa_acerto.toFixed(1)}% · {s.dias_sem_revisar}d sem revisar</p>
                    </div>
                    <PrioridadeBadge p={s.prioridade} />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Atividade recente */}
          {baterias.length > 0 && (
            <div className="bg-brand-card border border-brand-border rounded-2xl overflow-hidden">
              <div className="px-5 py-4 border-b border-brand-border flex items-center justify-between">
                <div>
                  <h2 className="text-sm font-semibold text-brand-text">Atividade recente</h2>
                  <p className="text-xs text-brand-muted mt-0.5">Últimas baterias registradas</p>
                </div>
                <Link to="/caderno-questoes" className="text-xs text-indigo-400 hover:text-indigo-300">Ver todas</Link>
              </div>
              <div className="divide-y divide-brand-border">
                {baterias.map((b) => (
                  <div key={b.bateria_id} className="px-5 py-3 flex items-center justify-between">
                    <div>
                      <p className="text-sm text-brand-text">{b.materias?.join(', ') || '—'}</p>
                      <p className="text-xs text-brand-muted">
                        {new Date(b.data).toLocaleDateString('pt-BR')} · {b.total_questoes} questões
                      </p>
                    </div>
                    <span className={`text-sm font-semibold ${b.percentual_geral >= 70 ? 'text-emerald-400' : b.percentual_geral >= 50 ? 'text-amber-400' : 'text-red-400'}`}>
                      {b.percentual_geral.toFixed(1)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
