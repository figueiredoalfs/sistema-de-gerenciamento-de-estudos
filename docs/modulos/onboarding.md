# Módulo: Onboarding

## Propósito
Coleta as preferências iniciais do aluno (área, fase, experiência, horas/semana, funcionalidades) e cria o `PerfilEstudo`. Ao concluir, dispara automaticamente a criação de Meta 00 (diagnóstico) para iniciantes ou Meta 01 (estudo) para experientes.

## Arquivos principais
- `app/routers/onboarding.py` — endpoint `POST /onboarding`
- `app/models/perfil_estudo.py` — model `PerfilEstudo`
- `app/schemas/` — schemas de onboarding
- `frontend/src/pages/Onboarding.jsx` — wizard multi-step
- `frontend/src/components/onboarding/steps/` — StepArea, StepAvailability, StepExperience, StepFeatures, StepPhase

## Fluxo de dados
```
POST /onboarding (autenticado)
  body: {area, fase_estudo, experiencia, horas_por_dia, dias_por_semana, funcionalidades[]}
  → Aluno.area = body.area
  → PerfilEstudo.upsert(aluno_id)
  → if experiencia == 'iniciante':
      criar Meta 00 (diagnóstico) via metas router
    else:
      criar Meta 01 (estudo semanal)
  → retorna {perfil, meta_criada}
```

## Guard frontend
```jsx
// ProtectedRoute verifica: se user.area == null → redireciona /onboarding
// OnboardingGuard verifica: se user.area != null → redireciona /
```

## Dependências externas
- `Aluno` (tabela `alunos` — atualiza campo `area`)
- `PerfilEstudo` (tabela `perfil_estudos`)
- `Meta` + lógica de `metas.py` (criação pós-onboarding)

## Regras de negócio críticas
- Onboarding é **idempotente** — pode ser refeito (upsert no PerfilEstudo)
- `Aluno.area = None` → usuário fica preso no `/onboarding` pelo guard
- `funcionalidades` é armazenado como JSON text em `PerfilEstudo.funcionalidades_json`
- Não cria tasks diretamente — delega para o módulo de metas

## Pontos de atenção
- Após mudança nos steps do wizard, verificar se os campos do body continuam mapeando para os campos do PerfilEstudo
- `horas_por_dia` e `dias_por_semana` são usados pelo engine de metas para calcular carga semanal
