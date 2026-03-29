import { useEffect, useState } from 'react'
import { getHierarquiaCompleta, getBancas, postBateria, listarBaterias, getBateriaDetail, putBateria } from '../api/bateria'

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
function newSubRow() { return { id: _nextId++, subtopico: '', acertos: '', total: '' } }
function newGroup() { return { id: _nextId++, materia: '', modulo: '', subtopicos: [newSubRow()] } }

function ModalEditarBateria({ bateriaId, bancasDisponiveis, onClose, onSaved }) {
  const [detalhe, setDetalhe] = useState(null)
  const [loading, setLoading] = useState(true)
  const [duracao, setDuracao] = useState('')
  const [banca, setBanca] = useState('')
  const [data, setData] = useState('')
  const [rows, setRows] = useState([])
  const [salvando, setSalvando] = useState(false)
  const [erro, setErro] = useState(null)

  useEffect(() => {
    getBateriaDetail(bateriaId)
      .then(d => {
        setDetalhe(d)
        setDuracao(d.duracao_min != null ? String(d.duracao_min) : '')
        setBanca(d.banca || '')
        setData(d.data ? d.data.split('T')[0] : hoje())
        setRows(d.proficiencias.map(p => ({ ...p, acertos: String(p.acertos), total: String(p.total) })))
      })
      .catch(() => setErro('Não foi possível carregar os dados.'))
      .finally(() => setLoading(false))
  }, [bateriaId])

  function updateRow(id, field, value) {
    setRows(prev => prev.map(r => r.id === id ? { ...r, [field]: value } : r))
  }

  async function handleSalvar(e) {
    e.preventDefault()
    setErro(null)
    for (const r of rows) {
      if (parseInt(r.acertos) > parseInt(r.total)) {
        setErro('Acertos não pode ser maior que o total.')
        return
      }
    }
    setSalvando(true)
    try {
      await putBateria(bateriaId, {
        duracao_min: duracao ? parseInt(duracao, 10) : null,
        banca: banca || null,
        data: data || null,
        proficiencias: rows.map(r => ({ id: r.id, acertos: parseInt(r.acertos), total: parseInt(r.total) })),
      })
      onSaved()
    } catch (err) {
      setErro(err.response?.data?.detail || err.message || 'Erro ao salvar.')
    } finally {
      setSalvando(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div className="bg-brand-card border border-brand-border rounded-2xl p-6 w-full max-w-lg space-y-5 shadow-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-brand-text">Editar Bateria</h2>
          <button onClick={onClose} className="text-brand-muted hover:text-brand-text text-xl leading-none">×</button>
        </div>

        {loading && <p className="text-brand-muted text-sm text-center py-4">Carregando...</p>}
        {!loading && detalhe && (
          <form onSubmit={handleSalvar} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <Campo label="Data">
                <input type="date" className={inputCls} value={data} onChange={e => setData(e.target.value)} max={hoje()} required />
              </Campo>
              <Campo label="Duração (min)">
                <input type="number" className={inputCls} placeholder="Ex: 60" value={duracao} onChange={e => setDuracao(e.target.value)} min="1" max="480" />
              </Campo>
            </div>

            <Campo label="Banca (opcional)">
              <select className={inputCls} value={banca} onChange={e => setBanca(e.target.value)}>
                <option value="">Sem banca</option>
                {(bancasDisponiveis.length > 0 ? bancasDisponiveis : ['CESPE/CEBRASPE', 'FCC', 'FGV', 'VUNESP', 'AOCP', 'IDECAN', 'IBFC', 'QUADRIX', 'IADES', 'UPENET', 'Outra banca']).map(b => (
                  <option key={b} value={b}>{b}</option>
                ))}
              </select>
            </Campo>

            <div className="space-y-2">
              <p className="text-xs font-medium text-brand-muted uppercase tracking-wide">Questões por matéria</p>
              {rows.map(r => {
                const pct = r.total > 0 ? Math.round((parseInt(r.acertos || 0) / parseInt(r.total)) * 100) : null
                return (
                  <div key={r.id} className="bg-brand-surface rounded-lg p-3 space-y-2">
                    <p className="text-xs text-brand-text font-medium">{r.materia}{r.subtopico ? ` — ${r.subtopico}` : ''}</p>
                    <div className="grid grid-cols-3 gap-2">
                      <Campo label="Acertos">
                        <input type="number" className={inputCls} min="0" value={r.acertos} onChange={e => updateRow(r.id, 'acertos', e.target.value)} required />
                      </Campo>
                      <Campo label="Total">
                        <input type="number" className={inputCls} min="1" value={r.total} onChange={e => updateRow(r.id, 'total', e.target.value)} required />
                      </Campo>
                      <Campo label="%">
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

            {erro && <p className="text-red-400 text-sm">{erro}</p>}

            <div className="flex gap-3 pt-1">
              <button type="button" onClick={onClose} className="flex-1 py-2.5 border border-brand-border rounded-xl text-brand-muted text-sm hover:text-brand-text transition-colors">
                Cancelar
              </button>
              <button type="submit" disabled={salvando} className="flex-1 py-2.5 bg-brand-gradient text-white rounded-xl font-semibold text-sm hover:opacity-90 transition-all disabled:opacity-50">
                {salvando ? 'Salvando...' : 'Salvar'}
              </button>
            </div>
          </form>
        )}
        {erro && !detalhe && <p className="text-red-400 text-sm text-center">{erro}</p>}
      </div>
    </div>
  )
}

export default function CadernoQuestoes() {
  const [hierarquia, setHierarquia] = useState([])
  const [bancasDisponiveis, setBancasDisponiveis] = useState([])
  const [baterias, setBaterias] = useState([])
  const [loadingHier, setLoadingHier] = useState(true)

  const [groups, setGroups] = useState([newGroup()])
  const [banco, setBanco] = useState('')
  const [banca, setBanca] = useState('')
  const [data, setData] = useState(hoje())
  const [duracao, setDuracao] = useState('')

  const [enviando, setEnviando] = useState(false)
  const [sucesso, setSucesso] = useState(null)
  const [erro, setErro] = useState(null)
  const [editandoBateria, setEditandoBateria] = useState(null)

  useEffect(() => {
    Promise.allSettled([getHierarquiaCompleta(), getBancas(), listarBaterias({ pagina: 1, por_pagina: 20 })])
      .then(([hierRes, bancasRes, bateRes]) => {
        if (hierRes.status === 'fulfilled') setHierarquia(Array.isArray(hierRes.value) ? hierRes.value : [])
        if (bancasRes.status === 'fulfilled') setBancasDisponiveis(bancasRes.value?.map(b => b.nome) || [])
        if (bateRes.status === 'fulfilled') setBaterias(Array.isArray(bateRes.value) ? bateRes.value : [])
      })
      .finally(() => setLoadingHier(false))
  }, [])

  function updateGroup(gid, field, value) {
    setGroups(prev => prev.map(g => {
      if (g.id !== gid) return g
      const updated = { ...g, [field]: value }
      if (field === 'materia') { updated.modulo = ''; updated.subtopicos = [newSubRow()] }
      if (field === 'modulo') { updated.subtopicos = updated.subtopicos.map(s => ({ ...s, subtopico: '' })) }
      return updated
    }))
  }

  function updateSubRow(gid, sid, field, value) {
    setGroups(prev => prev.map(g => {
      if (g.id !== gid) return g
      return { ...g, subtopicos: g.subtopicos.map(s => s.id === sid ? { ...s, [field]: value } : s) }
    }))
  }

  function addSubRow(gid) {
    setGroups(prev => prev.map(g => g.id === gid ? { ...g, subtopicos: [...g.subtopicos, newSubRow()] } : g))
  }

  function removeSubRow(gid, sid) {
    setGroups(prev => prev.map(g => {
      if (g.id !== gid) return g
      return { ...g, subtopicos: g.subtopicos.filter(s => s.id !== sid) }
    }))
  }

  function addGroup() { setGroups(prev => [...prev, newGroup()]) }
  function removeGroup(gid) { setGroups(prev => prev.filter(g => g.id !== gid)) }

  async function handleSalvar(e) {
    e.preventDefault()
    setErro(null)
    setSucesso(null)
    for (const g of groups) {
      for (const s of g.subtopicos) {
        if (parseInt(s.acertos) > parseInt(s.total)) {
          setErro('Acertos não pode ser maior que o total.')
          return
        }
      }
    }
    setEnviando(true)
    try {
      const questoes = groups.flatMap(g => {
        const materiaObj = hierarquia.find(m => m.id === g.materia)
        const moduloObj = materiaObj?.modulos?.find(m => m.id === g.modulo)
        return g.subtopicos.map(s => {
          const subObj = moduloObj?.subtopicos?.find(st => st.id === s.subtopico)
          return {
            materia: materiaObj?.nome || '',
            subtopico: subObj?.nome || moduloObj?.nome || '',
            topico_id: s.subtopico || g.modulo || null,
            acertos: parseInt(s.acertos),
            total: parseInt(s.total),
            fonte: BANCOS_FONTE[banco] || 'manual',
            banca: banca || null,
          }
        })
      })

      await postBateria(questoes, duracao ? parseInt(duracao, 10) : null)

      const totalAcertos = questoes.reduce((s, q) => s + q.acertos, 0)
      const totalQuestoes = questoes.reduce((s, q) => s + q.total, 0)
      const pct = totalQuestoes > 0 ? Math.round((totalAcertos / totalQuestoes) * 100) : 0
      setSucesso(`Registrado! ${questoes.length} lançamento(s) — ${pct}% médio`)
      setGroups([newGroup()])
      setDuracao('')

      listarBaterias({ pagina: 1, por_pagina: 20 }).then(b => setBaterias(Array.isArray(b) ? b : []))
    } catch (err) {
      setErro(err.response?.data?.detail || err.message || 'Erro ao registrar.')
    } finally {
      setEnviando(false)
    }
  }

  const canSubmit = groups.every(g =>
    g.materia && g.modulo &&
    g.subtopicos.every(s => s.acertos !== '' && s.total !== '')
  ) && banco

  return (
    <div className="max-w-2xl mx-auto px-4 py-8 space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-brand-text">Caderno de Questões</h1>
        <p className="text-brand-muted text-sm mt-1">Registre seus acertos e erros por subtópico</p>
      </div>

      <form onSubmit={handleSalvar} className="bg-brand-card border border-brand-border rounded-2xl p-6 space-y-5">
        <div className="space-y-4">
          {groups.map((group, gIdx) => {
            const materiaObj = hierarquia.find(m => m.id === group.materia) || null
            const modulos = materiaObj?.modulos || []
            const moduloObj = modulos.find(m => m.id === group.modulo) || null
            const subtopicosDisp = moduloObj?.subtopicos || []

            return (
              <div key={group.id} className="border border-brand-border rounded-xl p-4 space-y-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-semibold text-brand-muted uppercase tracking-wide">Matéria {gIdx + 1}</span>
                  {groups.length > 1 && (
                    <button type="button" onClick={() => removeGroup(group.id)} className="text-brand-muted hover:text-red-400 transition-colors text-sm px-1">×</button>
                  )}
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <Campo label="Matéria">
                    <select className={selectCls} value={group.materia} onChange={e => updateGroup(group.id, 'materia', e.target.value)} disabled={loadingHier} required>
                      <option value="">Selecione</option>
                      {hierarquia.map(m => <option key={m.id} value={m.id}>{m.nome}</option>)}
                    </select>
                  </Campo>
                  <Campo label="Módulo">
                    <select className={selectCls} value={group.modulo} onChange={e => updateGroup(group.id, 'modulo', e.target.value)} disabled={!group.materia} required>
                      <option value="">Selecione</option>
                      {modulos.map(m => <option key={m.id} value={m.id}>{m.nome}</option>)}
                    </select>
                  </Campo>
                </div>

                <div className="space-y-2">
                  {group.subtopicos.map((sub, sIdx) => {
                    const pct = sub.total > 0 ? Math.round((parseInt(sub.acertos || 0) / parseInt(sub.total)) * 100) : null
                    return (
                      <div key={sub.id} className="bg-brand-surface rounded-lg p-3 space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-brand-muted">Subtópico {sIdx + 1}</span>
                          {group.subtopicos.length > 1 && (
                            <button type="button" onClick={() => removeSubRow(group.id, sub.id)} className="text-brand-muted hover:text-red-400 transition-colors text-xs px-1">×</button>
                          )}
                        </div>
                        <Campo label="Subtópico (opcional)">
                          <select className={selectCls} value={sub.subtopico} onChange={e => updateSubRow(group.id, sub.id, 'subtopico', e.target.value)} disabled={!group.modulo}>
                            <option value="">Opcional</option>
                            {subtopicosDisp.map(s => <option key={s.id} value={s.id}>{s.nome}</option>)}
                          </select>
                        </Campo>
                        <div className="grid grid-cols-3 gap-3">
                          <Campo label="Acertos">
                            <input type="number" className={inputCls} placeholder="14" min="0" value={sub.acertos} onChange={e => updateSubRow(group.id, sub.id, 'acertos', e.target.value)} required />
                          </Campo>
                          <Campo label="Total">
                            <input type="number" className={inputCls} placeholder="20" min="1" value={sub.total} onChange={e => updateSubRow(group.id, sub.id, 'total', e.target.value)} required />
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
                  onClick={() => addSubRow(group.id)}
                  disabled={!group.modulo}
                  className="w-full py-1.5 border border-dashed border-brand-border rounded-lg text-brand-muted text-xs hover:text-brand-text hover:border-indigo-400 transition-colors disabled:opacity-40"
                >
                  ＋ Subtópico
                </button>
              </div>
            )
          })}
        </div>

        <button
          type="button"
          onClick={addGroup}
          className="w-full py-2 border border-dashed border-brand-border rounded-xl text-brand-muted text-sm hover:text-brand-text hover:border-indigo-500 transition-colors"
        >
          ＋ Adicionar matéria
        </button>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
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

          <Campo label="Duração (minutos, opcional)">
            <input type="number" className={inputCls} placeholder="Ex: 60" value={duracao} onChange={e => setDuracao(e.target.value)} min="1" max="480" />
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
                  <th className="px-5 py-3"></th>
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
                    <td className="px-5 py-3 text-right">
                      <button
                        onClick={() => setEditandoBateria(b.bateria_id)}
                        className="text-brand-muted hover:text-indigo-400 transition-colors text-base leading-none"
                        title="Editar"
                      >
                        ✏
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {editandoBateria && (
        <ModalEditarBateria
          bateriaId={editandoBateria}
          bancasDisponiveis={bancasDisponiveis}
          onClose={() => setEditandoBateria(null)}
          onSaved={() => {
            setEditandoBateria(null)
            listarBaterias({ pagina: 1, por_pagina: 20 }).then(b => setBaterias(Array.isArray(b) ? b : []))
          }}
        />
      )}
    </div>
  )
}
