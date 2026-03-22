"""
app/services/gerar_plano_base.py — Geração de PlanoBase via IA.

Opera sobre subtopico_ids (SubtopicoArea) — não mais nomes de matéria genéricos.
A IA recebe a lista de subtópicos com peso, complexidade e pré-requisitos e retorna
a ordem pedagógica respeitando:
  - Pré-requisitos entre subtópicos
  - Máx. 15-20 subtópicos na fase 1 (carga cognitiva)
  - Peso na área (subtópicos mais pesados com mais atenção)
  - Complexidade (baixa antes de alta)

Critérios de avanço padrão por perfil:
  - iniciante:     fase1=65% / fase2=70% / fase3=75% / fase4=80%
  - intermediario: fase1=70% / fase2=75% / fase3=80%
  - avancado:      fase1=75% / fase2=80%
"""
import json
import logging

from sqlalchemy.orm import Session

from app.core.ai_provider import AIProvider

logger = logging.getLogger("skolai.plano_base")


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

_CRITERIOS_AVANCO = {
    "iniciante":     [65, 70, 75, 80],
    "intermediario": [70, 75, 80],
    "avancado":      [75, 80],
}


def _build_prompt_subtopicos(area: str, perfil: str, subtopicos: list) -> str:
    """Constrói prompt com lista real de subtópicos para a área."""
    area_desc  = _AREA_DESC.get(area, area)
    perfil_desc = _PERFIL_DESC.get(perfil, perfil)
    criterios   = _CRITERIOS_AVANCO.get(perfil, [70, 75, 80])
    num_fases   = len(criterios)

    subs_desc = json.dumps(subtopicos, ensure_ascii=False, indent=2)

    return (
        "Você é um especialista em preparação para concursos públicos brasileiros.\n"
        f"Crie um plano de estudos estruturado em {num_fases} fases para a área: {area_desc}.\n"
        f"Perfil do candidato: {perfil_desc}.\n\n"
        "Abaixo está a lista de subtópicos disponíveis para esta área, com seus IDs, "
        "pesos no edital, complexidade (baixa/media/alta) e pré-requisitos:\n\n"
        f"{subs_desc}\n\n"
        "Regras obrigatórias:\n"
        "  1. Cada subtópico deve aparecer em EXATAMENTE UMA fase\n"
        "  2. Um subtópico só pode estar em uma fase posterior à de todos os seus pré-requisitos\n"
        f"  3. A fase 1 deve ter no máximo 20 subtópicos (carga cognitiva — Sweller)\n"
        "  4. Ordene dentro de cada fase: complexidade baixa antes de alta\n"
        "  5. Subtópicos com maior peso devem aparecer antes nas fases\n"
        f"  6. Critérios de avanço: fase 1={criterios[0]}%, fase 2={criterios[1] if len(criterios)>1 else criterios[0]}%"
        + (f", fase 3={criterios[2]}%" if len(criterios) > 2 else "")
        + (f", fase 4={criterios[3]}%" if len(criterios) > 3 else "") + "\n\n"
        "Formato de resposta — SOMENTE um array JSON válido, sem markdown, sem texto adicional:\n"
        '[{"numero":1,"nome":"Fundamentos","criterio_avanco":"65% de acertos","subtopicos":["id1","id2"],'
        '"subtopicos_novos":["id1","id2"]}]\n\n'
        "Resposta:"
    )


def _build_prompt_fallback(area: str, perfil: str) -> str:
    """Prompt fallback quando não há subtópicos cadastrados — usa matérias genéricas."""
    area_desc   = _AREA_DESC.get(area, area)
    perfil_desc = _PERFIL_DESC.get(perfil, perfil)

    return (
        "Você é um especialista em preparação para concursos públicos brasileiros.\n"
        f"Crie um plano de estudos estruturado em fases para a área: {area_desc}.\n"
        f"Perfil do candidato: {perfil_desc}.\n\n"
        "O plano deve ter entre 3 e 5 fases progressivas.\n"
        "Cada fase deve ter:\n"
        "  - numero (int, começando em 1)\n"
        "  - nome (string curto)\n"
        "  - criterio_avanco (string com % de acertos)\n"
        "  - materias (array de strings com nomes das disciplinas)\n"
        "  - subtopicos (array vazio [])\n"
        "  - subtopicos_novos (array vazio [])\n\n"
        "Retorne SOMENTE um array JSON válido, sem markdown:\n"
        '[{"numero":1,"nome":"Fundamentos","criterio_avanco":"65% de acertos",'
        '"materias":["Português","Matemática"],"subtopicos":[],"subtopicos_novos":[]}]\n\n'
        "Resposta:"
    )


