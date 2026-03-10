"""
services/decay.py
Determina o fator de esquecimento (λ) por categoria de matéria.

Lógica:
  Legislação (Direito*, Legislação*, Tributário, SUS...) → λ = 0.03  (decai lento — memorização)
  Raciocínio Lógico                                       → λ = 0.08  (decai rápido — raciocínio)
  Demais                                                  → λ = 0.05  (padrão)

λ individual por aluno/tópico virá do FSRS na F-06.
"""

# Palavras-chave que identificam matérias de legislação (decay lento)
_KEYWORDS_LEGISLACAO = (
    "direito",
    "legislaç",
    "tributár",
    "constitucional",
    "administrativ",
    "penal",
    "processual",
    "civil",
    "trabalhista",
    "previdenciári",
    "sus",
    "lei ",
    "norma",
    "estatuto",
    "regimento",
    "código",
    "codigo",
)

_KEYWORD_RL = "raciocínio lógico"


def get_decay_rate(nome_materia: str) -> float:
    """
    Retorna λ (decay rate) para a matéria informada.

    Args:
        nome_materia: nome da matéria ou tópico (case-insensitive)

    Returns:
        0.03 para Legislação, 0.08 para Raciocínio Lógico, 0.05 para demais
    """
    nome_lower = nome_materia.lower().strip()

    if _KEYWORD_RL in nome_lower or "raciocinio logico" in nome_lower:
        return 0.08

    for kw in _KEYWORDS_LEGISLACAO:
        if kw in nome_lower:
            return 0.03

    return 0.05


# Mapeamento direto para as matérias padrão (usado no seed/migração)
DECAY_POR_MATERIA: dict[str, float] = {
    # Raciocínio / Matemática (decai rápido)
    "Raciocínio Lógico":        0.08,
    "Matemática":               0.08,
    "Matemática Financeira":    0.08,

    # Legislação / Direito (decai lento)
    "Direito Constitucional":   0.03,
    "Direito Administrativo":   0.03,
    "Direito Penal":            0.03,
    "Direito Processual Penal": 0.03,
    "Direito Civil":            0.03,
    "Direito Processual Civil": 0.03,
    "Direito Tributário":       0.03,
    "Legislação do SUS":        0.03,
    "Legislação Específica":    0.03,

    # Demais (padrão)
    "Português":                0.05,
    "Contabilidade":            0.05,
    "Administração":            0.05,
    "Informática":              0.05,
    "Segurança da Informação":  0.05,
    "Redes de Computadores":    0.05,
    "Banco de Dados":           0.05,
    "Governança de TI":         0.05,
    "Saúde Pública":            0.05,
    "Atualidades":              0.05,
}
