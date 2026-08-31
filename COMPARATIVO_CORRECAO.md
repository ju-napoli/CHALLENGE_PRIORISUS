# Comparativo — correção metodológica do IPIS

**Data:** 2026-08-31  
**Status:** ⚠️ **NADA FOI SOBRESCRITO.** O `OUTPUT/resultado_ipis.csv` continua sendo o arquivo antigo (3.512 linhas). O ranking corrigido foi calculado executando o `05_integracao_indicadores.py` já alterado, com a pasta de saída redirecionada para um diretório temporário. O script 06 não foi executado.

Este relatório existe para você conferir os números **antes** de aceitar a mudança definitiva.

---

## 1. Cobertura do resultado final

| | Antes | Depois | Δ |
|---|---:|---:|---:|
| Municípios no resultado | 3512 | **5571** | +2059 |
| Cobertura da base IBGE (5.571) | 63.04 % | **100.00 %** | +36.96 p.p. |
| População representada | 198.005.624 | **213.421.037** | +15.415.413 |
| População não representada | 15.415.413 (7,22 %) | **0 (0 %)** | — |

✅ Meta atingida: **5.571 municípios**, exatamente o total da base do IBGE. O `assert len(ipis) == 5571` no script passa.

## 2. Top 20 — novo ranking vs. antigo

### 2.1 Top 20 corrigido

| # | UF | Município | População | UBS | Leitos SUS | IPIS | Estava no CSV antigo? |
|--:|---|---|--:|--:|--:|--:|---|
| 1 | SP | Pinhalzinho | 15.676 | — | 0 | 100.00 | 🔴 **NÃO** |
| 2 | RS | Balneário Pinhal | 15.413 | — | 0 | 100.00 | 🔴 **NÃO** |
| 3 | CE | Pires Ferreira | 10.984 | — | 0 | 100.00 | 🔴 **NÃO** |
| 4 | SP | Porangaba | 10.850 | — | 0 | 100.00 | 🔴 **NÃO** |
| 5 | RS | Paverama | 8.146 | — | 0 | 100.00 | 🔴 **NÃO** |
| 6 | PR | Guamiranga | 7.916 | — | 0 | 100.00 | 🔴 **NÃO** |
| 7 | SP | Euclides da Cunha Paulista | 7.883 | — | 0 | 100.00 | 🔴 **NÃO** |
| 8 | RS | Caraá | 7.555 | — | 0 | 100.00 | 🔴 **NÃO** |
| 9 | RS | Ibiraiaras | 6.827 | — | 0 | 100.00 | 🔴 **NÃO** |
| 10 | SP | Tarabai | 6.633 | — | 0 | 100.00 | 🔴 **NÃO** |
| 11 | PR | Reserva do Iguaçu | 6.493 | — | 0 | 100.00 | 🔴 **NÃO** |
| 12 | RS | Santa Maria do Herval | 6.486 | — | 0 | 100.00 | 🔴 **NÃO** |
| 13 | TO | Darcinópolis | 6.093 | — | 0 | 100.00 | 🔴 **NÃO** |
| 14 | RS | Amaral Ferrador | 5.384 | — | 0 | 100.00 | 🔴 **NÃO** |
| 15 | RS | Tavares | 5.319 | — | 0 | 100.00 | 🔴 **NÃO** |
| 16 | SE | Itabi | 4.816 | — | 0 | 100.00 | 🔴 **NÃO** |
| 17 | RS | Cacique Doble | 4.692 | — | 0 | 100.00 | 🔴 **NÃO** |
| 18 | RS | São José do Hortêncio | 4.555 | — | 0 | 100.00 | 🔴 **NÃO** |
| 19 | RS | Vila Maria | 4.515 | — | 0 | 100.00 | 🔴 **NÃO** |
| 20 | PR | Ramilândia | 4.279 | — | 0 | 100.00 | 🔴 **NÃO** |

➡️ **20 dos 20** municípios do novo Top 20 **não existiam** no `resultado_ipis.csv` antigo.

⚠️ **Empates no topo.** 37 municípios ficaram com IPIS = 100,00 (zero leitos SUS e, na maioria, também sem dado de UBS). A ordem entre eles nas posições acima é arbitrária — desempatei por população apenas para exibição. Isso é uma consequência esperada do teto do índice (o déficit satura em 100) e vale registrar como limitação, é o item b9 do diagnóstico.

### 2.2 Top 20 antigo — e onde esses municípios foram parar

