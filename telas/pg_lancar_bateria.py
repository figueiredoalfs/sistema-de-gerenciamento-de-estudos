"""
pg_lancar_bateria.py
Lança bateria de questões com registro de erros inline obrigatório.

Fluxo:
  Fase "form"  — usuário monta a bateria (matérias + acertos/total)
  Fase "erros" — para cada matéria com erros, obrigatório registrar
                  pelo menos 1 tópico + tipo antes de finalizar.
  Se todos com 100% → pula direto para o dashboard.
"""

import streamlit as st
from datetime import date
from database import (
    gerar_proximo_id, inserir_lancamentos, inserir_erro,
    get_materias_plano, get_plataformas_ativas,
)
from api_client import api_registrar_bateria, api_registrar_erro
from config_fontes import fontes_disponiveis
from config_materias import get_topicos, get_subtopicos
import threading

TIPOS_ERRO = {
    "Não sabia":  "nao_sabia",
    "Confundi":   "confundiu",
    "Esqueci":    "esqueceu",
}
TIPOS_DISPLAY = list(TIPOS_ERRO.keys())


def _perc_color(p: float) -> str:
    if p >= 85: return "#4ade80"
    if p >= 75: return "#27ae60"
    if p >= 65: return "#f39c12"
    return "#e74c3c"


def _inicializar():
    if "bat_id" not in st.session_state:
        uid = st.session_state.usuario["id"]
        plats = get_plataformas_ativas(uid)
        fontes = fontes_disponiveis(plats)   # [(slug, label), ...]
        st.session_state.bat_id       = gerar_proximo_id(uid)
        st.session_state.bat_data     = date.today()
        st.session_state.bat_fonte    = fontes[0][0]   # slug do primeiro
        st.session_state.bat_fontes   = fontes          # lista completa
        st.session_state.bat_itens    = []
        st.session_state.bat_fc       = 0
        st.session_state.bat_fase     = "form"
        st.session_state.bat_err_cnt  = {}


def _header(titulo: str, subtitulo: str = ""):
    sub = f'<div style="color:#7a9ab8;font-size:0.78rem;margin-top:4px;">{subtitulo}</div>' if subtitulo else ""
    st.html(f"""
        <div style="
            background:linear-gradient(135deg,#061020 0%,#0d1b2a 100%);
            border-radius:10px;padding:18px 24px;margin-bottom:20px;
            text-align:center;border-bottom:3px solid #00b4a6;
            box-shadow:0 4px 16px rgba(0,0,0,0.35);
        ">
            <span style="font-size:1.4rem;">&#128203;</span>
            <span style="color:#fff;font-weight:800;font-size:1.3rem;
                letter-spacing:0.12em;margin-left:10px;text-transform:uppercase;">
                {titulo}
            </span>
            {sub}
        </div>
    """)


def _gravar_bateria(id_b, data_str, fonte_val):
    """Grava a bateria no banco local e no FastAPI."""
    uid = st.session_state.usuario["id"]
    registros = []
    for item in st.session_state.bat_itens:
        perc = round(item["acertos"] / item["total"] * 100, 1) if item["total"] > 0 else 0.0
        registros.append({
            "id_bateria": id_b,
            "materia":    item["materia"],
            "data":       data_str,
            "acertos":    item["acertos"],
            "total":      item["total"],
            "fonte":      fonte_val,
            "subtopico":  item["subtopico"],
            "percentual": perc,
        })
    inserir_lancamentos(registros, uid)
    itens_api = [
        {"materia": r["materia"], "subtopico": r["subtopico"],
         "acertos": r["acertos"], "total": r["total"], "fonte": fonte_val}
        for r in registros
    ]
    resultado_api = api_registrar_bateria(itens_api, fonte_padrao=fonte_val)
    api_bid = resultado_api.get("bateria_id", id_b) if resultado_api else id_b
    st.session_state.api_bateria_id = api_bid


