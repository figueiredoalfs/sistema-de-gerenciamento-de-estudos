import { useEffect, useRef, useState } from 'react'
import { extrairQuestoesPdf, importarQuestoes, parsearTecPdfV2 } from '../api/adminQuestoes'

function ModalEditarQuestao({ item, onSave, onClose }) {
  const [form, setForm] = useState({
    materia:        item.materia        || '',
    subject:        item.subject        || '',
    statement:      item.statement      || '',
    correct_answer: item.correct_answer || '',
    board:          item.board          || '',
    year:           item.year           || '',
    altA: item.alternatives?.A || '',
    altB: item.alternatives?.B || '',
    altC: item.alternatives?.C || '',
    altD: item.alternatives?.D || '',
    altE: item.alternatives?.E || '',
  })

  const isCE = !['A','B','C','D','E'].includes(String(form.correct_answer).toUpperCase())

  function set(field) {
    return (e) => setForm((f) => ({ ...f, [field]: e.target.value }))
  }

  function handleSave() {
    const alts = isCE ? null : { A: form.altA, B: form.altB, C: form.altC, D: form.altD, E: form.altE }
    onSave({
      ...item,
      materia:        form.materia,
      subject:        form.subject,
      statement:      form.statement,
      correct_answer: form.correct_answer,
      board:          form.board || null,
      year:           form.year ? Number(form.year) : null,
      alternatives:   alts,
    })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4" onClick={onClose}>
      <div
        className="bg-brand-card border border-brand-border rounded-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto p-5 space-y-4"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-brand-text">Editar questão</h2>
          <button onClick={onClose} className="text-brand-muted hover:text-brand-text text-lg leading-none">×</button>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1">
            <label className="text-xs text-brand-muted">Matéria</label>
            <input className="w-full text-sm bg-brand-surface border border-brand-border rounded-lg px-3 py-2 text-brand-text focus:outline-none focus:border-indigo-500"
              value={form.materia} onChange={set('materia')} />
          </div>
          <div className="space-y-1">
            <label className="text-xs text-brand-muted">Assunto</label>
            <input className="w-full text-sm bg-brand-surface border border-brand-border rounded-lg px-3 py-2 text-brand-text focus:outline-none focus:border-indigo-500"
              value={form.subject} onChange={set('subject')} />
          </div>
        </div>

        <div className="space-y-1">
          <label className="text-xs text-brand-muted">Enunciado</label>
          <textarea
            className="w-full text-sm bg-brand-surface border border-brand-border rounded-lg px-3 py-2 text-brand-text focus:outline-none focus:border-indigo-500 resize-y min-h-[80px]"
            value={form.statement} onChange={set('statement')}
          />
        </div>

        <div className="grid grid-cols-3 gap-3">
          <div className="space-y-1">
            <label className="text-xs text-brand-muted">Gabarito</label>
            <input className="w-full text-sm bg-brand-surface border border-brand-border rounded-lg px-3 py-2 text-brand-text focus:outline-none focus:border-indigo-500"
              value={form.correct_answer} onChange={set('correct_answer')} placeholder="A B C D E CERTO ERRADO" />
          </div>
          <div className="space-y-1">
            <label className="text-xs text-brand-muted">Banca</label>
            <input className="w-full text-sm bg-brand-surface border border-brand-border rounded-lg px-3 py-2 text-brand-text focus:outline-none focus:border-indigo-500"
              value={form.board} onChange={set('board')} />
          </div>
          <div className="space-y-1">
            <label className="text-xs text-brand-muted">Ano</label>
            <input type="number" className="w-full text-sm bg-brand-surface border border-brand-border rounded-lg px-3 py-2 text-brand-text focus:outline-none focus:border-indigo-500"
              value={form.year} onChange={set('year')} />
          </div>
        </div>

        {!isCE && (
          <div className="space-y-2">
            <label className="text-xs text-brand-muted">Alternativas</label>
            {['A','B','C','D','E'].map((l) => (
              <div key={l} className="flex items-center gap-2">
                <span className="text-xs font-bold text-brand-muted w-4">{l}</span>
                <input
                  className="flex-1 text-sm bg-brand-surface border border-brand-border rounded-lg px-3 py-1.5 text-brand-text focus:outline-none focus:border-indigo-500"
                  value={form[`alt${l}`]} onChange={set(`alt${l}`)}
                />
              </div>
            ))}
          </div>
        )}

        <div className="flex justify-end gap-2 pt-2">
          <button onClick={onClose} className="px-4 py-2 text-sm rounded-lg border border-brand-border text-brand-muted hover:text-brand-text transition-colors">
            Cancelar
          </button>
          <button onClick={handleSave} className="px-4 py-2 text-sm rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white transition-colors">
            Salvar
          </button>
        </div>
      </div>
    </div>
  )
}

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
  const [aba, setAba]               = useState('json') // 'json' | 'tec' | 'pdf'
  const [rawText, setRawText]       = useState('')
  const [parseError, setParseError] = useState('')
  const [preview, setPreview]       = useState(null)
  const [importando, setImportando] = useState(false)
  const [resultado, setResultado]   = useState(null)
  const [dragging, setDragging]     = useState(false)
  const [editando, setEditando]     = useState(null) // { index, item }
  const [classificarSubtopicos, setClassificarSubtopicos] = useState(false)
  const [classificarAreas, setClassificarAreas]           = useState(false)
  // PDF (IA)
  const [pdfFile, setPdfFile]       = useState(null)
  const [extraindo, setExtraindo]   = useState(false)
  const [erroPdf, setErroPdf]       = useState('')
  const [draggingPdf, setDraggingPdf] = useState(false)
  // TEC
  const [tecFile, setTecFile]           = useState(null)
  const [tecDragging, setTecDragging]   = useState(false)
  const [tecExtraindo, setTecExtraindo] = useState(false)
  const [tecErro, setTecErro]           = useState('')
  const [tecQuestoes, setTecQuestoes]   = useState([])   // lista mutável (edições)
  const [tecStats, setTecStats]         = useState(null)  // {total, sem_gabarito}
  const [tecImportando, setTecImportando] = useState(false)
  const [tecResultado, setTecResultado]   = useState(null)
  const [tecEditando, setTecEditando]     = useState(null) // {index, item}
  const [tecClassificarIA, setTecClassificarIA] = useState(false)

  const fileRef     = useRef()
  const pdfRef      = useRef()
  const tecRef      = useRef()
  const resultadoRef = useRef()

  useEffect(() => {
    if (resultado) window.scrollTo({ top: 0, behavior: 'smooth' })
  }, [resultado])

  function trocarAba(novaAba) {
    setAba(novaAba)
    setPreview(null); setResultado(null); setParseError('')
    setErroPdf(''); setPdfFile(null); setRawText('')
    setTecFile(null); setTecErro(''); setTecQuestoes([]); setTecStats(null)
    setTecResultado(null); setTecEditando(null)
  }

  async function handleExtrairTec() {
    if (!tecFile) return
    setTecExtraindo(true); setTecErro(''); setTecQuestoes([]); setTecStats(null); setTecResultado(null)
    try {
      const res = await parsearTecPdfV2(tecFile)
      setTecQuestoes(res.questoes)
      setTecStats({ total: res.total, sem_gabarito: res.sem_gabarito })
    } catch (e) {
      const detail = e.response?.data?.detail
      const msg = Array.isArray(detail) ? detail.map(d => d.msg || JSON.stringify(d)).join('; ') : detail || e.message || 'Erro ao processar PDF'
      setTecErro(msg)
    } finally {
      setTecExtraindo(false)
    }
  }

  async function handleImportarTec() {
    if (!tecQuestoes.length) return
    setTecImportando(true); setTecResultado(null)
    try {
      const payload = tecQuestoes.map(q => ({
        materia: q.materia,
        subject: q.subject,
        board: q.board || null,
        year: q.year || null,
        statement: q.statement,
        alternatives: q.alternatives
          ? { A: q.alternatives.A || '', B: q.alternatives.B || '', C: q.alternatives.C || '',
              D: q.alternatives.D || '', E: q.alternatives.E || '' }
          : null,
        correct_answer: q.correct_answer ?? 'A',
      }))
      const res = await importarQuestoes({ questoes: payload, classificar_subtopicos: tecClassificarIA, classificar_areas: false })
      setTecResultado(res)
    } catch (e) {
      const detail = e.response?.data?.detail
      const msg = Array.isArray(detail) ? detail.map(d => d.msg || JSON.stringify(d)).join('; ') : detail || e.message || 'Erro ao importar'
      setTecResultado({ importadas: 0, erros: [msg], avisos_ia: [] })
    } finally {
      setTecImportando(false)
    }
  }

  function tecToModalItem(q) {
    return {
      materia: q.materia,
      subject: q.subject,
      statement: q.statement,
      correct_answer: q.correct_answer || '',
      board: q.board || '',
      year: q.year || '',
      alternatives: q.alternatives || null,
    }
  }

  function tecFromModalSave(original, saved) {
    const g = normalizarGabarito(saved.correct_answer)
    return {
      ...original,
      materia: saved.materia,
      subject: saved.subject,
      statement: saved.statement,
      correct_answer: g || null,
      board: saved.board || null,
      year: saved.year ? Number(saved.year) : null,
      alternatives: saved.alternatives || null,
      tipo: saved.alternatives ? 'multipla_escolha' : 'certo_errado',
    }
  }

  async function handleExtrairPdf() {
    if (!pdfFile) return
    setExtraindo(true)
    setErroPdf('')
    setPreview(null)
    setResultado(null)
    try {
      const questoes = await extrairQuestoesPdf(pdfFile)
      if (!Array.isArray(questoes) || questoes.length === 0) {
        setErroPdf('Nenhuma questão encontrada no PDF. Verifique se o arquivo contém questões de concurso.')
      } else {
        setPreview(questoes)
      }
    } catch (e) {
      const detail = e.response?.data?.detail
      const msg = Array.isArray(detail)
        ? detail.map(d => d.msg || JSON.stringify(d)).join('; ')
        : detail || e.message || 'Erro ao processar PDF. Tente novamente.'
      setErroPdf(msg)
    } finally {
      setExtraindo(false)
    }
  }

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
      const res = await importarQuestoes({ questoes: questoesNormalizadas, classificar_subtopicos: classificarSubtopicos, classificar_areas: classificarAreas })
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
        <p className="text-sm text-brand-muted mt-1">JSON, CSV ou PDF — subtópicos classificados por IA após importação.</p>
      </div>

      {/* Abas */}
      <div className="flex gap-1 border-b border-brand-border">
        {[
          { id: 'json', label: 'JSON / CSV' },
          { id: 'tec',  label: 'TEC Concursos' },
          { id: 'pdf',  label: 'PDF via IA' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => trocarAba(tab.id)}
            className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors ${
              aba === tab.id
                ? 'border-indigo-500 text-indigo-400'
                : 'border-transparent text-brand-muted hover:text-brand-text'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Aba PDF */}
      {aba === 'pdf' && (
        <div className="bg-brand-card border border-brand-border rounded-xl p-4 space-y-3">
          <h2 className="text-sm font-semibold text-brand-text">Upload de PDF</h2>
          <p className="text-xs text-brand-muted">
            O Gemini Flash analisa o PDF e extrai as questões automaticamente. Revise o preview antes de confirmar a importação.
          </p>

          {/* Drag-and-drop PDF */}
          <div
            onDragOver={(e) => { e.preventDefault(); setDraggingPdf(true) }}
            onDragLeave={() => setDraggingPdf(false)}
            onDrop={(e) => {
              e.preventDefault()
              setDraggingPdf(false)
              const f = e.dataTransfer.files[0]
              if (f && f.name.toLowerCase().endsWith('.pdf')) {
                setPdfFile(f)
                setErroPdf('')
                setPreview(null)
              } else {
                setErroPdf('Selecione um arquivo .pdf')
              }
            }}
            onClick={() => pdfRef.current.click()}
            className={`border-2 border-dashed rounded-xl p-6 flex flex-col items-center justify-center gap-2 cursor-pointer transition-colors select-none ${
              draggingPdf ? 'border-indigo-500 bg-indigo-500/5' : 'border-brand-border hover:border-brand-muted'
            }`}
          >
            <svg className="w-8 h-8 text-brand-muted" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            {pdfFile ? (
              <p className="text-sm text-indigo-400 font-medium">{pdfFile.name}</p>
            ) : (
              <>
                <p className="text-sm text-brand-muted">
                  Arraste um arquivo <span className="text-brand-text font-medium">.pdf</span> aqui
                </p>
                <p className="text-xs text-brand-muted">ou clique para selecionar</p>
              </>
            )}
            <input
              ref={pdfRef}
              type="file"
              accept=".pdf"
              className="hidden"
              onChange={(e) => {
                const f = e.target.files[0]
                if (f) { setPdfFile(f); setErroPdf(''); setPreview(null) }
              }}
            />
          </div>

          {erroPdf && <p className="text-xs text-red-400">{erroPdf}</p>}

          <div className="flex flex-wrap items-center gap-4">
            <div className="flex gap-2">
              <button
                onClick={handleExtrairPdf}
                disabled={!pdfFile || extraindo}
                className="flex items-center gap-2 px-4 py-2 text-sm rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white disabled:opacity-50 transition-all"
              >
                {extraindo && (
                  <span className="w-4 h-4 rounded-full border-2 border-white/30 border-t-white animate-spin" />
                )}
                {extraindo ? 'Extraindo via IA…' : 'Extrair questões via IA'}
              </button>
              {pdfFile && !extraindo && (
                <button
                  onClick={() => { setPdfFile(null); setPreview(null); setErroPdf('') }}
                  className="px-4 py-2 text-sm rounded-lg border border-brand-border text-brand-muted hover:text-brand-text transition-colors"
                >
                  Limpar
                </button>
              )}
            </div>
            <div className="flex flex-col gap-1 ml-2">
              <label className="flex items-center gap-2 text-xs text-brand-muted cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={classificarSubtopicos}
                  onChange={e => setClassificarSubtopicos(e.target.checked)}
                  className="rounded border-brand-border text-indigo-500 focus:ring-indigo-500"
                />
                Classificar subtópicos via IA ao importar
              </label>
              <label className="flex items-center gap-2 text-xs text-brand-muted cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={classificarAreas}
                  onChange={e => setClassificarAreas(e.target.checked)}
                  className="rounded border-brand-border text-indigo-500 focus:ring-indigo-500"
                />
                Classificar áreas via IA ao importar
              </label>
            </div>
          </div>
        </div>
      )}

      {/* Aba TEC Concursos */}
      {aba === 'tec' && (
        <div className="space-y-4">
          <div className="bg-brand-card border border-brand-border rounded-xl p-4 space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-sm font-semibold text-brand-text">Upload de PDF do TEC Concursos</h2>
                <p className="text-xs text-brand-muted mt-0.5">Parser direto — sem IA. Use o botão <strong className="text-brand-text">"Imprimir"</strong> do TEC Concursos e salve como PDF pelo navegador. Não use Ctrl+P ou "Print to PDF" do Windows.</p>
              </div>
            </div>

            {/* Drop zone TEC */}
            <div
              onDragOver={(e) => { e.preventDefault(); setTecDragging(true) }}
              onDragLeave={() => setTecDragging(false)}
              onDrop={(e) => {
                e.preventDefault(); setTecDragging(false)
                const f = e.dataTransfer.files[0]
                if (f && f.name.toLowerCase().endsWith('.pdf')) { setTecFile(f); setTecErro(''); setTecQuestoes([]); setTecStats(null) }
                else setTecErro('Selecione um arquivo .pdf')
              }}
              onClick={() => tecRef.current.click()}
              className={`border-2 border-dashed rounded-xl p-5 flex flex-col items-center justify-center gap-2 cursor-pointer transition-colors select-none ${
                tecDragging ? 'border-indigo-500 bg-indigo-500/5' : 'border-brand-border hover:border-brand-muted'
              }`}
            >
              <svg className="w-8 h-8 text-brand-muted" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              {tecFile
                ? <p className="text-sm text-indigo-400 font-medium">{tecFile.name}</p>
                : <><p className="text-sm text-brand-muted">Arraste um <span className="text-brand-text font-medium">.pdf</span> do TEC Concursos</p><p className="text-xs text-brand-muted">ou clique para selecionar</p></>}
              <input ref={tecRef} type="file" accept=".pdf" className="hidden"
                onChange={(e) => { const f = e.target.files[0]; if (f) { setTecFile(f); setTecErro(''); setTecQuestoes([]); setTecStats(null) } }} />
            </div>

            {tecErro && <p className="text-xs text-red-400">{tecErro}</p>}

            <div className="flex gap-2">
              <button onClick={handleExtrairTec} disabled={!tecFile || tecExtraindo}
                className="flex items-center gap-2 px-4 py-2 text-sm rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white disabled:opacity-50 transition-all">
                {tecExtraindo && <span className="w-4 h-4 rounded-full border-2 border-white/30 border-t-white animate-spin" />}
                {tecExtraindo ? 'Extraindo questões…' : 'Extrair questões'}
              </button>
              {tecFile && !tecExtraindo && (
                <button onClick={() => { setTecFile(null); setTecQuestoes([]); setTecStats(null); setTecErro('') }}
                  className="px-4 py-2 text-sm rounded-lg border border-brand-border text-brand-muted hover:text-brand-text transition-colors">
                  Limpar
                </button>
              )}
            </div>
          </div>

          {/* Stats bar */}
          {tecStats && (
            <div className="flex gap-4 text-sm">
              <span className="text-brand-muted">{tecStats.total} questão{tecStats.total !== 1 ? 'ões' : ''} extraída{tecStats.total !== 1 ? 's' : ''}</span>
              {tecStats.sem_gabarito > 0 && (
                <span className="text-yellow-400">{tecStats.sem_gabarito} sem gabarito — serão importadas com gabarito "A" (edite antes de confirmar)</span>
              )}
            </div>
          )}

          {/* Resultado TEC */}
          {tecResultado && (
            <div className={`border rounded-xl p-4 space-y-2 ${tecResultado.importadas > 0 ? 'bg-green-500/5 border-green-500/30' : 'bg-red-500/5 border-red-500/30'}`}>
              <p className="text-sm font-semibold text-brand-text">
                {tecResultado.importadas} questão{tecResultado.importadas !== 1 ? 'ões' : ''} importada{tecResultado.importadas !== 1 ? 's' : ''} com sucesso
              </p>
              {tecResultado.erros?.length > 0 && (
                <ul className="text-xs text-red-400 space-y-0.5 list-disc list-inside">
                  {tecResultado.erros.map((e, i) => <li key={i}>{e}</li>)}
                </ul>
              )}
            </div>
          )}

          {/* Preview TEC */}
          {tecQuestoes.length > 0 && (
            <div className="bg-brand-card border border-brand-border rounded-xl overflow-hidden">
              <div className="flex items-center justify-between px-4 py-3 border-b border-brand-border">
                <h2 className="text-sm font-semibold text-brand-text">{tecQuestoes.length} questão{tecQuestoes.length !== 1 ? 'ões' : ''} encontrada{tecQuestoes.length !== 1 ? 's' : ''}</h2>
                <div className="flex items-center gap-3">
                  <label className="flex items-center gap-1.5 text-xs text-brand-muted cursor-pointer select-none">
                    <input type="checkbox" checked={tecClassificarIA}
                      onChange={e => setTecClassificarIA(e.target.checked)}
                      className="accent-indigo-500" />
                    Classificar tópico/subtópico com IA
                  </label>
                  <button onClick={handleImportarTec} disabled={tecImportando}
                    className="flex items-center gap-2 px-4 py-2 text-sm rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white disabled:opacity-50 transition-all">
                    {tecImportando && <span className="w-4 h-4 rounded-full border-2 border-white/30 border-t-white animate-spin" />}
                    {tecImportando ? 'Importando…' : `Importar ${tecQuestoes.length} questões`}
                  </button>
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead className="border-b border-brand-border text-brand-muted">
                    <tr>
                      <th className="text-left px-3 py-2 w-8">#</th>
                      <th className="text-left px-3 py-2">Matéria</th>
                      <th className="text-left px-3 py-2">Subtópico (TEC)</th>
                      <th className="text-left px-3 py-2 w-28">Banca</th>
                      <th className="text-left px-3 py-2 w-16">Ano</th>
                      <th className="text-left px-3 py-2 w-20">Tipo</th>
                      <th className="text-left px-3 py-2 w-16">Gabarito</th>
                      <th className="w-8 px-3 py-2" />
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-brand-border/30">
                    {tecQuestoes.map((q, i) => {
                      const semGabarito = !q.correct_answer
                      return (
                        <tr key={i} className={semGabarito ? 'bg-yellow-500/5' : ''}>
                          <td className="px-3 py-2 text-brand-muted text-xs font-mono">{i + 1}</td>
                          <td className="px-3 py-2 text-brand-muted max-w-[120px] truncate">{q.materia}</td>
                          <td className="px-3 py-2 text-brand-muted max-w-[150px] truncate" title={q.subject}>{q.subject || '—'}</td>
                          <td className="px-3 py-2 text-brand-muted truncate">{q.board || '—'}</td>
                          <td className="px-3 py-2 text-brand-muted">{q.year || '—'}</td>
                          <td className="px-3 py-2 text-brand-muted whitespace-nowrap">
                            {q.tipo === 'certo_errado' ? <span className="text-indigo-400">C/E</span> : 'M.Esc.'}
                          </td>
                          <td className="px-3 py-2">
                            {q.correct_answer
                              ? <span className="px-1.5 py-0.5 rounded bg-indigo-500/10 text-indigo-400 font-bold">{q.correct_answer}</span>
                              : <span className="text-yellow-500/70 italic">— edite</span>}
                          </td>
                          <td className="px-3 py-2">
                            <button
                              onClick={() => setTecEditando({ index: i, item: tecToModalItem(q) })}
                              className="text-brand-muted hover:text-indigo-400 transition-colors"
                              title="Editar questão"
                            >
                              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                              </svg>
                            </button>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}

        </div>
      )}

      {/* Aba JSON/CSV */}
      {aba === 'json' && (
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
      )}

      {/* Formato esperado — só na aba JSON */}
      {aba === 'json' && <details className="bg-brand-card border border-brand-border rounded-xl overflow-hidden">
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
      </details>}

      {/* Resultado */}
      {resultado && (
        <section
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
            <div className="flex items-center gap-4">
              <div className="flex flex-col gap-1">
                <label className="flex items-center gap-2 text-xs text-brand-muted cursor-pointer select-none">
                  <input
                    type="checkbox"
                    checked={classificarSubtopicos}
                    onChange={e => setClassificarSubtopicos(e.target.checked)}
                    className="rounded border-brand-border text-indigo-500 focus:ring-indigo-500"
                  />
                  Classificar subtópicos via IA
                </label>
                <label className="flex items-center gap-2 text-xs text-brand-muted cursor-pointer select-none">
                  <input
                    type="checkbox"
                    checked={classificarAreas}
                    onChange={e => setClassificarAreas(e.target.checked)}
                    className="rounded border-brand-border text-indigo-500 focus:ring-indigo-500"
                  />
                  Classificar áreas via IA
                </label>
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
                  <th className="w-8" />
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
                      <td className="py-1.5 pl-1">
                        <button
                          onClick={() => setEditando({ index: i, item })}
                          className="text-brand-muted hover:text-indigo-400 transition-colors"
                          title="Editar questão"
                        >
                          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                          </svg>
                        </button>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {editando && (
        <ModalEditarQuestao
          item={editando.item}
          onSave={(updated) => {
            setPreview((prev) => prev.map((q, i) => i === editando.index ? updated : q))
            setEditando(null)
          }}
          onClose={() => setEditando(null)}
        />
      )}

      {tecEditando && (
        <ModalEditarQuestao
          item={tecEditando.item}
          onSave={(updated) => {
            setTecQuestoes(qs => qs.map((q, i) => i === tecEditando.index ? tecFromModalSave(q, updated) : q))
            setTecEditando(null)
          }}
          onClose={() => setTecEditando(null)}
        />
      )}
    </div>
  )
}
