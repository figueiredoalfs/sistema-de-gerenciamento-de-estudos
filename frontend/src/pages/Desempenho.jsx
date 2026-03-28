import { useEffect, useState, useMemo } from 'react'
import {
  getPorMateria, getHeatmapSubtopicos, getEvolucao,
  getVolumeSemanal, getConsistencia, getPorBanca, getPorBancoQuestoes,
} from '../api/desempenho'
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer,
} from 'recharts'

// ── Paleta ────────────────────────────────────────────────────────────────────
const CORES = ['#6366f1','#10b981','#f59e0b','#ef4444','#8b5cf6','#06b6d4','#84cc16','#f97316','#ec4899','#14b8a6']
const COR_STATUS = { dominado: '#10b981', 'atenção': '#f59e0b', crítico: '#ef4444', sem_dados: '#374151' }

// ── Helpers ───────────────────────────────────────────────────────────────────
function Spinner() {
  return (
    <div className="flex items-center justify-center py-20">
      <div className="w-8 h-8 rounded-full border-2 border-brand-border border-t-indigo-500 animate-spin" />
    </div>
  )
}

function Section({ title, sub, children }) {
  return (
    <div className="bg-brand-card border border-brand-border rounded-2xl overflow-hidden">
      <div className="px-5 py-4 border-b border-brand-border">
        <h2 className="text-sm font-semibold text-brand-text">{title}</h2>
        {sub && <p className="text-xs text-brand-muted mt-0.5">{sub}</p>}
      </div>
      <div className="px-4 py-4">{children}</div>
    </div>
  )
}

function Empty({ msg = 'Nenhum dado disponível para o período selecionado.' }) {
  return <p className="py-8 text-center text-brand-muted text-sm">{msg}</p>
}

const tooltipStyle = {
  contentStyle: { background: '#1a1a2e', border: '1px solid #2a2a3a', borderRadius: 8, fontSize: 12 },
  labelStyle: { color: '#ccc' },
}

function formatSemana(s) {
  // "2025-W12" → "Sem 12"
  if (!s) return s
  const parts = s.split('-W')
  return parts.length === 2 ? `Sem ${parts[1]}` : s
}

// ── Bloco 1: Radar de matérias ────────────────────────────────────────────────
function RadarMaterias({ dados }) {
  if (!dados || dados.length === 0) return <Empty />
  const radarData = dados.map(m => ({
    materia: m.materia.length > 14 ? m.materia.slice(0, 14) + '…' : m.materia,
    taxa: parseFloat((m.taxa_acerto ?? 0).toFixed(1)),
  }))
  return (
    <ResponsiveContainer width="100%" height={300}>
      <RadarChart data={radarData} margin={{ top: 10, right: 30, left: 30, bottom: 10 }}>
        <PolarGrid stroke="#2a2a3a" />
        <PolarAngleAxis dataKey="materia" tick={{ fill: '#888', fontSize: 11 }} />
        <PolarRadiusAxis domain={[0, 100]} tick={{ fill: '#555', fontSize: 10 }} tickCount={4} />
        <Radar name="Acertos %" dataKey="taxa" stroke="#6366f1" fill="#6366f1" fillOpacity={0.3} />
        <Tooltip {...tooltipStyle} formatter={v => [`${v}%`, 'Taxa']} />
      </RadarChart>
    </ResponsiveContainer>
  )
}

// ── Bloco 2: Heatmap de subtópicos ────────────────────────────────────────────
function HeatmapSubtopicos({ dados }) {
  if (!dados || dados.length === 0) return <Empty />
  const grupos = {}
  for (const s of dados) {
    const mat = s.materia || 'Sem matéria'
    if (!grupos[mat]) grupos[mat] = []
    grupos[mat].push(s)
  }
  return (
    <div className="space-y-4">
      {Object.entries(grupos).map(([mat, subs]) => (
        <div key={mat}>
          <p className="text-xs font-medium text-brand-muted uppercase tracking-wide mb-2">{mat}</p>
          <div className="flex flex-wrap gap-1.5">
            {subs.map((s) => {
              const cor = COR_STATUS[s.status] || COR_STATUS.sem_dados
              const pct = s.taxa_acerto != null ? `${s.taxa_acerto.toFixed(0)}%` : '–'
              const nome = s.subtopico || s.nome || '–'
              return (
                <div
                  key={s.topico_id || s.subtopico_id || nome}
                  title={`${nome}: ${pct} (${s.total_questoes ?? 0} questões)`}
                  className="rounded px-2 py-1 text-xs text-white font-medium cursor-default select-none"
                  style={{ backgroundColor: cor + 'cc', border: `1px solid ${cor}` }}
                >
                  {nome.length > 20 ? nome.slice(0, 20) + '…' : nome}
                  <span className="ml-1 opacity-75">{pct}</span>
                </div>
              )
            })}
          </div>
        </div>
      ))}
      <div className="flex items-center gap-4 pt-2 flex-wrap">
        {[['dominado','Dominado (≥70%)'],['atenção','Atenção (50–70%)'],['crítico','Crítico (<50%)'],['sem_dados','Sem dados']].map(([k,l]) => (
          <div key={k} className="flex items-center gap-1.5 text-xs text-brand-muted">
            <span className="w-3 h-3 rounded-sm inline-block" style={{ backgroundColor: COR_STATUS[k] }} />
            {l}
          </div>
        ))}
      </div>
    </div>
  )
}

