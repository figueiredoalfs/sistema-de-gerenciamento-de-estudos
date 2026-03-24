# AGORA.md — Skolai
> Modelo: Desenvolvimento Espiral/Incremental
> Visão: Gestor inteligente de estudos para concursos públicos
> O Skolai diz o que estudar, você estuda onde quiser, o Skolai analisa seu desempenho.
> Atualizado: 23/03/2026 | 22 concluídas | www.skolai.com.br no ar

---

## Visão do produto por volta

```
Volta 1 — Gestor de estudos funcional (beta fiscal)
Volta 2 — Análise e adaptação (lacunas e desempenho)
Volta 3 — Conteúdo de apoio (IA enriquece o estudo)
Volta 4 — Questões próprias (se validado pelo beta)
Volta 5 — Expansão (áreas militares, monetização)
```

---

## Stack
- Backend: FastAPI + SQLAlchemy + SQLite(dev) / PostgreSQL(prod)
- Frontend: React 18 + Vite + Tailwind + React Router v6 + Caddy
- IA: Gemini 1.5 Flash (tier gratuito para o beta)
- Deploy: Railway — Frontend (Dockerfile+Caddy) + Backend + PostgreSQL
- Roles: administrador / mentor / estudante

---

## Infraestrutura Railway — NÃO alterar sem necessidade

### Serviços ativos
| Serviço | URL | Status |
|---|---|---|
| Frontend | www.skolai.com.br | Online |
| Backend | domínio Railway interno | Online |
| PostgreSQL | gerado pelo Railway | Online |

### Variáveis de ambiente — Backend
- DATABASE_URL — PostgreSQL Railway (automático, não alterar)
- SECRET_KEY — chave JWT
- GEMINI_API_KEY — API Gemini (tier gratuito: 15 req/min, 1M tokens/dia)
- ALLOWED_ORIGINS — https://www.skolai.com.br
- ADMIN_EMAIL, ADMIN_NOME, ADMIN_SENHA

### Variáveis de ambiente — Frontend
- VITE_API_URL — URL pública do backend
- PORT = 80

### Arquivos críticos — nunca modificar sem necessidade
- `frontend/Dockerfile` — build 2 estágios: node:18-alpine + caddy:2-alpine
- `frontend/.dockerignore` — sem isso node_modules Windows quebra o build
- `frontend/Caddyfile` — try_files obrigatório para React Router funcionar
- `frontend/railway.toml` — builder = "dockerfile" (não nixpacks)
- Ferramentas de build (vite, tailwind) em `dependencies`, não devDependencies

### Proibições absolutas
- NÃO voltar para nixpacks — quebra build por NODE_ENV=production
- NÃO deletar .dockerignore do frontend
- NÃO remover PORT=80 das variáveis do frontend
- NÃO alterar DATABASE_URL manualmente
- NÃO commitar .env, dev.db ou sisfig.db
- NÃO remover fix postgres:// → postgresql:// em config.py
- NÃO alterar ALLOWED_ORIGINS para "*" em produção
- NÃO usar gemini-2.5-flash — usar gemini-1.5-flash ou gemini-1.5-flash-8b
- NÃO remover try_files do Caddyfile

### Fluxo obrigatório ao mudar schema do banco
```bash
alembic revision --autogenerate -m "descricao"
alembic upgrade head                          # testa local
git add alembic/versions/
git commit && git push                        # Railway faz deploy
railway run alembic upgrade head              # aplica no PostgreSQL
```
**O último passo é obrigatório — sem ele o backend quebra em produção.**

---

## Regras de implementação
1. Leia o módulo correspondente em `docs/modulos/` antes de implementar
2. Backend primeiro — testar no /docs antes de tocar no frontend
3. Frontend consome o endpoint confirmado
4. Só concluir quando funcionar no navegador de ponta a ponta
5. Contrato quebrado → corrigir backend, nunca adaptar frontend
6. IA só chamada por ação explícita — nunca em loop automático
7. Cache agressivo em todo conteúdo gerado por IA — gera uma vez, serve para todos
8. Modelo IA: gemini-1.5-flash-8b (tarefas simples) / gemini-1.5-flash (PDF e PlanoBase)

---

## Critérios pedagógicos fixos no código

```python
CRITERIOS_AVANCO = {1: 0.65, 2: 0.70, 3: 0.75, 4: 0.80, 5: 0.85}
MAX_MATERIAS_FASE_1 = 4
MAX_MATERIAS_NOVAS_POR_FASE = 3
LIMIAR_DOMINIO = {"baixa": 0.70, "media": 0.75, "alta": 0.80}
```

