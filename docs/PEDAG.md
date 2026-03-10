# Pedagogia — PEDAG-01 e FSRS

## Diagnóstico de situação por tópico (PEDAG-01)
Roda após cada sessão concluída via Celery

esquecimento:        acertava >70%, caiu para <50%
                     → revisão antecipada, intervalo ÷ 2

dificuldade_genuina: nunca atingiu >60% após 2+ ciclos
                     → verificar pré-requisitos em dependencias[]
                     → se pré-req < 60%: inserir na agenda com prioridade máxima
                     → gerar explicação alternativa (prompt modo=reexplicacao)
                     → interleaving forçado: nunca 2 sessões seguidas

misconception_ativa: erra sempre na mesma direção específica
                     → questão de confronto direto mostrando o conflito
                     (Chi 2008)

instavel:            oscila entre ciclos alternados
                     → aumentar frequência, reduzir intervalo

aprendendo:          progresso normal
consolidando:        taxa alta e estável

## FSRS
Campos stability e difficulty já na tabela Sessao desde F-01
Algoritmo implementado na F-06 (requer 3-4 meses de dados, 10+ alunos)

R(t) = exp(-t / stability)  ← retenção estimada
Após acerto: stability aumenta | Após erro: stability cai, difficulty sobe
Intervalo ideal = -stability × ln(0.9)  ← para manter R ≥ 90%

## Gamificação informacional (GAME-01)
Mapa de progresso: dominado=verde / em_progresso=amarelo / não_iniciado=cinza
Curva de mastery: histórico semanal do IP (Dweck 2006)
Desbloqueio visual: sessões trancadas até pré-req (Zeigarnik effect)
Simulado como chefe de fase (Csikszentmihalyi: flow)
Adversário calibrado F-06: mediana dos aprovados (Garcia & Tor 2009)
NÃO implementar: ranking entre usuários, streak obrigatório, pontos abstratos

## Índice de Prontidão (D-10)
IP = Σ(acerto × peso_norm × fator_decay × fator_cobertura) / Σ(peso_norm) × 100
fator_decay     = exp(-decay_rate × dias_sem_revisar)
fator_cobertura = 0 (nunca estudou) | 0.5 (só teoria) | 1.0 (teoria+exercicios)
Framing: diagnóstico — não pontuação a maximizar
