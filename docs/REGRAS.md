# Decisões tomadas — não questionar

## Arquitetura
- Frontend: React 18 + Vite + Tailwind. Streamlit: deletar completamente.
- Backend: FastAPI + SQLAlchemy. SQLite em dev, PostgreSQL no Railway.
- IA: Gemini Flash via ai_provider.py. Trocar via ConfigSistema sem redeploy.
- Auth: JWT. Roles: administrador / mentor / estudante.

## Produto
- Banco de questões vazio → FASE-0 é o desbloqueador de tudo
- Questões importadas via JSON/CSV pelo admin (IA externa converte PDF)
- StudyTask é o sistema ativo. Sessao/priorizacao.py são legado.
- Contrato quebrado → corrigir backend, nunca adaptar frontend
- Streamlit: não criar nada novo. Deletar na FASE-5.

## Engine pedagógica
- Meta = contêiner de tasks semanais (não calendário)
- tasks_meta = horas_por_dia × dias_por_semana
- Tipos: diagnostico→teoria→questionario→revisao→reforco
- Limiares: 1 exposure=60% / 2=70% / 3+=80% / domínio=85%
- Sem questões no banco: tasks geradas com questoes_json=null

## Deploy
- CORS: allow_origins=["*"] ok em dev, restringir antes do deploy
- Fix Railway obrigatório: DATABASE_URL.replace('postgres://', 'postgresql://')
- SECRET_KEY: ler do ambiente, levanta erro se não definido
