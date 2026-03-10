"""
config_fontes.py
─────────────────────────────────────────────────────────────────────────────
Grupos canônicos de fonte de questões.

  - GRUPOS_FONTE     : definição completa (slug → label + peso + ícone)
  - GRUPOS_FIXOS     : sempre aparecem na lista de fontes do lançamento
  - GRUPOS_OPCIONAIS : tipos de plataforma que o usuário ativa no perfil/onboarding

Os slugs são armazenados no campo `fonte` da tabela `lancamentos`.
Os pesos são usados pelo algoritmo de priorização (CONTEXTO.md).
─────────────────────────────────────────────────────────────────────────────
"""

from collections import OrderedDict

GRUPOS_FONTE: OrderedDict = OrderedDict([
    # ── Sempre disponíveis no selectbox de lançamento ─────────────────────
    ("prova_mesma_banca", {
        "label":     "Prova Original — mesma banca",
        "peso":      1.5,
        "fixo":      True,
        "icon":      "🏆",
        "descricao": "Questões de provas da mesma banca do seu concurso",
    }),
    ("prova_outra_banca", {
        "label":     "Prova Original — outra banca",
        "peso":      1.2,
        "fixo":      True,
        "icon":      "📋",
        "descricao": "Questões de provas de bancas diferentes",
    }),
    ("simulado", {
        "label":     "Simulado",
        "peso":      1.0,
        "fixo":      True,
        "icon":      "⏱️",
        "descricao": "Prova simulada cronometrada",
    }),
    # ── Ativados pelo usuário no perfil (tipos de plataforma) ─────────────
    ("banco_questoes", {
        "label":     "Banco de Questões",
        "peso":      1.0,
        "fixo":      False,
        "icon":      "📚",
        "descricao": "TEC, Qconcursos, Gran, Direção Concursos...",
    }),
    ("curso_online", {
        "label":     "Curso Online",
        "peso":      0.6,
        "fixo":      False,
        "icon":      "🎓",
        "descricao": "Estratégia, Grancursos, Cers, Alfacon, Damásio...",
    }),
    ("mentoria", {
        "label":     "Mentoria",
        "peso":      1.2,
        "fixo":      False,
        "icon":      "👨‍🏫",
        "descricao": "Mentores, aulas particulares, grupos de estudo...",
    }),
    ("material_proprio", {
        "label":     "Material Próprio",
        "peso":      0.8,
        "fixo":      False,
        "icon":      "📖",
        "descricao": "Apostilas, PDFs, resumos, livros...",
    }),
])

# Slugs que sempre aparecem no selectbox de lançamento
GRUPOS_FIXOS = [k for k, v in GRUPOS_FONTE.items() if v["fixo"]]

# Slugs que o usuário pode ativar no perfil/onboarding
GRUPOS_OPCIONAIS = [k for k, v in GRUPOS_FONTE.items() if not v["fixo"]]

# Padrão para novos usuários
PLATAFORMAS_DEFAULT = ["banco_questoes"]


def get_label(slug: str) -> str:
    """Retorna o label legível de um slug. Fallback: o próprio slug."""
    return GRUPOS_FONTE.get(slug, {}).get("label", slug)


def get_peso(slug: str) -> float:
    """Retorna o peso do grupo para o algoritmo de priorização."""
    return GRUPOS_FONTE.get(slug, {}).get("peso", 1.0)


def fontes_disponiveis(plataformas_ativas: list) -> list:
    """
    Retorna lista de (slug, label) para o selectbox de Lançar Bateria.
    Inclui sempre os GRUPOS_FIXOS + os grupos que o usuário ativou.
    """
    slugs = GRUPOS_FIXOS + [
        g for g in plataformas_ativas
        if g in GRUPOS_FONTE and not GRUPOS_FONTE[g]["fixo"]
    ]
    return [(s, GRUPOS_FONTE[s]["label"]) for s in slugs]
