"""
app/services/gerar_plano_base.py — Geração de PlanoBase via IA.

A IA analisa as matérias do concurso e decide apenas a sequência pedagógica:
  - Quais matérias entram em cada fase
  - A ordem dos subtópicos dentro de cada matéria
  - Pré-requisitos entre matérias

Critérios de avanço, limiares de domínio e número de questões são FIXOS no
sistema e não são gerados pela IA.
"""
import json
import logging

from sqlalchemy.orm import Session

from app.core.ai_provider import AIProvider

logger = logging.getLogger("skolai.plano_base")


# ── Constantes pedagógicas fixas (NÃO vêm da IA) ─────────────────────────────
CRITERIOS_AVANCO = {
    "iniciante":     [65, 70, 75, 80],
    "intermediario": [70, 75, 80],
    "avancado":      [75, 80],
}

MAX_MATERIAS_FASE_1 = 4
MAX_MATERIAS_NOVAS_POR_FASE = 3

LIMIAR_DOMINIO_POR_COMPLEXIDADE = {
    "baixa": 0.70,
    "media": 0.75,
    "alta":  0.80,
}


# ── Descrições de contexto ────────────────────────────────────────────────────
_PERFIL_DESC = {
    "iniciante":     "nunca estudou para concursos ou tem menos de 3 meses de estudo",
    "intermediario": "tem entre 3 meses e 1 ano de estudo contínuo",
    "avancado":      "tem mais de 1 ano de estudo ou já foi aprovado em etapas anteriores",
}

_AREA_DESC = {
    "fiscal":    "concursos fiscais/tributários (Receita Federal, SEFAZ, Auditor Fiscal)",
    "eaof_com":  "EAOF área de Comunicações (Escola de Aeronáutica — BET/BEI/BCO)",
    "eaof_svm":  "EAOF área de Serviços de Manutenção (Escola de Aeronáutica)",
    "cfoe_com":  "CFOE área de Comunicações — nível oficial (BET/BEI/BCO)",
    "juridica":  "concursos jurídicos (MP, Defensoria, Advocacia, Tribunais)",
    "policial":  "concursos policiais e de segurança pública (PF, PC, PM, PRF)",
    "ti":        "concursos de Tecnologia da Informação",
    "saude":     "concursos da área de saúde",
    "outro":     "concursos gerais",
}


def _carregar_materias_com_subtopicos(area: str, db: Session) -> dict:
    """
    Retorna dict {materia_nome: [subtopico_nome, ...]} para a área.
    Traversa a hierarquia: subtopico (nivel=2) → bloco (nivel=1) → materia (nivel=0).
    """
    try:
        from app.models.subtopico_area import SubtopicoArea
        from app.models.topico import Topico

        configs = db.query(SubtopicoArea).filter(SubtopicoArea.area == area).all()
        if not configs:
            return {}

        result: dict[str, list[str]] = {}

        for cfg in configs:
            sub = db.query(Topico).filter(
                Topico.id == cfg.subtopico_id,
                Topico.nivel == 2,
                Topico.ativo == True,  # noqa: E712
            ).first()
            if not sub:
                continue

            # Sobe na hierarquia: sub → bloco (nivel=1) → materia (nivel=0)
            materia_nome = "Outros"
            if sub.parent_id:
                pai = db.query(Topico).filter(Topico.id == sub.parent_id).first()
                if pai:
                    if pai.nivel == 0:
                        materia_nome = pai.nome
                    elif pai.parent_id:
                        avo = db.query(Topico).filter(Topico.id == pai.parent_id).first()
                        if avo and avo.nivel == 0:
                            materia_nome = avo.nome

            result.setdefault(materia_nome, [])
            if sub.nome not in result[materia_nome]:
                result[materia_nome].append(sub.nome)

        return result
    except Exception:
        return {}