A IA do PlanoBase retorna APENAS:
- `fases[]` — quais matérias entram em cada fase e em que ordem
- `ordem_subtopicos{}` — sequência pedagógica dos subtópicos por matéria
- `prerequisitos{}` — dependências diretas entre subtópicos
Nunca gera critérios de avanço, limiares ou configurações pedagógicas.

---

# VOLTA 1 — Gestor de estudos funcional

> Meta: um aluno fiscal consegue se cadastrar, receber um plano de estudo,
> acompanhar seu progresso e registrar seu desempenho sem encontrar erros.
> IA presente em 3 pontos específicos: PlanoBase, PDF explicativo, sugestão de vídeos.
> Tudo dentro do tier gratuito do Gemini para o beta.

## O que o aluno consegue fazer na Volta 1
1. Criar conta e fazer onboarding
2. Receber um plano de estudo adaptativo (gerado por IA uma vez, cacheado)
3. Ver no dashboard o que estudar hoje
4. Pedir um resumo do subtópico (PDF gerado por IA, cacheado)
5. Ver sugestões de onde estudar (vídeos YouTube por subtópico)
6. Registrar o que estudou e quantas questões fez (Caderno de Questões)
7. Ver seu desempenho evoluir semana a semana
8. Editar seu perfil e disponibilidade

## O que o admin consegue fazer na Volta 1
1. Gerenciar matérias e subtópicos
2. Gerenciar usuários
3. Ver quanto o sistema está gastando com IA

---

### V1-T01 — Migrar banco de dados local para o Railway
⬜ PENDING

**Leia antes:** `docs/modulos/database.md`

**Contexto:** O PostgreSQL de produção está vazio. Matérias, subtópicos
e ciclos estão só no dev.db local. Sem isso o site não tem estrutura nenhuma.

**O que implementar:**
Criar `scripts/migrar_dev_para_railway.py`:

```python
# Conecta ao dev.db local E ao PostgreSQL do Railway
# Migra nesta ordem (respeitar FKs):
# 1. topicos (nivel=0 matérias, nivel=1 tópicos, nivel=2 subtópicos)
# 2. ciclo_materias
# 3. subtopico_area (se existir)
# NÃO migrar: alunos, tasks, metas, sessões, questões

# Usar upsert para rodar mais de uma vez com segurança:
# PostgreSQL: INSERT ... ON CONFLICT (id) DO NOTHING
# Conectar ao Railway via variável DATABASE_URL do ambiente
```

**Como executar:**
```bash
railway run python scripts/migrar_dev_para_railway.py
```

**Como verificar:**
- https://www.skolai.com.br/admin/topicos → matérias aparecem
- https://www.skolai.com.br/admin/usuarios → página carrega sem erro

**Arquivos:**
- CRIAR: `scripts/migrar_dev_para_railway.py`

---

### V1-T02 — Corrigir modelo de IA e acesso admin
⬜ PENDING

**Leia antes:** `docs/modulos/ia.md`

**Contexto:** Dois problemas críticos.
1. O modelo gemini-2.5-flash causou R$47 de custo em um dia de testes
2. A senha admin com @ não funciona no Railway

**O que implementar:**

**Parte 1 — Trocar modelo:**
Em `app/core/ai_provider.py` e em qualquer arquivo que tenha
"gemini-2.5-flash" hardcoded (buscar com `grep -r "gemini-2.5" app/`):
```python
# DE: model="gemini-2.5-flash"
# PARA: model="gemini-1.5-flash-8b"  (tarefas simples)
# OU:   model="gemini-1.5-flash"     (PDF e PlanoBase)
```

Adicionar log de consumo após cada chamada:
```python
usage = response.usage_metadata
print(f"[AI] modelo={model} tipo={tipo} input={usage.prompt_token_count} output={usage.candidates_token_count}")
```

**Parte 2 — Reset de senha admin:**
Criar `scripts/reset_admin.py`:
```python
from app.core.database import SessionLocal
from app.models.aluno import Aluno
from app.core.security import hash_password
db = SessionLocal()
admin = db.query(Aluno).filter(Aluno.role == 'administrador').first()
if admin:
    admin.senha_hash = hash_password('SkolaiAdmin2026')
    db.commit()
    print(f'Senha resetada: {admin.email} / SkolaiAdmin2026')
db.close()
```
Executar: `railway run python scripts/reset_admin.py`

