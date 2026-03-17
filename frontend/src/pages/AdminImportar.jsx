import { useEffect, useRef, useState } from 'react'
import { importarQuestoes } from '../api/adminQuestoes'

const EXEMPLO_JSON = [
  {
    materia: 'Direito Administrativo',
    subject: 'Atos Administrativos',
    statement: 'A respeito dos atos administrativos, assinale a alternativa correta.',
    alternatives: { A: 'Opção A', B: 'Opção B', C: 'Opção C', D: 'Opção D', E: 'Opção E' },
    correct_answer: 'A',
    board: 'CESPE',
    year: 2024,
  },
  {
    materia: 'Direito Constitucional',
    subject: 'Direitos Fundamentais',
    statement: 'Os direitos fundamentais são absolutos.',
    correct_answer: 'ERRADO',
    board: 'CEBRASP',
    year: 2024,
  },
]

const ALTERNATIVAS = ['A', 'B', 'C', 'D', 'E']
const RESPOSTAS_VALIDAS = new Set(['A', 'B', 'C', 'D', 'E', 'CERTO', 'ERRADO', 'CERTA', 'ERRADA'])
const GABARITO_MAP = { CERTO: 'C', ERRADO: 'E', CERTA: 'C', ERRADA: 'E' }

function normalizarGabarito(v) {
  const upper = String(v || '').trim().toUpperCase()
  return GABARITO_MAP[upper] || upper
}

function isCertoErrado(item) {
  const g = normalizarGabarito(item.correct_answer)
  return !item.alternatives && (g === 'C' || g === 'E')
}

function parseCsv(text) {
  const lines = text.trim().split('\n')
  if (lines.length < 2) throw new Error('CSV vazio ou sem linhas de dados')
  const headers = lines[0].split(',').map((h) => h.trim().toLowerCase())
  return lines.slice(1).map((line) => {
    const cols = line.split(',')
    const obj = {}
    headers.forEach((h, idx) => { obj[h] = cols[idx]?.trim() || '' })
    if ('alt_a' in obj) {
      obj.alternatives = { A: obj.alt_a, B: obj.alt_b, C: obj.alt_c, D: obj.alt_d, E: obj.alt_e }
      delete obj.alt_a; delete obj.alt_b; delete obj.alt_c; delete obj.alt_d; delete obj.alt_e
    }
    if (obj.year) obj.year = Number(obj.year) || undefined
    return obj
  })
}

function validarItem(item) {
  const erros = []
  if (!item.materia) erros.push('"materia" ausente')
  if (!item.subject) erros.push('"subject" ausente')
  if (!item.statement) erros.push('"statement" ausente')
  if (!item.correct_answer) {
    erros.push('"correct_answer" ausente')
  } else if (!RESPOSTAS_VALIDAS.has(String(item.correct_answer).trim().toUpperCase())) {
    erros.push(`gabarito inválido: "${item.correct_answer}"`)
  }
  // Certo/Errado não precisa de alternatives
  if (!isCertoErrado(item)) {
    if (!item.alternatives) {
      erros.push('"alternatives" ausente (use "CERTO"/"ERRADO" para C/E)')
    } else {
      ALTERNATIVAS.forEach((k) => { if (!item.alternatives[k]) erros.push(`alt. ${k} ausente`) })
    }
  }
  return erros
}

