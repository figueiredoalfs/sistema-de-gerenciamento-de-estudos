import { useEffect, useState } from 'react'
import { getDesempenho, getEvolucao } from '../api/desempenho'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'

function Spinner() {
  return (
    <div className="flex items-center justify-center py-20">
      <div className="w-8 h-8 rounded-full border-2 border-brand-border border-t-indigo-500 animate-spin" />
    </div>
  )
}

function KpiCard({ label, value, sub, color = 'indigo' }) {
  const colors = {
    indigo: 'bg-indigo-500/10 border-indigo-500/20 text-indigo-400',
    emerald: 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400',
    red: 'bg-red-500/10 border-red-500/20 text-red-400',
    amber: 'bg-amber-500/10 border-amber-500/20 text-amber-400',
  }
  return (
    <div className={`rounded-2xl border p-5 ${colors[color]}`}>
      <p className="text-xs font-medium opacity-70 uppercase tracking-wide mb-1">{label}</p>
      <p className="text-2xl font-bold">{value}</p>
      {sub && <p className="text-xs opacity-60 mt-1 truncate">{sub}</p>}
    </div>
  )
}

function Tendencia({ atual, anterior }) {
  if (atual == null || anterior == null) return <span className="text-brand-muted text-xs">—</span>
  if (atual > anterior)
    return <span className="text-emerald-400 text-xs font-medium">↑ {atual.toFixed(1)}%</span>
  if (atual < anterior)
    return <span className="text-red-400 text-xs font-medium">↓ {atual.toFixed(1)}%</span>
  return <span className="text-brand-muted text-xs">{atual.toFixed(1)}%</span>
}

