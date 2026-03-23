# Módulo: Frontend

## Propósito
SPA React 18 + Vite + Tailwind servido por Caddy em produção. Consome a API FastAPI via Axios com interceptor de refresh token automático. Em dev, usa proxy Vite para evitar CORS.

## Arquivos principais
- `frontend/src/api/client.js` — instância Axios centralizada + interceptors
- `frontend/src/context/AuthContext.jsx` — estado global de autenticação
- `frontend/src/App.jsx` — definição de rotas (React Router v6)
- `frontend/src/api/*.js` — módulos de API por domínio
- `frontend/src/pages/*.jsx` — páginas
- `frontend/src/components/` — componentes reutilizáveis
- `frontend/vite.config.js` — proxy de dev + configuração de build
- `frontend/Dockerfile` — build multi-stage (Node → Caddy)
- `frontend/Caddyfile` — servidor de produção (SPA routing + gzip)

## Roteamento (App.jsx)
```
/login              → Login (público)
/onboarding         → Onboarding (OnboardingGuard)
/                   → Dashboard (ProtectedRoute)
/desempenho         → Desempenho (ProtectedRoute)
/lancar-bateria     → LancarBateria (ProtectedRoute)
/tarefa/:taskId     → TaskView (ProtectedRoute)
/mentor/alunos      → MentorAlunos (requireMentor)
/admin              → AdminDashboard (requireAdmin)
/admin/questoes     → AdminQuestoes (requireAdmin)
/admin/importar     → AdminImportar (requireAdmin)
/admin/topicos      → AdminTopicos (requireAdmin)
/admin/usuarios     → AdminUsuarios (requireAdmin)
/admin/planos-base  → AdminPlanoBase (requireAdmin)
/admin/pendencias   → AdminPendencias (requireAdmin)
/admin/config       → AdminConfig (requireAdmin)
*                   → Navigate to /
```

## Fluxo de autenticação
```
Login → AuthContext.login(email, senha)
  → api/auth.js:login() → POST /auth/login (form-urlencoded)
  → {access_token, refresh_token, role, nome}
  → localStorage.setItem('token', ...) + localStorage.setItem('refresh_token', ...)
  → AuthContext.user = {role, nome, area}

401 em qualquer request:
  → client.js interceptor tenta POST /auth/refresh
  → sucesso: retenta request original com novo token
  → falha: limpa localStorage → redireciona /login
```

## Configuração de API (dev vs prod)
```javascript
// client.js:
baseURL: import.meta.env.VITE_API_URL || '/'
// Dev:  VITE_API_URL vazio → usa proxy Vite (localhost:8000)
// Prod: VITE_API_URL = https://www.skolai.com.br (baked no build)
```

### Proxy de dev (vite.config.js)
Todos os prefixos de rota da API são proxiados para `http://localhost:8000`:
`/auth`, `/tasks`, `/metas`, `/onboarding`, `/desempenho`, `/bateria`, `/baterias`,
`/topicos`, `/questoes`, `/admin`, `/task-conteudo`, `/task-videos`, `/dev`

## Dependências externas
- `axios` — cliente HTTP
- `react-router-dom` v6 — roteamento
- `recharts` — gráficos de desempenho
- `tailwindcss` — estilização
- Env var de build: `VITE_API_URL`

## Regras de negócio críticas
- **`VITE_API_URL` é baked no build** — mudar a var exige redeploy do frontend
- Toda chamada de API passa por `client.js` — nunca usar `fetch` ou `axios` direto nas páginas
- Guards de rota (`ProtectedRoute`, `requireAdmin`, `requireMentor`) são client-side — o backend também valida via JWT
- `user.area == null` → guard força `/onboarding` — não remover essa lógica

## Pontos de atenção
- Ao adicionar nova rota de API no backend, adicionar o prefixo no proxy do `vite.config.js` para funcionar em dev
- `localStorage` para tokens — não usar cookies httpOnly (decisão arquitetural atual)
- Timeout padrão 10s no client; exceções: importação (600s), PDF (30s)
- Build de produção: `npm run build` → `/dist` copiado para `/srv` no Caddy
- Caddy: `try_files {path} /index.html` garante SPA routing (não quebrar isso no Caddyfile)