**Como verificar:**
- Logar em www.skolai.com.br com admin@skolai.com / SkolaiAdmin2026
- Verificar no console que logs mostram gemini-1.5-flash

**Arquivos:**
- MODIFICAR: `app/core/ai_provider.py`
- BUSCAR E MODIFICAR: qualquer arquivo com "gemini-2.5"
- CRIAR: `scripts/reset_admin.py`

---

### V1-T03 — Corrigir PlanoBase: prompt e parser
⬜ PENDING

**Leia antes:** `docs/modulos/ia.md`

**Contexto:** A geração do PlanoBase retorna "A IA não retornou fases válidas".
O prompt atual pede critérios de avanço que são fixos no código.

**O que implementar:**
Localizar o service de geração do PlanoBase com:
```bash
grep -r "plano_base\|PlanoBase\|gerar_plano" app/services/ app/routers/
```

Substituir o prompt por:
```python
PROMPT_PLANO_BASE = """
Você é especialista em pedagogia de concursos públicos brasileiros.
Analise as matérias e subtópicos e organize um plano progressivo.

ÁREA: {area}
PERFIL: {perfil}
MATÉRIAS DISPONÍVEIS: {lista_materias_subtopicos}

Retorne SOMENTE JSON válido, sem texto adicional, sem markdown:
{{
  "fases": [
    {{"numero": 1, "nome": "Fundação", "materias": ["Materia1", "Materia2"]}},
    {{"numero": 2, "nome": "Aprofundamento", "materias_novas": ["Materia3"]}}
  ],
  "ordem_subtopicos": {{
    "Nome da Materia": ["subtopico1", "subtopico2"]
  }},
  "prerequisitos": {{
    "subtopico_avancado": ["subtopico_base"]
  }}
}}

REGRAS:
- Fase 1: máximo 4 matérias independentes e fundamentais
- Fases seguintes: máximo 3 matérias novas
- ordem_subtopicos: do mais básico ao mais complexo
- Listar TODOS os subtópicos de TODAS as matérias
- NÃO incluir critérios de avanço, percentuais ou limiares
"""
```

Corrigir o parser do retorno:
```python
# 1. Remover markdown: raw = raw.replace("```json","").replace("```","").strip()
# 2. Encontrar JSON: inicio = raw.find("{"), fim = raw.rfind("}") + 1
# 3. Parsear: dados = json.loads(raw[inicio:fim])
# 4. Validar: assert "fases" in dados and "ordem_subtopicos" in dados
```

**Como verificar:**
- Admin → Configurações → gerar PlanoBase fiscal/iniciante
- Deve gerar sem erro e mostrar fases no editor visual

**Arquivos:**
- MODIFICAR: service de geração do PlanoBase (localizar com grep)

---

### V1-T04 — Corrigir dashboard: Meta 00 e bloqueio de diagnóstico
⬜ PENDING

**Leia antes:** `docs/modulos/tasks.md`

**Contexto:** Dois bugs relacionados ao diagnóstico inicial.
1. Banner "diagnóstico pendente" aparece mesmo após concluído
2. Alunos não-iniciantes não veem a Meta 00

**O que implementar:**

**Parte 1 — Remover banner, implementar bloqueio:**
Em `frontend/src/pages/Dashboard.jsx`:
- Remover completamente o banner/aviso de diagnóstico pendente
- Se `user.diagnostico_pendente === true`, renderizar tela de bloqueio:
```jsx
// Em vez do dashboard normal, mostrar:
<div>
  <h2>Complete seu diagnóstico inicial</h2>
  <p>Isso nos ajuda a montar seu plano personalizado</p>
  <button onClick={() => navigate('/tasks/diagnostico')}>
    Iniciar Diagnóstico
  </button>
</div>
```

**Parte 2 — Meta 00 visível:**
Em `app/routers/study_tasks.py`, endpoint `GET /tasks/today`:
- Se `aluno.diagnostico_pendente == True` E `aluno.experiencia != "iniciante"`:
  retornar APENAS tasks do tipo `diagnostico` da Meta 00
- Verificar em `app/services/engine_pedagogica.py` se a Meta 00
  está sendo gerada corretamente para não-iniciantes

**Como verificar:**
- Criar aluno com experiencia="tempo_de_estudo" → ver Meta 00 no dashboard
- Concluir diagnóstico → dashboard normal aparece sem banner
- Criar aluno iniciante → não ver diagnóstico, ver dashboard direto

