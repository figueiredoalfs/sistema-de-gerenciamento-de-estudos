# ConcursoAI — Contexto do Projeto

> Leia este arquivo antes de qualquer tarefa. Ele contém todas as decisões de arquitetura,
> diferenciais e convenções do projeto. Sempre consulte a planilha `concursoai_roadmap_v3_FINAL.xlsx`
> para ver os prompts detalhados de cada fase.

---

## O que é o projeto

Plataforma de gestão de estudos para concursos públicos com IA. Transforma editais em
planos de estudo dinâmicos e adaptativos. Posicionamento: "A camada de inteligência que
conecta tudo que você já usa."

---

## Stack técnica

| Camada | Tecnologia |
|---|---|
| Backend | FastAPI (Python) |
| Banco local (dev) | SQLite — `DATABASE_URL=sqlite:///./dev.db` |
| Banco produção | PostgreSQL no Railway |
| Cache / Filas | Redis + Celery |
| IA | Gemini 1.5 Flash (gratuito) → Anthropic Claude (escala) |
| Deploy | Railway |
| Auth | JWT com roles: `admin` / `aluno` |
| PDF extração | pdfplumber |
| PDF geração | reportlab |

### Fix obrigatório para Railway
```python
DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://')
```

### Celery local (sem Redis)
```python
CELERY_TASK_ALWAYS_EAGER = True  # só no .env local — remover antes do deploy
```

---

## Estrutura de pastas

```
concurso-ai/
  app/
    main.py
    core/
      config.py         # variáveis de ambiente com pydantic-settings
      database.py       # engine SQLAlchemy — detecta SQLite vs Postgres
      security.py       # JWT: criar token, verificar, get_current_user, require_admin
    models/             # um arquivo por model
    schemas/            # Pydantic v2 — request + response
    routers/            # auth, desempenho, onboarding, agenda, cronograma,
                        # quiz, dashboard, admin, relatorio, simulado
    services/           # toda a lógica de negócio
    workers/            # tasks Celery
    scripts/            # migrar_sisfig.py, criar_usuario.py
  alembic/
  tests/
  .env                  # DATABASE_URL, SECRET_KEY, ALGORITHM, GEMINI_API_KEY
  requirements.txt
  Procfile
  railway.toml
  .gitignore
```

---

## Models do banco — campos importantes

### Sessao (campos críticos — não remover)
```python
tipo        ENUM: teoria_pdf / exercicios / video / flashcard_texto / calibracao
stability   Float nullable   # FSRS — coleta desde o início
difficulty  Float nullable   # FSRS — coleta desde o início
duracao_real_min  Int nullable    # feedback de tempo real (beta)
confianca   ENUM: baixa / media / alta   default='baixa'
uma_vez     Bool default=False           # calibracao nunca se repete
```

### Proficiencia (campos críticos)
```python
fonte  ENUM: qconcursos / tec / prova_anterior_mesma_banca /
             prova_anterior_outra_banca / simulado / quiz_ia /
             manual / calibracao
peso_fonte  Float default=1.0
```

### MetaSemanal
```python
deficit_min  Int default=0   # campo PRIVADO — visível só admin/mentor
```

---

## Pesos por fonte de questão

| Fonte | Peso |
|---|---|
| prova_anterior_mesma_banca | 1.5× |
| prova_anterior_outra_banca | 1.2× |
| calibracao | 1.2× |
| qconcursos / tec / simulado | 1.0× |
| quiz_ia / manual | 0.8× |
| curso / material externo | 0.6× |

---

## Algoritmo de priorização

```
Score = W1×Urgência + W2×Lacuna + W3×Peso + W4×FatorErros

Urgência  = 1 - (dias_restantes / dias_totais)^0.5
Lacuna    = 1 - (taxa_acerto/100) × e^(−λ × dias_desde_estudo)
Peso      = peso_edital_topico / max(pesos do cronograma)
FatorErros= min(erros_pendentes / 10.0, 1.0)

Pesos default (ajustáveis pelo admin):
  W1=0.35  W2=0.30  W3=0.20  W4=0.15

λ por categoria:
  Legislação=0.03 / Raciocínio Lógico=0.08 / demais=0.05
```

