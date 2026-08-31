import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Pasta para análises
pasta_analises = Path("OUTPUT/Analises")
pasta_analises.mkdir(
    parents=True,
    exist_ok=True
)


# Carregamos o resultado final do IPIS.
ipis = pd.read_csv(
    "OUTPUT/resultado_ipis.csv"
)

ipis.head()

# Verificamos a estrutura geral da base.
ipis.info()


# Analisamos estatísticas descritivas do IPIS.
ipis["IPIS"].describe()


# Selecionamos os 10 municípios com maior prioridade de investimento segundo o IPIS.

top10 = ipis.nlargest(
    10,
    "IPIS"
)[
    [
        "UF",
        "NOME DO MUNICÍPIO",
        "POPULAÇÃO ESTIMADA",
        "UBS_POR_10MIL",
        "LEITOS_SUS_POR_10MIL",
        "IPIS",
        "FAIXA_IPIS"
    ]
]

top10

# Gráfico dos municípios mais populosos dentro da faixa de alta prioridade.
#
# O critério de seleção deste gráfico não é o nlargest("IPIS") usado acima.
# O IPIS satura em 100 por construção (o déficit é limitado a esse teto), e
# após a correção metodológica há 37 municípios empatados em exatamente
# 100,00. Selecionar por IPIS produzia 10 barras de comprimento idêntico —
# um gráfico sem poder de discriminação.
#
# Selecionamos, em vez disso, os 10 municípios de maior população dentro da
# faixa "Alta prioridade" (o terço mais carente da base). Isso responde a uma
# pergunta orçamentária mais útil: entre os municípios prioritários, onde o
# investimento alcança mais pessoas. Nesta seleção o IPIS volta a variar
# (amplitude de cerca de 10 pontos), então as barras discriminam de novo.
#
# A variável top10 acima permanece intacta: ela alimenta o
# top10_municipios_ipis.csv exportado ao final do script.

alta_prioridade = ipis[
    ipis["FAIXA_IPIS"] == "Alta prioridade"
]

top10_populosos = alta_prioridade.nlargest(
    10,
    "POPULAÇÃO ESTIMADA"
)

top10_grafico = top10_populosos.sort_values(
    "IPIS",
    ascending=True
)

plt.figure(figsize=(10, 6))

barras = plt.barh(
    top10_grafico["NOME DO MUNICÍPIO"],
    top10_grafico["IPIS"]
)

# Anotamos a população em cada barra, já que ela é o critério de seleção
# mas não está representada no comprimento da barra.

for barra, populacao in zip(barras, top10_grafico["POPULAÇÃO ESTIMADA"]):
    plt.text(
        barra.get_width() + 1,
        barra.get_y() + barra.get_height() / 2,
        f"{populacao:,.0f}".replace(",", ".") + " hab",
        va="center",
        fontsize=8
    )

# Mantemos a escala completa do índice (0 a 100) para não exagerar
# visualmente as diferenças entre os municípios selecionados.

plt.xlim(0, 115)
plt.xlabel("IPIS")
plt.ylabel("Município")
plt.title("10 municípios de alta prioridade com maior população")

plt.tight_layout()

plt.savefig(
    pasta_analises / "10_municipios.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()



# Analisamos a distribuição dos valores de IPIS.

plt.figure(figsize=(10, 6))

plt.hist(
    ipis["IPIS"],
    bins=20,
    edgecolor="black"
)

plt.xlabel("IPIS")
plt.ylabel("Quantidade de municípios")
plt.title("Distribuição do Índice de Prioridade de Investimento em Saúde")

plt.tight_layout()

plt.savefig(
    pasta_analises / "distribuicao_ipis.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()


# Contamos os municípios em cada faixa de prioridade.

distribuicao_faixas = (
    ipis["FAIXA_IPIS"]
    .value_counts()
    .reindex(
        [
            "Baixa prioridade",
            "Prioridade moderada",
            "Alta prioridade"
        ]
    )
)

distribuicao_faixas


# Visualizamos a quantidade de municípios em cada faixa de prioridade.

plt.figure(figsize=(8, 5))

distribuicao_faixas.plot(
    kind="bar"
)

plt.xlabel("Faixa de prioridade")
plt.ylabel("Quantidade de municípios")
plt.title("Municípios por faixa de prioridade")

plt.xticks(rotation=0)
plt.tight_layout()

plt.savefig(
    pasta_analises / "distribuicao_faixas.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()

# Calculamos o IPIS médio por estado.

ipis_estado = (
    ipis.groupby("UF")["IPIS"]
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)

ipis_estado.head(10)


# Selecionamos os 10 estados com maior IPIS médio.

top10_estados = ipis_estado.head(10).sort_values(
    "IPIS",
    ascending=True
)

plt.figure(figsize=(10, 6))

plt.barh(
    top10_estados["UF"],
    top10_estados["IPIS"]
)

plt.xlabel("IPIS médio")
plt.ylabel("Estado")
plt.title("Estados com maior IPIS médio")

plt.tight_layout()

plt.savefig(
    pasta_analises / "maior_ipis_medios.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()


# Analisamos a relação entre disponibilidade de UBS e prioridade de investimento.

plt.figure(figsize=(8, 6))

plt.scatter(
    ipis["UBS_POR_10MIL"],
    ipis["IPIS"],
    alpha=0.5
)

plt.xlabel("UBS por 10 mil habitantes")
plt.ylabel("IPIS")
plt.title("Relação entre disponibilidade de UBS e IPIS")

plt.tight_layout()

plt.savefig(
    pasta_analises / "relacao_ubs_ipis.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()


# Analisamos a relação entre disponibilidade de leitos SUS e prioridade de investimento.

plt.figure(figsize=(8, 6))

plt.scatter(
    ipis["LEITOS_SUS_POR_10MIL"],
    ipis["IPIS"],
    alpha=0.5
)

plt.xlabel("Leitos SUS por 10 mil habitantes")
plt.ylabel("IPIS")
plt.title("Relação entre disponibilidade de leitos SUS e IPIS")

plt.tight_layout()

plt.savefig(
    pasta_analises / "relacao_leitos_ipis.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()


# Armazenar os resultados da análise em uma pasta específica.

top10.to_csv(
    pasta_analises / "top10_municipios_ipis.csv",
    index=False,
    encoding="utf-8-sig"
)

ipis_estado.to_csv(
    pasta_analises / "ipis_medio_estados.csv",
    index=False,
    encoding="utf-8-sig"
)

