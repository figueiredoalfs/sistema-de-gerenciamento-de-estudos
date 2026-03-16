import { useEffect, useState } from 'react'
import { useNavigate, useParams, useLocation } from 'react-router-dom'
import { getTodayTasks, updateTaskStatus } from '../api/tasks'
import QuestionFlow from '../components/task/QuestionFlow'
import VideoList from '../components/task/VideoList'
import PdfPanel from '../components/task/PdfPanel'

const TIPO_CONFIG = {
  teoria:       { label: 'Teoria',      color: 'bg-blue-500/20 text-blue-400' },
  revisao:      { label: 'Revisão',     color: 'bg-purple-500/20 text-purple-400' },
  questionario: { label: 'Questões',    color: 'bg-amber-500/20 text-amber-400' },
  reforco:      { label: 'Reforço',     color: 'bg-red-500/20 text-red-400' },
  diagnostico:  { label: 'Diagnóstico', color: 'bg-indigo-500/20 text-indigo-400' },
  simulado:     { label: 'Simulado',    color: 'bg-pink-500/20 text-pink-400' },
}

// Tipos que exibem aba de conteúdo (vídeos + PDF + questões)
const TIPOS_CONTEUDO = ['teoria', 'revisao']

export default function TaskView() {
  const { taskId } = useParams()
  const { state } = useLocation()
  const navigate = useNavigate()

  const [task, setTask] = useState(state?.task ?? null)
  const [tab, setTab] = useState('videos')
  const [concluindo, setConcluindo] = useState(false)

  useEffect(() => {
    if (!task) {
      getTodayTasks().then(tasks => {
        const found = tasks.find(t => t.id === taskId)
        if (found) setTask(found)
      })
    }
  }, [taskId, task])

  async function handleConcluir() {
    setConcluindo(true)
    try {
      await updateTaskStatus(taskId, 'completed')
      navigate('/')
    } finally {
      setConcluindo(false)
    }
  }

  if (!task) return (
    <div className="flex items-center justify-center py-20">
      <div className="w-8 h-8 rounded-full border-2 border-brand-border border-t-indigo-500 animate-spin" />
    </div>
  )

  const cfg = TIPO_CONFIG[task.tipo] ?? { label: task.tipo, color: 'bg-slate-500/20 text-slate-400' }
  const temConteudo = TIPOS_CONTEUDO.includes(task.tipo)

  return (
    <div className="max-w-2xl mx-auto px-4 py-8 space-y-5">
      {/* Voltar */}
      <button
        onClick={() => navigate('/')}
        className="text-brand-muted hover:text-brand-text transition-colors text-sm flex items-center gap-1"
      >
        ← Voltar
      </button>

      {/* Header da tarefa */}
      <div className="bg-brand-card border border-brand-border rounded-2xl p-5">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            <h1 className="text-lg font-bold text-brand-text leading-tight">
              {task.subject_nome ?? task.subject_id}
            </h1>
            {task.topic_nome && (
              <p className="text-brand-muted text-sm mt-0.5">{task.topic_nome}</p>
            )}
            {task.subtopic_nome && (
              <p className="text-brand-muted text-xs mt-0.5">{task.subtopic_nome}</p>
            )}
          </div>
          <span className={`text-xs font-medium px-2.5 py-1 rounded-full flex-shrink-0 ${cfg.color}`}>
            {cfg.label}
          </span>
        </div>
      </div>

      {/* Conteúdo por tipo */}
      {temConteudo ? (
        <div className="space-y-4">
          {/* Tabs */}
          <div className="flex gap-2">
            {[['videos', 'Vídeos'], ['pdf', 'Material PDF'], ['questoes', 'Questões']].map(([key, label]) => (
              <button
                key={key}
                onClick={() => setTab(key)}
                className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                  tab === key
                    ? 'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30'
                    : 'text-brand-muted hover:text-brand-text border border-transparent'
                }`}
              >
                {label}
              </button>
            ))}
          </div>

          {/* Conteúdo da aba */}
          {tab === 'videos' && (
            task.task_code
              ? <VideoList taskCode={task.task_code} />
              : <EmptyConteudo mensagem="Vídeos disponíveis após geração do cronograma." />
          )}
          {tab === 'pdf' && (
            task.task_code
              ? <PdfPanel taskCode={task.task_code} />
              : <EmptyConteudo mensagem="Material disponível após geração do cronograma." />
          )}
          {tab === 'questoes' && (
            <QuestionFlow taskId={taskId} onConcluir={handleConcluir} />
          )}

          {/* Botão concluir (só nas abas sem QuestionFlow) */}
          {tab !== 'questoes' && (
            <button
              onClick={handleConcluir}
              disabled={concluindo}
              className="w-full py-3 bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 font-semibold rounded-xl text-sm hover:bg-emerald-500/30 transition-all duration-300 disabled:opacity-50"
            >
              {concluindo ? 'Concluindo...' : '✓ Concluir tarefa'}
            </button>
          )}
        </div>
      ) : (
        // Tipos de questões: vai direto para o fluxo
        <QuestionFlow taskId={taskId} onConcluir={handleConcluir} />
      )}
    </div>
  )
}

function EmptyConteudo({ mensagem }) {
  return (
    <div className="bg-brand-card border border-brand-border rounded-xl p-8 text-center">
      <p className="text-brand-muted text-sm">{mensagem}</p>
    </div>
  )
}