---

## Sessões multimodais por tópico (D-14)

| Tipo | Duração | Ordem | Quando desbloqueia |
|---|---|---|---|
| teoria_pdf | 50 min | 1ª | Sempre disponível |
| exercicios | 45 min | 2ª | Após teoria_pdf concluída |
| video | 30 min | 3ª | Após exercicios concluída |
| flashcard_texto | 20 min | 4ª | Após exercicios concluída |
| calibracao | 20 min | especial | uma_vez=True por matéria |

**Por peso do tópico:**
- Alto (≥0.7): 4 sessões completas
- Médio (0.3–0.69): teoria_pdf + exercicios + flashcard_texto
- Complementar (<0.3): teoria_pdf + exercicios

**Estrutura do PDF gerado pela IA:**
caso_concreto → conceito → por_quê → quando → distinção
(Van Merriënboer 1997: exemplo concreto ANTES do conceito abstrato)

---

## Calibração adaptativa (UX-02)

```
Perfil B no onboarding: aluno declara tempo de estudo por matéria
  <1m = básico (nível 1-2)
  1-3m = intermediário (2-3)
  3-6m = avançado (3-4)
  >6m = expert (4-5)

15 questões em 3 fases:
  Fase 1 — âncora: 5q no nível estimado
    4-5 acertos → sobe / 2-3 → mantém / 0-1 → desce
  Fase 2 — refinamento: 7q no nível ajustado
  Fase 3 — confirmação: 3q no nível onde oscilou

fonte=calibracao, peso=1.2× — diluído após 3 baterias reais
UI: sem timer, framing de diagnóstico (não de prova)
```

---

## PEDAG-01 — Diagnóstico de situação por tópico

```
esquecimento:       acertava >70%, caiu para <50%
                    → revisão antecipada, intervalo ÷ 2

dificuldade_genuina: nunca atingiu >60% após 2+ ciclos
                    → verificar pré-requisitos → nova explicação

misconception_ativa: erra sempre na mesma direção específica
                    → questão de confronto direto (Chi 2008)

instavel:           oscila entre ciclos alternados
                    → aumentar frequência, reduzir intervalo

aprendendo:         em progresso normal
consolidando:       taxa alta e estável
```

---

## Gamificação informacional (GAME-01)

- **Mapa de progresso**: tópicos coloridos por situacao (verde/amarelo/cinza)
- **Curva de mastery**: histórico semanal do IP em gráfico
- **Desbloqueio visual**: sessões aparecem trancadas até pré-req concluído
- **Simulado como chefe de fase**: framing de desafio calibrado ao nível
- **Adversário calibrado** (F-06): mediana dos aprovados na última edição

NÃO implementar: ranking entre usuários reais, streak obrigatório, pontos abstratos.

---

## FSRS — preparação desde F-01

Os campos `stability` e `difficulty` na tabela `Sessao` são coletados desde o início.
O algoritmo completo só é implementado na F-06, quando houver dados suficientes (3-4 meses, 10+ alunos).

```python
R(t) = exp(-t / stability)   # retenção estimada
# stability e difficulty aprendidos por aluno/tópico com o uso
```

---

## Onboarding (UX-01) — 5 telas, < 3 minutos

```
Tela 1: seleção de área (1 clique)
Tela 2: edital disponível? + upload PDF + data da prova
Tela 3: já vem estudando? → 3 perfis:
  Perfil A: começando do zero
  Perfil B: tempo declarado por matéria → gera calibração
  Perfil C: importar CSV do Qconcursos/TEC
Tela 4: horas/dia + dias/semana
Tela 5: cronograma gerado — aluno vê valor imediato
```

