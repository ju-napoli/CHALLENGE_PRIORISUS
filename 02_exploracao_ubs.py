# %%
# 2. Exploração dos dados de UBS
import pandas as pd

# %%
# Carregamos a base de UBS.
# O arquivo utiliza ponto e vírgula como separador das colunas.

ubs = pd.read_csv(
    "RAW/Unidades_Basicas_Saude-UBS.csv",
    sep=";"
)

ubs.head()

# %%
# Verificamos a quantidade de unidades e colunas disponíveis.
ubs.shape

# %%
# Verificamos os tipos de dados das colunas.
ubs.dtypes

# %%
# Verificamos a quantidade de valores ausentes em cada coluna.
ubs.isna().sum()

# %%
# Verificamos quantos municípios diferentes aparecem na base de UBS.
ubs["IBGE"].nunique()

# %%
# Verificamos alguns dos códigos de município presentes na base.
ubs["IBGE"].head(10)

# %%
# Visualizamos alguns registros da base de UBS para entender
# a relação entre UF e código IBGE do município.
ubs[["UF", "IBGE", "NOME"]].head(10)

# %%
# Verificamos se os códigos IBGE dos municípios são únicos na base de UBS.
ubs["IBGE"].duplicated().sum()

# %%
# Contamos quantas UBS existem em cada município.
ubs_por_municipio = (
    ubs.groupby("IBGE")
    .size()
    .reset_index(name="QTD_UBS")
)

ubs_por_municipio.head()

# %%
# Verificamos quantos municípios possuem pelo menos uma UBS.
ubs_por_municipio.shape

# %%
# Analisamos a distribuição da quantidade de UBS por município.
ubs_por_municipio["QTD_UBS"].describe()

# %%
# Identificamos os municípios com maior quantidade de UBS.
ubs_por_municipio.nlargest(10, "QTD_UBS")
# %%
