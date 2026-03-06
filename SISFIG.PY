import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import pandas as pd
from openpyxl import Workbook, load_workbook
from datetime import datetime
import os
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ─── Aparencia ────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

FILE_NAME = "controle_desempenho.xlsx"


# ─── BANCO DE DADOS ───────────────────────────────────────────────────────────
class Database:
    def __init__(self):
        if not os.path.exists(FILE_NAME):
            self._criar_arquivo()
        self._garantir_aba_cadastros()

    def _criar_arquivo(self):
        wb = Workbook()
        ws1 = wb.active
        ws1.title = "LANCAMENTOS"
        ws1.append(["ID Bateria", "Materia", "Data", "Acertos", "Total", "Fonte", "Subtopico", "Percentual"])
        ws2 = wb.create_sheet("ERROS")
        ws2.append(["ID Bateria", "Materia", "Topico", "Qtd Erros", "Data", "Observacao", "Providencia"])
        ws3 = wb.create_sheet("CADASTROS")
        ws3.append(["Materia", "Assunto"])
        wb.save(FILE_NAME)

    def gerar_proximo_id(self):
        df = self.ler_dados("LANCAMENTOS")
        if df.empty:
            return "B001"
        ids = df["ID Bateria"].dropna().astype(str).tolist()
        nums = []
        for id_ in ids:
            try:
                nums.append(int(id_.lstrip("Bb")))
            except ValueError:
                pass
        return f"B{(max(nums) + 1):03d}" if nums else "B001"

    def salvar_bateria(self, dados):
        wb = load_workbook(FILE_NAME)
        ws = wb["LANCAMENTOS"]
        ws.append(dados)
        wb.save(FILE_NAME)

    def salvar_erro(self, dados):
        wb = load_workbook(FILE_NAME)
        ws = wb["ERROS"]
        ws.append(dados)
        wb.save(FILE_NAME)

    def ler_dados(self, aba):
        try:
            df = pd.read_excel(FILE_NAME, sheet_name=aba, dtype={"ID Bateria": str})
            if aba == "LANCAMENTOS":
                df["Acertos"]   = pd.to_numeric(df.get("Acertos"),   errors="coerce").fillna(0).astype(int)
                df["Total"]     = pd.to_numeric(df.get("Total"),     errors="coerce").fillna(0).astype(int)
                df["Percentual"]= pd.to_numeric(df.get("Percentual"),errors="coerce").fillna(0)
            elif aba == "ERROS":
                df["Qtd Erros"] = pd.to_numeric(df.get("Qtd Erros"), errors="coerce").fillna(0).astype(int)
            return df
        except Exception:
            return pd.DataFrame()

    def exportar_relatorio(self, df_l, df_e, label):
        nome = f"relatorio_{label}.xlsx"
        wb = Workbook()

        # Aba resumo
        ws1 = wb.active
        ws1.title = "Resumo"
        ws1.append([f"Relatorio de Desempenho — {label}"])
        ws1.append([])
        ws1.append(["Materia", "Questoes", "Acertos", "% Acertos"])
        if not df_l.empty:
            resumo = df_l.groupby("Materia").agg(Acertos=("Acertos","sum"), Total=("Total","sum"))
            resumo["Perc"] = (resumo["Acertos"] / resumo["Total"] * 100).round(1)
            for mat, row in resumo.iterrows():
                ws1.append([mat, int(row["Total"]), int(row["Acertos"]), f"{row['Perc']:.1f}%"])

        # Aba lancamentos
        ws2 = wb.create_sheet("Lancamentos")
        if not df_l.empty:
            ws2.append(list(df_l.columns))
            for _, row in df_l.iterrows():
                ws2.append(list(row))

        # Aba erros
        ws3 = wb.create_sheet("Erros")
        if not df_e.empty:
            ws3.append(list(df_e.columns))
            for _, row in df_e.iterrows():
                ws3.append(list(row))

        wb.save(nome)
        return os.path.abspath(nome)

    def _garantir_aba_cadastros(self):
        wb = load_workbook(FILE_NAME)
        if "CADASTROS" not in wb.sheetnames:
            ws = wb.create_sheet("CADASTROS")
            ws.append(["Materia", "Assunto"])
            wb.save(FILE_NAME)

    def salvar_cadastro(self, materia, assunto):
        wb = load_workbook(FILE_NAME)
        ws = wb["CADASTROS"]
        ws.append([materia, assunto])
        wb.save(FILE_NAME)

    def remover_cadastro(self, materia, assunto):
        wb = load_workbook(FILE_NAME)
        ws = wb["CADASTROS"]
        for row in list(ws.iter_rows(min_row=2)):
            if str(row[0].value) == materia and str(row[1].value) == assunto:
                ws.delete_rows(row[0].row)
                break
        wb.save(FILE_NAME)

    def remover_materia(self, materia):
        wb = load_workbook(FILE_NAME)
        ws = wb["CADASTROS"]
        linhas = [r[0].row for r in ws.iter_rows(min_row=2) if str(r[0].value) == materia]
        for r in reversed(linhas):
            ws.delete_rows(r)
        wb.save(FILE_NAME)

    def get_materias(self):
        df = self.ler_dados("CADASTROS")
        if df.empty or "Materia" not in df.columns:
            return []
        return sorted(df["Materia"].dropna().astype(str).unique().tolist())

    def get_assuntos(self, materia):
        df = self.ler_dados("CADASTROS")
        if df.empty or "Assunto" not in df.columns:
            return []
        mask = (df["Materia"].astype(str) == materia) & (df["Assunto"].notna()) & (df["Assunto"].astype(str) != "")
        return df[mask]["Assunto"].astype(str).tolist()


# ─── BOTAO SIDEBAR ────────────────────────────────────────────────────────────
class SidebarButton(ctk.CTkButton):
    def __init__(self, parent, text, command, **kwargs):
        super().__init__(
            parent, text=text, command=command,
            anchor="w", fg_color="transparent",
            text_color="#cccccc", hover_color="#1f3a6e",
            height=42, corner_radius=8,
            font=ctk.CTkFont("Roboto", 13),
            **kwargs,
        )

    def set_active(self, active):
        if active:
            self.configure(fg_color="#1f538d", text_color="#ffffff",
                           font=ctk.CTkFont("Roboto", 13, weight="bold"))
        else:
            self.configure(fg_color="transparent", text_color="#cccccc",
                           font=ctk.CTkFont("Roboto", 13))