---

## Metas semanais

```
Janela móvel de 7 dias (sem dia fixo de reset)
Níveis: conservador=85% / moderado=75% / agressivo=65% da carga
Déficit: campo privado — visível só admin/mentor
Regras:
  - Meta NUNCA cresce por atraso
  - teoria_pdf não feita → migra para próxima janela
  - video/flashcard não feito → reagenda pelo decay
  - Se conclusão < 60%: replanejamento silencioso (sem alerta ao aluno)
  - 14 dias antes da prova: ativa Modo Revisão Final automaticamente
```

---

## Modo Revisão Final (D-13)

```
Ativa: automaticamente 14 dias antes da data_prova
Efeito:
  - Congela novas sessões teoria_pdf para tópicos não iniciados
  - Agenda filtra apenas flashcard_texto e exercicios
  - Ordena por: (1-taxa_acerto) × peso_edital × exp(decay × dias_sem_revisar)
  - Simulado obrigatório na penúltima semana
```

---

## Inteligência coletiva (D-IC) — F-06

```
Agrupa por: área + banca + cargo (os três cruzados)
Mínimo 5 alunos por perfil para ativar
Job Celery Beat: toda segunda-feira às 3h (nunca real-time)
Dados sempre agregados e anônimos — nunca individuais
Aprende: tempo real por tópico, dificuldade coletiva,
         frequência em editais, tópicos cobrados fora do edital,
         calibração dos pesos por fonte de questão
```

---

## Camada de IA (ai_provider.py)

```python
class AIProvider:           # interface base
class GeminiProvider:       # gemini-1.5-flash — gratuito
class AnthropicProvider:    # claude-sonnet-4-20250514 — escala

get_ai_provider():
  lê ConfigSistema['ia_provider']  # default='gemini'
  admin troca via painel sem redeploy
```

---

## Painel Admin — endpoints principais

```
GET/POST/PATCH  /admin/usuarios
GET             /admin/dashboard-geral
POST            /admin/editais
PUT/DELETE      /admin/topicos/{id}
PATCH           /admin/cronograma/{aluno_id}
PATCH           /admin/config/ia-provider
PATCH           /admin/config/pesos-algoritmo   # W1,W2,W3,W4 — soma deve = 1.0
GET             /admin/meta/{aluno_id}/historico  # déficit privado
GET             /admin/padrao-cognitivo/{aluno_id}
GET             /admin/confianca-estimativas      # alertas beta
```

---

## Decisões já tomadas — não questionar

- Docker incompatível com o Windows do usuário → SQLite local
- Flashcard por texto (não áudio) — self-explanation effect preservado
- Déficit de meta invisível para o aluno — só admin/mentor vê
- Sem ranking entre usuários reais
- Calibração não se repete (uma_vez=True)
- Interleaving: máximo 2 sessões da mesma matéria por dia
- Deploy: Railway (gratuito no beta)

---

## Bases científicas das features principais

| Feature | Referência |
|---|---|
| Exercícios + flashcards | Roediger & Karpicke 2006 |
| Agendamento por decay | Ebbinghaus 1885 / Cepeda 2006 |
| FSRS | Wozniak / Jarrett Ye 2022 |
| Interleaving | Rohrer & Taylor 2007 |
| Questões elaborativas | Dunlosky 2013 |
| Multimodalidade | Paivio 1971 / Mayer 2003 |
| Calibração adaptativa | van der Linden & Hambleton 1997 |
| Diagnóstico de situação | VanLehn 2011 |
| Misconception | Chi 2008 |
| Exemplo concreto primeiro | Van Merriënboer 1997 |
| Flashcard por texto | Chi 1994 (self-explanation) |
| Adversário calibrado | Garcia & Tor 2009 |
| Curva de mastery | Dweck 2006 |
| Mapa de progresso | Bandura 1997 |
| Gamificação informacional | Deci & Ryan 2000 / Mekler 2017 |
| Simulado como desafio | Csikszentmihalyi (flow) |
| Horário de estudo | Walker 2017 |