**Arquivos:**
- MODIFICAR: `frontend/src/pages/Dashboard.jsx`
- VERIFICAR/MODIFICAR: `app/routers/study_tasks.py`
- VERIFICAR: `app/services/engine_pedagogica.py`

---

### V1-T05 — Corrigir geração de PDF e sugestão de vídeos
⬜ PENDING

**Leia antes:** `docs/modulos/tasks.md` e `docs/modulos/ia.md`

**Contexto:** Botões "Gerar PDF" e "Vídeo Aula" nas tasks não funcionam.
O PDF é o principal recurso de apoio ao estudo da Volta 1.
Com cache, é gerado uma vez por subtópico e serve para todos os alunos.

**O que implementar:**

**Parte 1 — Verificar backend:**
Testar no /docs os endpoints:
- `POST /task-conteudo/{task_code}/gerar-pdf`
- `GET /task-conteudo/{task_code}/videos`
- `POST /task-conteudo/{task_code}/videos/buscar`

Se retornarem erro 500, corrigir o service.
O PDF deve ser gerado com prompt contextualizado para concursos:
```python
prompt = f"""
Crie um resumo didático sobre '{subtopico}' ({materia})
para candidatos a concursos públicos fiscais brasileiros.
Foque no que é cobrado em prova. Máximo 800 palavras.
Organize em: Conceito, Pontos principais, O que cai em prova, Dicas.
"""
```

**Parte 2 — Corrigir frontend:**
No componente TaskCard expandido
(localizar em `frontend/src/components/`):

Botão PDF:
```jsx
// 1. Mostrar loading "Gerando resumo..." (pode levar ~15s)
// 2. POST /task-conteudo/{task_code}/gerar-pdf
// 3. Exibir conteúdo em área expandida ou modal
// 4. Adicionar abaixo: "⚠️ Gerado por IA — pode conter imprecisões"
```

Botão Vídeo:
```jsx
// 1. GET /task-conteudo/{task_code}/videos
// 2. Se lista vazia: POST .../videos/buscar (IA busca no YouTube)
// 3. Exibir cards: thumbnail + título + link para YouTube
// 4. Não executar o vídeo dentro do Skolai — abrir no YouTube
```

**Como verificar:**
- Expandir task de teoria → clicar "Gerar PDF" → resumo aparece em ~15s
- Clicar "Ver Vídeos" → lista de vídeos do YouTube aparece

**Arquivos:**
- VERIFICAR/MODIFICAR: `app/routers/task_conteudo.py`
- MODIFICAR: componente TaskCard (localizar com `find frontend/src -name "TaskCard*"`)

---

### V1-T06 — Caderno de Questões funcionando
⬜ PENDING

**Leia antes:** `docs/modulos/bateria.md`

**Contexto:** O aluno estuda no TEC Concursos ou Qconcursos e registra
os resultados aqui. O sistema analisa e adapta o plano.
A tela existe mas a lista de matérias não carrega.

**O que implementar:**

**Parte 1 — Verificar backend:**
Confirmar que existe endpoint para listar matérias:
```bash
# Testar no /docs:
GET /topicos?nivel=0  # ou GET /topicos/hierarquia
```
Se não existir ou retornar vazio, criar/corrigir.

**Parte 2 — Corrigir e renomear frontend:**
Renomear `LancarBateria.jsx` → `CadernoQuestoes.jsx`
Atualizar rota de `/lancar-bateria` → `/caderno-questoes`
Atualizar link na Sidebar e no App.jsx/router.

Na página CadernoQuestoes.jsx:
```jsx
// Ao montar: buscar matérias da API e popular select
useEffect(() => {
  api.get('/topicos?nivel=0').then(res => setMaterias(res.data))
}, [])

// Ao selecionar matéria: buscar subtópicos
const onMateriaSelecionada = (materiaId) => {
  api.get(`/topicos?parent_id=${materiaId}&nivel=2`)
    .then(res => setSubtopicos(res.data))
}

// Bancas disponíveis (hardcoded):
const BANCAS = [
  'CESPE/CEBRASPE', 'FCC', 'FGV', 'VUNESP', 'AOCP',
  'IDECAN', 'IBFC', 'QUADRIX', 'IADES', 'UPENET',
  'Outra banca', 'Simulado próprio'
]

// Campos do formulário:
// - Select matéria (obrigatório)
// - Select subtópico (obrigatório)
// - Input acertos (número, obrigatório)
// - Input total questões (número, obrigatório)
// - Select banca (obrigatório)
// - Input data (opcional, default hoje)

// Após salvar com sucesso:
// - Mostrar "Sessão registrada com sucesso!"
// - Limpar formulário para registrar outra
// - Atualizar histórico abaixo
```

