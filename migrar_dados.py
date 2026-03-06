"""
MIGRAR_DADOS.PY
Importa os lancamentos e erros do CSV legado para o controle_desempenho.xlsx
que o SISFIG usa.

Como rodar:
    cd C:\Users\figue\Desktop\SISFIG
    python migrar_dados.py
"""

import pandas as pd
from openpyxl import Workbook
import os

CSV_PATH  = r"C:\Users\figue\Downloads\DESEMPENHO_MELHORADO (1) - LANCAMENTOS.csv"
XLSX_PATH = r"C:\Users\figue\Desktop\SISFIG\controle_desempenho.xlsx"

# ─── Leitura do CSV ───────────────────────────────────────────────────────────
# O arquivo tem 2 linhas de cabecalho:
#   Linha 1: titulo decorativo (com emojis)
#   Linha 2: nomes das colunas
# Pulamos as 2 e atribuimos nomes manualmente para evitar conflitos de duplicatas.

print("Lendo CSV...")
for enc in ("utf-8-sig", "utf-8", "latin-1", "cp1252"):
    try:
        df_raw = pd.read_csv(
            CSV_PATH,
            skiprows=2,
            header=None,
            dtype=str,
            encoding=enc,
            keep_default_na=False,
        )
        print(f"  Encoding: {enc}  |  {len(df_raw)} linhas brutas  |  {len(df_raw.columns)} colunas")
        break
    except Exception as exc:
        print(f"  Falhou com {enc}: {exc}")
else:
    raise RuntimeError("Nao foi possivel ler o CSV. Verifique o caminho e o encoding.")

# Garante pelo menos 14 colunas
while len(df_raw.columns) < 14:
    df_raw[len(df_raw.columns)] = ""

df_raw.columns = list(range(len(df_raw.columns)))

# ─── LANCAMENTOS (colunas 0-7) ────────────────────────────────────────────────
df_l = df_raw[[0, 1, 2, 3, 4, 5, 6, 7]].copy()
df_l.columns = ["Materia", "Data", "Acertos", "Total", "Percentual", "Fonte", "Subtopico", "Mes"]

# Filtra linhas com Materia valida
df_l = df_l[df_l["Materia"].str.strip().astype(bool)].copy()
df_l = df_l.reset_index(drop=True)

# Limpeza numerica
df_l["Acertos"] = pd.to_numeric(df_l["Acertos"].str.strip(), errors="coerce").fillna(0).astype(int)
df_l["Total"]   = pd.to_numeric(df_l["Total"].str.strip(),   errors="coerce").fillna(0).astype(int)

# Percentual: "66,7%" ou "66.7%" -> float
df_l["Percentual"] = (
    df_l["Percentual"]
    .str.replace("%", "", regex=False)
    .str.replace(",", ".", regex=False)
    .str.strip()
)
df_l["Percentual"] = pd.to_numeric(df_l["Percentual"], errors="coerce").fillna(0).round(1)

# Recalcula percentual para garantir consistencia
mask = df_l["Total"] > 0
df_l.loc[mask, "Percentual"] = (df_l.loc[mask, "Acertos"] / df_l.loc[mask, "Total"] * 100).round(1)

df_l["Data"]      = df_l["Data"].str.strip()
df_l["Materia"]   = df_l["Materia"].str.strip()
df_l["Fonte"]     = df_l["Fonte"].str.strip()
df_l["Subtopico"] = df_l["Subtopico"].str.strip()

# Atribui IDs sequenciais
df_l["ID Bateria"] = [f"B{i+1:03d}" for i in range(len(df_l))]

print(f"  Lancamentos encontrados: {len(df_l)}")

# ─── ERROS (colunas 8-13) ─────────────────────────────────────────────────────
df_e = df_raw[[8, 9, 10, 11, 12, 13]].copy()
df_e.columns = ["Materia", "Topico", "Qtd Erros", "Data", "Observacao", "Providencia"]