| # antigo | UF | Município | População | IPIS antigo | IPIS novo | Posição nova | Δ posição |
|--:|---|---|--:|--:|--:|--:|---|
| 1 | SP | Embu-Guaçu | 68.913 | 96.49 | 96.18 | 43 | ↓ 42 |
| 2 | SC | Palhoça | 253.469 | 93.32 | 94.48 | 49 | ↓ 47 |
| 3 | SP | Mirassol | 65.811 | 92.49 | 93.79 | 52 | ↓ 49 |
| 4 | PR | Colombo | 241.672 | 91.07 | 92.02 | 69 | ↓ 65 |
| 5 | RJ | São João de Meriti | 466.503 | 90.97 | 90.43 | 99 | ↓ 94 |
| 6 | SP | Carapicuíba | 398.236 | 90.81 | 90.00 | 109 | ↓ 103 |
| 7 | RS | Cachoeirinha | 141.503 | 90.81 | 89.75 | 116 | ↓ 109 |
| 8 | CE | Pindoretama | 24.919 | 90.70 | 89.92 | 111 | ↓ 103 |
| 9 | PA | Anajás | 30.247 | 90.67 | 89.71 | 117 | ↓ 108 |
| 10 | SP | Embu das Artes | 259.788 | 90.45 | 90.69 | 86 | ↓ 76 |
| 11 | PR | Congonhinhas | 8.445 | 90.45 | 91.66 | 72 | ↓ 61 |
| 12 | SP | Arujá | 90.273 | 90.28 | 90.69 | 87 | ↓ 75 |
| 13 | PA | Novo Repartimento | 63.796 | 90.05 | 88.51 | 153 | ↓ 140 |
| 14 | SP | Mauá | 429.014 | 90.04 | 89.61 | 121 | ↓ 107 |
| 15 | PR | São José dos Pinhais | 349.880 | 89.91 | 90.25 | 101 | ↓ 86 |
| 16 | SP | Hortolândia | 248.842 | 89.67 | 90.06 | 106 | ↓ 90 |
| 17 | SP | Santana de Parnaíba | 163.787 | 89.41 | 89.57 | 123 | ↓ 106 |
| 18 | SP | Itaquaquecetuba | 382.983 | 89.23 | 88.42 | 157 | ↓ 139 |
| 19 | SP | Ibiúna | 77.801 | 89.12 | 88.00 | 177 | ↓ 158 |
| 20 | PR | Fazenda Rio Grande | 165.943 | 88.94 | 88.98 | 143 | ↓ 123 |

Nenhum município do Top 20 antigo desapareceu — todos continuam na base. O que mudou foi a posição relativa: eles foram empurrados para baixo pela entrada dos municípios que antes eram descartados.

## 3. Estabilidade do Top 100

| | Municípios |
|---|---:|
| Top 100 antigo que **permanecem** no Top 100 novo | **8** |
| Top 100 antigo que **saíram** do Top 100 novo | **92** |
| Entrantes no Top 100 novo | **92** |
| — destes, que **não existiam** no CSV antigo | **92** |

Ou seja: **92 % do Top 100 foi substituído**, e 92 das 92 vagas novas foram ocupadas por municípios que o pipeline antigo apagava por completo.

**Para onde foram os 92 que saíram do Top 100** (nenhum foi excluído, apenas deslocado):

| Posição antiga | UF | Município | IPIS antigo | IPIS novo | Posição nova |
|--:|---|---|--:|--:|--:|
| 6 | SP | Carapicuíba | 90.81 | 90.00 | 109 |
| 7 | RS | Cachoeirinha | 90.81 | 89.75 | 116 |
| 8 | CE | Pindoretama | 90.70 | 89.92 | 111 |
| 9 | PA | Anajás | 90.67 | 89.71 | 117 |
| 13 | PA | Novo Repartimento | 90.05 | 88.51 | 153 |
| 14 | SP | Mauá | 90.04 | 89.61 | 121 |
| 15 | PR | São José dos Pinhais | 89.91 | 90.25 | 101 |
| 16 | SP | Hortolândia | 89.67 | 90.06 | 106 |
| 17 | SP | Santana de Parnaíba | 89.41 | 89.57 | 123 |
| 18 | SP | Itaquaquecetuba | 89.23 | 88.42 | 157 |
| 19 | SP | Ibiúna | 89.12 | 88.00 | 177 |
| 20 | PR | Fazenda Rio Grande | 88.94 | 88.98 | 143 |
| 21 | RJ | Cabo Frio | 88.92 | 87.09 | 228 |
| 22 | SP | Guapiara | 88.88 | 88.22 | 163 |
| 23 | SP | Ribeirão Pires | 88.64 | 89.27 | 138 |