function PercBar({ perc }) {
  const color =
    perc >= 70 ? 'bg-emerald-500' : perc >= 50 ? 'bg-amber-500' : 'bg-red-500'
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 bg-brand-border rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${Math.min(perc, 100)}%` }} />
      </div>
      <span className="text-xs text-brand-muted w-10 text-right">{perc.toFixed(1)}%</span>
    </div>
  )
}

const CORES_LINHA = [
  '#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
  '#06b6d4', '#84cc16', '#f97316', '#ec4899', '#14b8a6',
]

function formatarMes(mesAno) {
  // "2025-03" → "Mar/25"
  const [ano, mes] = mesAno.split('-')
  const nomes = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']
  return `${nomes[parseInt(mes, 10) - 1]}/${ano.slice(2)}`
}

function GraficoEvolucao({ pontos }) {
  if (!pontos || pontos.length === 0) {
    return (
      <div className="py-10 text-center text-brand-muted text-sm">
        Nenhum dado ainda — lance suas primeiras baterias
      </div>
    )
  }

  // Transformar lista de pontos em [ { mes: "Jan/25", Materia1: 80, Materia2: 65 }, ... ]
  const materias = [...new Set(pontos.map(p => p.materia))].sort()
  const mesesOrdenados = [...new Set(pontos.map(p => p.mes))].sort()

  const dadosGrafico = mesesOrdenados.map(mes => {
    const obj = { mes: formatarMes(mes) }
    for (const mat of materias) {
      const ponto = pontos.find(p => p.mes === mes && p.materia === mat)
      obj[mat] = ponto ? ponto.perc : null
    }
    return obj
  })

  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={dadosGrafico} margin={{ top: 4, right: 16, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3a" />
        <XAxis dataKey="mes" tick={{ fill: '#888', fontSize: 12 }} />
        <YAxis domain={[0, 100]} tickFormatter={v => `${v}%`} tick={{ fill: '#888', fontSize: 12 }} width={40} />
        <Tooltip
          contentStyle={{ background: '#1a1a2e', border: '1px solid #2a2a3a', borderRadius: 8, fontSize: 12 }}
          labelStyle={{ color: '#ccc' }}
          formatter={(val, name) => val != null ? [`${val.toFixed(1)}%`, name] : ['—', name]}
        />
        <Legend wrapperStyle={{ fontSize: 12, color: '#888' }} />
        {materias.map((mat, i) => (
          <Line
            key={mat}
            type="monotone"
            dataKey={mat}
            stroke={CORES_LINHA[i % CORES_LINHA.length]}
            strokeWidth={2}
            dot={{ r: 3 }}
            connectNulls={false}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  )
}

export default function Desempenho() {
  const [data, setData] = useState(null)
  const [evolucao, setEvolucao] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    Promise.all([getDesempenho(), getEvolucao()])
      .then(([d, e]) => { setData(d); setEvolucao(e) })
      .catch(() => setError('Erro ao carregar dados de desempenho.'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <Spinner />

  if (error)
    return (
      <div className="max-w-3xl mx-auto px-4 py-8">
        <div className="bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3 text-red-400 text-sm">
          {error}
        </div>
      </div>
    )

  if (!data)
    return (
      <div className="max-w-3xl mx-auto px-4 py-8">
        <div className="bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3 text-red-400 text-sm">
          Não foi possível carregar os dados. Tente recarregar a página.
        </div>
      </div>
    )

  const { total_questoes = 0, perc_geral = 0, por_materia = [] } = data
  const lista = Array.isArray(por_materia) ? por_materia : []
  const maisForte = lista[0] ?? null
  const maisFraca = lista[lista.length - 1] ?? null

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 space-y-8">
      {/* Título */}
      <div>
        <h1 className="text-2xl font-bold text-brand-text">Desempenho</h1>
        <p className="text-brand-muted text-sm mt-1">Visão geral do seu progresso por matéria</p>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <KpiCard label="Questões feitas" value={(total_questoes ?? 0).toLocaleString()} color="indigo" />
        <KpiCard label="Aproveitamento geral" value={`${(perc_geral ?? 0).toFixed(1)}%`} color={(perc_geral ?? 0) >= 70 ? 'emerald' : (perc_geral ?? 0) >= 50 ? 'amber' : 'red'} />
        <KpiCard
          label="Mais forte"
          value={maisForte ? `${maisForte.perc.toFixed(1)}%` : '—'}
          sub={maisForte?.materia}
          color="emerald"
        />
        <KpiCard
          label="Mais fraca"
          value={maisFraca ? `${maisFraca.perc.toFixed(1)}%` : '—'}
          sub={maisFraca?.materia}
          color="red"
        />
      </div>

      {/* Evolução mensal */}
      <div className="bg-brand-card border border-brand-border rounded-2xl overflow-hidden">
        <div className="px-5 py-4 border-b border-brand-border">
          <h2 className="text-sm font-semibold text-brand-text">Evolução mensal</h2>
          <p className="text-xs text-brand-muted mt-0.5">% de acertos por matéria ao longo dos meses</p>
        </div>
        <div className="px-4 py-4">
          <GraficoEvolucao pontos={evolucao} />
        </div>
      </div>

      {/* Tabela por matéria */}
      {lista.length === 0 ? (
        <div className="bg-brand-card border border-brand-border rounded-2xl p-8 text-center">
          <p className="text-brand-muted text-sm">Nenhum dado de desempenho ainda. Responda questões para ver suas estatísticas aqui.</p>
        </div>
      ) : (
        <div className="bg-brand-card border border-brand-border rounded-2xl overflow-hidden">
          <div className="px-5 py-4 border-b border-brand-border">
            <h2 className="text-sm font-semibold text-brand-text">Por matéria</h2>
          </div>
          <div className="divide-y divide-brand-border">
            {lista.map((m) => (
              <div key={m.materia} className="px-5 py-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-brand-text">{m.materia}</span>
                  <div className="flex items-center gap-4 text-xs text-brand-muted">
                    <span>{m.acertos}/{m.realizadas} acertos</span>
                    <Tendencia atual={m.tend_perc_atual} anterior={m.tend_perc_anterior} />
                  </div>
                </div>
                <PercBar perc={m.perc} />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
