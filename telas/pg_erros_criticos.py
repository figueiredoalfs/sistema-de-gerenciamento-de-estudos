"""
pg_erros_criticos.py
Tabela de todos os erros registrados, ordenada por quantidade (do maior para o menor).
"""

import streamlit as st
from database import ler_erros


def render():
    st.title("Erros Criticos")

    df = ler_erros()

    if df.empty:
        st.info("Nenhum erro registrado ainda.")
        return

    total_e = int(df["Qtd Erros"].sum())
    total_t = df["Topico"].nunique()
    st.caption(f"Total: {total_e} erros em {total_t} topicos distintos")

    df_s = (
        df.sort_values("Qtd Erros", ascending=False)
        .reset_index(drop=True)
    )
    df_s.index += 1  # exibe ranking a partir de 1

    st.dataframe(
        df_s[["Topico", "Materia", "Qtd Erros", "Data", "Observacao", "Providencia"]],
        use_container_width=True,
    )
