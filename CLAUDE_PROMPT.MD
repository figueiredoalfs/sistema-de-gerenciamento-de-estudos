# Instruções para o Claude Code — Skolai

Antes de qualquer implementação, leia:
1. `AGORA.md` — planejamento completo, tasks, regras e infraestrutura
2. `SESSAO.md` — contexto da sessão atual

## Regras
- Siga estritamente a arquitetura e regras definidas no AGORA.md
- Não implemente funcionalidades fora da task atual
- Não refatore código existente sem necessidade
- Backend primeiro — testar no /docs antes de tocar no frontend
- Contrato quebrado → corrigir backend, nunca adaptar frontend
- Nunca chamar IA em loop automático — só por ação explícita do usuário
- Nunca usar gemini-2.5-flash — usar gemini-1.5-flash-8b ou gemini-1.5-flash
- Qualquer nova tabela ou coluna exige migration Alembic antes de usar

## Fluxo
1. Leia AGORA.md
2. Identifique a primeira task ⬜ PENDING na FASE-6
3. Implemente completamente — backend + frontend
4. Só conclua quando funcionar no navegador de ponta a ponta
5. Aguarde novas instruções antes de avançar para a próxima task
