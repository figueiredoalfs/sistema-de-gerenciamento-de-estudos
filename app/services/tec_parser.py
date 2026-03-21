"""
services/tec_parser.py
Parser de PDF do TEC Concursos — sem IA, sem custo.

IMPORTANTE: funciona apenas com PDFs gerados pelo botão "Imprimir"
do TEC Concursos (via navegador → Salvar como PDF).
NÃO funciona com PDFs gerados pelo "Print to PDF" do Windows.
"""

import io
import re
from typing import Optional

try:
    import pdfplumber
except ImportError:
    raise ImportError("pdfplumber não instalado. Execute: pip install pdfplumber")

_BANCAS = {
    'CEBRASPE': 'CEBRASPE (CESPE)',
    'CESPE': 'CEBRASPE (CESPE)',
    'FGV': 'FGV',
    'FCC': 'FCC',
    'VUNESP': 'VUNESP',
    'FUNDATEC': 'FUNDATEC',
    'AOCP': 'AOCP',
    'IDECAN': 'IDECAN',
    'IBFC': 'IBFC',
    'QUADRIX': 'QUADRIX',
    'IADES': 'IADES',
    'UPENET': 'UPENET',
}

_GABARITO_MAP = {
    'A': 'A', 'B': 'B', 'C': 'C', 'D': 'D', 'E': 'E',
    'CERTO': 'C', 'ERRADO': 'E',
    'CERTA': 'C', 'ERRADA': 'E',
}


def _extrair_texto(pdf_bytes: bytes) -> str:
    texto = ""
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                texto += t + "\n"
    return texto


def _normalizar_banca(cabecalho: str) -> Optional[str]:
    parte_banca = cabecalho.split(' - ')[0].strip().upper()
    for chave, nome in _BANCAS.items():
        if chave in parte_banca:
            return nome
    return cabecalho.split('(')[0].split(' - ')[0].strip() or None


def _extrair_ano(cabecalho: str) -> Optional[int]:
    m = re.search(r'/(\d{4})$', cabecalho.strip())
    return int(m.group(1)) if m else None


def _extrair_gabarito(texto: str) -> dict:
    gabarito_map = {}
    matches = re.findall(
        r'(\d+)\)\s*(A|B|C|D|E|Certo|Errado|CERTO|ERRADO)',
        texto,
        re.IGNORECASE,
    )
    for num, resp in matches:
        gabarito_map[int(num)] = _GABARITO_MAP.get(resp.strip().upper(), resp.upper())
    return gabarito_map


def parse_pdf_tec(pdf_bytes: bytes) -> dict:
    """
    Parseia um PDF do TEC Concursos.
    Retorna dict com: total, questoes[], sem_gabarito, erro
    """
    texto = _extrair_texto(pdf_bytes)

    if not texto.strip():
        return {
            "total": 0, "questoes": [], "sem_gabarito": 0,
            "erro": (
                "PDF sem texto extraível. "
                "Use o botão 'Imprimir' do TEC Concursos e salve como PDF pelo navegador. "
                "Não use 'Print to PDF' do Windows."
            ),
        }

    if 'tecconcursos.com.br/questoes/' not in texto:
        return {
            "total": 0, "questoes": [], "sem_gabarito": 0,
            "erro": "PDF não reconhecido como exportação do TEC Concursos.",
        }

    gabarito_map = _extrair_gabarito(texto)
    blocos = re.split(r'www\.tecconcursos\.com\.br/questoes/(\d+)', texto)

    questoes = []
    questao_num = 0
    i = 1

    while i < len(blocos) - 1:
        id_tec = blocos[i]
        conteudo = blocos[i + 1].strip()
        i += 2

        linhas = [l.strip() for l in conteudo.split('\n') if l.strip()]
        if len(linhas) < 3:
            continue

        cabecalho = linhas[0]
        banca = _normalizar_banca(cabecalho)
        ano = _extrair_ano(cabecalho)

        materia_linha = linhas[1] if len(linhas) > 1 else ""
        materia = ""
        subtopico = ""
        if ' - ' in materia_linha:
            partes = materia_linha.split(' - ', 1)
            materia = partes[0].strip()
            subtopico = partes[1].strip()
        else:
            materia = materia_linha.strip()

        questao_num += 1

        enunciado_inicio = 2
        for j, linha in enumerate(linhas[2:], start=2):
            if re.match(r'^\d+\)', linha):
                enunciado_inicio = j
                break

        linhas_enunciado = []
        alternativas = {}
        tipo = 'multipla_escolha'
        capturando_enunciado = True

        for linha in linhas[enunciado_inicio:]:
            if 'tecconcursos.com.br' in linha:
                break

            m_alt = re.match(r'^([a-e])\)\s*(.+)$', linha, re.IGNORECASE)
            if m_alt:
                capturando_enunciado = False
                alternativas[m_alt.group(1).upper()] = m_alt.group(2).strip()
                continue

            if re.match(r'^(Certo|Errado)$', linha, re.IGNORECASE):
                capturando_enunciado = False
                tipo = 'certo_errado'
                continue

            if capturando_enunciado:
                linha_limpa = re.sub(r'^\d+\)\s*', '', linha)
                if linha_limpa:
                    linhas_enunciado.append(linha_limpa)

        enunciado = ' '.join(linhas_enunciado).strip()
        if not enunciado:
            questao_num -= 1
            continue

        gabarito = gabarito_map.get(questao_num)

        questoes.append({
            'id_tec': id_tec,
            'materia': materia,
            'subject': subtopico,
            'board': banca,
            'year': ano,
            'tipo': tipo,
            'statement': enunciado,
            'alternatives': alternativas if alternativas else None,
            'correct_answer': gabarito,
        })

    sem_gabarito = sum(1 for q in questoes if not q['correct_answer'])
    return {
        'total': len(questoes),
        'questoes': questoes,
        'sem_gabarito': sem_gabarito,
        'erro': None,
    }


def extrair_texto_debug(pdf_bytes: bytes) -> str:
    """Retorna texto bruto extraído pelo pdfplumber (para debug)."""
    return _extrair_texto(pdf_bytes)