*(15 primeiros de 92; a posição nova de todos ficou entre 101 e 596)*

## 4. Viés por porte do município (correlação IPIS × população)

| | Correlação de Pearson IPIS × População |
|---|---:|
| Ranking antigo (3.512 municípios) | **+0.1715** |
| Ranking corrigido (5.571 municípios) | **+0.0706** |

**A correlação NÃO inverteu de sinal — ela enfraqueceu.** Continua positiva (municípios maiores ainda pontuam um pouco mais alto), mas perdeu 59 % da força. Este era o risco que você pediu para monitorar, e a resposta é: o viés por porte **não** mudou de direção, ele se achatou.

### IPIS médio por quartil de população

| Quartil de população | IPIS médio ANTES | n antes | IPIS médio DEPOIS | n depois |
|---|--:|--:|--:|--:|
| Q1 (menores) | 39.00 | 878 | **61.28** | 1393 |
| Q2 | 49.47 | 878 | **57.24** | 1393 |
| Q3 | 56.27 | 878 | **56.41** | 1392 |
| Q4 (maiores) | 66.18 | 878 | **65.05** | 1393 |

| Δ por quartil | Q1 | Q2 | Q3 | Q4 |
|---|--:|--:|--:|--:|
| Variação no IPIS médio | **+22.3** | +7.8 | +0.1 | -1.1 |

**Leitura crítica — o padrão mudou de forma, não de direção.** Antes o IPIS subia monotonicamente com o porte (39,0 → 49,5 → 56,3 → 66,2): o índice apontava prioridade para os grandes. Agora a curva é um **U**: 61.3 → 57.2 → 56.4 → 65.0. Os dois extremos pontuam alto e o miolo pontua baixo.

São dois mecanismos distintos convivendo no mesmo número:

- **Q1 saltou +22.3 pontos** — municípios pequenos que não têm hospital no território agora recebem déficit de leitos em vez de serem descartados. É o efeito pretendido da correção.
- **Q4 praticamente não se moveu (-1.1)** — os grandes já estavam no ranking e continuam com oferta per capita diluída.

**O que isso significa para a sua decisão:** o cenário que eu havia sinalizado como risco no item 3.6 do diagnóstico — o ranking ser tomado de assalto por municípios minúsculos — **não se concretizou nesta magnitude**. Q1 subiu até aproximadamente empatar com Q4, não até ultrapassá-lo. O índice deixou de ser enviesado a favor dos grandes sem passar a ser enviesado a favor dos pequenos.

A ressalva do item **b6** (acessibilidade regional) continua válida, porém, e aparece concentrada no topo: os 37 municípios empatados em IPIS = 100 são todos pequenos e sem hospital próprio — situação que, no SUS, muitas vezes é regionalização normal e não carência. Enquanto b6 não entrar, o IPIS corrigido responde bem "onde não há infraestrutura no território", mas ainda não responde "onde há população sem acesso a infraestrutura", que é a pergunta de política pública.

## 5. Teste prático do item b3 — onde caíram os municípios com dado de UBS ausente

**83 municípios** ficaram com `DADO_UBS_AUSENTE = True` — exatamente os 83 identificados na auditoria. Para eles o IPIS foi calculado apenas sobre `DEFICIT_LEITOS`; `QTD_UBS`, `UBS_POR_10MIL` e `DEFICIT_UBS` permanecem vazios no CSV.

### Distribuição no ranking

| Faixa do ranking (5.571 posições) | Municípios com dado de UBS ausente |
|---|---:|
| Terço superior (mais prioritário) | 48 |
| Terço do meio | 10 |
| Terço inferior | 25 |

| Estatística da posição | Valor |
|---|---:|
| Melhor posição (mais prioritário) | 1 |
| Mediana | 1160 |
| Pior posição | 5544 |
| Quantos no Top 100 | 38 |
| Quantos no Top 500 | 38 |

### O teste decisivo: separar os 83 em dois subgrupos

A distribuição agregada acima esconde o que importa. Os 83 municípios com dado de UBS ausente não são um grupo homogêneo — separá-los pela situação de **leitos** é o que mostra se o item b3 foi bem tratado:

| | Subgrupo A: sem UBS **e** sem leitos | Subgrupo B: sem UBS mas **com** leitos |
|---|---:|---:|
| Municípios | **37** | **46** |
| IPIS mediano | 100.00 | 51.61 |
| Posição mediana (de 5.571) | **1** | **3884** |
| Melhor / pior posição | 1 / 1 | 61 / 5544 |
| Quantos no Top 100 | **37** | **1** |

✅ **O tratamento assimétrico funcionou.** A leitura é direta:

