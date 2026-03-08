"""
pg_erros_criticos.py
Tabela de todos os erros registrados, ordenada por quantidade (do maior para o menor).
"""

import streamlit as st
from database import ler_erros


def render():
    st.html("""
        <div style="
            background: linear-gradient(135deg, #061020 0%, #0d1b2a 100%);
            border-radius: 10px;
            padding: 18px 24px;
            margin-bottom: 20px;
            text-align: center;
            border-bottom: 3px solid #e74c3c;
            box-shadow: 0 4px 16px rgba(0,0,0,0.35);
        ">
            <span style="font-size:1.4rem;">&#128680;</span>
            <span style="
                color:#ffffff;
                font-weight:800;
                font-size:1.3rem;
                letter-spacing:0.12em;
                margin-left:10px;
                text-transform:uppercase;
            ">ERROS CRITICOS</span>
        </div>
    """)

    df = ler_erros(st.session_state.usuario["id"])

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