---

## Como usar este arquivo

Salve este arquivo na raiz do projeto. Para iniciar qualquer sessão de desenvolvimento,
basta digitar:

```
leia o arquivo contexto na pasta do projeto
```

O Claude Code vai executar a rotina abaixo automaticamente.

---

## Rotina de sessão — SEGUIR SEMPRE ESTA ORDEM

Quando o usuário disser **"leia o arquivo contexto na pasta do projeto"**,
execute exatamente os passos abaixo — sem pular nenhum.

### PASSO 1 — Carregar contexto e verificar progresso

1. Leia este arquivo `CONTEXTO.md` na íntegra
2. Abra `concursoai_roadmap_v3_FINAL.xlsx` e rode o script de verificação:

```python
import openpyxl
wb = openpyxl.load_workbook('concursoai_roadmap_v3_FINAL.xlsx')
ws = wb['🗓️ Cronograma']
concluidos = []
pendentes = []
for row in ws.iter_rows(min_row=5, values_only=True):
    if row[1] and row[2] and row[19]:
        if '✅' in str(row[19]):
            concluidos.append(row[2])
        elif '⬜' in str(row[19]) or '🟡' in str(row[19]):
            pendentes.append((row[1], row[2], row[20] or ''))
print(f'Concluídas: {len(concluidos)} | Pendentes: {len(pendentes)}')
for fase, tarefa, nota in pendentes[:1]:
    print(f'Próximo: [{fase}] {tarefa}')
    if nota: print(f'Nota: {nota}')
```

### PASSO 2 — Apresentar o próximo passo ao usuário

Responda neste formato exato:

---
**📋 Progresso atual:** X de Y tarefas concluídas

**⏭️ Próximo passo:**
> [FASE] — [Nome da tarefa]
> [Nota da tarefa se houver]

**O que será implementado:**
[Descrição clara e resumida do que o código vai fazer — 3 a 5 linhas]

**Deseja iniciar a implementação?** `[ Sim / Não ]`

---

Aguarde a confirmação do usuário antes de escrever qualquer código.

### PASSO 3 — Implementar (somente após confirmação)

1. Marque a tarefa como `🟡 Em andamento` na planilha imediatamente
2. Implemente o código conforme o prompt detalhado na aba ⚡ Comandos & Prompts
3. Ao concluir, avise o usuário neste formato:

---
**✅ Implementação concluída**

**O que foi feito:**
[Lista do que foi criado/modificado — arquivos, funções, endpoints]

**Para testar:**
[Instruções claras e objetivas de como o usuário deve testar agora]
[Ex: "Rode uvicorn app.main:app --reload e acesse http://localhost:8000/docs"]
[Ex: "Execute python -m app.scripts.migrar_sisfig sisfig.db <seu_aluno_id>"]

⚠️ **Me avise quando os testes estiverem ok ou se precisar de ajustes.**

---

### PASSO 4 — Ciclo de ajustes (se necessário)

- O usuário pode pedir quantos ajustes quiser antes de confirmar o passo
- Cada ajuste é implementado e o usuário testa novamente
- Só avançar quando o usuário confirmar que está ok

### PASSO 5 — Finalizar o passo (quando usuário confirmar ok)

Quando o usuário disser que o passo foi finalizado:

1. Marque a tarefa como `✅ Concluído` na planilha:

