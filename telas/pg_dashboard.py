"""
pg_dashboard.py
Tela principal: KPIs de desempenho, tabela por materia e ranking de erros.
"""

import streamlit as st
import pandas as pd
from database import ler_lancamentos, ler_erros


def _filtrar(df: pd.DataFrame, mes: int, ano: int) -> pd.DataFrame:
    """Aplica filtro de mes e/ou ano a um DataFrame de lancamentos."""
    if df.empty or (mes is None and ano is None):
        return df
    df = df.copy()
    df["_dt"] = pd.to_datetime(df["Data"], dayfirst=True, errors="coerce")
    if mes:
        df = df[df["_dt"].dt.month == mes]
    if ano:
        df = df[df["_dt"].dt.year == ano]
    return df.drop(columns=["_dt"])


def render():
    st.title("Dashboard")

    df_l_all = ler_lancamentos()
    df_e_all = ler_erros()

    # ── Filtro de periodo ──────────────────────────────────────────────────────
    meses_map = {
        "Todos": None, "Jan": 1, "Fev": 2, "Mar": 3, "Abr": 4,
        "Mai": 5,      "Jun": 6, "Jul": 7, "Ago": 8,
        "Set": 9,      "Out": 10,"Nov": 11,"Dez": 12,
    }
    col_f1, col_f2, _ = st.columns([1, 1, 4])
    mes_sel = col_f1.selectbox("Mes", list(meses_map.keys()), key="dash_mes")

    anos_disp = ["Todos"]
    if not df_l_all.empty:
        dts = pd.to_datetime(df_l_all["Data"], dayfirst=True, errors="coerce").dropna()
        anos_disp += sorted(dts.dt.year.unique().astype(str).tolist(), reverse=True)
    ano_sel = col_f2.selectbox("Ano", anos_disp, key="dash_ano")

    mes_int = meses_map.get(mes_sel)
    ano_int = int(ano_sel) if ano_sel != "Todos" else None
    df_l = _filtrar(df_l_all, mes_int, ano_int)

    # ── KPIs ──────────────────────────────────────────────────────────────────
    total_q = int(df_l["Total"].sum())   if not df_l.empty else 0
    total_a = int(df_l["Acertos"].sum()) if not df_l.empty else 0
    perc    = round(total_a / total_q * 100, 1) if total_q > 0 else 0.0

    ids_l     = set(df_l["ID Bateria"].dropna().unique())    if not df_l.empty else set()
    ids_e     = set(df_e_all["ID Bateria"].dropna().unique()) if not df_e_all.empty else set()
    pendentes = len(ids_l - ids_e)
    total_err = int(df_e_all["Qtd Erros"].sum()) if not df_e_all.empty else 0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total de Questoes",    total_q)
    k2.metric("Acertos",              f"{total_a}  ({perc:.1f}%)")
    k3.metric("Erros Registrados",    total_err)
    k4.metric("Baterias Pendentes",   pendentes,
              help="Baterias sem nenhum erro vinculado")

    st.divider()

    # ── Desempenho por materia + Ranking de erros ──────────────────────────────
    col_mat, col_err = st.columns([3, 2])

    with col_mat:
        st.subheader("Desempenho por Materia")
        if df_l.empty:
            st.info("Nenhum dado disponivel.")
        else:
            resumo = (
                df_l.groupby("Materia")
                .agg(Acertos=("Acertos", "sum"), Total=("Total", "sum"))
                .assign(Perc=lambda x: (x["Acertos"] / x["Total"] * 100).round(1))
                .sort_values("Perc", ascending=False)
                .reset_index()
                .rename(columns={"Perc": "% Acertos"})
            )
            st.dataframe(
                resumo[["Materia", "Total", "Acertos", "% Acertos"]],
                use_container_width=True,
                hide_index=True,
            )

    with col_err:
        st.subheader("Top Erros por Topico")
        if df_e_all.empty:
            st.info("Nenhum erro registrado.")
        else:
            ranking = (
                df_e_all.groupby("Topico")["Qtd Erros"]
                .sum()
                .sort_values(ascending=False)
                .head(18)
                .reset_index()
            )
            st.dataframe(ranking, use_container_width=True, hide_index=True)
