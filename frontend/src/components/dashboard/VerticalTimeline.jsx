import TaskCard from './TaskCard'

export default function VerticalTimeline({ tasks, heroTask, onStart, onComplete }) {
  const timelineTasks = tasks.filter((t) => t.id !== heroTask?.id)

  if (timelineTasks.length === 0 && !heroTask) return null

  return (
    <div>
      <h3 className="text-brand-muted text-xs uppercase tracking-wider mb-4">Tarefas do dia</h3>
      {timelineTasks.length === 0 ? (
        <p className="text-brand-muted text-sm text-center py-6">Todas as tarefas concluídas! 🎉</p>
      ) : (
        <div>
          {timelineTasks.map((task) => (
            <TaskCard
              key={task.id}
              task={task}
              onStart={onStart}
              onComplete={onComplete}
              isHero={false}
            />
          ))}
          {/* Fim da timeline */}
          <div className="flex gap-4">
            <div className="flex flex-col items-center">
              <span className="text-brand-border text-lg">◇</span>
            </div>
            <p className="text-brand-muted text-xs pt-0.5">Fim do dia</p>
          </div>
        </div>
      )}
    </div>
  )
}