export default function AdminImportar() {
  const [rawText, setRawText]       = useState('')
  const [parseError, setParseError] = useState('')
  const [preview, setPreview]       = useState(null)
  const [importando, setImportando] = useState(false)
  const [resultado, setResultado]   = useState(null)
  const [dragging, setDragging]     = useState(false)
  const fileRef     = useRef()
  const resultadoRef = useRef()

  useEffect(() => {
    if (resultado) resultadoRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }, [resultado])

  function processar(text, ext = 'json') {
    setParseError('')
    setPreview(null)
    setResultado(null)
    try {
      let items
      if (ext === 'csv') {
        items = parseCsv(text)
      } else {
        const parsed = JSON.parse(text)
        if (!Array.isArray(parsed)) throw new Error('O JSON deve ser um array [ ... ]')
        items = parsed
      }
      if (items.length === 0) throw new Error('Nenhum item encontrado')
      setPreview(items)
    } catch (e) {
      setParseError(e.message)
    }
  }

  function handleValidar() {
    const ext = rawText.trim().startsWith('[') || rawText.trim().startsWith('{') ? 'json' : 'csv'
    processar(rawText, ext)
  }

  function handleFile(file) {
    const ext = file.name.endsWith('.csv') ? 'csv' : 'json'
    const reader = new FileReader()
    reader.onload = (e) => {
      const text = e.target.result
      setRawText(text)
      processar(text, ext)
    }
    reader.readAsText(file)
  }

  function handleDrop(e) {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }

  function handleLimpar() {
    setRawText('')
    setPreview(null)
    setParseError('')
    setResultado(null)
  }

  async function handleImportar() {
    if (!preview) return
    setImportando(true)
    setResultado(null)
    try {
      const questoesNormalizadas = preview.map((item) => {
        const gabarito = normalizarGabarito(item.correct_answer)
        const base = { ...item, correct_answer: gabarito }
        if (item.alternatives) {
          base.alternatives = {
            A: item.alternatives.A || '',
            B: item.alternatives.B || '',
            C: item.alternatives.C || '',
            D: item.alternatives.D || '',
            E: item.alternatives.E || '',
          }
        }
        return base
      })
      const res = await importarQuestoes({ questoes: questoesNormalizadas })
      setResultado(res)
    } catch (e) {
      const detail = e.response?.data?.detail
      const msg = Array.isArray(detail)
        ? detail.map((d) => d.msg || JSON.stringify(d)).join('; ')
        : detail || 'Erro ao importar'
      setResultado({ importadas: 0, erros: [msg], avisos_ia: [] })
    } finally {
      setImportando(false)
    }
  }

  const totalErros   = preview ? preview.reduce((acc, item) => acc + validarItem(item).length, 0) : 0
  const totalValidas = preview ? preview.filter((item) => validarItem(item).length === 0).length : 0
  const podeImportar = preview && totalValidas > 0 && !importando

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-xl font-bold text-brand-text">Importar Questões em Lote</h1>
        <p className="text-sm text-brand-muted mt-1">JSON ou CSV — subtópicos classificados por IA após importação.</p>
      </div>

      {/* Upload */}
      <div className="bg-brand-card border border-brand-border rounded-xl p-4 space-y-3">
        <h2 className="text-sm font-semibold text-brand-text">Arquivo ou colar conteúdo</h2>

        {/* Drag-and-drop */}
        <div
          onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
          onClick={() => fileRef.current.click()}
          className={`border-2 border-dashed rounded-xl p-6 flex flex-col items-center justify-center gap-2 cursor-pointer transition-colors select-none ${
            dragging ? 'border-indigo-500 bg-indigo-500/5' : 'border-brand-border hover:border-brand-muted'
          }`}
        >
          <svg className="w-8 h-8 text-brand-muted" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
          </svg>
          <p className="text-sm text-brand-muted">
            Arraste um arquivo <span className="text-brand-text font-medium">.json</span> ou{' '}
            <span className="text-brand-text font-medium">.csv</span> aqui
          </p>
          <p className="text-xs text-brand-muted">ou clique para selecionar</p>
          <input
            ref={fileRef}
            type="file"
            accept=".json,.csv"
            className="hidden"
            onChange={(e) => e.target.files[0] && handleFile(e.target.files[0])}
          />
        </div>

        <p className="text-xs text-brand-muted text-center">— ou cole o conteúdo abaixo —</p>

        <textarea
          className="w-full h-40 text-xs font-mono bg-brand-surface border border-brand-border rounded-lg p-3 text-brand-text resize-y focus:outline-none focus:border-indigo-500"
          placeholder='[ { "subject": "...", "statement": "...", "alternatives": { "A": "...", ... }, "correct_answer": "A" } ]'
          value={rawText}
          onChange={(e) => { setRawText(e.target.value); setParseError(''); setPreview(null) }}
        />

        {parseError && <p className="text-xs text-red-400">{parseError}</p>}

        <div className="flex gap-2">
          <button
            onClick={handleValidar}
            disabled={!rawText.trim()}
            className="px-4 py-2 text-sm rounded-lg bg-brand-surface border border-brand-border text-brand-text hover:border-indigo-500 disabled:opacity-40 transition-all"
          >
            Validar e Pré-visualizar
          </button>
          <button
            onClick={handleLimpar}
            className="px-4 py-2 text-sm rounded-lg border border-brand-border text-brand-muted hover:text-brand-text transition-colors"
          >
            Limpar
          </button>
        </div>
      </div>

      {/* Formato esperado */}
      <details className="bg-brand-card border border-brand-border rounded-xl overflow-hidden">
        <summary className="px-4 py-3 text-sm font-semibold text-brand-text cursor-pointer hover:bg-brand-surface transition-colors">
          Ver formato esperado
        </summary>
        <div className="px-4 pb-4 space-y-3">
          <div>
            <p className="text-xs font-medium text-brand-muted mb-1">JSON:</p>
            <pre className="text-xs text-brand-muted bg-brand-surface rounded-lg p-3 overflow-x-auto">
              {JSON.stringify(EXEMPLO_JSON, null, 2)}
            </pre>
            <p className="text-xs text-brand-muted mt-2">
              Obrigatórios: <code className="text-indigo-400">materia, subject, statement, correct_answer</code>
              <br />
              Opcional: <code className="text-indigo-400">alternatives (A–E)</code> — omitir em questões Certo/Errado
              <br />
              Opcionais: <code className="text-indigo-400">board, year</code>
              <br />
              Gabarito aceito: <code className="text-indigo-400">A B C D E CERTO ERRADO</code>
            </p>
          </div>
          <div>
            <p className="text-xs font-medium text-brand-muted mb-1">CSV — colunas:</p>
            <code className="text-xs text-indigo-400">subject, statement, correct_answer, board, year, alt_a, alt_b, alt_c, alt_d, alt_e</code>
          </div>
        </div>
      </details>

      {/* Preview */}
      {preview && (
        <section className="bg-brand-card border border-brand-border rounded-xl p-4 space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-semibold text-brand-text">
                Preview — {preview.length} questão{preview.length !== 1 ? 'ões' : ''}
              </h2>
              {totalErros > 0 && (
                <p className="text-xs text-red-400 mt-0.5">
                  {totalErros} erro{totalErros !== 1 ? 's' : ''} de validação —{' '}
                  {totalValidas > 0
                    ? `${totalValidas} questão${totalValidas !== 1 ? 'ões' : ''} válida${totalValidas !== 1 ? 's' : ''} serão importadas`
                    : 'nenhuma questão válida para importar'}
                </p>
              )}
            </div>
            <button
              onClick={handleImportar}
              disabled={!podeImportar}
              className="flex items-center gap-2 px-4 py-2 text-sm rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white disabled:opacity-50 transition-all"
            >
              {importando && (
                <span className="w-4 h-4 rounded-full border-2 border-white/30 border-t-white animate-spin" />
              )}
              {importando ? 'Importando…' : 'Importar'}
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="text-brand-muted border-b border-brand-border">
                  <th className="text-left py-1 pr-3 w-8">#</th>
                  <th className="text-left py-1 pr-3">Matéria</th>
                  <th className="text-left py-1 pr-3">Assunto</th>
                  <th className="text-left py-1 pr-3">Enunciado</th>
                  <th className="text-left py-1 pr-3 w-16">Gabarito</th>
                  <th className="text-left py-1 pr-3 w-24">Banca/Ano</th>
                  <th className="text-left py-1 w-20">Status</th>
                </tr>
              </thead>
              <tbody>
                {preview.map((item, i) => {
                  const erros = validarItem(item)
                  return (
                    <tr
                      key={i}
                      className={`border-b border-brand-border/30 ${erros.length > 0 ? 'bg-red-500/5' : ''}`}
                    >
                      <td className="py-1.5 pr-3 text-brand-muted">{i + 1}</td>
                      <td className="py-1.5 pr-3 text-brand-muted max-w-[120px] truncate">
                        {item.materia || <span className="text-red-400">—</span>}
                      </td>
                      <td className="py-1.5 pr-3 text-brand-muted max-w-[120px] truncate">
                        {item.subject || <span className="text-red-400">—</span>}
                      </td>
                      <td className="py-1.5 pr-3 text-brand-text max-w-xs truncate">
                        {item.statement || <span className="text-red-400">—</span>}
                      </td>
                      <td className="py-1.5 pr-3 text-brand-muted">
                        {normalizarGabarito(item.correct_answer) || '—'}
                        {isCertoErrado(item) && (
                          <span className="ml-1 text-xs text-indigo-400">C/E</span>
                        )}
                      </td>
                      <td className="py-1.5 pr-3 text-brand-muted whitespace-nowrap">
                        {[item.board, item.year].filter(Boolean).join(' ') || '—'}
                      </td>
                      <td className="py-1.5">
                        {erros.length === 0 ? (
                          <span className="text-green-400 font-medium">OK</span>
                        ) : (
                          <span className="text-red-400 cursor-help" title={erros.join('; ')}>
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
        <section
          ref={resultadoRef}
          className={`border rounded-xl p-4 space-y-3 ${
            resultado.importadas > 0 ? 'bg-green-500/5 border-green-500/30' : 'bg-red-500/5 border-red-500/30'
          }`}
        >
          <p className="text-sm font-semibold text-brand-text">
            {resultado.importadas} questão{resultado.importadas !== 1 ? 'ões' : ''} importada
            {resultado.importadas !== 1 ? 's' : ''} com sucesso
          </p>
          {resultado.erros?.length > 0 && (
            <div>
              <p className="text-xs font-medium text-red-400 mb-1">Erros:</p>
              <ul className="text-xs text-red-400 space-y-0.5 list-disc list-inside">
                {resultado.erros.map((e, i) => <li key={i}>{e}</li>)}
              </ul>
            </div>
          )}
          {resultado.avisos_ia?.length > 0 && (
            <div>
              <p className="text-xs font-medium text-yellow-400 mb-1">Avisos IA (classificação):</p>
              <ul className="text-xs text-yellow-400/80 space-y-0.5 list-disc list-inside">
                {resultado.avisos_ia.map((a, i) => <li key={i}>{a}</li>)}
              </ul>
            </div>
          )}
        </section>
      )}
    </div>
  )
}