// ── Bloco 3: Evolução temporal ────────────────────────────────────────────────
function EvolucaoTemporal({ dados, periodo }) {
  if (!dados || dados.length === 0) return <Empty />

  const materias = [...new Set(dados.map(p => p.materia))].sort()
  const semanas = [...new Set(dados.map(p => p.semana))].sort()

  const chartData = semanas.map(sem => {
    const obj = { semana: formatSemana(sem) }
    for (const m of materias) {
      const pt = dados.find(p => p.semana === sem && p.materia === m)
      obj[m] = pt ? parseFloat((pt.taxa_acerto ?? 0).toFixed(1)) : null
    }
    return obj
  })

  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={chartData} margin={{ top: 4, right: 16, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3a" />
        <XAxis dataKey="semana" tick={{ fill: '#888', fontSize: 11 }} />
        <YAxis domain={[0, 100]} tickFormatter={v => `${v}%`} tick={{ fill: '#888', fontSize: 11 }} width={38} />
        <Tooltip {...tooltipStyle} formatter={(v, n) => v != null ? [`${v}%`, n] : ['—', n]} />
        <Legend wrapperStyle={{ fontSize: 12, color: '#888' }} />
        {materias.map((m, i) => (
          <Line key={m} type="monotone" dataKey={m} stroke={CORES[i % CORES.length]}
            strokeWidth={2} dot={{ r: 2 }} connectNulls={false} />
        ))}
      </LineChart>
    </ResponsiveContainer>
  )
}

// ── Bloco 4: Volume semanal empilhado ─────────────────────────────────────────
function VolumeSemanal({ dados }) {
  if (!dados || dados.length === 0) return <Empty />

  const materias = [...new Set(dados.flatMap(d => Object.keys(d.por_materia || {})))].sort()
  const chartData = dados.map(d => {
    const obj = { semana: formatSemana(d.semana) }
    for (const m of materias) obj[m] = d.por_materia?.[m] ?? 0
    return obj
  })

  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={chartData} margin={{ top: 4, right: 16, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3a" />
        <XAxis dataKey="semana" tick={{ fill: '#888', fontSize: 11 }} />
        <YAxis tick={{ fill: '#888', fontSize: 11 }} width={30} />
        <Tooltip {...tooltipStyle} />
        <Legend wrapperStyle={{ fontSize: 12, color: '#888' }} />
        {materias.map((m, i) => (
          <Bar key={m} dataKey={m} stackId="a" fill={CORES[i % CORES.length]} />
        ))}
      </BarChart>
    </ResponsiveContainer>
  )
}

// ── Bloco 5: Heatmap de consistência (GitHub-style) ───────────────────────────
function HeatmapConsistencia({ dados }) {
  if (!dados || dados.length === 0) return <Empty />

  const porData = {}
  for (const d of dados) porData[d.data] = d.total_questoes || 0

  // Últimas 26 semanas
  const hoje = new Date()
  const dias = []
  for (let i = 181; i >= 0; i--) {
    const d = new Date(hoje)
    d.setDate(d.getDate() - i)
    const key = d.toISOString().split('T')[0]
    dias.push({ key, val: porData[key] || 0, dow: d.getDay() })
  }

  // Agrupa em semanas (colunas)
  const semanas = []
  let semAtual = []
  for (const dia of dias) {
    semAtual.push(dia)
    if (dia.dow === 6 || dia === dias[dias.length - 1]) {
      semanas.push(semAtual)
      semAtual = []
    }
  }

  function cor(val) {
    if (val === 0) return '#1f2937'
    if (val < 10) return '#3730a3'
    if (val < 30) return '#4f46e5'
    if (val < 60) return '#6366f1'
    return '#818cf8'
  }

  return (
    <div className="overflow-x-auto">
      <div className="flex gap-0.5 min-w-max">
        {semanas.map((sem, si) => (
          <div key={si} className="flex flex-col gap-0.5">
            {sem.map((dia) => (
              <div
                key={dia.key}
                title={`${dia.key}: ${dia.val} questões`}
                className="w-3 h-3 rounded-sm cursor-default"
                style={{ backgroundColor: cor(dia.val) }}
              />
            ))}
          </div>
        ))}
      </div>
      <div className="flex items-center gap-2 mt-2">
        <span className="text-xs text-brand-muted">Menos</span>
        {[0, 5, 20, 50, 80].map(v => (
          <div key={v} className="w-3 h-3 rounded-sm" style={{ backgroundColor: cor(v) }} />
        ))}
        <span className="text-xs text-brand-muted">Mais</span>
      </div>
    </div>
  )
}

// ── Bloco 6: Por banca ────────────────────────────────────────────────────────
function PorBanca({ dados }) {
  if (!dados || dados.length === 0) return <Empty msg="Nenhum registro com banca identificada." />
  const sorted = [...dados].sort((a, b) => b.taxa_acerto - a.taxa_acerto)
  return (
    <ResponsiveContainer width="100%" height={Math.max(200, sorted.length * 36)}>
      <BarChart data={sorted} layout="vertical" margin={{ top: 4, right: 40, left: 10, bottom: 4 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3a" horizontal={false} />
        <XAxis type="number" domain={[0, 100]} tickFormatter={v => `${v}%`} tick={{ fill: '#888', fontSize: 11 }} />
        <YAxis type="category" dataKey="banca" tick={{ fill: '#ccc', fontSize: 12 }} width={120} />
        <Tooltip {...tooltipStyle} formatter={(v, n) => [`${v.toFixed(1)}%`, 'Taxa']} />
        <Bar dataKey="taxa_acerto" fill="#6366f1" radius={[0, 4, 4, 0]}
          label={{ position: 'right', fill: '#888', fontSize: 11, formatter: v => `${v.toFixed(0)}%` }} />
      </BarChart>
    </ResponsiveContainer>
  )
}

// ── Bloco 7: Por banco de questões ────────────────────────────────────────────
function PorBancoQuestoes({ dados }) {
  if (!dados || dados.length === 0) return <Empty />
  const sorted = [...dados].sort((a, b) => b.taxa_acerto - a.taxa_acerto)
  return (
    <ResponsiveContainer width="100%" height={Math.max(200, sorted.length * 40)}>
      <BarChart data={sorted} layout="vertical" margin={{ top: 4, right: 40, left: 10, bottom: 4 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3a" horizontal={false} />
        <XAxis type="number" domain={[0, 100]} tickFormatter={v => `${v}%`} tick={{ fill: '#888', fontSize: 11 }} />
        <YAxis type="category" dataKey="banco" tick={{ fill: '#ccc', fontSize: 12 }} width={120} />
        <Tooltip {...tooltipStyle} formatter={(v) => [`${v.toFixed(1)}%`, 'Taxa']} />
        <Bar dataKey="taxa_acerto" fill="#10b981" radius={[0, 4, 4, 0]}
          label={{ position: 'right', fill: '#888', fontSize: 11, formatter: v => `${v.toFixed(0)}%` }} />
      </BarChart>
    </ResponsiveContainer>
  )
}

// ── Componente principal ──────────────────────────────────────────────────────
const PERIODOS = [
  { value: '7d', label: '7 dias' },
  { value: '30d', label: '30 dias' },
  { value: '90d', label: '90 dias' },
  { value: 'tudo', label: 'Tudo' },
]

export default function Desempenho() {
  const [periodo, setPeriodo] = useState('30d')
  const [loading, setLoading] = useState(true)
  const [erros, setErros] = useState({})

  const [porMateria, setPorMateria] = useState(null)
  const [heatmapSubs, setHeatmapSubs] = useState(null)
  const [evolucao, setEvolucao] = useState(null)
  const [volumeSemanal, setVolumeSemanal] = useState(null)
  const [consistencia, setConsistencia] = useState(null)
  const [porBanca, setPorBanca] = useState(null)
  const [porBanco, setPorBanco] = useState(null)

  useEffect(() => {
    setLoading(true)
    const params = { periodo }
    Promise.allSettled([
      getPorMateria(params),
      getHeatmapSubtopicos(params),
      getPorMateria(params),  // evolução vem de getPorMateria
      getVolumeSemanal(),
      getConsistencia(),
      getPorBanca(),
      getPorBancoQuestoes(),
    ]).then(([pmRes, hsRes, _evRes, vsRes, consRes, bancaRes, bancoRes]) => {
      const e = {}
      if (pmRes.status === 'fulfilled') setPorMateria(pmRes.value)
      else e.porMateria = true
      if (hsRes.status === 'fulfilled') setHeatmapSubs(hsRes.value)
      else e.heatmapSubs = true
      // evolução: extrair pontos semanais de porMateria
      if (pmRes.status === 'fulfilled') {
        const pts = []
        for (const m of (pmRes.value || [])) {
          for (const pt of (m.evolucao_semanal || [])) {
            pts.push({ materia: m.materia, semana: pt.semana, taxa_acerto: pt.taxa ?? pt.taxa_acerto ?? 0 })
          }
        }
        setEvolucao(pts)
      }
      if (vsRes.status === 'fulfilled') setVolumeSemanal(vsRes.value)
      else e.volumeSemanal = true
      if (consRes.status === 'fulfilled') setConsistencia(consRes.value)
      else e.consistencia = true
      if (bancaRes.status === 'fulfilled') setPorBanca(bancaRes.value)
      else e.porBanca = true
      if (bancoRes.status === 'fulfilled') setPorBanco(bancoRes.value)
      else e.porBanco = true
      setErros(e)
    }).finally(() => setLoading(false))
  }, [periodo])

  const hasAnyData = porMateria?.length > 0 || heatmapSubs?.length > 0

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">
      {/* Cabeçalho + filtro de período */}
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-bold text-brand-text">Desempenho</h1>
          <p className="text-brand-muted text-sm mt-1">Análise detalhada do seu progresso</p>
        </div>
        <div className="flex items-center gap-1 bg-brand-card border border-brand-border rounded-xl p-1">
          {PERIODOS.map(p => (
            <button
              key={p.value}
              onClick={() => setPeriodo(p.value)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                periodo === p.value
                  ? 'bg-indigo-600 text-white'
                  : 'text-brand-muted hover:text-brand-text'
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {loading ? <Spinner /> : !hasAnyData ? (
        <div className="bg-brand-card border border-brand-border rounded-2xl p-10 text-center">
          <p className="text-brand-muted text-sm">Nenhum dado no período selecionado. Lance questões no Caderno de Questões para ver seus gráficos aqui.</p>
        </div>
      ) : (
        <>
          {/* Bloco 1 — Radar de matérias */}
          <Section title="Radar de matérias" sub="Visão geral do aproveitamento por matéria">
            <RadarMaterias dados={porMateria} />
          </Section>

          {/* Bloco 2 — Mapa de calor de subtópicos */}
          <Section title="Mapa de subtópicos" sub="Status de cada subtópico estudado">
            <HeatmapSubtopicos dados={heatmapSubs} />
          </Section>

          {/* Bloco 3 — Evolução temporal */}
          <Section title="Evolução temporal" sub="Taxa de acertos por semana e matéria">
            <EvolucaoTemporal dados={evolucao} periodo={periodo} />
          </Section>

          {/* Bloco 4 — Volume semanal */}
          <Section title="Volume semanal" sub="Questões respondidas por semana (últimas 8 semanas)">
            <VolumeSemanal dados={volumeSemanal} />
          </Section>

          {/* Bloco 5 — Consistência */}
          <Section title="Consistência" sub="Questões por dia nos últimos 6 meses">
            <HeatmapConsistencia dados={consistencia} />
          </Section>

          {/* Bloco 6 — Por banca */}
          <Section title="Desempenho por banca" sub="Taxa de acertos por banca examinadora">
            <PorBanca dados={porBanca} />
          </Section>

          {/* Bloco 7 — Por banco de questões */}
          <Section title="Desempenho por banco" sub="Taxa de acertos por banco de questões utilizado">
            <PorBancoQuestoes dados={porBanco} />
          </Section>
        </>
      )}
    </div>
  )
}
