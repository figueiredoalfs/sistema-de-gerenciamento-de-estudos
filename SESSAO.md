# ConcursoAI — Arquivo de Sessão

> Leia só este arquivo no início de cada sessão.
> Se AGORA.md existir na pasta, leia também — ele tem prioridade sobre o STATUS.json.
> Consulte /docs apenas quando a tarefa em execução exigir.

## Projeto
Plataforma de estudos para concursos públicos com IA.
Stack: FastAPI + SQLite(dev)/PostgreSQL(prod) + Celery/Redis + Gemini/Anthropic.
Frontend: Streamlit. Deploy: Railway. Auth: JWT (roles: admin / aluno).

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
