import { useEffect, useState } from 'react'
import { getHierarquiaCompleta, getBancas, postBateria, listarBaterias } from '../api/bateria'

const inputCls = 'w-full bg-brand-surface border border-brand-border rounded-xl px-3 py-2.5 text-sm text-brand-text focus:outline-none focus:border-indigo-500 transition-colors disabled:opacity-50'
const selectCls = inputCls

function Campo({ label, children }) {
  return (
    <div className="space-y-1.5">
      <label className="text-xs font-medium text-brand-muted uppercase tracking-wide">{label}</label>
      {children}
    </div>
  )
}

function hoje() {
  return new Date().toISOString().split('T')[0]
}

const BANCOS = ['TEC Concursos', 'Qconcursos', 'Gran Cursos', 'Estratégia', 'CERS', 'Simulado Próprio', 'Outro']
const BANCOS_FONTE = {
  'TEC Concursos': 'tec',
  'Qconcursos': 'qconcursos',
  'Gran Cursos': 'manual',
  'Estratégia': 'manual',
  'CERS': 'manual',
  'Simulado Próprio': 'simulado',
  'Outro': 'manual',
}

let _nextId = 1
function newRow() { return { id: _nextId++, materia: '', modulo: '', subtopico: '', acertos: '', total: '' } }

