"""
pg_dashboard.py
Painel de desempenho com tabela estilizada e colunas de tendencia, status e prioridade.
"""

import streamlit as st
import pandas as pd
from database import ler_lancamentos, ler_erros
from api_client import api_obter_desempenho

# ── Paleta de desempenho (limites: >85 / 75-85 / 65-75 / <65) ─────────────────
def _perc_color(perc: float) -> str:
    if perc > 85:
        return "#4ade80"   # verde claro
    elif perc >= 75:
        return "#27ae60"   # verde escuro
    elif perc >= 65:
        return "#f39c12"   # laranja
    else:
        return "#e74c3c"   # vermelho


def _status(perc: float):
    """Icone e texto de status baseado no % acerto."""
    if perc > 85:
        return "#4ade80", "&#9679;", "Dominando"
    elif perc >= 75:
        return "#27ae60", "&#9679;", "Meta"
    elif perc >= 65:
        return "#f39c12", "&#9679;", "Atencao"
    else:
        return "#e74c3c", "&#9679;", "Critico"


def _prioridade(perc: float):
    """Rotulo de prioridade baseado no % acerto."""
    if perc > 85:
        return "#4ade80", "&#9989;", "Dominando o Assunto"
    elif perc >= 75:
        return "#27ae60", "&#128218;", "Zona de Classificacao"
    elif perc >= 65:
        return "#f39c12", "&#128203;", "Moderada"
    else:
        return "#e74c3c", "&#128680;", "URGENTE"


def _tendencia(df_all: pd.DataFrame, materia: str):
    """Compara o ultimo mes disponivel vs o penultimo para a materia."""
    df_m = df_all[df_all["Materia"] == materia].copy()
    if df_m.empty:
        return "&rarr;", "Estavel", "#7a9ab8"
    df_m["_dt"] = pd.to_datetime(df_m["Data"], dayfirst=True, errors="coerce")
    df_m["_mes"] = df_m["_dt"].dt.to_period("M")
    meses = sorted(df_m["_mes"].dropna().unique())
    if len(meses) < 2:
        return "&rarr;", "Estavel", "#7a9ab8"
    ult = df_m[df_m["_mes"] == meses[-1]]
    pen = df_m[df_m["_mes"] == meses[-2]]
    p1 = ult["Acertos"].sum() / ult["Total"].sum() * 100 if ult["Total"].sum() > 0 else 0
    p2 = pen["Acertos"].sum() / pen["Total"].sum() * 100 if pen["Total"].sum() > 0 else 0
    diff = p1 - p2
    if diff > 1:
        return "&#9650;", "Subindo", "#00b4a6"
    elif diff < -1:
        return "&#9660;", "Caindo", "#e74c3c"
    else:
        return "&rarr;", "Estavel", "#7a9ab8"


def _filtrar(df: pd.DataFrame, mes: int, ano: int) -> pd.DataFrame:
    if df.empty or (mes is None and ano is None):
        return df
    df = df.copy()
    df["_dt"] = pd.to_datetime(df["Data"], dayfirst=True, errors="coerce")
    if mes:
        df = df[df["_dt"].dt.month == mes]
    if ano:
        df = df[df["_dt"].dt.year == ano]
    return df.drop(columns=["_dt"])


def _dark_header(titulo: str, subtitulo: str = ""):
    icone = "&#127942;"
    sub_html = (
        f'<div style="color:#7a9ab8;font-size:0.78rem;margin-top:4px;">{subtitulo}</div>'
        if subtitulo else ""
    )
    st.html(f"""
        <div style="
            background: linear-gradient(135deg, #061020 0%, #0d1b2a 100%);
            border-radius: 10px;
            padding: 18px 24px;
            margin-bottom: 20px;
            text-align: center;
            border-bottom: 3px solid #00b4a6;
            box-shadow: 0 4px 16px rgba(0,0,0,0.35);
        ">
            <span style="font-size:1.4rem;">{icone}</span>
            <span style="
                color:#ffffff;
                font-weight:800;
                font-size:1.3rem;
                letter-spacing:0.12em;
                margin-left:10px;
                text-transform:uppercase;
            ">{titulo}</span>
            {sub_html}
        </div>
    """)


def _tend_from_api(tend_atual, tend_ant):
    """Calcula seta/texto/cor de tendência a partir dos dados da API."""
    if tend_atual is None or tend_ant is None:
        return "&rarr;", "Estavel", "#7a9ab8"
    diff = tend_atual - tend_ant
    if diff > 1:
        return "&#9650;", "Subindo", "#00b4a6"
    elif diff < -1:
        return "&#9660;", "Caindo", "#e74c3c"
    else:
        return "&rarr;", "Estavel", "#7a9ab8"