# ─── APP PRINCIPAL ────────────────────────────────────────────────────────────
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.title("SISFIG — Gestao de Desempenho em Concursos")
        self.geometry("1300x800")
        self.minsize(1050, 660)

        self._filtro_mes = None
        self._filtro_ano = None
        self._current_page = "dashboard"

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()

        self.main_container = ctk.CTkFrame(self, corner_radius=12, fg_color="#1c1c2e")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=(0, 12), pady=12)

        self.show_dashboard()

    # ── Sidebar ──────────────────────────────────────────────────────────────
    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=225, corner_radius=0, fg_color="#13131f")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        logo = ctk.CTkFrame(self.sidebar, fg_color="#0d0d1a", height=85, corner_radius=0)
        logo.pack(fill="x")
        ctk.CTkLabel(logo, text="SISFIG", font=ctk.CTkFont("Roboto", 24, weight="bold"),
                     text_color="#4a9eff").pack(pady=(18, 2))
        ctk.CTkLabel(logo, text="Gestao de Concursos",
                     font=ctk.CTkFont("Roboto", 10), text_color="#555577").pack(pady=(0, 15))

        ctk.CTkFrame(self.sidebar, height=1, fg_color="#252540").pack(fill="x")

        self._nav_buttons = {}
        nav_items = [
            ("dashboard",  "   Dashboard",        self.show_dashboard),
            ("registrar",  "   Lancar Bateria",   self.show_registrar),
            ("historico",  "   Historico",         self.show_historico),
            ("erros",      "   Erros Criticos",    self.show_erros),
            ("grafico",    "   Evolucao Mensal",   self.show_grafico),
            ("cadastro",   "   Cadastro",          self.show_cadastro),
        ]
        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.pack(fill="x", padx=8, pady=10)

        for key, label, cmd in nav_items:
            btn = SidebarButton(nav_frame, text=label,
                                command=lambda k=key, c=cmd: self._nav(k, c))
            btn.pack(fill="x", pady=2)
            self._nav_buttons[key] = btn

        ctk.CTkFrame(self.sidebar, height=1, fg_color="#252540").pack(fill="x", side="bottom", pady=0)
        ctk.CTkButton(
            self.sidebar, text="   Exportar Relatorio",
            command=self._exportar, anchor="w",
            fg_color="transparent", text_color="#888899",
            hover_color="#1a2a1a", height=38,
            font=ctk.CTkFont("Roboto", 12),
        ).pack(fill="x", padx=8, pady=6, side="bottom")

    def _nav(self, key, cmd):
        self._current_page = key
        for k, btn in self._nav_buttons.items():
            btn.set_active(k == key)
        cmd()

    def _set_active(self, key):
        self._current_page = key
        for k, btn in self._nav_buttons.items():
            btn.set_active(k == key)

    def clear_container(self):
        for w in self.main_container.winfo_children():
            w.destroy()

    # ── Filtro de periodo ─────────────────────────────────────────────────────
    def _build_filtro_bar(self, parent):
        bar = ctk.CTkFrame(parent, fg_color="#13131f", corner_radius=8, height=48)
        bar.pack(fill="x", padx=10, pady=(4, 6))
        bar.pack_propagate(False)

        ctk.CTkLabel(bar, text="Periodo:", font=ctk.CTkFont("Roboto", 12),
                     text_color="#888899").pack(side="left", padx=(14, 4))

        meses_label = ["Todos", "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
                        "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        self._var_mes = ctk.StringVar(value="Todos" if self._filtro_mes is None
                                      else meses_label[self._filtro_mes])

        ctk.CTkOptionMenu(bar, values=meses_label, variable=self._var_mes,
                          width=82, height=30, command=self._aplicar_filtro
                          ).pack(side="left", padx=4)

        df_tmp = self.db.ler_dados("LANCAMENTOS")
        anos = ["Todos"]
        if not df_tmp.empty:
            dts = pd.to_datetime(df_tmp["Data"], dayfirst=True, errors="coerce").dropna()
            anos += sorted(dts.dt.year.unique().astype(str).tolist(), reverse=True)
        ano_atual = str(datetime.now().year)
        if ano_atual not in anos:
            anos.append(ano_atual)

        self._var_ano = ctk.StringVar(value="Todos" if self._filtro_ano is None
                                      else str(self._filtro_ano))
        ctk.CTkOptionMenu(bar, values=anos, variable=self._var_ano,
                          width=88, height=30, command=self._aplicar_filtro
                          ).pack(side="left", padx=4)

        if self._filtro_mes or self._filtro_ano:
            partes = []
            if self._filtro_mes:
                partes.append(meses_label[self._filtro_mes])
            if self._filtro_ano:
                partes.append(str(self._filtro_ano))
            ctk.CTkLabel(bar, text=f"Filtro: {' '.join(partes)}",
                         font=ctk.CTkFont("Roboto", 11, weight="bold"),
                         text_color="#4a9eff").pack(side="right", padx=14)

    def _aplicar_filtro(self, _=None):
        meses_map = {"Todos": None, "Jan": 1, "Fev": 2, "Mar": 3, "Abr": 4,
                     "Mai": 5, "Jun": 6, "Jul": 7, "Ago": 8,
                     "Set": 9, "Out": 10, "Nov": 11, "Dez": 12}
        self._filtro_mes = meses_map.get(getattr(self, "_var_mes", ctk.StringVar()).get())
        ano_str = getattr(self, "_var_ano", ctk.StringVar()).get()
        self._filtro_ano = int(ano_str) if ano_str != "Todos" else None

        if self._current_page == "dashboard":
            self.show_dashboard()
        elif self._current_page == "historico":
            self.show_historico()

    def _filtrar_df(self, df):
        if df.empty or (self._filtro_mes is None and self._filtro_ano is None):
            return df
        df = df.copy()
        df["_dt"] = pd.to_datetime(df["Data"], dayfirst=True, errors="coerce")
        if self._filtro_mes:
            df = df[df["_dt"].dt.month == self._filtro_mes]
        if self._filtro_ano:
            df = df[df["_dt"].dt.year == self._filtro_ano]
        return df.drop(columns=["_dt"])

    # ── KPI card ──────────────────────────────────────────────────────────────
    def _kpi(self, parent, titulo, valor, cor, col, subtitulo=None):
        card = ctk.CTkFrame(parent, fg_color=cor, corner_radius=10, height=95)
        card.grid(row=0, column=col, padx=5, pady=4, sticky="ew")
        card.grid_propagate(False)
        ctk.CTkLabel(card, text=titulo,
                     font=ctk.CTkFont("Roboto", 11), text_color="#cccccc").pack(pady=(12, 0))
        ctk.CTkLabel(card, text=str(valor),
                     font=ctk.CTkFont("Roboto", 21, weight="bold"), text_color="#ffffff").pack()
        if subtitulo:
            ctk.CTkLabel(card, text=subtitulo,
                         font=ctk.CTkFont("Roboto", 9), text_color="#dddddd").pack(pady=(0, 8))

    # ─────────────────────────────────────────────────────────────────────────
    # DASHBOARD
    # ─────────────────────────────────────────────────────────────────────────
    def show_dashboard(self):
        self._set_active("dashboard")
        self.clear_container()

        df_l_all = self.db.ler_dados("LANCAMENTOS")
        df_e_all = self.db.ler_dados("ERROS")
        df_l = self._filtrar_df(df_l_all)

        # Titulo + filtro
        top = ctk.CTkFrame(self.main_container, fg_color="transparent")
        top.pack(fill="x", padx=12, pady=(14, 0))
        ctk.CTkLabel(top, text="Dashboard",
                     font=ctk.CTkFont("Roboto", 22, weight="bold"),
                     text_color="#4a9eff").pack(side="left")
        self._build_filtro_bar(self.main_container)

        # KPIs
        total_q = int(df_l["Total"].sum())   if not df_l.empty else 0
        total_a = int(df_l["Acertos"].sum()) if not df_l.empty else 0
        perc    = (total_a / total_q * 100) if total_q > 0 else 0

        ids_l       = set(df_l["ID Bateria"].dropna().unique())    if not df_l.empty else set()
        ids_e       = set(df_e_all["ID Bateria"].dropna().unique()) if not df_e_all.empty else set()
        pendentes   = len(ids_l - ids_e)
        total_erros = int(df_e_all["Qtd Erros"].sum()) if not df_e_all.empty else 0

        kf = ctk.CTkFrame(self.main_container, fg_color="transparent")
        kf.pack(fill="x", padx=12, pady=4)
        kf.columnconfigure((0, 1, 2, 3), weight=1)

        self._kpi(kf, "Total de Questoes", total_q, "#1a3a6e", 0)
        perc_cor = "#1a4a1a" if perc >= 80 else "#4a3a00" if perc >= 65 else "#4a1a1a"
        self._kpi(kf, "Acertos", f"{total_a}  ({perc:.1f}%)", perc_cor, 1)
        self._kpi(kf, "Erros Registrados", total_erros, "#3a0a5a", 2)
        alert_cor = "#4a3000" if pendentes > 0 else "#0a2a1a"
        sub_alerta = "  sem erros vinculados" if pendentes > 0 else "todas vinculadas"
        self._kpi(kf, "Baterias Pendentes", pendentes, alert_cor, 3, sub_alerta)

        # Corpo: tabela de materias + ranking de erros
        body = ctk.CTkFrame(self.main_container, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=12, pady=(4, 12))
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        self._tabela_materias(body, df_l)
        self._ranking_erros(body, df_e_all)

    def _tabela_materias(self, parent, df_l):
        frame = ctk.CTkFrame(parent, fg_color="#13131f", corner_radius=10)
        frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        ctk.CTkLabel(frame, text="Desempenho por Materia",
                     font=ctk.CTkFont("Roboto", 14, weight="bold"),
                     text_color="#4a9eff").pack(anchor="w", padx=14, pady=(12, 4))

        hdr = ctk.CTkFrame(frame, fg_color="#0d0d1a", height=28, corner_radius=0)
        hdr.pack(fill="x", padx=10)
        for txt, w, anc in [("MATERIA", 170, "w"), ("PROGRESSO", 160, "w"),
                             ("%", 60, "e"), ("Q / A", 80, "e")]:
            ctk.CTkLabel(hdr, text=txt, width=w, anchor=anc,
                         font=ctk.CTkFont("Roboto", 10, weight="bold"),
                         text_color="#555577").pack(side="left", padx=6)

        scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent", corner_radius=0)
        scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        if df_l.empty:
            ctk.CTkLabel(scroll, text="Nenhum dado disponivel.",
                         text_color="#444455").pack(pady=20)
            return

        resumo = df_l.groupby("Materia").agg(Acertos=("Acertos", "sum"),
                                              Total=("Total", "sum"))
        resumo["Perc"] = (resumo["Acertos"] / resumo["Total"] * 100).fillna(0)
        resumo = resumo.sort_values("Perc", ascending=False)

        for i, (mat, row) in enumerate(resumo.iterrows()):
            p   = row["Perc"]
            cor = "#228B22" if p >= 80 else "#DAA520" if p >= 65 else "#B22222"
            bg  = "#222232" if i % 2 == 0 else "#1c1c2c"

            f = ctk.CTkFrame(scroll, fg_color=bg, height=36, corner_radius=5)
            f.pack(fill="x", pady=1)
            f.pack_propagate(False)

            ctk.CTkLabel(f, text=str(mat), width=170, anchor="w",
                         font=ctk.CTkFont("Roboto", 12)).pack(side="left", padx=6)

            pb = ctk.CTkProgressBar(f, progress_color=cor, width=150, height=9, corner_radius=5)
            pb.set(p / 100)
            pb.pack(side="left", padx=5, pady=10)

            ctk.CTkLabel(f, text=f"{p:.1f}%", width=60, anchor="e",
                         font=ctk.CTkFont("Roboto", 12, weight="bold"),
                         text_color=cor).pack(side="left", padx=4)

            ctk.CTkLabel(f, text=f"{int(row['Total'])} / {int(row['Acertos'])}",
                         width=80, anchor="e",
                         font=ctk.CTkFont("Roboto", 10), text_color="#666677").pack(side="right", padx=8)

    def _ranking_erros(self, parent, df_e):
        frame = ctk.CTkFrame(parent, fg_color="#13131f", corner_radius=10)
        frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        ctk.CTkLabel(frame, text="Top Erros por Topico",
                     font=ctk.CTkFont("Roboto", 14, weight="bold"),
                     text_color="#e05050").pack(anchor="w", padx=14, pady=(12, 4))

        scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent", corner_radius=0)
        scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        if df_e.empty:
            ctk.CTkLabel(scroll, text="Nenhum erro registrado.",
                         text_color="#444455").pack(pady=20)
            return

        resumo = (df_e.groupby("Topico")["Qtd Erros"]
                  .sum().sort_values(ascending=False).reset_index())
        max_e = resumo["Qtd Erros"].max() or 1

        for i, row in resumo.head(18).iterrows():
            bg  = "#222232" if i % 2 == 0 else "#1c1c2c"
            f   = ctk.CTkFrame(scroll, fg_color=bg, height=40, corner_radius=5)
            f.pack(fill="x", pady=1)
            f.pack_propagate(False)

            rank = i + 1
            badge_c = "#8b1a1a" if rank <= 3 else "#5a3000" if rank <= 7 else "#2a2a3a"
            badge = ctk.CTkFrame(f, fg_color=badge_c, width=26, height=26, corner_radius=13)
            badge.pack(side="left", padx=(8, 4), pady=7)
            badge.pack_propagate(False)
            ctk.CTkLabel(badge, text=str(rank),
                         font=ctk.CTkFont("Roboto", 9, weight="bold"), width=26).pack(expand=True)

            qtd = int(row["Qtd Erros"])
            ctk.CTkLabel(f, text=str(row["Topico"])[:28], anchor="w",
                         font=ctk.CTkFont("Roboto", 11)).pack(side="left", padx=4, expand=True)

            ctk.CTkLabel(f, text=str(qtd), width=32, anchor="e",
                         font=ctk.CTkFont("Roboto", 12, weight="bold"),
                         text_color="#e05050").pack(side="right", padx=4)

            frac = qtd / max_e
            bw   = 55
            bar_bg = ctk.CTkFrame(f, fg_color="#2a2a3a", width=bw, height=7, corner_radius=3)
            bar_bg.pack(side="right", padx=(0, 4))
            bar_bg.pack_propagate(False)
            ctk.CTkFrame(bar_bg, fg_color="#b22222",
                         width=max(3, int(bw * frac)), height=7,
                         corner_radius=3).place(x=0, y=0)

    # ─────────────────────────────────────────────────────────────────────────
    # LANCAR BATERIA  (suporta mono e multidisciplinar)
    # ─────────────────────────────────────────────────────────────────────────
    def show_registrar(self):
        self._set_active("registrar")
        self.clear_container()

        outer = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent")
        outer.pack(fill="both", expand=True, padx=14, pady=14)

        ctk.CTkLabel(outer, text="Lancar Nova Bateria",
                     font=ctk.CTkFont("Roboto", 20, weight="bold"),
                     text_color="#4a9eff").pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(outer,
                     text="Adicione quantas materias/disciplinas quiser antes de finalizar.",
                     font=ctk.CTkFont("Roboto", 11), text_color="#555577").pack(anchor="w", pady=(0, 10))

        # ── Bloco 1: dados fixos da bateria ──────────────────────────────────
        card_bat = ctk.CTkFrame(outer, fg_color="#13131f", corner_radius=12)
        card_bat.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(card_bat, text="Identificacao da Bateria",
                     font=ctk.CTkFont("Roboto", 12, weight="bold"),
                     text_color="#666688").pack(anchor="w", padx=18, pady=(14, 6))

        fb = ctk.CTkFrame(card_bat, fg_color="transparent")
        fb.pack(padx=18, pady=(0, 16), fill="x")
        fb.columnconfigure((0, 1, 2), weight=1)

        sugestao = self.db.gerar_proximo_id()
        hoje     = datetime.now().strftime("%d/%m/%Y")

        def _mk_entry(parent, label, placeholder, prefill, row, col, colspan=1):
            ctk.CTkLabel(parent, text=label, font=ctk.CTkFont("Roboto", 11),
                         text_color="#9999bb").grid(row=row * 2, column=col,
                                                    columnspan=colspan, sticky="w",
                                                    padx=(0, 12), pady=(4, 2))
            e = ctk.CTkEntry(parent, placeholder_text=placeholder, height=34)
            e.grid(row=row * 2 + 1, column=col, columnspan=colspan,
                   sticky="ew", padx=(0, 12), pady=(0, 8))
            if prefill:
                e.insert(0, prefill)
            return e

        ctk.CTkLabel(fb, text="ID da Bateria", font=ctk.CTkFont("Roboto", 11),
                     text_color="#9999bb").grid(row=0, column=0, sticky="w",
                                                padx=(0, 12), pady=(4, 2))
        en_id = ctk.CTkEntry(fb, height=34, fg_color="#0d0d1a", text_color="#4a9eff",
                             font=ctk.CTkFont("Roboto", 12, weight="bold"))
        en_id.insert(0, sugestao)
        en_id.configure(state="disabled")
        en_id.grid(row=1, column=0, sticky="ew", padx=(0, 12), pady=(0, 8))
        en_data  = _mk_entry(fb, "Data",            "DD/MM/AAAA",                hoje,     0, 1)
        en_fonte = _mk_entry(fb, "Fonte principal", "GURUJA / GEMINI / TEC / ...", "",     0, 2)

        # ── Bloco 2: lista de materias ja adicionadas ─────────────────────────
        card_lista = ctk.CTkFrame(outer, fg_color="#13131f", corner_radius=10)
        card_lista.pack(fill="x", pady=(0, 8))

        lbl_resumo = ctk.CTkLabel(card_lista,
                                   text="Materias nesta bateria: 0  |  Total: 0 questoes  |  Acertos: 0",
                                   font=ctk.CTkFont("Roboto", 11), text_color="#666677")
        lbl_resumo.pack(anchor="w", padx=14, pady=(10, 4))

        hdr_lista = ctk.CTkFrame(card_lista, fg_color="#0d0d1a", height=24, corner_radius=0)
        hdr_lista.pack(fill="x", padx=14)
        for txt, w in [("Materia", 130), ("Subtopico / Assunto", 260),
                       ("Acertos", 72), ("Total", 72), ("%", 72)]:
            ctk.CTkLabel(hdr_lista, text=txt, width=w, anchor="w",
                         font=ctk.CTkFont("Roboto", 9, weight="bold"),
                         text_color="#555577").pack(side="left", padx=4)

        itens_frame = ctk.CTkFrame(card_lista, fg_color="transparent")
        itens_frame.pack(fill="x", padx=14, pady=(0, 10))

        # entradas salvas: [materia, acertos, total, subtopico]
        entradas = []

        def _atualizar_lista():
            for w in itens_frame.winfo_children():
                w.destroy()
            tot_q = sum(e[2] for e in entradas)
            tot_a = sum(e[1] for e in entradas)
            perc_g = f"{tot_a/tot_q*100:.1f}%" if tot_q > 0 else "—"
            lbl_resumo.configure(
                text=f"Materias nesta bateria: {len(entradas)}"
                     f"  |  Total: {tot_q} questoes"
                     f"  |  Acertos: {tot_a}  ({perc_g})"
            )
            for i, (mat, ace, tot, sub) in enumerate(entradas):
                p   = ace / tot * 100 if tot > 0 else 0
                p_c = "#228B22" if p >= 80 else "#DAA520" if p >= 65 else "#B22222"
                bg  = "#1e1e30" if i % 2 == 0 else "#191928"
                f   = ctk.CTkFrame(itens_frame, fg_color=bg, height=30, corner_radius=4)
                f.pack(fill="x", pady=1)
                f.pack_propagate(False)
                ctk.CTkLabel(f, text=mat, width=130, anchor="w",
                             font=ctk.CTkFont("Roboto", 11, weight="bold")).pack(side="left", padx=4)
                ctk.CTkLabel(f, text=str(sub)[:38], width=260, anchor="w",
                             font=ctk.CTkFont("Roboto", 10),
                             text_color="#888899").pack(side="left", padx=4)
                ctk.CTkLabel(f, text=str(ace), width=72, anchor="center",
                             font=ctk.CTkFont("Roboto", 11)).pack(side="left", padx=4)
                ctk.CTkLabel(f, text=str(tot), width=72, anchor="center",
                             font=ctk.CTkFont("Roboto", 11)).pack(side="left", padx=4)
                ctk.CTkLabel(f, text=f"{p:.1f}%", width=72, anchor="center",
                             font=ctk.CTkFont("Roboto", 11, weight="bold"),
                             text_color=p_c).pack(side="left", padx=4)

        # ── Bloco 3: formulario de cada materia ───────────────────────────────
        card_mat = ctk.CTkFrame(outer, fg_color="#13131f", corner_radius=12)
        card_mat.pack(fill="x")

        ctk.CTkLabel(card_mat, text="Adicionar Materia / Disciplina",
                     font=ctk.CTkFont("Roboto", 12, weight="bold"),
                     text_color="#666688").pack(anchor="w", padx=18, pady=(14, 6))

        fm = ctk.CTkFrame(card_mat, fg_color="transparent")
        fm.pack(padx=18, pady=(0, 4), fill="x")
        fm.columnconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkLabel(fm, text="Materia / Disciplina", font=ctk.CTkFont("Roboto", 11),
                     text_color="#9999bb").grid(row=0, column=0, sticky="w",
                                                padx=(0, 12), pady=(4, 2))
        ctk.CTkLabel(fm, text="Subtopico / Assunto", font=ctk.CTkFont("Roboto", 11),
                     text_color="#9999bb").grid(row=0, column=3, sticky="w",
                                                padx=(0, 12), pady=(4, 2))

        en_sub = ctk.CTkComboBox(fm, values=[""], height=34)
        en_sub.grid(row=1, column=3, sticky="ew", padx=(0, 12), pady=(0, 8))
        en_sub.set("")

        def _on_mat_change(mat):
            assuntos = self.db.get_assuntos(mat)
            en_sub.configure(values=assuntos if assuntos else [""])
            en_sub.set(assuntos[0] if assuntos else "")

        materias_lista = self.db.get_materias()
        en_mat = ctk.CTkComboBox(fm, values=materias_lista if materias_lista else [""],
                                  height=34, command=_on_mat_change)
        en_mat.grid(row=1, column=0, sticky="ew", padx=(0, 12), pady=(0, 8))
        en_mat.set("")

        en_ace = _mk_entry(fm, "Acertos",           "0", "0", 0, 1)
        en_tot = _mk_entry(fm, "Total de Questoes", "0", "0", 0, 2)

        def _coletar_materia():
            mat = en_mat.get().strip()
            sub = en_sub.get().strip()
            if not mat:
                raise ValueError("Informe a Materia / Disciplina.")
            try:
                ace = int(en_ace.get().strip() or 0)
                tot = int(en_tot.get().strip() or 0)
            except ValueError:
                raise ValueError("Acertos e Total devem ser numeros inteiros.")
            if tot <= 0:
                raise ValueError("Total de questoes deve ser maior que zero.")
            if ace > tot:
                raise ValueError(f"Acertos ({ace}) nao pode ser maior que Total ({tot}).")
            return mat, ace, tot, sub

        def _limpar_mat():
            en_mat.set("")
            en_sub.set("")
            en_ace.delete(0, "end"); en_ace.insert(0, "0")
            en_tot.delete(0, "end"); en_tot.insert(0, "0")

        def _validar_cabecalho():
            id_b  = en_id.get().strip()
            data  = en_data.get().strip()
            fonte = en_fonte.get().strip()
            if not id_b:
                raise ValueError("ID da Bateria e obrigatorio.")
            return id_b, data, fonte

        def _salvar_entrada(mat, ace, tot, sub):
            id_b, data, fonte = _validar_cabecalho()
            perc = round(ace / tot * 100, 1)
            self.db.salvar_bateria([id_b, mat, data, ace, tot, fonte, sub, perc])
            entradas.append((mat, ace, tot, sub))
            _atualizar_lista()

        def adicionar_materia():
            try:
                mat, ace, tot, sub = _coletar_materia()
                _salvar_entrada(mat, ace, tot, sub)
                _limpar_mat()
            except ValueError as exc:
                messagebox.showerror("Dados Invalidos", str(exc))

        def finalizar():
            # Se o campo Materia esta preenchido, tenta salvar a entrada atual tbm
            if en_mat.get().strip():
                try:
                    mat, ace, tot, sub = _coletar_materia()
                    _salvar_entrada(mat, ace, tot, sub)
                    _limpar_mat()
                except ValueError as exc:
                    messagebox.showerror("Dados Invalidos", str(exc))
                    return

            if not entradas:
                messagebox.showwarning("Atencao",
                                       "Adicione pelo menos uma materia antes de finalizar.")
                return

            id_b  = en_id.get().strip()
            tot_q = sum(e[2] for e in entradas)
            tot_a = sum(e[1] for e in entradas)
            mats  = ", ".join(dict.fromkeys(e[0] for e in entradas))
            perc_g = tot_a / tot_q * 100 if tot_q > 0 else 0

            if messagebox.askyesno(
                    "Bateria Finalizada!",
                    f"Bateria {id_b}\n"
                    f"Materias: {mats}\n"
                    f"{tot_a}/{tot_q} questoes  ({perc_g:.1f}%)\n\n"
                    "Deseja registrar os erros desta bateria agora?"):
                self.show_registrar_erro(id_b, mats)
            else:
                self.show_dashboard()

        btn_row = ctk.CTkFrame(card_mat, fg_color="transparent")
        btn_row.pack(fill="x", padx=18, pady=(0, 18))

        ctk.CTkButton(btn_row, text="+ Adicionar Materia", height=40,
                      fg_color="#1a3050", hover_color="#1f538d",
                      font=ctk.CTkFont("Roboto", 12),
                      command=adicionar_materia).pack(side="left")
        ctk.CTkButton(btn_row, text="Finalizar Bateria", height=40,
                      fg_color="#1a4a1a", hover_color="#228B22",
                      font=ctk.CTkFont("Roboto", 12, weight="bold"),
                      command=finalizar).pack(side="left", padx=8)
        ctk.CTkButton(btn_row, text="Cancelar", height=40,
                      fg_color="transparent", text_color="#666677",
                      hover_color="#222233", font=ctk.CTkFont("Roboto", 12),
                      command=self.show_dashboard).pack(side="left")

    # ─────────────────────────────────────────────────────────────────────────
    # REGISTRAR ERROS
    # ─────────────────────────────────────────────────────────────────────────
    def show_registrar_erro(self, id_bateria, materia):
        self.clear_container()

        outer = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent")
        outer.pack(fill="both", expand=True, padx=14, pady=14)

        ctk.CTkLabel(outer, text=f"Registrar Erros — {id_bateria}",
                     font=ctk.CTkFont("Roboto", 20, weight="bold"),
                     text_color="#e05050").pack(anchor="w", pady=(0, 2))
        ctk.CTkLabel(outer, text=f"Disciplina(s): {materia}",
                     font=ctk.CTkFont("Roboto", 12), text_color="#888899").pack(anchor="w", pady=(0, 10))

        # Painel de registrados
        reg_frame = ctk.CTkFrame(outer, fg_color="#13131f", corner_radius=10)
        reg_frame.pack(fill="x", pady=(0, 8))
        lbl_count = ctk.CTkLabel(reg_frame, text="Topicos registrados nesta sessao: 0",
                                  font=ctk.CTkFont("Roboto", 11), text_color="#666677")
        lbl_count.pack(anchor="w", padx=14, pady=(8, 4))
        lista_frame = ctk.CTkFrame(reg_frame, fg_color="transparent")
        lista_frame.pack(anchor="w", padx=14, pady=(0, 8))
        registrados = []

        # Formulario
        card = ctk.CTkFrame(outer, fg_color="#13131f", corner_radius=12)
        card.pack(fill="x")

        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(padx=24, pady=20, fill="x")
        form.columnconfigure(0, weight=1)

        def campo(label, placeholder, r):
            ctk.CTkLabel(form, text=label, font=ctk.CTkFont("Roboto", 12),
                         text_color="#9999bb").grid(row=r * 2, column=0, sticky="w", pady=(6, 2))
            e = ctk.CTkEntry(form, placeholder_text=placeholder, height=36)
            e.grid(row=r * 2 + 1, column=0, sticky="ew", pady=(0, 8))
            return e

        en_mat_e  = campo("Materia do Erro",     materia if "," not in materia else "",          0)
        en_topico = campo("Topico do Erro",     "Ex: Processo Administrativo — Fases",         1)
        en_qtd    = campo("Quantidade de Erros", "Ex: 3",                                       2)
        en_obs    = campo("Observacao",          "Ex: Confundiu prazo recursal com prazo de ato",3)
        en_prov   = campo("Providencia",         "Ex: Revisar flashcard / refazer questoes CEI", 4)
        if "," not in materia:
            en_mat_e.insert(0, materia)

        def _limpar():
            for e in (en_topico, en_qtd, en_obs, en_prov):
                e.delete(0, "end")
            if "," in materia:
                en_mat_e.delete(0, "end")

        def _coletar():
            mat_erro = en_mat_e.get().strip()
            topico   = en_topico.get().strip()
            qtd_s    = en_qtd.get().strip()
            obs      = en_obs.get().strip()
            prov     = en_prov.get().strip()
            if not mat_erro:
                raise ValueError("Materia do erro e obrigatoria.")
            if not topico:
                raise ValueError("Topico do erro e obrigatorio.")
            try:
                qtd = int(qtd_s)
                if qtd <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                raise ValueError("Quantidade de erros deve ser um numero inteiro positivo.")
            return [id_bateria, mat_erro, topico, qtd,
                    datetime.now().strftime("%d/%m/%Y"), obs, prov]

        def _atualizar_lista():
            for w in lista_frame.winfo_children():
                w.destroy()
            for t in registrados:
                ctk.CTkLabel(lista_frame, text=f"  {t}",
                             font=ctk.CTkFont("Roboto", 10),
                             text_color="#228B22").pack(anchor="w")
            lbl_count.configure(text=f"Topicos registrados nesta sessao: {len(registrados)}")

        def _adicionar():
            try:
                dados = _coletar()
                self.db.salvar_erro(dados)
                registrados.append(dados[2])
                _atualizar_lista()
                _limpar()
                en_topico.focus()
            except ValueError as exc:
                messagebox.showerror("Erro", str(exc))

        def _finalizar_com_erro():
            try:
                dados = _coletar()
                self.db.salvar_erro(dados)
                self.show_dashboard()
            except ValueError as exc:
                messagebox.showerror("Erro", str(exc))

        def _finalizar_sem_mais():
            self.show_dashboard()

        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(fill="x", padx=24, pady=(0, 20))

        ctk.CTkButton(btn_row, text="+ Adicionar Outro Topico", height=40,
                      fg_color="#1a3050", hover_color="#1f538d",
                      font=ctk.CTkFont("Roboto", 12),
                      command=_adicionar).pack(side="left")
        ctk.CTkButton(btn_row, text="Salvar e Finalizar", height=40,
                      fg_color="#1a4a1a", hover_color="#228B22",
                      font=ctk.CTkFont("Roboto", 12, weight="bold"),
                      command=_finalizar_com_erro).pack(side="left", padx=8)
        ctk.CTkButton(btn_row, text="Finalizar sem mais erros", height=40,
                      fg_color="transparent", text_color="#666677",
                      hover_color="#222233",
                      font=ctk.CTkFont("Roboto", 12),
                      command=_finalizar_sem_mais).pack(side="left")

    # ─────────────────────────────────────────────────────────────────────────
    # HISTORICO
    # ─────────────────────────────────────────────────────────────────────────
    def show_historico(self, page=0):
        self._set_active("historico")
        self.clear_container()

        df_l_all = self.db.ler_dados("LANCAMENTOS")
        df_e     = self.db.ler_dados("ERROS")
        df_l     = self._filtrar_df(df_l_all)

        ctk.CTkLabel(self.main_container, text="Historico de Baterias",
                     font=ctk.CTkFont("Roboto", 20, weight="bold"),
                     text_color="#4a9eff").pack(anchor="w", padx=14, pady=(14, 4))

        self._build_filtro_bar(self.main_container)

        PAGE = 20
        total      = len(df_l)
        total_pag  = max(1, (total + PAGE - 1) // PAGE)
        page       = max(0, min(page, total_pag - 1))

        ids_e = set(df_e["ID Bateria"].dropna().unique()) if not df_e.empty else set()

        # Header tabela
        hdr = ctk.CTkFrame(self.main_container, fg_color="#0d0d1a", height=32, corner_radius=0)
        hdr.pack(fill="x", padx=12)
        cols_hdr = [("ID", 80, "w"), ("Materia", 190, "w"), ("Data", 95, "w"),
                    ("Acertos", 70, "c"), ("Total", 70, "c"), ("%", 68, "c"),
                    ("Fonte", 110, "w"), ("Status", 120, "e")]
        for txt, w, _ in cols_hdr:
            ctk.CTkLabel(hdr, text=txt, width=w, anchor="w",
                         font=ctk.CTkFont("Roboto", 10, weight="bold"),
                         text_color="#555577").pack(side="left", padx=4)

        scroll = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent", corner_radius=0)
        scroll.pack(fill="both", expand=True, padx=12)

        if df_l.empty:
            ctk.CTkLabel(scroll, text="Nenhum lancamento encontrado.",
                         text_color="#444455", font=ctk.CTkFont("Roboto", 13)).pack(pady=30)
        else:
            df_page = df_l.iloc[page * PAGE: page * PAGE + PAGE]
            for i, (_, row) in enumerate(df_page.iterrows()):
                bg = "#1e1e30" if i % 2 == 0 else "#191928"
                f  = ctk.CTkFrame(scroll, fg_color=bg, height=34, corner_radius=4)
                f.pack(fill="x", pady=1)
                f.pack_propagate(False)

                id_b    = str(row.get("ID Bateria", ""))
                tem_err = id_b in ids_e
                pct     = float(row.get("Percentual", 0))
                pct_c   = "#228B22" if pct >= 80 else "#DAA520" if pct >= 65 else "#B22222"

                ctk.CTkLabel(f, text=id_b, width=80, anchor="w",
                             font=ctk.CTkFont("Roboto", 11)).pack(side="left", padx=4)
                ctk.CTkLabel(f, text=str(row.get("Materia", ""))[:24],
                             width=190, anchor="w",
                             font=ctk.CTkFont("Roboto", 11)).pack(side="left", padx=4)
                ctk.CTkLabel(f, text=str(row.get("Data", "")), width=95, anchor="w",
                             font=ctk.CTkFont("Roboto", 10),
                             text_color="#888899").pack(side="left", padx=4)
                ctk.CTkLabel(f, text=str(int(row.get("Acertos", 0))),
                             width=70, anchor="center",
                             font=ctk.CTkFont("Roboto", 11)).pack(side="left", padx=4)
                ctk.CTkLabel(f, text=str(int(row.get("Total", 0))),
                             width=70, anchor="center",
                             font=ctk.CTkFont("Roboto", 11)).pack(side="left", padx=4)
                ctk.CTkLabel(f, text=f"{pct:.1f}%", width=68, anchor="center",
                             font=ctk.CTkFont("Roboto", 11, weight="bold"),
                             text_color=pct_c).pack(side="left", padx=4)
                ctk.CTkLabel(f, text=str(row.get("Fonte", ""))[:14],
                             width=110, anchor="w",
                             font=ctk.CTkFont("Roboto", 10),
                             text_color="#666677").pack(side="left", padx=4)

                if tem_err:
                    sb = ctk.CTkFrame(f, fg_color="#0d2a0d", corner_radius=5)
                    ctk.CTkLabel(sb, text="Com erros",
                                 font=ctk.CTkFont("Roboto", 9),
                                 text_color="#4caf50").pack(padx=6, pady=3)
                else:
                    sb = ctk.CTkFrame(f, fg_color="#3a2000", corner_radius=5)
                    ctk.CTkLabel(sb, text="Pendente",
                                 font=ctk.CTkFont("Roboto", 9),
                                 text_color="#FFD700").pack(padx=6, pady=3)
                sb.pack(side="right", padx=8, pady=4)

        # Paginacao
        pag = ctk.CTkFrame(self.main_container, fg_color="transparent", height=40)
        pag.pack(fill="x", padx=12, pady=5)
        ctk.CTkLabel(pag, text=f"Pagina {page + 1} de {total_pag}  ({total} registros)",
                     font=ctk.CTkFont("Roboto", 11), text_color="#555577").pack(side="left", padx=10)
        if page < total_pag - 1:
            ctk.CTkButton(pag, text="Proximo", width=90, height=28,
                          fg_color="#1f538d",
                          command=lambda: self.show_historico(page + 1)).pack(side="right", padx=4)
        if page > 0:
            ctk.CTkButton(pag, text="Anterior", width=90, height=28,
                          fg_color="#1f538d",
                          command=lambda: self.show_historico(page - 1)).pack(side="right", padx=4)

    # ─────────────────────────────────────────────────────────────────────────
    # ERROS CRITICOS
    # ─────────────────────────────────────────────────────────────────────────
    def show_erros(self):
        self._set_active("erros")
        self.clear_container()

        df = self.db.ler_dados("ERROS")

        ctk.CTkLabel(self.main_container, text="Topicos com Mais Erros",
                     font=ctk.CTkFont("Roboto", 20, weight="bold"),
                     text_color="#e05050").pack(anchor="w", padx=14, pady=(14, 6))

        if df.empty:
            ctk.CTkLabel(self.main_container, text="Nenhum erro registrado ainda.",
                         font=ctk.CTkFont("Roboto", 14), text_color="#444455").pack(pady=40)
            return

        # Resumo rapido
        info = ctk.CTkFrame(self.main_container, fg_color="#13131f", corner_radius=8, height=42)
        info.pack(fill="x", padx=14, pady=(0, 6))
        info.pack_propagate(False)
        total_e = int(df["Qtd Erros"].sum())
        total_t = df["Topico"].nunique()
        ctk.CTkLabel(info, text=f"Total: {total_e} erros em {total_t} topicos distintos",
                     font=ctk.CTkFont("Roboto", 12), text_color="#888899").pack(side="left", padx=14)

        # Header tabela
        hdr = ctk.CTkFrame(self.main_container, fg_color="#0d0d1a", height=30, corner_radius=0)
        hdr.pack(fill="x", padx=14)
        for txt, w in [("#", 36), ("Topico", 185), ("Materia", 145), ("Erros", 58),
                       ("Data", 88), ("Observacao", 220), ("Providencia", 195)]:
            ctk.CTkLabel(hdr, text=txt, width=w, anchor="w",
                         font=ctk.CTkFont("Roboto", 10, weight="bold"),
                         text_color="#555577").pack(side="left", padx=4)

        scroll = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=14, pady=(0, 12))

        df_s = df.sort_values("Qtd Erros", ascending=False).reset_index(drop=True)

        for i, row in df_s.iterrows():
            bg = "#1e1e30" if i % 2 == 0 else "#191928"
            f  = ctk.CTkFrame(scroll, fg_color=bg, height=38, corner_radius=4)
            f.pack(fill="x", pady=1)
            f.pack_propagate(False)

            qtd   = int(row.get("Qtd Erros", 0))
            e_cor = "#B22222" if qtd >= 5 else "#DAA520" if qtd >= 3 else "#888899"

            ctk.CTkLabel(f, text=str(i + 1), width=36, anchor="w",
                         font=ctk.CTkFont("Roboto", 10),
                         text_color="#444455").pack(side="left", padx=4)
            ctk.CTkLabel(f, text=str(row.get("Topico", ""))[:22],
                         width=185, anchor="w",
                         font=ctk.CTkFont("Roboto", 11, weight="bold")).pack(side="left", padx=4)
            ctk.CTkLabel(f, text=str(row.get("Materia", ""))[:18],
                         width=145, anchor="w",
                         font=ctk.CTkFont("Roboto", 10),
                         text_color="#888899").pack(side="left", padx=4)
            ctk.CTkLabel(f, text=str(qtd), width=58, anchor="center",
                         font=ctk.CTkFont("Roboto", 13, weight="bold"),
                         text_color=e_cor).pack(side="left", padx=4)
            ctk.CTkLabel(f, text=str(row.get("Data", "")), width=88, anchor="w",
                         font=ctk.CTkFont("Roboto", 10),
                         text_color="#666677").pack(side="left", padx=4)
            ctk.CTkLabel(f, text=str(row.get("Observacao", ""))[:30],
                         width=220, anchor="w",
                         font=ctk.CTkFont("Roboto", 10),
                         text_color="#cccccc").pack(side="left", padx=4)
            ctk.CTkLabel(f, text=str(row.get("Providencia", ""))[:28],
                         width=195, anchor="w",
                         font=ctk.CTkFont("Roboto", 10),
                         text_color="#6699dd").pack(side="left", padx=4)

    # ─────────────────────────────────────────────────────────────────────────
    # GRAFICO — EVOLUCAO MENSAL
    # ─────────────────────────────────────────────────────────────────────────
    def show_grafico(self):
        self._set_active("grafico")
        self.clear_container()

        ctk.CTkLabel(self.main_container, text="Evolucao Mensal por Materia",
                     font=ctk.CTkFont("Roboto", 20, weight="bold"),
                     text_color="#4a9eff").pack(anchor="w", padx=14, pady=(14, 6))

        df = self.db.ler_dados("LANCAMENTOS")

        if df.empty:
            ctk.CTkLabel(self.main_container, text="Sem dados para exibir o grafico.",
                         font=ctk.CTkFont("Roboto", 14), text_color="#444455").pack(pady=40)
            return

        df = df.copy()
        df["_dt"]  = pd.to_datetime(df["Data"], dayfirst=True, errors="coerce")
        df         = df.dropna(subset=["_dt"])
        df["Mes"]  = df["_dt"].dt.to_period("M")

        resumo = (df.groupby(["Mes", "Materia"])
                    .agg(Acertos=("Acertos", "sum"), Total=("Total", "sum"))
                    .reset_index())
        resumo["Perc"] = (resumo["Acertos"] / resumo["Total"] * 100).fillna(0)

        materias = resumo["Materia"].unique()

        plt.style.use("dark_background")
        fig, ax = plt.subplots(figsize=(9, 4.8), facecolor="#1c1c2e")
        ax.set_facecolor("#13131f")

        cores = plt.cm.tab10.colors
        for idx, mat in enumerate(materias):
            sub  = resumo[resumo["Materia"] == mat].sort_values("Mes")
            mstr = [str(m) for m in sub["Mes"]]
            ax.plot(mstr, sub["Perc"], marker="o", label=mat,
                    color=cores[idx % len(cores)], linewidth=2, markersize=6)

        ax.axhline(80, color="#228B22", linestyle="--", alpha=0.5, linewidth=1.2, label="Meta 80%")
        ax.axhline(65, color="#DAA520", linestyle=":",  alpha=0.5, linewidth=1.2, label="Limite 65%")

        ax.set_ylim(0, 108)
        ax.set_ylabel("% de Acertos", color="#888899", fontsize=11)
        ax.set_xlabel("Mes", color="#888899", fontsize=11)
        ax.tick_params(colors="#888899")
        plt.xticks(rotation=30, ha="right")
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
        ax.spines["bottom"].set_color("#252540")
        ax.spines["left"].set_color("#252540")
        ax.grid(axis="y", color="#252540", linewidth=0.6)
        ax.legend(facecolor="#13131f", edgecolor="#252540",
                  labelcolor="white", fontsize=9, loc="upper left")
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.main_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=14, pady=(0, 14))

    # ─────────────────────────────────────────────────────────────────────────
    # CADASTRO DE MATERIAS E ASSUNTOS
    # ─────────────────────────────────────────────────────────────────────────
    def show_cadastro(self):
        self._set_active("cadastro")
        self.clear_container()

        ctk.CTkLabel(self.main_container, text="Cadastro de Materias e Assuntos",
                     font=ctk.CTkFont("Roboto", 20, weight="bold"),
                     text_color="#4a9eff").pack(anchor="w", padx=14, pady=(14, 6))

        body = ctk.CTkFrame(self.main_container, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        # ── Painel esquerdo: Materias ────────────────────────────────────────
        left = ctk.CTkFrame(body, fg_color="#13131f", corner_radius=12)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        ctk.CTkLabel(left, text="Materias",
                     font=ctk.CTkFont("Roboto", 14, weight="bold"),
                     text_color="#4a9eff").pack(anchor="w", padx=14, pady=(12, 6))

        add_mat_frame = ctk.CTkFrame(left, fg_color="transparent")
        add_mat_frame.pack(fill="x", padx=14, pady=(0, 8))
        en_nova_mat = ctk.CTkEntry(add_mat_frame, placeholder_text="Nova materia...", height=34)
        en_nova_mat.pack(side="left", fill="x", expand=True, padx=(0, 6))

        mat_scroll = ctk.CTkScrollableFrame(left, fg_color="transparent")
        mat_scroll.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        # ── Painel direito: Assuntos ─────────────────────────────────────────
        right = ctk.CTkFrame(body, fg_color="#13131f", corner_radius=12)
        right.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        ctk.CTkLabel(right, text="Assuntos",
                     font=ctk.CTkFont("Roboto", 14, weight="bold"),
                     text_color="#4a9eff").pack(anchor="w", padx=14, pady=(12, 6))

        lbl_mat_sel = ctk.CTkLabel(right, text="Selecione uma materia ao lado",
                                    font=ctk.CTkFont("Roboto", 11), text_color="#555577")
        lbl_mat_sel.pack(anchor="w", padx=14, pady=(0, 4))

        add_ass_frame = ctk.CTkFrame(right, fg_color="transparent")
        add_ass_frame.pack(fill="x", padx=14, pady=(0, 8))
        en_novo_ass = ctk.CTkEntry(add_ass_frame, placeholder_text="Novo assunto...", height=34)
        en_novo_ass.pack(side="left", fill="x", expand=True, padx=(0, 6))

        ass_scroll = ctk.CTkScrollableFrame(right, fg_color="transparent")
        ass_scroll.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        mat_selecionada = [None]

        def _refresh_assuntos():
            for w in ass_scroll.winfo_children():
                w.destroy()
            if not mat_selecionada[0]:
                return
            lbl_mat_sel.configure(text=f"Materia selecionada:  {mat_selecionada[0]}")
            for ass in self.db.get_assuntos(mat_selecionada[0]):
                row_f = ctk.CTkFrame(ass_scroll, fg_color="#1e1e30", height=34, corner_radius=4)
                row_f.pack(fill="x", pady=1)
                row_f.pack_propagate(False)
                ctk.CTkLabel(row_f, text=ass, anchor="w",
                             font=ctk.CTkFont("Roboto", 11)).pack(side="left", padx=8,
                                                                   fill="x", expand=True)
                ctk.CTkButton(row_f, text="✕", width=28, height=24,
                              fg_color="#4a1a1a", hover_color="#8b1a1a",
                              font=ctk.CTkFont("Roboto", 10),
                              command=lambda a=ass: _remover_assunto(a)).pack(side="right", padx=4)

        def _refresh_materias():
            for w in mat_scroll.winfo_children():
                w.destroy()
            for mat in self.db.get_materias():
                row_f = ctk.CTkFrame(mat_scroll, fg_color="#1e1e30", height=34, corner_radius=4)
                row_f.pack(fill="x", pady=1)
                row_f.pack_propagate(False)
                is_sel = (mat_selecionada[0] == mat)
                ctk.CTkButton(row_f, text=mat, anchor="w",
                              fg_color="#1f538d" if is_sel else "#1e1e30",
                              hover_color="#1f538d", text_color="#ffffff",
                              font=ctk.CTkFont("Roboto", 11),
                              command=lambda m=mat: _selecionar_mat(m)).pack(
                                  side="left", fill="x", expand=True, padx=(4, 0))
                ctk.CTkButton(row_f, text="✕", width=28, height=24,
                              fg_color="#4a1a1a", hover_color="#8b1a1a",
                              font=ctk.CTkFont("Roboto", 10),
                              command=lambda m=mat: _remover_materia(m)).pack(side="right", padx=4)

        def _selecionar_mat(mat):
            mat_selecionada[0] = mat
            _refresh_materias()
            _refresh_assuntos()

        def _adicionar_materia():
            nova = en_nova_mat.get().strip()
            if not nova:
                messagebox.showwarning("Atencao", "Informe o nome da materia.")
                return
            if nova in self.db.get_materias():
                messagebox.showwarning("Atencao", f"A materia '{nova}' ja existe.")
                return
            self.db.salvar_cadastro(nova, "")
            en_nova_mat.delete(0, "end")
            mat_selecionada[0] = nova
            _refresh_materias()
            _refresh_assuntos()

        def _remover_materia(mat):
            if messagebox.askyesno("Confirmar",
                                   f"Remover a materia '{mat}' e todos os seus assuntos?"):
                self.db.remover_materia(mat)
                if mat_selecionada[0] == mat:
                    mat_selecionada[0] = None
                    lbl_mat_sel.configure(text="Selecione uma materia ao lado")
                    for w in ass_scroll.winfo_children():
                        w.destroy()
                _refresh_materias()

        def _adicionar_assunto():
            if not mat_selecionada[0]:
                messagebox.showwarning("Atencao", "Selecione uma materia primeiro.")
                return
            novo = en_novo_ass.get().strip()
            if not novo:
                messagebox.showwarning("Atencao", "Informe o nome do assunto.")
                return
            if novo in self.db.get_assuntos(mat_selecionada[0]):
                messagebox.showwarning("Atencao",
                                       f"O assunto '{novo}' ja existe para esta materia.")
                return
            self.db.salvar_cadastro(mat_selecionada[0], novo)
            en_novo_ass.delete(0, "end")
            _refresh_assuntos()

        def _remover_assunto(ass):
            if messagebox.askyesno("Confirmar", f"Remover o assunto '{ass}'?"):
                self.db.remover_cadastro(mat_selecionada[0], ass)
                _refresh_assuntos()

        ctk.CTkButton(add_mat_frame, text="+ Adicionar", height=34, width=95,
                      fg_color="#1a3050", hover_color="#1f538d",
                      font=ctk.CTkFont("Roboto", 12),
                      command=_adicionar_materia).pack(side="left")

        ctk.CTkButton(add_ass_frame, text="+ Adicionar", height=34, width=95,
                      fg_color="#1a3050", hover_color="#1f538d",
                      font=ctk.CTkFont("Roboto", 12),
                      command=_adicionar_assunto).pack(side="left")

        _refresh_materias()

    # ─────────────────────────────────────────────────────────────────────────
    # EXPORTAR
    # ─────────────────────────────────────────────────────────────────────────
    def _exportar(self):
        df_l = self.db.ler_dados("LANCAMENTOS")
        df_e = self.db.ler_dados("ERROS")
        df_f = self._filtrar_df(df_l)

        meses = ["", "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
                 "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        if self._filtro_mes and self._filtro_ano:
            label = f"{meses[self._filtro_mes]}_{self._filtro_ano}"
        elif self._filtro_ano:
            label = str(self._filtro_ano)
        elif self._filtro_mes:
            label = meses[self._filtro_mes]
        else:
            label = "geral"

        try:
            caminho = self.db.exportar_relatorio(df_f, df_e, label)
            messagebox.showinfo("Exportado!", f"Relatorio salvo em:\n{caminho}")
        except Exception as exc:
            messagebox.showerror("Erro ao exportar", str(exc))


# ─── ENTRY POINT ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.mainloop()