export default function CadernoQuestoes() {
  const [hierarquia, setHierarquia] = useState([])
  const [bancasDisponiveis, setBancasDisponiveis] = useState([])
  const [baterias, setBaterias] = useState([])
  const [loadingHier, setLoadingHier] = useState(true)

  const [rows, setRows] = useState([newRow()])
  const [banco, setBanco] = useState('')
  const [banca, setBanca] = useState('')
  const [data, setData] = useState(hoje())

  const [enviando, setEnviando] = useState(false)
  const [sucesso, setSucesso] = useState(null)
  const [erro, setErro] = useState(null)

  useEffect(() => {
    Promise.allSettled([getHierarquiaCompleta(), getBancas(), listarBaterias({ pagina: 1, por_pagina: 20 })])
      .then(([hierRes, bancasRes, bateRes]) => {
        if (hierRes.status === 'fulfilled') setHierarquia(Array.isArray(hierRes.value) ? hierRes.value : [])
        if (bancasRes.status === 'fulfilled') setBancasDisponiveis(bancasRes.value?.map(b => b.nome) || [])
        if (bateRes.status === 'fulfilled') setBaterias(Array.isArray(bateRes.value) ? bateRes.value : [])
      })
      .finally(() => setLoadingHier(false))
  }, [])

  function updateRow(id, field, value) {
    setRows(prev => prev.map(r => {
      if (r.id !== id) return r
      const updated = { ...r, [field]: value }
      if (field === 'materia') { updated.modulo = ''; updated.subtopico = '' }
      if (field === 'modulo') { updated.subtopico = '' }
      return updated
    }))
  }

  function addRow() { setRows(prev => [...prev, newRow()]) }
  function removeRow(id) { setRows(prev => prev.filter(r => r.id !== id)) }

  async function handleSalvar(e) {
    e.preventDefault()
    setErro(null)
    setSucesso(null)
    for (const r of rows) {
      if (parseInt(r.acertos) > parseInt(r.total)) {
        setErro('Acertos não pode ser maior que o total.')
        return
      }
    }
    setEnviando(true)
    try {
      const questoes = rows.map(r => {
        const materiaObj = hierarquia.find(m => m.id === r.materia)
        const modulos = materiaObj?.modulos || []
        const moduloObj = modulos.find(m => m.id === r.modulo)
        const subtopicos = moduloObj?.subtopicos || []
        const subObj = subtopicos.find(s => s.id === r.subtopico)
        return {
          materia: materiaObj?.nome || '',
          subtopico: subObj?.nome || moduloObj?.nome || '',
          topico_id: r.subtopico || r.modulo || null,
          acertos: parseInt(r.acertos),
          total: parseInt(r.total),
          fonte: BANCOS_FONTE[banco] || 'manual',
          banca: banca || null,
        }
      })
      await postBateria(questoes)

      const totalAcertos = rows.reduce((s, r) => s + parseInt(r.acertos || 0), 0)
      const totalQuestoes = rows.reduce((s, r) => s + parseInt(r.total || 0), 0)
      const pct = totalQuestoes > 0 ? Math.round((totalAcertos / totalQuestoes) * 100) : 0
      setSucesso(`Registrado! ${rows.length} matéria(s) — ${pct}% médio`)
      setRows([newRow()])

      listarBaterias({ pagina: 1, por_pagina: 20 }).then(b => setBaterias(Array.isArray(b) ? b : []))
    } catch (err) {
      setErro(err.response?.data?.detail || err.message || 'Erro ao registrar.')
    } finally {
      setEnviando(false)
    }
  }

  const canSubmit = rows.every(r => r.materia && r.modulo && r.acertos && r.total) && banco

  return (
    <div className="max-w-2xl mx-auto px-4 py-8 space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-brand-text">Caderno de Questões</h1>
        <p className="text-brand-muted text-sm mt-1">Registre seus acertos e erros por subtópico</p>
      </div>

      <form onSubmit={handleSalvar} className="bg-brand-card border border-brand-border rounded-2xl p-6 space-y-5">
        <div className="space-y-4">
          {rows.map((row, idx) => {
            const materiaObj = hierarquia.find(m => m.id === row.materia) || null
            const modulos = materiaObj?.modulos || []
            const moduloObj = modulos.find(m => m.id === row.modulo) || null
            const subtopicos = moduloObj?.subtopicos || []
            const pct = row.total > 0 ? Math.round((parseInt(row.acertos || 0) / parseInt(row.total)) * 100) : null

            return (
              <div key={row.id} className="border border-brand-border rounded-xl p-4 space-y-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-semibold text-brand-muted uppercase tracking-wide">Matéria {idx + 1}</span>
                  {rows.length > 1 && (
                    <button type="button" onClick={() => removeRow(row.id)} className="text-brand-muted hover:text-red-400 transition-colors text-sm px-1">×</button>
                  )}
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <Campo label="Matéria">
                    <select className={selectCls} value={row.materia} onChange={e => updateRow(row.id, 'materia', e.target.value)} disabled={loadingHier} required>
                      <option value="">Selecione</option>
                      {hierarquia.map(m => <option key={m.id} value={m.id}>{m.nome}</option>)}
                    </select>
                  </Campo>
                  <Campo label="Módulo">
                    <select className={selectCls} value={row.modulo} onChange={e => updateRow(row.id, 'modulo', e.target.value)} disabled={!row.materia} required>
                      <option value="">Selecione</option>
                      {modulos.map(m => <option key={m.id} value={m.id}>{m.nome}</option>)}
                    </select>
                  </Campo>
                  <Campo label="Subtópico">
                    <select className={selectCls} value={row.subtopico} onChange={e => updateRow(row.id, 'subtopico', e.target.value)} disabled={!row.modulo}>
                      <option value="">Opcional</option>
                      {subtopicos.map(s => <option key={s.id} value={s.id}>{s.nome}</option>)}
                    </select>
                  </Campo>
                </div>

                <div className="grid grid-cols-3 gap-3">
                  <Campo label="Acertos">
                    <input type="number" className={inputCls} placeholder="14" min="0" value={row.acertos} onChange={e => updateRow(row.id, 'acertos', e.target.value)} required />
                  </Campo>
                  <Campo label="Total">
                    <input type="number" className={inputCls} placeholder="20" min="1" value={row.total} onChange={e => updateRow(row.id, 'total', e.target.value)} required />
                  </Campo>
                  <Campo label="Aproveitamento">
                    <div className={`${inputCls} flex items-center`}>
                      <span className={`font-semibold ${pct == null ? 'text-brand-muted' : pct >= 70 ? 'text-emerald-400' : pct >= 50 ? 'text-amber-400' : 'text-red-400'}`}>
                        {pct != null ? `${pct}%` : '—'}
                      </span>
                    </div>
                  </Campo>
                </div>
              </div>
            )
          })}
        </div>

        <button
          type="button"
          onClick={addRow}
          className="w-full py-2 border border-dashed border-brand-border rounded-xl text-brand-muted text-sm hover:text-brand-text hover:border-indigo-500 transition-colors"
        >
          ＋ Adicionar matéria
        </button>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Campo label="Banco de questões">
            <select className={selectCls} value={banco} onChange={e => setBanco(e.target.value)} required>
              <option value="">Selecione</option>
              {BANCOS.map(b => <option key={b} value={b}>{b}</option>)}
            </select>
          </Campo>

          <Campo label="Banca (opcional)">
            <select className={selectCls} value={banca} onChange={e => setBanca(e.target.value)}>
              <option value="">Sem banca</option>
              {(bancasDisponiveis.length > 0 ? bancasDisponiveis : ['CESPE/CEBRASPE', 'FCC', 'FGV', 'VUNESP', 'AOCP', 'IDECAN', 'IBFC', 'QUADRIX', 'IADES', 'UPENET', 'Outra banca']).map(b => (
                <option key={b} value={b}>{b}</option>
              ))}
            </select>
          </Campo>

          <Campo label="Data">
            <input type="date" className={inputCls} value={data} onChange={e => setData(e.target.value)} max={hoje()} required />
          </Campo>
        </div>

        {sucesso && (
          <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl px-4 py-3 text-emerald-400 text-sm">{sucesso}</div>
        )}
        {erro && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3 text-red-400 text-sm">{erro}</div>
        )}

        <button
          type="submit"
          disabled={enviando || !canSubmit}
          className="w-full py-3 bg-brand-gradient text-white rounded-xl font-semibold text-sm hover:opacity-90 transition-all duration-300 disabled:opacity-50"
        >
          {enviando ? 'Salvando...' : 'Registrar'}
        </button>
      </form>

      {baterias.length > 0 && (
        <div className="bg-brand-card border border-brand-border rounded-2xl overflow-hidden">
          <div className="px-5 py-4 border-b border-brand-border">
            <h2 className="text-sm font-semibold text-brand-text">Histórico</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-brand-border text-xs text-brand-muted">
                  <th className="text-left px-5 py-3">Data</th>
                  <th className="text-left px-5 py-3">Matérias</th>
                  <th className="text-right px-5 py-3">Questões</th>
                  <th className="text-right px-5 py-3">Acertos</th>
                  <th className="text-right px-5 py-3">%</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-brand-border">
                {baterias.map(b => (
                  <tr key={b.bateria_id} className="hover:bg-brand-surface/40 transition-colors">
                    <td className="px-5 py-3 text-brand-muted">{new Date(b.data).toLocaleDateString('pt-BR')}</td>
                    <td className="px-5 py-3 text-brand-text max-w-xs truncate">{b.materias?.join(', ') || '—'}</td>
                    <td className="px-5 py-3 text-right text-brand-muted">{b.total_questoes}</td>
                    <td className="px-5 py-3 text-right text-brand-muted">{b.total_acertos}</td>
                    <td className={`px-5 py-3 text-right font-semibold ${b.percentual_geral >= 70 ? 'text-emerald-400' : b.percentual_geral >= 50 ? 'text-amber-400' : 'text-red-400'}`}>
                      {b.percentual_geral.toFixed(1)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
