"""
app/services/gerar_plano_base.py — Geração de PlanoBase via IA.

Constrói um prompt descrevendo a área e o perfil do aluno e pede ao
modelo que retorne uma estrutura JSON com fases de estudo, critérios
de avanço e matérias por fase.
"""
import json

from app.core.ai_provider import AIProvider

_PERFIL_DESC = {
    "iniciante": "nunca estudou para concursos ou tem menos de 3 meses de estudo",
    "intermediario": "tem entre 3 meses e 1 ano de estudo contínuo",
    "avancado": "tem mais de 1 ano de estudo ou já foi aprovado em etapas anteriores",
}

_AREA_DESC = {
    "fiscal": "concursos fiscais / tributários (Receita Federal, SEFAZ, Auditor Fiscal)",
    "juridica": "concursos jurídicos (MP, Defensoria, Advocacia, Tribunais)",
    "policial": "concursos policiais e de segurança pública (PF, PC, PM, PRF)",
    "ti": "concursos de Tecnologia da Informação (ANAC, BACEN, TCU)",
    "saude": "concursos da área de saúde (ANVISA, ANS)",
    "outro": "concursos gerais",
}


def _build_prompt(area: str, perfil: str) -> str:
    area_desc = _AREA_DESC.get(area, area)
    perfil_desc = _PERFIL_DESC.get(perfil, perfil)

    return (
        "Você é um especialista em preparação para concursos públicos brasileiros.\n"
        f"Crie um plano de estudos estruturado em fases para a área: {area_desc}.\n"
        f"Perfil do candidato: {perfil_desc}.\n\n"
        "O plano deve ter entre 3 e 5 fases progressivas.\n"
        "Cada fase deve ter:\n"
        "  - numero (int, começando em 1)\n"
        "  - nome (string curto, ex: 'Fundamentos')\n"
        "  - criterio_avanco (string descrevendo o critério, ex: '70% de acertos nas matérias da fase')\n"
        "  - materias (array de strings com os nomes das disciplinas)\n\n"
        "Retorne SOMENTE um array JSON válido com as fases, sem markdown, sem texto adicional.\n"
        "Exemplo de formato:\n"
        '[{"numero":1,"nome":"Fundamentos","criterio_avanco":"70% de acertos","materias":["Português","Matemática"]}]\n\n'
        "Resposta:"
    )


def _parse_fases(raw: str) -> list:
    text = raw.strip()

    # Remove markdown code fences
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1] if len(parts) > 1 else text
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return []

    if not isinstance(parsed, list):
        return []

    fases = []
    for item in parsed:
        if not isinstance(item, dict):
            continue
        if not all(k in item for k in ("numero", "nome", "criterio_avanco", "materias")):
            continue
        fases.append({
            "numero": int(item["numero"]),
            "nome": str(item["nome"]),
            "criterio_avanco": str(item["criterio_avanco"]),
            "materias": [str(m) for m in item.get("materias", [])],
        })

    return sorted(fases, key=lambda f: f["numero"])


def gerar_plano_via_ia(area: str, perfil: str, ai: AIProvider) -> list:
    """
    Retorna lista de fases gerada pela IA.
    Nunca lança exceção — retorna [] em caso de falha.
    """
    try:
        prompt = _build_prompt(area, perfil)
        raw = ai.generate(prompt, max_tokens=2048)
        return _parse_fases(raw)
    except Exception:
        return []