def _build_prompt(area: str, perfil: str, materias_subtopicos: dict) -> str:
    area_desc   = _AREA_DESC.get(area, area)
    perfil_desc = _PERFIL_DESC.get(perfil, perfil)

    if materias_subtopicos:
        materias_json = json.dumps(materias_subtopicos, ensure_ascii=False, indent=2)
        materias_section = (
            "MATÉRIAS DISPONÍVEIS (com seus subtópicos cadastrados):\n"
            f"{materias_json}\n\n"
        )
    else:
        materias_section = (
            "MATÉRIAS DISPONÍVEIS: liste as matérias típicas deste tipo de concurso "
            "e seus subtópicos habituais.\n\n"
        )

    exemplo = json.dumps({
        "fases": [
            {"numero": 1, "nome": "Fundação", "materias": ["Língua Portuguesa", "Raciocínio Lógico", "Matemática"]},
            {"numero": 2, "nome": "Base Jurídica", "materias_novas": ["Direito Constitucional", "Direito Administrativo"]},
            {"numero": 3, "nome": "Núcleo Fiscal", "materias_novas": ["Direito Tributário", "Contabilidade Geral"]},
        ],
        "ordem_subtopicos": {
            "Língua Portuguesa": ["Interpretação de Texto", "Ortografia", "Sintaxe", "Semântica"],
            "Direito Tributário": ["Conceito de Tributo", "Espécies Tributárias", "Obrigação Tributária", "Crédito Tributário"],
        },
        "prerequisitos": {
            "Contabilidade de Custos": ["Contabilidade Geral"],
            "Legislação Tributária": ["Direito Tributário"],
        },
    }, ensure_ascii=False, indent=2)

    return (
        "Você é um especialista em pedagogia de concursos públicos brasileiros.\n\n"
        "Analise as matérias do concurso abaixo e organize um plano de estudo progressivo.\n\n"
        f"ÁREA: {area_desc}\n"
        f"PERFIL DO ALUNO: {perfil} — {perfil_desc}\n\n"
        f"{materias_section}"
        "Retorne SOMENTE um JSON válido com esta estrutura exata, sem texto adicional:\n"
        f"{exemplo}\n\n"
        "REGRAS obrigatórias:\n"
        f"1. Fase 1: máximo {MAX_MATERIAS_FASE_1} matérias — as mais independentes e fundamentais\n"
        f"2. Fases seguintes: máximo {MAX_MATERIAS_NOVAS_POR_FASE} matérias novas por fase\n"
        "3. Respeitar dependências pedagógicas (ex: Contabilidade Geral antes de Auditoria, "
        "Direito Tributário antes de Legislação Tributária Específica)\n"
        "4. Matérias de baixa interdependência (Português, Inglês, Matemática, Informática) "
        "podem entrar cedo como 'respiro cognitivo'\n"
        "5. ordem_subtopicos: do mais básico/conceitual para o mais complexo/aplicado\n"
        "6. Listar TODOS os subtópicos de TODAS as matérias em ordem_subtopicos\n"
        "7. prerequisitos: apenas dependências diretas e necessárias\n"
        "8. NÃO inclua critérios de avanço, percentuais de acerto ou configurações "
        "pedagógicas — esses são fixos no sistema\n\n"
        "Resposta:"
    )


def _parse_resultado(raw: str) -> dict:
    """Parseia a resposta da IA e retorna {fases, ordem_subtopicos, prerequisitos}."""
    text = raw.strip()
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1] if len(parts) > 1 else text
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    parsed = None
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        inicio = text.find("{")
        fim = text.rfind("}") + 1
        if inicio != -1 and fim > 0:
            try:
                parsed = json.loads(text[inicio:fim])
            except json.JSONDecodeError:
                pass

    if parsed is None or not isinstance(parsed, dict):
        return {}

    fases_raw = parsed.get("fases", [])
    if not isinstance(fases_raw, list):
        return {}

    fases = []
    for item in fases_raw:
        if not isinstance(item, dict):
            continue
        if "numero" not in item or "nome" not in item:
            continue
        fases.append({
            "numero":        int(item["numero"]),
            "nome":          str(item["nome"]),
            "materias":      [str(m) for m in item.get("materias", [])],
            "materias_novas": [str(m) for m in item.get("materias_novas", [])],
        })

    if not fases:
        return {}

    return {
        "fases":             sorted(fases, key=lambda f: f["numero"]),
        "ordem_subtopicos":  parsed.get("ordem_subtopicos") or {},
        "prerequisitos":     parsed.get("prerequisitos") or {},
    }


def gerar_plano_via_ia(area: str, perfil: str, ai: AIProvider, db: Session = None) -> dict:
    """
    Retorna dict {fases, ordem_subtopicos, prerequisitos} gerado pela IA.
    Critérios de avanço são fixos no sistema (CRITERIOS_AVANCO) — não vêm da IA.
    Lança ValueError com mensagem descritiva em caso de falha.
    """
    materias_subtopicos: dict = {}
    if db is not None:
        materias_subtopicos = _carregar_materias_com_subtopicos(area, db)

    prompt = _build_prompt(area, perfil, materias_subtopicos)

    try:
        raw = ai.generate(prompt, max_tokens=4000)
    except Exception as exc:
        logger.error("Erro ao chamar IA para gerar plano area=%s perfil=%s: %s", area, perfil, exc)
        raise ValueError(f"Erro ao chamar IA: {exc}") from exc

    logger.debug("Resposta da IA para plano area=%s perfil=%s: %s", area, perfil, raw[:300])
    resultado = _parse_resultado(raw)
    if not resultado or not resultado.get("fases"):
        logger.error(
            "IA não retornou fases válidas. area=%s perfil=%s raw=%r",
            area, perfil, raw[:500],
        )
        raise ValueError(f"IA não retornou fases válidas. Resposta recebida: {raw[:300]!r}")
    return resultado