Adicionar seção de histórico:
```jsx
// GET /baterias?aluno_id=me&limit=10
// Mostrar tabela: data | matéria | subtópico | acertos/total | % | banca
```

**Como verificar:**
- Acessar /caderno-questoes → matérias carregam no select
- Selecionar matéria → subtópicos carregam
- Preencher e salvar → feedback de sucesso
- Histórico mostra a sessão

**Arquivos:**
- RENOMEAR: `frontend/src/pages/LancarBateria.jsx` → `CadernoQuestoes.jsx`
- MODIFICAR: `frontend/src/App.jsx` (rota)
- MODIFICAR: `frontend/src/components/layout/Sidebar.jsx` (link)
- VERIFICAR/CRIAR: endpoint de listagem de matérias no backend

---

### V1-T07 — Página de perfil do usuário
⬜ PENDING

**Leia antes:** `docs/modulos/auth.md`

**Contexto:** Não existe página de perfil. O aluno não consegue
trocar senha ou atualizar disponibilidade de estudo.

**O que implementar:**

**Parte 1 — Backend:**
Verificar se existem os endpoints. Se não existirem, criar:

`PATCH /auth/me` — atualizar dados:
```python
# Body: { nome, email, horas_por_dia, dias_por_semana }
# Retorna: AlunoResponse atualizado
```

`POST /auth/alterar-senha`:
```python
# Body: { senha_atual, nova_senha, confirmar_senha }
# Validar senha_atual com verify_password()
# Se válida: hash(nova_senha) e salvar
# Se inválida: retornar 400 "Senha atual incorreta"
```

**Parte 2 — Frontend:**
Criar `frontend/src/pages/Perfil.jsx` com 4 seções:

```jsx
// Seção 1 — Dados pessoais
// Campos: nome, email
// Botão Salvar → PATCH /auth/me

// Seção 2 — Disponibilidade de estudo
// Campos: horas por dia (1-12), dias por semana (1-7)
// Botão Salvar → PATCH /auth/me

// Seção 3 — Alterar senha
// Campos: senha atual, nova senha, confirmar nova senha
// Validar: nova === confirmar antes de enviar
// Botão Salvar → POST /auth/alterar-senha

// Seção 4 — Minha conta (somente leitura)
// Mostrar: área, experiência, data de cadastro
// Botão "Refazer onboarding" → navigate('/onboarding')
```

Adicionar link para /perfil na Sidebar (ícone de usuário, abaixo do logout).

**Como verificar:**
- Acessar /perfil → dados atuais preenchidos
- Editar nome → atualiza na sidebar
- Trocar senha → consegue logar com nova senha

**Arquivos:**
- CRIAR: `frontend/src/pages/Perfil.jsx`
- CRIAR/MODIFICAR: endpoints em `app/routers/auth.py`
- MODIFICAR: `frontend/src/components/layout/Sidebar.jsx`
- MODIFICAR: `frontend/src/App.jsx` (adicionar rota /perfil)

---

### V1-T08 — Monitoramento de custos de IA
⬜ PENDING

**Leia antes:** `docs/modulos/ia.md`

**Contexto:** Após o episódio dos R$47, precisamos monitorar
custos antes de abrir para usuários beta.
Gemini 1.5 Flash tem tier gratuito de 1M tokens/dia.
Com cache, o beta com 20 usuários provavelmente não paga nada.
Mas precisamos saber quando cruzar o limite.

**O que implementar:**

**Parte 1 — Model LogIA:**
Verificar se já existe. Se não existir, criar `app/models/log_ia.py`:
```python
class LogIA(Base):
    __tablename__ = "log_ia"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tipo = Column(String(50))       # "pdf", "plano_base", "video", "questao"
    modelo = Column(String(100))    # "gemini-1.5-flash-8b"
    tokens_input = Column(Integer, default=0)
    tokens_output = Column(Integer, default=0)
    custo_usd = Column(Float, default=0.0)
    aluno_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.utcnow())
```
Criar migration Alembic para essa tabela.

**Parte 2 — Registrar em ai_provider.py:**
Após cada `generate()`, salvar no banco:
```python
# gemini-1.5-flash-8b: $0.075/1M input, $0.30/1M output
custo = (tokens_input * 0.000000075) + (tokens_output * 0.0000003)
# salvar LogIA no banco
```

