# Camada de IA — ConcursoAI

## AIProvider (app/services/ai_provider.py)
Classe base: gerar_texto(prompt, system) → str | gerar_json(prompt) → dict
GeminiProvider:    gemini-1.5-flash via google-generativeai (gratuito)
AnthropicProvider: claude-sonnet-4-20250514 via anthropic
get_ai_provider(): lê ConfigSistema['ia_provider'] default='gemini'
Admin troca via PATCH /admin/config/ia-provider sem redeploy

## Prompt de geração de teoria (arvore_generator)
Estrutura obrigatória: caso_concreto → conceito → por_quê → quando → distinção
(Van Merriënboer 1997: exemplo concreto ANTES do conceito abstrato)
Retorna JSON: {blocos: [{titulo, topicos: [{titulo, nivel_complexidade,
               tempo_teoria_min, tempo_exercicios_min, dependencias[]}]}]}

## Prompt de quiz (quiz_generator)
Parâmetro momento: 'primeiro_contato' ou 'revisao'
Foco nos erros críticos pendentes do tópico
Anti-alucinação: grounding no material real do aluno
Retorna JSON: [{enunciado, alternativas[5], gabarito, justificativa, tipo}]

## Prompt de calibração
Questões no nível estimado pelo tempo declarado
Ajuste dinâmico a cada fase (âncora→refinamento→confirmação)

## Flashcard
Perguntas de geração ativa (não reconhecimento)
IA avalia resposta digitada: conceitos_esperados vs texto_digitado
Retorna: {taxa_cobertura, conceitos_ok[], conceitos_faltando[], feedback}

## NLP Mapper (L-01 — Modo Mentor)
Input livre do aluno → tópico da árvore
IA recebe texto + lista de tópicos → retorna topico_id ou null

## Padrão Cognitivo (D-09)
Ativa com ≥50 questões erradas
Classifica cada erro: excecao/dupla_negativa/aplicacao/conceito/comparacao
Padrão detectado se taxa_categoria > 1.5× taxa_geral
Celery task a cada 10 novos erros