# Filtra linhas com Materia E Topico validos
df_e = df_e[df_e["Materia"].str.strip().astype(bool)].copy()
df_e = df_e[df_e["Topico"].str.strip().astype(bool)].copy()
df_e = df_e.reset_index(drop=True)

df_e["Qtd Erros"]  = pd.to_numeric(df_e["Qtd Erros"].str.strip(), errors="coerce").fillna(1).astype(int)
df_e["Data"]       = df_e["Data"].str.strip()
df_e["Materia"]    = df_e["Materia"].str.strip()
df_e["Topico"]     = df_e["Topico"].str.strip()
df_e["Observacao"] = df_e["Observacao"].str.strip()
df_e["Providencia"]= df_e["Providencia"].str.strip()

print(f"  Erros encontrados: {len(df_e)}")

# ─── Vinculacao: Erro -> Bateria ──────────────────────────────────────────────
# Estrategia: para cada erro, encontra o lancamento da mesma materia
# com a data mais recente igual ou anterior a data do erro.
# Se nao houver, usa o primeiro lancamento daquela materia.

df_l["_dt"] = pd.to_datetime(df_l["Data"], dayfirst=True, errors="coerce")
df_e["_dt"] = pd.to_datetime(df_e["Data"], dayfirst=True, errors="coerce")

def encontrar_id(materia, dt_erro):
    candidatos = df_l[df_l["Materia"] == materia].copy()
    if candidatos.empty:
        return "LEGADO"
    if pd.isna(dt_erro):
        return candidatos.iloc[-1]["ID Bateria"]
    antes = candidatos[candidatos["_dt"] <= dt_erro]
    if not antes.empty:
        return antes.iloc[-1]["ID Bateria"]
    return candidatos.iloc[0]["ID Bateria"]

df_e["ID Bateria"] = df_e.apply(
    lambda r: encontrar_id(r["Materia"], r["_dt"]), axis=1
)

# ─── Salva XLSX ───────────────────────────────────────────────────────────────
if os.path.exists(XLSX_PATH):
    resp = input(f"\nArquivo '{XLSX_PATH}' ja existe. Sobrescrever? (s/n): ").strip().lower()
    if resp != "s":
        print("Operacao cancelada.")
        exit()

print("\nGerando controle_desempenho.xlsx...")

wb = Workbook()

# Aba LANCAMENTOS
ws1 = wb.active
ws1.title = "LANCAMENTOS"
ws1.append(["ID Bateria", "Materia", "Data", "Acertos", "Total", "Fonte", "Subtopico", "Percentual"])
for _, row in df_l.iterrows():
    ws1.append([
        row["ID Bateria"],
        row["Materia"],
        row["Data"],
        int(row["Acertos"]),
        int(row["Total"]),
        row["Fonte"],
        row["Subtopico"],
        float(row["Percentual"]),
    ])

# Aba ERROS
ws2 = wb.create_sheet("ERROS")
ws2.append(["ID Bateria", "Materia", "Topico", "Qtd Erros", "Data", "Observacao", "Providencia"])
for _, row in df_e.iterrows():
    ws2.append([
        row["ID Bateria"],
        row["Materia"],
        row["Topico"],
        int(row["Qtd Erros"]),
        row["Data"],
        row["Observacao"],
        row["Providencia"],
    ])

wb.save(XLSX_PATH)

# ─── Resumo ───────────────────────────────────────────────────────────────────
print("\n" + "=" * 55)
print("MIGRACAO CONCLUIDA")
print("=" * 55)
print(f"  Lancamentos importados : {len(df_l)}")
print(f"  Erros importados       : {len(df_e)}")

ids_l   = set(df_l["ID Bateria"].unique())
ids_e   = set(df_e["ID Bateria"].unique())
pend    = ids_l - ids_e
print(f"  Baterias sem erro vinc.: {len(pend)}")

print(f"\nArquivo salvo em:\n  {XLSX_PATH}")
print("\nAgora abra o SISFIG normalmente.")
print("=" * 55)
