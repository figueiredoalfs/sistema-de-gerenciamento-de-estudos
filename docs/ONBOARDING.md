# Onboarding + Calibração — UX-01 e UX-02

## Fluxo onboarding (5 telas, < 3 minutos)
Tela 1: seleção de área (1 clique) — Fiscal/Jurídica/Policial/TI/Saúde/Outro
Tela 2: edital disponível? + upload PDF + data da prova (parser em background)
Tela 3: já vem estudando? → 3 perfis:
  Perfil A: começando do zero
  Perfil B: tempo declarado por matéria → gera sessão calibracao
  Perfil C: importar CSV do Qconcursos/TEC → popula Proficiencia
Tela 4: horas/dia + dias/semana (slider)
Tela 5: cronograma gerado — valor imediato sem mais formulários

## POST /onboarding — orquestra tudo
1. Criar Cronograma
2. Perfil A: arvore_generator para cada matéria da AreaBase
3. Perfil B: arvore_generator + sessão calibracao por matéria com nivel_inicial
4. Perfil C: parsear CSV → Proficiencia fonte=qconcursos peso=1.0
5. edital_parser em background se PDF enviado
6. session_generator → todas as sessões
7. meta_semanal.gerar_nova_janela()
8. Retornar: {cronograma_id, total_sessoes, primeira_semana: [5 sessões]}

## Calibração adaptativa (UX-02)
Tempo declarado → nível inicial da calibração:
  <1m=básico(1-2) | 1-3m=inter(2-3) | 3-6m=avançado(3-4) | >6m=expert(4-5)

15 questões em 3 fases:
  Fase 1 (5q): âncora no nível estimado
    4-5 acertos→sobe | 2-3→mantém | 0-1→desce
  Fase 2 (7q): refinamento no nível ajustado
  Fase 3 (3q): confirmação no nível de maior oscilação

fonte=calibracao, peso_fonte=1.2 — diluído após 3 baterias reais
UI: sem timer, framing diagnóstico não prova
Feedback: nível detectado + pontos fortes + lacunas

## Metas semanais
Janela móvel 7 dias (sem reset fixo)
conservador=85% | moderado=75% | agressivo=65% da carga
deficit_min: campo privado — só admin/mentor
Meta nunca cresce por atraso
teoria_pdf não feita → migra | video/flashcard → reagenda pelo decay
<60% conclusão → replanejamento silencioso