def _parse_fases(raw: str) -> list:
    text = raw.strip()
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1] if len(parts) > 1 else text
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    # Tenta parse direto; se falhar, busca o array JSON no texto
    parsed = None
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        inicio = text.find("[")
        fim = text.rfind("]") + 1
        if inicio != -1 and fim > 0:
            try:
                parsed = json.loads(text[inicio:fim])
            except json.JSONDecodeError:
                pass

    if parsed is None or not isinstance(parsed, list):
        return []

    fases = []
    for item in parsed:
        if not isinstance(item, dict):
            continue
        if "numero" not in item or "nome" not in item:
            continue
        fases.append({
            "numero":          int(item["numero"]),
            "nome":            str(item["nome"]),
            "criterio_avanco": str(item.get("criterio_avanco", "")),
            "materias":        [str(m) for m in item.get("materias", [])],
            "subtopicos":      [str(s) for s in item.get("subtopicos", [])],
            "subtopicos_novos":[str(s) for s in item.get("subtopicos_novos", [])],
        })

    return sorted(fases, key=lambda f: f["numero"])


def _carregar_subtopicos_area(area: str, db: Session) -> list:
    """Busca SubtopicoArea para a área e monta lista para o prompt."""
    try:
        from app.models.subtopico_area import SubtopicoArea
        from app.models.topico import Topico

        configs = db.query(SubtopicoArea).filter(SubtopicoArea.area == area).all()
        if not configs:
            return []

        result = []
        for cfg in configs:
            sub = db.query(Topico).filter(Topico.id == cfg.subtopico_id, Topico.nivel == 2, Topico.ativo == True).first()
            if not sub:
                continue
            import json as _json
            prereqs = []
            try:
                prereqs = _json.loads(sub.prerequisitos_json or "[]")
            except Exception:
                pass
            result.append({
                "id":            sub.id,
                "nome":          sub.nome,
                "peso":          cfg.peso,
                "complexidade":  cfg.complexidade,
                "prerequisitos": prereqs,
            })
        return sorted(result, key=lambda s: -s["peso"])
    except Exception:
        return []


def gerar_plano_via_ia(area: str, perfil: str, ai: AIProvider, db: Session = None) -> list:
    """
    Retorna lista de fases gerada pela IA.
    Tenta usar subtopico_ids se db estiver disponível; caso contrário usa matérias genéricas.
    Lança ValueError com mensagem descritiva em caso de falha.
    """
    if db is not None:
        subtopicos = _carregar_subtopicos_area(area, db)
        if subtopicos:
            prompt = _build_prompt_subtopicos(area, perfil, subtopicos)
        else:
            prompt = _build_prompt_fallback(area, perfil)
    else:
        prompt = _build_prompt_fallback(area, perfil)

    try:
        raw = ai.generate(prompt, max_tokens=3000)
    except Exception as exc:
        logger.error("Erro ao chamar IA para gerar plano area=%s perfil=%s: %s", area, perfil, exc)
        raise ValueError(f"Erro ao chamar IA: {exc}") from exc

    logger.debug("Resposta da IA para plano area=%s perfil=%s: %s", area, perfil, raw[:300])
    fases = _parse_fases(raw)
    if not fases:
        logger.error("IA não retornou fases válidas. area=%s perfil=%s raw=%r", area, perfil, raw[:500])
        raise ValueError(f"IA não retornou fases válidas. Resposta recebida: {raw[:300]!r}")
    return fases