**Parte 3 — Endpoint e página admin:**
`GET /admin/financeiro/custos-ia` retorna:
```json
{
  "total_mes_usd": 0.00,
  "total_mes_brl": 0.00,
  "limite_gratuito_tokens_dia": 1000000,
  "consumido_hoje_tokens": 15000,
  "por_tipo": {"pdf": 0.00, "plano_base": 0.00, "video": 0.00}
}
```

Criar `frontend/src/pages/admin/AdminFinanceiro.jsx`:
- Card "Custo total do mês" (USD e BRL a R$5,70)
- Card "Tokens consumidos hoje / 1M (gratuito)"
- Tabela: custo por tipo de operação
- Aviso em vermelho se consumo > 80% do limite gratuito

**Como verificar:**
- Gerar PDF de uma task
- Acessar /admin/financeiro → custo aparece (provavelmente $0.00)
- Tokens consumidos aparecem

**Arquivos:**
- CRIAR: `app/models/log_ia.py`
- MODIFICAR: `app/core/ai_provider.py`
- CRIAR: endpoint em novo `app/routers/admin_financeiro.py`
- CRIAR: `frontend/src/pages/admin/AdminFinanceiro.jsx`
- Criar migration Alembic

---

# VOLTA 2 — Análise e adaptação
> Só iniciar após Volta 1 validada com usuários beta reais.
> Foco: o sistema aprende com o que o aluno registra no Caderno.

- V2-T01: Mapa de Lacunas (baseado no Caderno de Questões)
- V2-T02: Desempenho detalhado (radar, heatmap, velocidade de domínio)
- V2-T03: Índice de Prontidão
- V2-T04: Personalização por funcionalidades do onboarding
- V2-T05: Perfil de uso (com plano externo / sem plano externo)
- V2-T06: Confirmação de email e recuperação de senha
- V2-T07: Horas líquidas de estudo
- V2-T08: Ordem de aparição dos subtópicos

---

# VOLTA 3 — Conteúdo de apoio
> Foco: IA enriquece o estudo com fontes confiáveis.

- V3-T01: Base de conhecimento com PDFs do admin (RAG)
- V3-T02: PDF explicativo usando fontes upadas (mais preciso)
- V3-T03: Chat com IA contextualizado por subtópico
- V3-T04: Fluxo pós-edital via upload de PDF
- V3-T05: Sistema de reporte de conteúdo incorreto
- V3-T06: Seleção de modelo IA por tipo de operação (admin)

---

# VOLTA 4 — Questões próprias (se validado)
> Só implementar se o modelo pedagógico estiver validado pelo beta.
> O Caderno de Questões pode ser suficiente — validar antes de construir.

- V4-T01: Banco de questões básico (importação por PDF TEC)
- V4-T02: QuestionFlow dentro do Skolai
- V4-T03: Progressão de dificuldade por exposure_count
- V4-T04: Questões geradas por IA como fallback
- V4-T05: Aviso de origem nas questões

---

# VOLTA 5 — Expansão
> Produto validado, crescimento planejado.

- V5-T01: Áreas militares (COM e SVM)
- V5-T02: Mapa de Concursos
- V5-T03: Monetização (planos e gateway)
- V5-T04: Backup PostgreSQL → Google Drive
- V5-T05: Sentry + auditoria admin
- V5-T06: Upload de PDF de prova pelo aluno

---

## Rotas React — Volta 1

| Rota | Página | Role |
|---|---|---|
| /login | Login | público |
| /onboarding | Onboarding | autenticado sem area |
| / | Dashboard | estudante |
| /desempenho | Desempenho | estudante |
| /caderno-questoes | CadernoQuestoes | estudante |
| /perfil | Perfil | estudante |
| /admin | AdminDashboard | administrador |
| /admin/topicos | AdminTopicos | administrador |
| /admin/usuarios | AdminUsuarios | administrador |
| /admin/financeiro | AdminFinanceiro | administrador |
| /mentor | MentorDashboard | mentor |
| /mentor/aluno/:id | MentorAlunoDetalhe | mentor |

## Rotas a adicionar nas próximas voltas
- /mapa-lacunas (Volta 2)
- /admin/fontes (Volta 3)
- /admin/questoes (Volta 4)
- /admin/importar (Volta 4)
- /admin/reportes (Volta 3)
- /admin/configuracoes (Volta 3)
- /mapa-concursos (Volta 5)