def _gravar_erros(id_b, data_str):
    """Grava os erros registrados inline."""
    uid = st.session_state.usuario["id"]
    itens_com_erros = [i for i in st.session_state.bat_itens if i["acertos"] < i["total"]]
    api_bid = st.session_state.get("api_bateria_id", id_b)

    for mi, item in enumerate(itens_com_erros):
        n = st.session_state.bat_err_cnt.get(mi, item["total"] - item["acertos"])
        for li in range(n):
            topico_key   = f"err_{mi}_{li}_top"
            subtop_key   = f"err_{mi}_{li}_sub"
            tipo_key     = f"err_{mi}_{li}_tipo"
            topico   = st.session_state.get(topico_key, "")
            subtop   = st.session_state.get(subtop_key, "")
            tipo_d   = st.session_state.get(tipo_key, TIPOS_DISPLAY[0])
            if not topico or topico == "— selecione o tópico —":
                continue
            tipo_val = TIPOS_ERRO.get(tipo_d, "nao_sabia")
            dados = {
                "id_bateria":    id_b,
                "materia":       item["materia"],
                "topico":        topico,
                "subtopico_erro": subtop if subtop and subtop != "— opcional —" else "",
                "qtd_erros":     1,
                "data":          data_str,
                "tipo_erro":     tipo_val,
                "status":        "pendente",
            }
            inserir_erro(dados, uid)
            threading.Thread(
                target=api_registrar_erro,
                kwargs={"materia": item["materia"], "topico_texto": topico,
                        "qtd_erros": 1, "observacao": tipo_val, "id_bateria": api_bid},
                daemon=True,
            ).start()


def _limpar_e_ir_dashboard():
    for k in list(st.session_state.keys()):
        if k.startswith("bat_") or k.startswith("err_"):
            st.session_state.pop(k, None)
    st.session_state.pagina = "dashboard"
    st.rerun()


# ── FASE FORM ─────────────────────────────────────────────────────────────────

