import { useEffect, useMemo, useState } from 'react'
import { importarLote, listarTopicos } from '../api/questoes'

const EXEMPLO = [
  {
    subject_id: '<id_da_materia>',
    topic_id: '<id_do_bloco>',
    subtopic_id: '<id_do_subtopico>',
    enunciado: 'Texto da questão...',
    alternativas: { A: '...', B: '...', C: '...', D: '...', E: '...' },
    resposta_correta: 'A',
    fonte: 'tec',
    banca: 'CESPE',
    ano: 2024,
  },
]

export default function AdminImportar() {
  const [topicos, setTopicos] = useState([])
  const [loadingTopicos, setLoadingTopicos] = useState(true)

  const [json, setJson] = useState('')
  const [preview, setPreview] = useState(null)
  const [parseError, setParseError] = useState('')

  const [resultado, setResultado] = useState(null)
  const [importando, setImportando] = useState(false)

  const [filtroMateria, setFiltroMateria] = useState('')

  useEffect(() => {
    listarTopicos()
      .then(setTopicos)
      .catch(() => {})
      .finally(() => setLoadingTopicos(false))
  }, [])

  const subjects = useMemo(
    () => topicos.filter((t) => t.nivel === 0).sort((a, b) => a.nome.localeCompare(b.nome)),
    [topicos]
  )
  const blocos = useMemo(
    () =>
      topicos
        .filter((t) => t.nivel === 1 && (!filtroMateria || t.parent_id === filtroMateria))
        .sort((a, b) => a.nome.localeCompare(b.nome)),
    [topicos, filtroMateria]
  )
  const subtopicosVisiveis = useMemo(() => {
    const blocoIds = new Set(blocos.map((b) => b.id))
    return topicos
      .filter((t) => t.nivel === 2 && (!filtroMateria || blocoIds.has(t.parent_id)))
      .sort((a, b) => a.nome.localeCompare(b.nome))
  }, [topicos, blocos, filtroMateria])

  function handleParse() {
    setParseError('')
    setPreview(null)
    setResultado(null)
    try {
      const parsed = JSON.parse(json)
      if (!Array.isArray(parsed)) throw new Error('O JSON deve ser um array [ ... ]')
      if (parsed.length === 0) throw new Error('Array vazio')
      setPreview(parsed)
    } catch (e) {
      setParseError(e.message)
    }
  }

  async function handleImportar() {
    if (!preview) return
    setImportando(true)
    setResultado(null)
    try {
      const res = await importarLote(preview)
      setResultado(res)
    } catch (e) {
      setResultado({ importadas: 0, erros: [e.response?.data?.detail || 'Erro ao importar'] })
    } finally {
      setImportando(false)
    }
  }

  const camposObrigatorios = ['subject_id', 'topic_id', 'subtopic_id', 'enunciado', 'alternativas', 'resposta_correta']

  function validarItem(item) {
    const faltando = camposObrigatorios.filter((c) => !item[c])
    const altKeys = item.alternativas ? Object.keys(item.alternativas) : []
    const altFaltando = ['A', 'B', 'C', 'D', 'E'].filter((k) => !altKeys.includes(k))
    return [...faltando.map((c) => `campo "${c}" ausente`), ...altFaltando.map((k) => `alternativa ${k} ausente`)]
  }

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      <h1 className="text-xl font-bold text-brand-text">Importar Questões em Lote</h1>

      {/* Referência de IDs */}
      <section className="bg-brand-card border border-brand-border rounded-xl p-4 space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-brand-text">Referência de IDs</h2>
          <select
            className="text-xs bg-brand-surface border border-brand-border rounded-lg px-2 py-1 text-brand-muted"
            value={filtroMateria}
            onChange={(e) => setFiltroMateria(e.target.value)}
          >
            <option value="">Todas as matérias</option>
            {subjects.map((s) => (
              <option key={s.id} value={s.id}>{s.nome}</option>
            ))}
          </select>
        </div>

        {loadingTopicos ? (
          <p className="text-xs text-brand-muted">Carregando tópicos...</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="text-brand-muted border-b border-brand-border">
                  <th className="text-left py-1 pr-4">Nível</th>
                  <th className="text-left py-1 pr-4">Nome</th>
                  <th className="text-left py-1 font-mono">ID</th>
                </tr>
              </thead>
              <tbody>
                {subjects
                  .filter((s) => !filtroMateria || s.id === filtroMateria)
                  .map((s) => (
                    <>
                      <tr key={s.id} className="border-b border-brand-border/40">
                        <td className="py-1 pr-4 text-indigo-400 font-medium">Matéria</td>
                        <td className="py-1 pr-4 text-brand-text font-medium">{s.nome}</td>
                        <td className="py-1 font-mono text-brand-muted select-all">{s.id}</td>
                      </tr>
                      {blocos
                        .filter((b) => b.parent_id === s.id)
                        .map((b) => (
                          <>
                            <tr key={b.id} className="border-b border-brand-border/30">
                              <td className="py-1 pr-4 pl-3 text-sky-400">Bloco</td>
                              <td className="py-1 pr-4 text-brand-muted">{b.nome}</td>
                              <td className="py-1 font-mono text-brand-muted/70 select-all">{b.id}</td>
                            </tr>
                            {subtopicosVisiveis
                              .filter((st) => st.parent_id === b.id)
                              .map((st) => (
                                <tr key={st.id} className="border-b border-brand-border/20">
                                  <td className="py-1 pr-4 pl-6 text-green-400 text-xs">Subtópico</td>
                                  <td className="py-1 pr-4 text-brand-muted/80 text-xs">{st.nome}</td>
                                  <td className="py-1 font-mono text-brand-muted/60 text-xs select-all">{st.id}</td>
                                </tr>
                              ))}
                          </>
                        ))}
                    </>
                  ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* Formato esperado */}
      <section className="bg-brand-card border border-brand-border rounded-xl p-4 space-y-2">
        <h2 className="text-sm font-semibold text-brand-text">Formato JSON esperado</h2>
        <pre className="text-xs text-brand-muted bg-brand-surface rounded-lg p-3 overflow-x-auto">
          {JSON.stringify(EXEMPLO, null, 2)}
        </pre>
        <p className="text-xs text-brand-muted">
          Fontes válidas: <code className="text-indigo-400">admin | qconcursos | tec | prova_real | simulado</code>
        </p>
      </section>

      {/* Editor JSON */}
      <section className="bg-brand-card border border-brand-border rounded-xl p-4 space-y-3">
        <h2 className="text-sm font-semibold text-brand-text">Cole o JSON das questões</h2>
        <textarea
          className="w-full h-48 text-xs font-mono bg-brand-surface border border-brand-border rounded-lg p-3 text-brand-text resize-y focus:outline-none focus:border-indigo-500"
          placeholder="[ { ... }, { ... } ]"
          value={json}
          onChange={(e) => { setJson(e.target.value); setParseError(''); setPreview(null) }}
        />
        {parseError && <p className="text-xs text-red-400">{parseError}</p>}
        <button
          onClick={handleParse}
          disabled={!json.trim()}
          className="px-4 py-2 text-sm rounded-lg bg-brand-surface border border-brand-border text-brand-text hover:border-indigo-500 disabled:opacity-40 transition-all"
        >
          Validar e Pré-visualizar
        </button>
      </section>

      {/* Preview */}
      {preview && (
        <section className="bg-brand-card border border-brand-border rounded-xl p-4 space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-brand-text">
              Preview — {preview.length} questão{preview.length !== 1 ? 'ões' : ''}
            </h2>
            <button
              onClick={handleImportar}
              disabled={importando}
              className="px-4 py-2 text-sm rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white disabled:opacity-50 transition-all"
            >
              {importando ? 'Importando...' : 'Importar'}
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="text-brand-muted border-b border-brand-border">
                  <th className="text-left py-1 pr-3">#</th>
                  <th className="text-left py-1 pr-3">Enunciado</th>
                  <th className="text-left py-1 pr-3">Gabarito</th>
                  <th className="text-left py-1 pr-3">Fonte</th>
                  <th className="text-left py-1">Status</th>
                </tr>
              </thead>
              <tbody>
                {preview.map((item, i) => {
                  const erros = validarItem(item)
                  return (
                    <tr key={i} className="border-b border-brand-border/30">
                      <td className="py-1.5 pr-3 text-brand-muted">{i + 1}</td>
                      <td className="py-1.5 pr-3 text-brand-text max-w-xs truncate">
                        {item.enunciado || <span className="text-red-400">—</span>}
                      </td>
                      <td className="py-1.5 pr-3 text-brand-muted">{item.resposta_correta || '—'}</td>
                      <td className="py-1.5 pr-3 text-brand-muted">{item.fonte || '—'}</td>
                      <td className="py-1.5">
                        {erros.length === 0 ? (
                          <span className="text-green-400">OK</span>
                        ) : (
                          <span className="text-red-400" title={erros.join(', ')}>
                            {erros.length} erro{erros.length > 1 ? 's' : ''}
                          </span>
                        )}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* Resultado */}
      {resultado && (
        <section className={`border rounded-xl p-4 space-y-2 ${resultado.importadas > 0 ? 'bg-green-500/5 border-green-500/30' : 'bg-red-500/5 border-red-500/30'}`}>
          <p className="text-sm font-semibold text-brand-text">
            {resultado.importadas} questão{resultado.importadas !== 1 ? 'ões' : ''} importada{resultado.importadas !== 1 ? 's' : ''} com sucesso
          </p>
          {resultado.erros?.length > 0 && (
            <ul className="text-xs text-red-400 space-y-0.5">
              {resultado.erros.map((e, i) => <li key={i}>{e}</li>)}
            </ul>
          )}
        </section>
      )}
    </div>
  )
}