- O **subgrupo A** (37 municípios) está todo no topo, empatado em IPIS = 100. Eles chegaram lá **pelo componente de leitos**, que é um zero verificado na base — não pela falta de UBS. É legítimo.
- O **subgrupo B** (46 municípios) — os que têm hospital e cuja falta de UBS é quase certamente lacuna de cadastro — tem posição mediana **3884 de 5.571**, ou seja, na **metade inferior** do ranking. Apenas 1 deles aparece no Top 100.

Este é exatamente o comportamento que a decisão de **não** aplicar `fillna(0)` em UBS pretendia produzir. Se tivéssemos zerado o componente de UBS, os 83 teriam recebido `DEFICIT_UBS = 100` e subido em bloco ao topo — incluindo municípios com hospital e centenas de leitos SUS, priorizados por investimento em cima de um erro de cadastro.

**Caso de controle — Araruama/RJ** (o exemplo do item b3): 137.906 hab, 186 leitos SUS, dado de UBS ausente.

| | Valor |
|---|---|
| Situação antes | ❌ excluída do CSV |
| IPIS agora | **67.50** |
| Posição no novo ranking | **2114 de 5.571** |
| Faixa | Prioridade moderada |

✅ É o resultado desejado: Araruama volta ao ranking (deixa de ser invisível), mas **não** é catapultada ao topo por um dado que não temos. Sua posição reflete os leitos SUS que ela de fato possui.

## 6. Efeitos colaterais que valem revisão

### 6.1 Régua de normalização (item b4)

| Percentil 95 | Antes (amostra de 3.512) | Depois (base completa) | Δ |
|---|--:|--:|--:|
| `UBS_POR_10MIL` | 7,0842 | **8,5701** | +21,0 % |
| `LEITOS_SUS_POR_10MIL` | 49,6016 | **41,5055** | −16,3 % |

O p95 de UBS agora é calculado sobre os 5.488 municípios que têm dado de UBS (o `quantile` ignora os 83 NaN), e não sobre os 3.512 sobreviventes do filtro antigo. O de leitos é calculado sobre os 5.571.

### 6.2 Distribuição das faixas de prioridade

| Faixa | Antes | % antes | Depois | % depois |
|---|--:|--:|--:|--:|
| Baixa prioridade | 396 | 11.3 % | **387** | 6.9 % |
| Prioridade moderada | 2521 | 71.8 % | **3398** | 61.0 % |
| Alta prioridade | 595 | 16.9 % | **1786** | 32.1 % |

A faixa "Alta prioridade" saltou de 595 para 1786 municípios (16.9 % → 32.1 % da base). Os cortes fixos em 30/70 (item b10 do diagnóstico) foram calibrados para a distribuição antiga e provavelmente precisam ser revistos — uma faixa de "alta prioridade" com 32 % dos municípios perde poder de discriminação para orientar orçamento.

### 6.3 Empates no teto do índice

37 municípios estão empatados em IPIS = 100,00 e 108 em IPIS ≥ 90. Para uso orçamentário real seria preciso um critério de desempate (população, distância ao hospital mais próximo, indicadores de necessidade). Item b9/b11.

## 7. Verificações de integridade do script corrigido

| Checagem | Resultado |
|---|---|
| `assert len(populacao) == 5571` | ✅ passou |
| `assert IBGE.str.len() == 6` | ✅ passou |
| `assert not IBGE.duplicated()` | ✅ passou |
| `assert len(ipis) == 5571` | ✅ passou |
| NaN em `IPIS` | 0 |
| NaN em `DEFICIT_LEITOS` | 0 |
| NaN em `DEFICIT_UBS` | 83 (esperado — os `DADO_UBS_AUSENTE`) |
| NaN em `FAIXA_IPIS` | 0 |
| Linhas no resultado | 5.571 |
| Nova coluna `DADO_UBS_AUSENTE` no CSV | ✅ presente |

---

## O que falta decidir

1. **Aceitar a inversão do viés de porte** (seção 4) ou condicioná-la a resolver antes o item b6 (acessibilidade regional). Esta é a decisão de fundo — as outras são consequência dela.
2. **Recalibrar as faixas** 30/70 (seção 6.2) para a nova distribuição.
3. **Critério de desempate** para os 37 municípios no teto (seção 6.3).
4. Autorizar a sobrescrita do `OUTPUT/resultado_ipis.csv` e a execução do script 06.

> ⚠️ Lembrete: `matplotlib` **não está instalado** neste ambiente, então o script 06 vai falhar com `ModuleNotFoundError` até rodar `pip install -r requirements.txt`.
