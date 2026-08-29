# %%
# 1. Exploração e entendimento dos dados

import pandas as pd


# %%
# Carregamos a aba "Municípios" do arquivo do IBGE,
# pois ela contém os dados de população em nível municipal.

populacao = pd.read_excel(
    "RAW/POP2025_20260113.xls",
    sheet_name="Municípios",
    header=1
)


# %%
# O arquivo possui linhas adicionais de fonte e notas de rodapé.
# Mantemos apenas os registros que possuem população preenchida.

populacao = populacao[
    populacao["POPULAÇÃO ESTIMADA"].notna()
]


# %%
# Verificamos a quantidade de registros após a filtragem.

populacao.shape


# %%
# Verificamos se a combinação UF + código do município é única.
# Essa combinação será utilizada como identificador do município.

populacao.duplicated(
    subset=["UF", "COD. MUNIC"]
).sum()


# %%
# Verificamos a distribuição dos municípios por UF.

populacao["UF"].value_counts().sort_index()

# %%
# Verificamos os tipos de dados de cada coluna.
populacao.dtypes

# %%
# Verificamos os valores presentes na coluna de código da UF.
populacao["COD. UF"].value_counts(dropna=False).head(10)

# %%
# Verificamos a quantidade de valores ausentes em cada coluna.
populacao.isna().sum()

# %%
# Removemos a coluna auxiliar que contém notas e observações do arquivo original.
populacao = populacao.drop(columns=["Unnamed: 5"])

# %%
# Analisamos estatísticas básicas da população dos municípios.
populacao["POPULAÇÃO ESTIMADA"].describe()

# %%
# Identificamos os 10 municípios com maior população estimada.
populacao.nlargest(10, "POPULAÇÃO ESTIMADA")[
    ["UF", "NOME DO MUNICÍPIO", "POPULAÇÃO ESTIMADA"]
]

# %%
# Criamos o código IBGE no mesmo padrão utilizado pela base de UBS.
# A base do IBGE possui o código municipal completo com 7 dígitos,
# enquanto a base de UBS utiliza os 6 primeiros dígitos.

populacao["IBGE"] = (
    populacao["COD. UF"].astype(str)
    + populacao["COD. MUNIC"].astype(int).astype(str).str.zfill(5)
).str[:6]

# %%
# Procuramos Belo Horizonte na base de população
# para verificar como o código do município está representado.

populacao[
    populacao["NOME DO MUNICÍPIO"].str.contains(
        "Belo Horizonte",
        case=False,
        na=False
    )
][
    ["UF", "COD. UF", "COD. MUNIC", "IBGE", "NOME DO MUNICÍPIO"]
]
# %%
