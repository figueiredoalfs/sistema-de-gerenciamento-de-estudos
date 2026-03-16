# SESSAO.md — Skolai

> Leia este arquivo no início de cada sessão.
> Se AGORA.md existir, leia também — tem prioridade sobre o STATUS.json.

## Projeto
Plataforma de estudos para concursos públicos.
Backend: FastAPI + SQLAlchemy + SQLite(dev)/PostgreSQL(prod) + Gemini Flash.
Frontend: React 18 + Vite + Tailwind + React Router v6.
**Streamlit: abandonado. Tudo em React.**

## Arquivos de referência (ler só quando a task exigir)
```
AGORA.md         ← planejamento completo + task list
STATUS.json      ← progresso das tasks
docs/MODELS.md   ← schema do banco
docs/ALGORITMO.md← engine pedagógica
docs/IA.md       ← camada de IA
docs/REGRAS.md   ← decisões fixas
```

---

## Rotina de sessão

### 1. Verificar progresso
```python
import json
with open('STATUS.json', encoding='utf-8') as f:
    s = json.load(f)
pendentes = [(i,t) for i,t in enumerate(s['tarefas']) if t['status'] != 'concluida']
print(f"Progresso: {s['concluidas']}/{s['total']}")
prox_idx, prox = pendentes[0]
print(f"Próxima [{prox_idx}]: [{prox['fase']}] {prox['tarefa']}")
if prox['nota']: print(f"Nota: {prox['nota']}")
em_and = [t for _,t in pendentes if t['status']=='em_andamento']
if em_and:
    print("Em andamento:")
    for t in em_and: print(f"  [{t['fase']}] {t['tarefa'][:70]}")
```

### 2. Apresentar ao usuário
```
📋 Progresso: X/Y
⏭️ [FASE] — [tarefa]
[nota se houver]

O que será feito: [2-3 linhas objetivas]
Deseja iniciar? [Sim / Não]
```
**Aguarde confirmação. Não escreva código antes.**

### 3. Implementar (só após confirmação)
- Marque como em_andamento no STATUS.json
- Consulte AGORA.md para contexto da task
- Consulte /docs se precisar de detalhe técnico
- Ao concluir:
```
✅ Feito
Criado/alterado: [arquivos]
Para testar: [instruções diretas]
⚠️ Me avise quando ok ou se precisar de ajustes.
```

### 4. Quando usuário confirmar ok
```python
import json
with open('STATUS.json', encoding='utf-8') as f:
    s = json.load(f)
s['tarefas'][INDICE]['status'] = 'concluida'
s['concluidas'] += 1
s['em_andamento'] = max(0, s['em_andamento'] - 1)
with open('STATUS.json', 'w', encoding='utf-8') as f:
    json.dump(s, f, ensure_ascii=False, indent=2)
```
Depois:
```
🎯 Registrado. Continuar ou encerrar? [Continuar / Encerrar]
```

---

## Regras
1. Nunca implemente sem confirmação
2. Nunca avance sem o usuário confirmar que testou
3. Nunca encerre sem atualizar STATUS.json
4. Contrato quebrado → corrigir backend, nunca adaptar frontend
5. Streamlit: deletar. Não criar nada novo em Streamlit.
6. Se algo quebrar: avise e aguarde, não corrija silenciosamente
