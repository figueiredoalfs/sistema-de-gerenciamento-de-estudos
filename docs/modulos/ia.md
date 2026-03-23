# Módulo: IA

## Propósito
Abstrai o provedor de IA (Gemini / Anthropic) atrás de uma interface comum. O modelo ativo é configurado dinamicamente via banco de dados (tabela de configurações admin). Usado para geração de explicações, planos de estudo, conteúdo e classificação de questões.

## Arquivos principais
- `app/core/ai_provider.py` — `AIProvider` (abstract), `GeminiProvider`, `StubProvider`
- `app/routers/admin_config.py` — configura modelo ativo
- `app/routers/explicacoes.py` — gera explicações de questões
- `app/routers/task_conteudo.py` — gera conteúdo de tasks (vídeos, PDF)
- `app/routers/conhecimento.py` — base de conhecimento IA

## Arquitetura
```python
class AIProvider(ABC):
    def generate(self, prompt: str, **kwargs) -> str: ...

class GeminiProvider(AIProvider):
    # usa google-generativeai
    # modelo configurável: gemini-1.5-flash, gemini-1.5-pro, gemini-2.0-flash, …

class StubProvider(AIProvider):
    # retorna mensagem de erro amigável quando GEMINI_API_KEY não definida
```

### Seleção dinâmica de modelo
```python
# ai_provider.py:
def get_provider(db: Session) -> AIProvider:
    config = db.query(Config).filter(Config.chave == "modelo_ia").first()
    model = config.valor if config else "gemini-1.5-flash"
    return GeminiProvider(model=model)
```

## Dependências externas
- `google-generativeai` — SDK Gemini
- `anthropic` — SDK Anthropic (se usado)
- Env vars: `GEMINI_API_KEY`, `ANTHROPIC_API_KEY`
- Tabela `configs` (chave `modelo_ia`) — modelo ativo

## Regras de negócio críticas
- Se `GEMINI_API_KEY` vazia → `StubProvider` — não quebra a app, retorna erro legível
- Modelo é lido do banco a cada request (não cacheado) — mudança admin tem efeito imediato
- Prompts são definidos nos routers que usam IA — não centralizado em `ai_provider.py`
- Timeout padrão: 30s para geração de conteúdo; 600s para importação

## Pontos de atenção
- Trocar de Gemini para Anthropic exige nova implementação de `AnthropicProvider(AIProvider)`
- Rate limits e quotas do Gemini são externos — erros de quota chegam como exceção no `generate()`
- Não logar prompts completos em produção (podem conter conteúdo sensível do aluno)
- Modelos disponíveis listados em `GET /admin/config/modelos-ia` — lista hardcoded no router