def _render_tabela(por_materia: list, df_l_all: pd.DataFrame, usar_api: bool):
    """Renderiza a tabela de desempenho por matéria."""
    st.html("""
        <div style="
            background:#0d1b2a;
            border-radius:8px 8px 0 0;
            padding:10px 18px;
            border-bottom:2px solid #00b4a6;
        ">
            <span style="
                color:#ffffff;
                font-weight:700;
                font-size:0.82rem;
                letter-spacing:0.12em;
                text-transform:uppercase;
            ">DESEMPENHO POR MATERIA</span>
        </div>
    """)

    if not por_materia:
        st.info("Nenhum dado disponivel para os filtros selecionados.")
        return

    cols_header = ["MATERIA", "REALIZADAS", "ACERTOS", "% ACERTO", "TENDENCIA", "STATUS", "PRIORIDADE"]
    th_style = (
        "padding:10px 14px;"
        "text-align:center;"
        "font-size:0.71rem;"
        "letter-spacing:0.08em;"
        "color:#7a9ab8;"
        "font-weight:600;"
        "white-space:nowrap;"
    )
    header_html = "".join(f'<th style="{th_style}">{h}</th>' for h in cols_header)

    rows_html = ""
    for i, item in enumerate(por_materia):
        if usar_api:
            mat        = item["materia"]
            realizadas = item["realizadas"]
            acertos    = item["acertos"]
            perc_mat   = item["perc"]
            seta, tend_txt, tend_cor = _tend_from_api(item.get("tend_perc_atual"), item.get("tend_perc_anterior"))
        else:
            mat        = item["Materia"]
            realizadas = int(item["Realizadas"])
            acertos    = int(item["Acertos"])
            perc_mat   = item["Perc"]
            seta, tend_txt, tend_cor = _tendencia(df_l_all, mat)

        perc_cor             = _perc_color(perc_mat)
        st_cor, st_icone, st_txt = _status(perc_mat)
        pr_cor, pr_icone, pr_txt = _prioridade(perc_mat)
        row_bg = "#0a1628" if i % 2 == 0 else "#0d1b2a"

        td = "padding:10px 14px;text-align:center;white-space:nowrap;"
        rows_html += f"""
        <tr style="background:{row_bg};border-bottom:1px solid #1a3050;">
            <td style="{td}font-weight:800;color:#ffffff;font-size:0.9rem;">{mat}</td>
            <td style="{td}color:#c8d6e5;">{realizadas}</td>
            <td style="{td}color:#c8d6e5;">{acertos}</td>
            <td style="{td}font-weight:700;color:{perc_cor};font-size:0.95rem;">{perc_mat}%</td>
            <td style="{td}font-weight:600;color:{tend_cor};">{seta}&nbsp;{tend_txt}</td>
            <td style="{td}">
                <span style="color:{st_cor};font-size:0.85rem;">{st_icone}</span>
                <span style="color:#c8d6e5;margin-left:4px;">{st_txt}</span>
            </td>
            <td style="{td}font-weight:700;color:{pr_cor};">{pr_icone}&nbsp;{pr_txt}</td>
        </tr>
        """

    st.html(f"""
        <div style="
            background:#0d1b2a;
            border-radius:0 0 8px 8px;
            overflow:hidden;
            border:1px solid #1a3050;
            border-top:none;
            box-shadow:0 6px 20px rgba(0,0,0,0.4);
            margin-bottom:20px;
        ">
            <table style="width:100%;border-collapse:collapse;">
                <thead>
                    <tr style="background:#061020;">
                        {header_html}
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
    """)


@st.cache_data(ttl=60, show_spinner=False)
def _fetch_lancamentos(usuario_id: str) -> pd.DataFrame:
    return ler_lancamentos(usuario_id)


