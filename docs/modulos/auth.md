# Módulo: Auth

## Propósito
Gerencia autenticação JWT (login, register, refresh token, me, alterar senha) e controle de acesso por roles. Inclui rate limiting por IP e seed do admin.

## Arquivos principais
- `app/routers/auth.py` — endpoints públicos e autenticados
- `app/core/security.py` — JWT, hashing, rate limit, guards de role
- `app/scripts/seed_admin.py` — cria admin idempotente na startup
- `app/schemas/auth.py` — schemas Pydantic (AlunoCreate, AlunoResponse, TokenResponse…)
- `app/models/aluno.py` — model de usuário

## Fluxo de dados

### Login
```
POST /auth/login (form-urlencoded: username, password)
  → check_login_rate_limit(ip)           # 5 tentativas / 60s por IP
  → query Aluno por email + ativo=True
  → verify_password(password, senha_hash)
  → create_access_token + create_refresh_token
  → retorna TokenResponse {access_token, refresh_token, role, nome}
```

### Register
```
POST /auth/register (JSON: nome, email, password, role)
  → verifica email duplicado
  → Aluno(senha_hash=hash_password(...))
  → retorna AlunoResponse
```

### Refresh
```
POST /auth/refresh (JSON: refresh_token)
  → verify_refresh_token → payload {sub, role}
  → query Aluno ativo
  → emite novos access + refresh tokens
```

### Guards de role
```python
# Em qualquer router:
current_user: Aluno = Depends(get_current_user)          # qualquer auth
current_user: Aluno = Depends(require_admin)              # só administrador
current_user: Aluno = Depends(require_admin_or_mentor)    # admin + mentor
```

## Dependências externas
- `python-jose` — JWT
- `passlib[bcrypt]` — hashing de senha
- `Aluno` model (tabela `alunos`)

## Regras de negócio críticas
- **Rate limit**: 5 tentativas de login por IP por 60 segundos (in-memory dict — reinicia com o processo)
- **Token expiry**: `ACCESS_TOKEN_EXPIRE_MINUTES` (padrão 60 min), `REFRESH_TOKEN_EXPIRE_DAYS` (30 dias)
- **Roles válidos**: `administrador`, `mentor`, `estudante`
- `Aluno.ativo = False` → login bloqueado mesmo com senha correta
- O `role` é embutido no JWT — mudança de role no banco exige novo login

## Pontos de atenção
- `seed_admin.py`: busca admin por `ADMIN_EMAIL`, cria se não existir usando `ADMIN_SENHA`. Não atualiza senha se admin já existe — a senha vem do hash gravado no banco.
- Para resetar senha do admin em produção: alterar diretamente no banco ou via `/auth/alterar-senha` autenticado.
- Rate limit é in-memory: reinicia com cada deploy/restart.
- `SECRET_KEY` default `troque-em-producao` levanta `RuntimeError` em produção (banco não-SQLite).
