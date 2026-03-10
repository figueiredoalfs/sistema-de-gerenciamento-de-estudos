# Algoritmo de Priorização — ConcursoAI

## Fórmula
Score = W1×Urgência + W2×Lacuna + W3×Peso + W4×FatorErros

Urgência  = 1 - (dias_restantes / dias_totais)^0.5
Lacuna    = 1 - (taxa_acerto/100) × e^(−λ × dias_desde_estudo)
Peso      = peso_edital_topico / max(pesos do cronograma)
FatorErros= min(erros_pendentes / 10.0, 1.0)

## Pesos default (ajustáveis pelo admin via ConfigSistema)
W1=0.35  W2=0.30  W3=0.20  W4=0.15  → soma deve = 1.0

## λ por categoria
Legislação=0.03 | Raciocínio Lógico=0.08 | demais=0.05
(λ individual por aluno/tópico virá do FSRS na F-06)

## Interleaving
Máximo 2 sessões da mesma matéria por resultado de /agenda
Rohrer & Taylor 2007

## Agenda
GET /agenda?top=5
Retorna top-N sessões com score_breakdown (urgência, lacuna, peso, erros)
Cache Redis: agenda:{aluno_id} TTL=1h
Recalcular após: POST /bateria | POST /sessao/input | PATCH /erro/{id}/status

## Modo Revisão Final (D-13)
Ativa: 14 dias antes de data_prova
Efeito: só flashcard_texto e exercicios
Ordem: (1-taxa_acerto) × peso_edital × exp(decay × dias_sem_revisar)
Simulado obrigatório na penúltima semana
