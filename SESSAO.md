# ConcursoAI — Arquivo de Sessão

> Leia só este arquivo no início de cada sessão.
> Consulte /docs apenas quando a tarefa em execução exigir.

## Projeto
Plataforma de estudos para concursos — **foco primário: Área Fiscal**.
Stack: FastAPI + SQLite(dev)/PostgreSQL(prod) + Celery(eager/sync) + Gemini/Anthropic.
Frontend: Streamlit. Deploy: Railway. Auth: JWT (roles: admin / aluno).

### Estado atual (2026-03-14)
- Onboarding pré-selecionado para fiscal (pula Tela 1, vai direto à Tela 2)
- Tela 6 do onboarding chama POST /onboarding → gera sessões reais no banco
- seed_topicos.py com pesos diferenciados por matéria (PESO_FISCAL)
- Agenda do Dia: tabela compacta com estrelas de relevância, KPIs, abas
- Timer de estudo (cronômetro JS client-side) no topo de todas as telas
- Sidebar com ícones + 8 itens de menu (incl. Erros Críticos e Meu Perfil)
- Header padronizado (page_title / page_header) em todas as telas
- `telas/components.py` com componentes reutilizáveis

### Fluxo funcional para testar
```
1. uvicorn app.main:app --reload
2. python -m app.scripts.seed_topicos
3. streamlit run app.py
4. Login → Onboarding (Tela 2 direto) → Tela 6 "N sessões geradas"
5. Agenda do Dia → tabela de sessões fiscais → concluir → % acerto
6. Desempenho → tabela por matéria com KPIs
```

## Arquivos de referência (ler só quando necessário)
```
docs/MODELS.md      → schema completo do banco
docs/ALGORITMO.md   → fórmula de priorização e pesos
docs/SESSOES.md     → lógica sessões multimodais D-14
docs/ONBOARDING.md  → fluxo UX-01 e calibração UX-02
docs/IA.md          → camada AIProvider e prompts
docs/PEDAG.md       → PEDAG-01, FSRS, diagnóstico de situação
docs/REGRAS.md      → decisões tomadas — não questionar
```

---

## Rotina de sessão — siga sempre esta ordem

### 0. Classificar a solicitação por camada

Antes de qualquer implementação, identificar a camada afetada (ver `CAMADAS.md`):

| Camada  | Arquivos principais                                         |
|---------|-------------------------------------------------------------|
| BD      | `database.py`, `app/models/`, `alembic/`                   |
| API     | `app/routers/`, `app/services/`, `app/schemas/`             |
| UI      | `telas/`, `app.py`                                          |
| CONFIG  | `config_*.py`, `.env`, `*.md`                               |
| INT     | `api_client.py`                                             |

**Alterar SOMENTE os arquivos da camada identificada.**
Se múltiplas camadas, avisar e aguardar confirmação.

---

### 1. Verificar progresso
```python
import json
with open('STATUS.json', encoding='utf-8') as f:
    s = json.load(f)
pendentes = [(i,t) for i,t in enumerate(s['tarefas']) if t['status'] != 'concluida']
print(f"Progresso: {s['concluidas']}/{s['total']} | {s['em_andamento']} em andamento")
prox_idx, prox = pendentes[0]
print(f"\nPróxima [{prox_idx}]: [{prox['fase']}] {prox['tarefa']}")
if prox['nota']: print(f"Nota: {prox['nota']}")
em_and = [t for _,t in pendentes if t['status']=='em_andamento']
if em_and:
    print("\nEm andamento:")
    for t in em_and: print(f"  [{t['fase']}] {t['tarefa'][:70]}")
```

### 2. Apresentar ao usuário
```
📋 Progresso: X/135 concluídas

⏭️ Próximo: [FASE] — [tarefa]
[nota se houver]

O que será feito: [2-3 linhas objetivas]

Deseja iniciar? [Sim / Não]
```
**Aguarde confirmação. Não escreva código antes.**

### 3. Implementar (só após confirmação)
- Marque como 🟡 em andamento no STATUS.json imediatamente
- Consulte o doc de referência em /docs se a tarefa exigir
- Ao concluir, avise:

```
✅ Feito
Criado/alterado: [lista de arquivos]
Para testar: [instruções diretas e objetivas]

⚠️ Me avise quando ok ou se precisar de ajustes.
```

### 4. Ciclo de ajustes
Implemente quantos ajustes o usuário pedir antes de confirmar o passo.

### 5. Quando usuário confirmar ok
```python
import json
with open('STATUS.json', encoding='utf-8') as f:
    s = json.load(f)
s['tarefas'][INDICE]['status'] = 'concluida'
s['concluidas'] += 1
s['em_andamento'] = max(0, s['em_andamento'] - 1)
with open('STATUS.json', 'w', encoding='utf-8') as f:
    json.dump(s, f, ensure_ascii=False, indent=2)
print("✅ STATUS.json atualizado")
```
Depois pergunte:
```
🎯 Registrado. Continuar ou encerrar? [Continuar / Encerrar]
```
- **Continuar** → volte ao passo 1
- **Encerrar** → resuma o que foi feito e encerre

---

## Regras
1. Nunca implemente sem confirmação do usuário
2. Nunca avance sem o usuário confirmar que testou
3. Nunca encerre sem atualizar o STATUS.json
4. deficit_min é campo privado — nunca exibir ao aluno
5. Se algo quebrar: avise claramente e aguarde — não corrija silenciosamente
