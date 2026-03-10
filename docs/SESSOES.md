# Sessões Multimodais — D-14

## Tipos e durações
teoria_pdf      50 min  → PDF com estrutura: caso_concreto→conceito→por_quê→quando→distinção
exercicios      45 min  → quiz com parâmetro momento (primeiro_contato / revisao)
video           30 min  → reconsolidação dias depois (YouTube Data API)
flashcard_texto 20 min  → resposta digitada avaliada por IA
calibracao      20 min  → 15q adaptativas, uma_vez=True

## Por peso do tópico
Alto   (≥0.7):    4 sessões: teoria → exercicios → video → flashcard_texto
Médio  (0.3-0.69):3 sessões: teoria → exercicios → flashcard_texto
Complementar(<0.3):2 sessões: teoria → exercicios

## Desbloqueio em cascata
exercicios:      bloqueada até teoria_pdf concluída
video:           bloqueada até exercicios concluída
flashcard_texto: bloqueada até exercicios concluída

## Agendamento de revisão por taxa de acerto
≥80% → +15 dias | 60-79% → +7 dias | 40-59% → +3 dias | <40% → +1 dia

## Quiz por momento
primeiro_contato: 70% conceito_puro, 20% aplicação, 10% contraste
revisao:          30% conceito, 30% contraste, 20% aplicação, 20% exceção
(Woloshyn 1992: elaboração requer conhecimento prévio)

## Flashcard por texto
IA gera perguntas de geração ativa (não reconhecimento)
Aluno digita resposta livre
IA verifica conceitos cobertos → retorna cobertura, ok, faltando, feedback
(Chi 1994: self-explanation effect preservado pela digitação)

## FSRS — campos na tabela Sessao
stability: intervalo onde aluno manteve ≥90% acerto
difficulty: 1 - taxa_acerto_media das últimas 3 sessões
Algoritmo completo implementado na F-06 com 3-4 meses de dados