@st.cache_data(ttl=60, show_spinner=False)
def _fetch_desempenho_api(token: str, mes, ano, fontes) -> dict | None:
    """Chamada cacheada ao endpoint /desempenho. Chave: token + filtros."""
    import requests
    params = {}
    if mes:
        params["mes"] = mes
    if ano:
        params["ano"] = ano
    if fontes:
        params["fonte"] = list(fontes)
    if not token:
        return None
    try:
        headers = {"Authorization": f"Bearer {token}"}
        r = requests.get(
            "http://localhost:8000/desempenho",
            params=params,
            headers=headers,
            timeout=2,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def render():
    _dark_header("Painel de Desempenho")

    # ── Filtros ────────────────────────────────────────────────────────────────
    meses_map = {
        "Geral": None, "Jan": 1, "Fev": 2, "Mar": 3, "Abr": 4,
        "Mai": 5, "Jun": 6, "Jul": 7, "Ago": 8,
        "Set": 9, "Out": 10, "Nov": 11, "Dez": 12,
    }

    # Carrega dados locais para popular filtro de ano/fonte (cacheado 60s)
    df_l_all = _fetch_lancamentos(st.session_state.usuario["id"])

    col_f1, col_f2, col_f3 = st.columns([1, 1, 2])

    with col_f1:
        st.caption("Mes")
        mes_sel = st.selectbox("Mes", list(meses_map.keys()), key="dash_mes",
                               label_visibility="collapsed")

    with col_f2:
        anos_disp = ["Todos"]
        if not df_l_all.empty:
            dts = pd.to_datetime(df_l_all["Data"], dayfirst=True, errors="coerce").dropna()
            anos_disp += sorted(dts.dt.year.unique().astype(str).tolist(), reverse=True)
        st.caption("Ano")
        ano_sel = st.selectbox("Ano", anos_disp, key="dash_ano",
                               label_visibility="collapsed")

    with col_f3:
        fontes_disp = ["Todas"]
        if not df_l_all.empty and "Fonte" in df_l_all.columns:
            fontes_unicas = sorted(df_l_all["Fonte"].dropna().unique().tolist())
            fontes_disp += fontes_unicas
        st.caption("Fonte das Questoes")
        fonte_sel = st.multiselect("Fonte", fontes_disp[1:], key="dash_fonte",
                                   placeholder="Todas as fontes",
                                   label_visibility="collapsed")

    mes_int = meses_map.get(mes_sel)
    ano_int = int(ano_sel) if ano_sel != "Todos" else None

    # ── API usada apenas na view geral (sem filtros) ──────────────────────────
    # Filtros aplicados sobre dados locais (instantâneo, sem nova chamada HTTP)
    token = st.session_state.get("api_token", "")
    usa_api = (mes_int is None and ano_int is None and not fonte_sel)
    dados_api = _fetch_desempenho_api(token=token, mes=None, ano=None, fontes=None) if usa_api else None

    if dados_api is not None:
        # ── KPIs via API ───────────────────────────────────────────────────────
        total_q    = dados_api["total_questoes"]
        total_a    = dados_api["total_acertos"]
        perc_geral = dados_api["perc_geral"]

        k1, k2 = st.columns(2)
        k1.metric("Total de Questoes", total_q)
        k2.metric("Acertos", f"{total_a}  ({perc_geral:.1f}%)")

        st.divider()
        _render_tabela(dados_api["por_materia"], df_l_all, usar_api=True)

    else:
        # ── Fallback: dados locais ─────────────────────────────────────────────
        df_l = _filtrar(df_l_all, mes_int, ano_int)
        if fonte_sel and not df_l.empty:
            df_l = df_l[df_l["Fonte"].isin(fonte_sel)]

        total_q    = int(df_l["Total"].sum())   if not df_l.empty else 0
        total_a    = int(df_l["Acertos"].sum()) if not df_l.empty else 0
        perc_geral = round(total_a / total_q * 100, 1) if total_q > 0 else 0.0

        k1, k2 = st.columns(2)
        k1.metric("Total de Questoes", total_q)
        k2.metric("Acertos", f"{total_a}  ({perc_geral:.1f}%)")

        st.divider()

        if df_l.empty:
            st.html("""
                <div style="
                    background:#0d1b2a;
                    border-radius:8px 8px 0 0;
                    padding:10px 18px;
                    border-bottom:2px solid #00b4a6;
                ">
                    <span style="
                        color:#ffffff;
                        font-weight:700;
                        font-size:0.82rem;
                        letter-spacing:0.12em;
                        text-transform:uppercase;
                    ">DESEMPENHO POR MATERIA</span>
                </div>
            """)
            st.info("Nenhum dado disponivel para os filtros selecionados.")
            return

        resumo = (
            df_l.groupby("Materia")
            .agg(Realizadas=("Total", "sum"), Acertos=("Acertos", "sum"))
            .assign(Perc=lambda x: (x["Acertos"] / x["Realizadas"] * 100).round(1))
            .sort_values("Perc", ascending=False)
            .reset_index()
        )
        _render_tabela(resumo.to_dict("records"), df_l_all, usar_api=False)
