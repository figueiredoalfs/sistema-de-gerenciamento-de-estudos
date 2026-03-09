"""
config_app.py
─────────────────────────────────────────────────────────────────────────────
Configuracao central de identidade da plataforma.

Para trocar nome, logo ou autor no futuro, edite APENAS este arquivo.
Todo o app.py, sidebar e telas usam estas constantes.
─────────────────────────────────────────────────────────────────────────────
"""

# ── Identidade do produto ─────────────────────────────────────────────────────
APP_NAME    = "AprovAI"               # Nome exibido na sidebar, title e login
APP_SLOGAN  = "Gestao Inteligente de Concursos"
APP_AUTHOR  = "Alfredo Figueiredo"    # Exibido abaixo da logo na sidebar

# ── Arquivos de midia ─────────────────────────────────────────────────────────
LOGO_FILE   = "logo.png"              # Caminho relativo ao app.py

# ── Confirmação de e-mail ─────────────────────────────────────────────────────
# False em desenvolvimento local (SQLite).
# Para ativar no Railway: adicionar variável de ambiente EMAIL_CONFIRMACAO=true
import os as _os
EMAIL_CONFIRMACAO_ATIVO: bool = _os.getenv("EMAIL_CONFIRMACAO", "false").lower() == "true"

# ── Configuracoes de tema (nao alterar sem revisao do style.py) ───────────────
THEME_PRIMARY   = "#00b4a6"   # teal — destaque, botoes, borda ativa
THEME_DARK      = "#0d1b2a"   # azul escuro — sidebar, titulos
THEME_BG        = "#111e2b"   # fundo principal (dark)
THEME_CARD      = "#19293a"   # fundo de cards / metricas (dark)
THEME_TEXT      = "#d0e4f0"   # texto geral no tema escuro
