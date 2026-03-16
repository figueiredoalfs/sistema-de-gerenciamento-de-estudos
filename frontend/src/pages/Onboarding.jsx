import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { submitOnboarding } from '../api/onboarding'
import StepIndicator from '../components/onboarding/StepIndicator'
import StepArea from '../components/onboarding/steps/StepArea'
import StepPhase from '../components/onboarding/steps/StepPhase'
import StepExperience from '../components/onboarding/steps/StepExperience'
import StepFeatures from '../components/onboarding/steps/StepFeatures'

const TOTAL_STEPS = 4

export default function Onboarding() {
  const { refreshUser } = useAuth()
  const navigate = useNavigate()
  const [step, setStep] = useState(1)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const [form, setForm] = useState({
    area: '',
    fase_estudo: '',
    experiencia: '',
    tempoEstudo: '',
    funcionalidades: [],
  })

  function canAdvance() {
    if (step === 1) return !!form.area
    if (step === 2) return !!form.fase_estudo
    if (step === 3) return !!form.experiencia && (form.experiencia === 'iniciante' || !!form.tempoEstudo)
    if (step === 4) return form.funcionalidades.length > 0
    return false
  }

  async function handleNext() {
    if (step < TOTAL_STEPS) {
      setStep((s) => s + 1)
      return
    }
    // Submete no último step
    setLoading(true)
    setError('')
    try {
      await submitOnboarding({
        area: form.area,
        fase_estudo: form.fase_estudo,
        experiencia: form.experiencia,
        tempo_estudo: form.tempoEstudo || null,
        funcionalidades: form.funcionalidades,
      })
      await refreshUser()
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao salvar suas preferências')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-brand-bg flex flex-col items-center justify-center px-4 py-12">
      <div className="w-full max-w-[800px]">
        {/* Logo */}
        <div className="text-center mb-10">
          <h1 className="text-3xl font-bold gradient-text">Skolai</h1>
          <p className="text-brand-muted text-sm mt-1">Vamos configurar sua experiência</p>
        </div>

        <StepIndicator currentStep={step} />

        <div className="bg-brand-card border border-brand-border rounded-2xl p-8">
          {step === 1 && (
            <StepArea value={form.area} onChange={(v) => setForm((f) => ({ ...f, area: v }))} />
          )}
          {step === 2 && (
            <StepPhase value={form.fase_estudo} onChange={(v) => setForm((f) => ({ ...f, fase_estudo: v }))} />
          )}
          {step === 3 && (
            <StepExperience
              experiencia={form.experiencia}
              tempoEstudo={form.tempoEstudo}
              onChange={(field, value) => setForm((f) => ({ ...f, [field]: value }))}
            />
          )}
          {step === 4 && (
            <StepFeatures
              selected={form.funcionalidades}
              onChange={(v) => setForm((f) => ({ ...f, funcionalidades: v }))}
            />
          )}

          {error && (
            <p className="mt-4 text-red-400 text-sm bg-red-400/10 border border-red-400/20 rounded-lg px-3 py-2">
              {error}
            </p>
          )}

          <div className="flex items-center justify-between mt-8">
            <button
              type="button"
              onClick={() => setStep((s) => s - 1)}
              disabled={step === 1}
              className="px-5 py-2.5 rounded-lg border border-brand-border text-brand-muted text-sm hover:text-brand-text hover:border-brand-text transition-all duration-300 disabled:opacity-0 disabled:pointer-events-none"
            >
              Voltar
            </button>
            <button
              type="button"
              onClick={handleNext}
              disabled={!canAdvance() || loading}
              className="px-7 py-2.5 rounded-lg bg-brand-gradient text-white text-sm font-semibold transition-all duration-300 hover:opacity-90 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {loading ? 'Salvando...' : step === TOTAL_STEPS ? 'Começar' : 'Continuar'}
            </button>
          </div>
        </div>

        <p className="text-center text-brand-muted text-xs mt-4">
          Passo {step} de {TOTAL_STEPS}
        </p>
      </div>
    </div>
  )
}
