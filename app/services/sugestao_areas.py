"""
app/services/sugestao_areas.py — Classificação de questões por área concursal via IA.

Segue o mesmo padrão de sugestao_subtopicos.py.
"""
import json
import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.ai_provider import AIProvider
from app.models.area import Area
from app.models.questao_banco import QuestaoBanco
from app.models.question_area import QuestionArea


def _build_prompt(questao: QuestaoBanco, areas: list[Area]) -> str:
    catalog_lines = [f'  {{"id": "{a.id}", "nome": "{a.nome}"}}' for a in areas]
    catalog = "[\n" + ",\n".join(catalog_lines) + "\n]"

    try:
        alts = json.loads(questao.alternatives_json)
        alts_text = "\n".join(f"  {k}) {v}" for k, v in alts.items())
    except Exception:
        alts_text = ""

    return (
        "Você é um classificador de questões para concursos públicos brasileiros.\n"
        "Analise a questão abaixo e identifique a quais áreas concursais ela pertence.\n"
        "Retorne SOMENTE um array JSON com os IDs das áreas relevantes do catálogo (máximo 3).\n"
        "Se nenhuma for relevante, retorne [].\n\n"
        f"DISCIPLINA: {questao.materia or questao.subject}\n"
        f"ASSUNTO: {questao.subject}\n\n"
        f"ENUNCIADO:\n{questao.statement}\n\n"
        + (f"ALTERNATIVAS:\n{alts_text}\n\n" if alts_text else "")
        + f"CATÁLOGO DE ÁREAS DISPONÍVEIS:\n{catalog}\n\n"
        "Resposta (apenas o array JSON, sem markdown, sem texto adicional):"
    )


def _parse_ids(raw: str, valid_ids: set) -> list[str]:
    text = raw.strip()
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

    return [str(item) for item in parsed if isinstance(item, str) and item in valid_ids][:3]


def sugerir_areas(
    questao: QuestaoBanco,
    areas_disponiveis: list[Area],
    ai: AIProvider,
) -> list[str]:
    """
    Retorna lista de IDs de áreas sugeridas pela IA para a questão.
    Nunca lança exceção — retorna [] em caso de falha.
    """
    if not areas_disponiveis:
        return []

    valid_ids = {str(a.id) for a in areas_disponiveis}
    prompt = _build_prompt(questao, areas_disponiveis)

    try:
        raw = ai.generate(prompt, max_tokens=512)
        return _parse_ids(raw, valid_ids)
    except Exception:
        return []


def salvar_sugestoes_areas(question_id: str, area_ids: list[str], db: Session) -> None:
    """
    Persiste as associações de área sugeridas pela IA com fonte='ia'.
    Ignora duplicatas silenciosamente.
    """
    for area_id in area_ids:
        try:
            with db.begin_nested():
                assoc = QuestionArea(
                    id=str(uuid.uuid4()),
                    question_id=question_id,
                    area_id=area_id,
                    fonte="ia",
                )
                db.add(assoc)
                db.flush()
        except IntegrityError:
            pass
