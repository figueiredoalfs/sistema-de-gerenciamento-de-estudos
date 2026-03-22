# Estado Atual do Deploy — Skolai

Última atualização: 2026-03-22

---

## Infraestrutura Railway

### Serviços ativos
| Serviço  | URL                       | Status  |
|----------|---------------------------|---------|
| Backend  | (domínio Railway interno) | Online  |
| Frontend | www.skolai.com.br         | Online  |

### Variáveis de ambiente — Backend
- `DATABASE_URL` — PostgreSQL Railway (gerado automaticamente)
- `SECRET_KEY` — chave JWT
- `GEMINI_API_KEY` — acesso à API Gemini
- `ALLOWED_ORIGINS` — deve conter a URL do frontend (`https://www.skolai.com.br`)
- `ADMIN_EMAIL`, `ADMIN_NOME`, `ADMIN_SENHA` — conta admin inicial

### Variáveis de ambiente — Frontend
- `VITE_API_URL` — URL pública do backend (baked no bundle em build time)
- `PORT = 80` — porta que o Caddy escuta; obrigatório para Railway rotear corretamente

---

## Arquivos críticos do deploy — NÃO alterar sem necessidade

### `frontend/Dockerfile`
Build em dois estágios: `node:18-alpine` para build, `caddy:2-alpine` para servir.

**Por que não usar nixpacks:** o nixpacks bake `NODE_ENV=production` como instrução `ENV` no Dockerfile gerado, fazendo o `npm ci` pular devDependencies. Nenhuma configuração de variável Railway ou `nixpacks.toml` consegue sobrescrever isso. O Dockerfile customizado resolve completamente.

```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM caddy:2-alpine
COPY --from=builder /app/dist /srv
COPY Caddyfile /etc/caddy/Caddyfile
```

### `frontend/.dockerignore`
```
node_modules
dist
.env
```

**Por que é crítico:** sem esse arquivo, o `COPY . .` copia a pasta `node_modules` local (gerada no Windows) para dentro da imagem Docker. Binários Windows não têm bits de execução Unix — o `vite` retorna "Permission denied" (exit code 126) e o build falha.

### `frontend/Caddyfile`
```
:{$PORT:80}

root * /srv
encode gzip
try_files {path} /index.html
file_server
```

`try_files {path} /index.html` é obrigatório para o React Router funcionar: sem ele, qualquer rota diferente de `/` retorna 404 ao recarregar a página.

### `frontend/railway.toml`
```toml
[build]
builder = "dockerfile"
dockerfilePath = "Dockerfile"

[deploy]
restartPolicyType = "on_failure"
```

`builder = "dockerfile"` força o Railway a usar o Dockerfile customizado em vez do nixpacks.

### `frontend/package.json` — dependências de build em `dependencies`
As ferramentas de build (`vite`, `@vitejs/plugin-react`, `autoprefixer`, `postcss`, `tailwindcss`) estão em `dependencies`, não em `devDependencies`. Isso foi necessário durante o processo de debug do nixpacks e mantido por segurança.

---

## Domínio customizado

- Domínio: `www.skolai.com.br`
- Configurado em Railway → Frontend → Settings → Domains
- DNS: registro CNAME `www` apontando para o domínio `.up.railway.app` do serviço
- Porta informada no Railway ao gerar o domínio: `80`

---

## O que NÃO fazer

- Não voltar para nixpacks (`builder = "nixpacks"`) — vai quebrar o build por causa do NODE_ENV=production
- Não deletar `.dockerignore` do frontend — vai quebrar o build com "Permission denied"
- Não remover `PORT = 80` das variáveis do frontend no Railway — o Caddy não vai conseguir subir na porta certa
- Não mover `vite` e ferramentas de build de volta para `devDependencies` sem testar em ambiente Docker limpo
- Não alterar o `Caddyfile` removendo `try_files` — vai quebrar o React Router em refresh de página