```python
import openpyxl
from openpyxl.styles import Font

wb = openpyxl.load_workbook('concursoai_roadmap_v3_FINAL.xlsx')
ws = wb['🗓️ Cronograma']
for row in ws.iter_rows(min_row=5):
    tarefa_cell = row[2]   # coluna C = TAREFA
    status_cell = row[19]  # coluna T = STATUS
    if tarefa_cell.value and 'NOME_EXATO_DA_TAREFA' in str(tarefa_cell.value):
        status_cell.value = '✅ Concluído'
        status_cell.font = Font(name='Arial', color='3FB950', size=8)
wb.save('concursoai_roadmap_v3_FINAL.xlsx')
print('Planilha atualizada.')
```

2. Pergunte ao usuário:

---
**🎯 Passo concluído e registrado na planilha.**

**Deseja continuar para o próximo passo ou encerrar a sessão?**
`[ Continuar / Encerrar ]`

---

- Se **Continuar**: volte ao PASSO 2 com a próxima tarefa pendente
- Se **Encerrar**: responda com um resumo do que foi feito na sessão e encerre

---

## Regras que nunca devem ser quebradas

1. **Nunca implemente sem confirmação** — sempre aguardar o "sim" do usuário
2. **Nunca encerre sem atualizar a planilha** — cada tarefa concluída deve ser marcada
3. **Nunca avance para o próximo passo sem o usuário confirmar** que o atual está ok
4. **Planilha deve estar fechada** quando for editada via Python
5. **Se algo quebrar**, avise claramente o erro e aguarde instrução — não tente corrigir silenciosamente

---

## Atualização automática da planilha — OBRIGATÓRIO

Ao concluir qualquer tarefa, o Claude Code DEVE atualizar o STATUS na planilha
`concursoai_roadmap_v3_FINAL.xlsx` antes de encerrar a sessão.

**Regra:** nunca encerre uma sessão sem atualizar a planilha.

### Como atualizar via Python (openpyxl)

```python
import openpyxl

wb = openpyxl.load_workbook('concursoai_roadmap_v3_FINAL.xlsx')
ws = wb['🗓️ Cronograma']

# Coluna 20 = STATUS. Buscar pela tarefa e atualizar.
for row in ws.iter_rows():
    tarefa_cell = row[2]  # coluna C = TAREFA
    status_cell = row[19] # coluna T = STATUS
    if tarefa_cell.value and 'NOME_DA_TAREFA' in str(tarefa_cell.value):
        status_cell.value = '✅ Concluído'
        status_cell.font = openpyxl.styles.Font(
            name='Arial', color='3FB950', size=8)

wb.save('concursoai_roadmap_v3_FINAL.xlsx')
print('Planilha atualizada.')
```

### Status disponíveis

| Status | Significado |
|---|---|
| `⬜ Pendente` | Ainda não iniciado |
| `🟡 Em andamento` | Iniciado mas não concluído |
| `✅ Concluído` | Implementado e testado |
| `🔴 Bloqueado` | Impedido por dependência ou erro |

### Fluxo por sessão

```
1. Início: leia CONTEXTO.md + verifique STATUS na planilha
2. Durante: marque 🟡 Em andamento ao iniciar cada tarefa
3. Final:   marque ✅ Concluído em tudo que foi implementado
4. ATENÇÃO: planilha deve estar FECHADA ao editar via Python
```

### Ao iniciar nova sessão

Sempre comece verificando o que está concluído:

```python
import openpyxl
wb = openpyxl.load_workbook('concursoai_roadmap_v3_FINAL.xlsx')
ws = wb['🗓️ Cronograma']
pendentes = []
concluidos = []
for row in ws.iter_rows(min_row=5, values_only=True):
    if row[1] and row[2] and row[19]:  # FASE, TAREFA, STATUS
        if '✅' in str(row[19]):
            concluidos.append(row[2])
        elif '⬜' in str(row[19]) or '🟡' in str(row[19]):
            pendentes.append((row[1], row[2]))
print(f'Concluídas: {len(concluidos)} | Pendentes: {len(pendentes)}')
print('Próximas tarefas:')
for fase, tarefa in pendentes[:5]:
    print(f'  [{fase}] {tarefa}')
```