def _render_form():
    _header("Lançar Nova Bateria", "Adicione as matérias e clique em Finalizar")

    # ── Identificação ────────────────────────────────────────────────────────
    c1, c2 = st.columns([1, 2])
    st.session_state.bat_data = c1.date_input("Data", value=st.session_state.bat_data, key="bat_data_inp")
    fontes = st.session_state.bat_fontes
    slugs  = [f[0] for f in fontes]
    labels = [f[1] for f in fontes]
    idx_atual = slugs.index(st.session_state.bat_fonte) if st.session_state.bat_fonte in slugs else 0
    fonte_label = c2.selectbox("Fonte das Questões", labels, index=idx_atual, key="bat_fonte_sel")
    st.session_state.bat_fonte = slugs[labels.index(fonte_label)]

    st.divider()

    # ── Itens adicionados ────────────────────────────────────────────────────
    itens = st.session_state.bat_itens
    if itens:
        tot_q  = sum(i["total"]   for i in itens)
        tot_a  = sum(i["acertos"] for i in itens)
        perc_g = tot_a / tot_q * 100 if tot_q > 0 else 0

        rows_html = ""
        for i, it in enumerate(itens):
            p = it["acertos"] / it["total"] * 100 if it["total"] > 0 else 0
            cor = _perc_color(p)
            rows_html += f"""
            <tr style="background:{'#0a1628' if i%2==0 else '#0d1b2a'};border-bottom:1px solid #1a3050;">
                <td style="padding:8px 14px;color:#fff;font-weight:700;">{it['materia']}</td>
                <td style="padding:8px 14px;color:#c8d6e5;">{it['subtopico'] or '—'}</td>
                <td style="padding:8px 14px;text-align:center;color:#c8d6e5;">{it['acertos']}/{it['total']}</td>
                <td style="padding:8px 14px;text-align:center;font-weight:700;color:{cor};">{p:.1f}%</td>
            </tr>"""

        cor_g = _perc_color(perc_g)
        st.html(f"""
            <div style="background:#0d1b2a;border-radius:8px 8px 0 0;
                padding:8px 14px;border-bottom:2px solid #00b4a6;">
                <span style="color:#7a9ab8;font-size:0.75rem;font-weight:600;
                    letter-spacing:0.1em;text-transform:uppercase;">
                    {len(itens)} matéria(s) &nbsp;·&nbsp; {tot_q} questões &nbsp;·&nbsp;
                    <span style="color:{cor_g};font-weight:800;">{perc_g:.1f}%</span>
                </span>
            </div>
            <div style="background:#0d1b2a;border-radius:0 0 8px 8px;overflow:hidden;
                border:1px solid #1a3050;border-top:none;margin-bottom:16px;">
                <table style="width:100%;border-collapse:collapse;">
                    <thead><tr style="background:#061020;">
                        <th style="padding:8px 14px;color:#7a9ab8;font-size:0.72rem;text-transform:uppercase;text-align:left;">Matéria</th>
                        <th style="padding:8px 14px;color:#7a9ab8;font-size:0.72rem;text-transform:uppercase;text-align:left;">Subtópico</th>
                        <th style="padding:8px 14px;color:#7a9ab8;font-size:0.72rem;text-transform:uppercase;text-align:center;">Acertos</th>
                        <th style="padding:8px 14px;color:#7a9ab8;font-size:0.72rem;text-transform:uppercase;text-align:center;">%</th>
                    </tr></thead>
                    <tbody>{rows_html}</tbody>
                </table>
            </div>
        """)
    else:
        st.info("Nenhuma matéria adicionada ainda.")

    # ── Formulário de adição ─────────────────────────────────────────────────
    st.subheader("Incluir Matéria")
    fc = st.session_state.bat_fc
    uid = st.session_state.usuario["id"]
    materias = get_materias_plano(uid)

    col_m, col_s, col_a, col_t = st.columns([2, 2, 1, 1])
    mat_sel  = col_m.selectbox("Matéria", [""] + materias, key=f"fm_{fc}")
    topicos  = get_topicos(mat_sel) if mat_sel else []
    sub_sel  = col_s.selectbox("Tópico", [""] + topicos, key=f"fs_{fc}")
    acertos  = col_a.number_input("Acertos", min_value=0, value=0, step=1, key=f"fa_{fc}")
    total    = col_t.number_input("Total",   min_value=1, value=10, step=1, key=f"ft_{fc}")

    # Preview do % em tempo real
    if total > 0:
        p_prev = acertos / total * 100
        cor_prev = _perc_color(p_prev)
        st.html(f'<div style="color:{cor_prev};font-weight:700;font-size:0.9rem;'
                f'margin:-8px 0 8px 0;">{p_prev:.1f}%</div>')

    col_b1, col_b2, col_b3 = st.columns([2, 2, 2])

    if col_b1.button("Incluir", use_container_width=True):
        if not mat_sel:
            st.error("Selecione a matéria.")
        elif acertos > total:
            st.error(f"Acertos ({acertos}) não pode ser maior que Total ({total}).")
        else:
            st.session_state.bat_itens.append({
                "materia":   mat_sel,
                "subtopico": sub_sel.strip(),
                "acertos":   int(acertos),
                "total":     int(total),
            })
            st.session_state.bat_fc += 1
            st.rerun()

    if col_b2.button("Finalizar Bateria", type="primary", use_container_width=True):
        if not st.session_state.bat_itens:
            st.warning("Adicione pelo menos uma matéria antes de finalizar.")
        else:
            itens_com_erros = [i for i in st.session_state.bat_itens
                               if i["acertos"] < i["total"]]
            id_b     = st.session_state.bat_id
            data_str = st.session_state.bat_data.strftime("%d/%m/%Y")
            fonte_val = st.session_state.bat_fonte   # já é o slug
            _gravar_bateria(id_b, data_str, fonte_val)

            if itens_com_erros:
                # Pré-preenche: 1 linha por erro de cada matéria (total - acertos)
                for mi, it in enumerate(itens_com_erros):
                    st.session_state.bat_err_cnt[mi] = it["total"] - it["acertos"]
                st.session_state.bat_fase = "erros"
                st.rerun()
            else:
                # Sem erros — finaliza direto
                _limpar_e_ir_dashboard()

    if col_b3.button("Cancelar", use_container_width=True):
        _limpar_e_ir_dashboard()


# ── FASE ERROS ────────────────────────────────────────────────────────────────

