import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { listarPlanos } from '../api/adminPlanoBase'

const CARDS = [
  {
    to: '/admin/questoes',
    label: 'Questões',
    desc: 'Filtrar, editar e deletar questões do banco',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
          d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
      </svg>
    ),
  },
  {
    to: '/admin/importar',
    label: 'Importar Questões',
    desc: 'Upload JSON em lote com validação e IA',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
          d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
      </svg>
    ),
  },
  {
    to: '/admin/topicos',
    label: 'Tópicos',
    desc: 'Gerenciar matérias, tópicos e subtópicos',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
          d="M4 6h16M4 10h16M4 14h16M4 18h16" />
      </svg>
    ),
  },
  {
    to: '/admin/usuarios',
    label: 'Usuários',
    desc: 'Ativar, desativar e atribuir mentores',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
          d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0" />
      </svg>
    ),
  },
  {
    to: '/admin/planos-base',
    label: 'Planos Base',
    desc: 'Gerar via IA e revisar planos de estudo por área',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
          d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
      </svg>
    ),
  },
]

export default function AdminDashboard() {
  const { user } = useAuth()
  const [pendentesPlano, setPendentesPlano] = useState(0)

  useEffect(() => {
    listarPlanos({ pendente_revisao: true })
      .then((data) => setPendentesPlano(data.length))
      .catch(() => { /* silencia */ })
  }, [])

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-brand-text">Painel Admin</h1>
        <p className="text-brand-muted text-sm mt-1">Olá, {user?.nome}. Gerencie a plataforma Skolai.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {CARDS.map((card) =>
          card.disabled ? (
            <div
              key={card.to}
              className="bg-brand-card border border-brand-border rounded-xl p-5 opacity-50 cursor-not-allowed"
            >
              <div className="flex items-center gap-3 mb-2">
                <span className="text-brand-muted">{card.icon}</span>
                <span className="font-semibold text-brand-text">{card.label}</span>
                <span className="ml-auto text-xs text-brand-muted border border-brand-border rounded px-2 py-0.5">Em breve</span>
              </div>
              <p className="text-brand-muted text-sm">{card.desc}</p>
            </div>
          ) : (
            <Link
              key={card.to}
              to={card.to}
              className="bg-brand-card border border-brand-border rounded-xl p-5 hover:border-indigo-500/40 hover:bg-indigo-500/5 transition-all duration-200 group"
            >
              <div className="flex items-center gap-3 mb-2">
                <span className="text-indigo-400">{card.icon}</span>
                <span className="font-semibold text-brand-text group-hover:text-indigo-300 transition-colors">{card.label}</span>
                {card.to === '/admin/planos-base' && pendentesPlano > 0 && (
                  <span className="ml-auto text-xs px-2 py-0.5 rounded-full bg-yellow-500/15 text-yellow-400 border border-yellow-500/20 font-medium">
                    {pendentesPlano} pendente{pendentesPlano !== 1 ? 's' : ''}
                  </span>
                )}
              </div>
              <p className="text-brand-muted text-sm">{card.desc}</p>
            </Link>
          )
        )}
      </div>
    </div>
  )
}