def _render_erros():
    itens_com_erros = [i for i in st.session_state.bat_itens if i["acertos"] < i["total"]]
    id_b     = st.session_state.bat_id
    data_str = st.session_state.bat_data.strftime("%d/%m/%Y")

    # Resumo da bateria
    tot_q = sum(i["total"]   for i in st.session_state.bat_itens)
    tot_a = sum(i["acertos"] for i in st.session_state.bat_itens)
    perc  = tot_a / tot_q * 100 if tot_q > 0 else 0
    cor   = _perc_color(perc)

    _header(
        "Registrar Erros",
        f"Bateria {id_b} &nbsp;·&nbsp; {tot_q} questões &nbsp;·&nbsp; "
        f"<span style='color:{cor};font-weight:800;'>{perc:.1f}%</span>"
    )

    st.html("""
        <div style="background:#162535;border-left:3px solid #00b4a6;
            border-radius:6px;padding:10px 16px;margin-bottom:16px;font-size:0.85rem;color:#8ab0c8;">
            Para cada questão errada, informe o tópico e o motivo.
        </div>
    """)

    uid = st.session_state.usuario["id"]
    todos_preenchidos = True

    for mi, item in enumerate(itens_com_erros):
        n_erros       = st.session_state.bat_err_cnt.get(mi, item["total"] - item["acertos"])
        subtopico_bat = item["subtopico"].strip()   # subtópico escolhido no lançamento

        # Tópico fixo se o usuário especificou subtópico; caso contrário, fallback para cadastros
        topico_fixo   = subtopico_bat if subtopico_bat else None
        opcoes_topico = None if topico_fixo else (["— selecione o tópico —"] + get_assuntos(item["materia"], uid))

        subtopico_label = f" — {subtopico_bat}" if subtopico_bat else ""
        st.html(f"""
            <div style="background:#0d1b2a;border-radius:8px 8px 0 0;
                padding:10px 16px;border-bottom:2px solid #e74c3c;margin-top:12px;">
                <span style="color:#fff;font-weight:700;font-size:0.95rem;">{item['materia']}</span>
                <span style="color:#7a9ab8;font-size:0.85rem;">{subtopico_label}</span>
                <span style="color:#e74c3c;font-size:0.8rem;margin-left:10px;">
                    {n_erros} erro{'s' if n_erros>1 else ''}
                </span>
            </div>
        """)

        with st.container():
            for li in range(n_erros):
                topico_key = f"err_{mi}_{li}_top"
                subtop_key = f"err_{mi}_{li}_sub"
                tipo_key   = f"err_{mi}_{li}_tipo"
                lbl = li == 0  # exibe labels só na primeira linha

                col_num, col_top, col_sub, col_tipo = st.columns([0.4, 2, 2, 1.8])

                col_num.markdown(
                    f'<div style="color:#e74c3c;font-weight:700;font-size:0.85rem;'
                    f'padding-top:30px;">#{li+1}</div>',
                    unsafe_allow_html=True,
                )

                if topico_fixo:
                    # Tópico vem do lançamento → fixo, só escolhe subtópico e motivo
                    st.session_state[topico_key] = topico_fixo
                    col_top.markdown(
                        f'<div style="padding-top:{"4px" if lbl else "28px"};">'
                        f'{"<small style=color:#8ab0c8>Tópico</small><br>" if lbl else ""}'
                        f'<span style="color:#d0e4f0;font-weight:600;">{topico_fixo}</span></div>',
                        unsafe_allow_html=True,
                    )
                    subtopicos = get_subtopicos(item["materia"], topico_fixo)
                else:
                    # Sem tópico → usuário seleciona da hierarquia
                    topico_val = col_top.selectbox(
                        "Tópico" if lbl else " ",
                        opcoes_topico,
                        key=topico_key,
                        label_visibility="visible" if lbl else "hidden",
                    )
                    if topico_val == "— selecione o tópico —":
                        todos_preenchidos = False
                    subtopicos = get_subtopicos(item["materia"], topico_val) if topico_val and topico_val != "— selecione o tópico —" else []

                # Subtópico (nível 3) — opcional
                opcoes_sub = ["— opcional —"] + subtopicos
                col_sub.selectbox(
                    "Subtópico" if lbl else " ",
                    opcoes_sub,
                    key=subtop_key,
                    label_visibility="visible" if lbl else "hidden",
                )

                col_tipo.radio(
                    "Motivo" if lbl else " ",
                    TIPOS_DISPLAY,
                    key=tipo_key,
                    horizontal=True,
                    label_visibility="visible" if lbl else "hidden",
                )

        st.html('<div style="background:#1a3050;height:1px;margin:8px 0 4px 0;"></div>')

    st.markdown("")
    col_fin, col_can = st.columns([3, 1])

    if col_fin.button(
        "Registrar e Finalizar ✓",
        type="primary",
        use_container_width=True,
        disabled=not todos_preenchidos,
    ):
        _gravar_erros(id_b, data_str)
        _limpar_e_ir_dashboard()

    if col_can.button("Cancelar", use_container_width=True):
        _limpar_e_ir_dashboard()


# ── RENDER PRINCIPAL ──────────────────────────────────────────────────────────

def render():
    _inicializar()
    if st.session_state.bat_fase == "erros":
        _render_erros()
    else:
        _render_form()
