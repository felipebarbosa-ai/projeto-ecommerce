```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from database import carregar_fato


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Vendas em E-commerce no Brasil",
    page_icon="🛒",
    layout="wide"
)

sns.set_theme(style="whitegrid")


# ============================================================
# CARREGAMENTO E PREPARAÇÃO DOS DADOS
# ============================================================

@st.cache_data
def carregar_dados():

    df = carregar_fato()

    # Garante que a coluna data seja reconhecida como datetime
    df["data"] = pd.to_datetime(
        df["data"],
        errors="coerce"
    )

    # Margem de lucro em porcentagem
    df["margem_lucro"] = np.where(
        df["faturamento"] != 0,
        df["lucro"] / df["faturamento"] * 100,
        0
    )

    # Como a base não possui ID do pedido,
    # o ticket médio é calculado por unidade vendida
    df["ticket_medio"] = np.where(
        df["quantidade"] != 0,
        df["faturamento"] / df["quantidade"],
        0
    )

    # Nome abreviado do mês
    df["mes_nome"] = df["data"].dt.strftime("%b")

    return df


df = carregar_dados()


# ============================================================
# FUNÇÃO PARA FORMATAÇÃO DE MOEDA
# ============================================================

def moeda(valor):

    return (
        f"R$ {valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


# ============================================================
# TÍTULO
# ============================================================

st.title("🛒 Vendas em E-commerce no Brasil")

st.markdown(
    "### Projeto G1 — Análise e Visualização de Dados"
)

# ============================================================
# IDENTIFICAÇÃO ACADÊMICA
# ============================================================

st.markdown(
    """
    <div style="
        background-color: #0e1c2d;
        border: 1px solid #20364d;
        border-radius: 12px;
        padding: 15px 20px;
        margin: 10px 0 20px 0;
    ">
        <strong>📚 Disciplina:</strong>
        Linguagens de Programação
        <br>

        <strong>👨‍🏫 Professor:</strong>
        Alexandre Neves Louzada
        <br>

        <strong>👨‍🎓 Aluno:</strong>
        Felipe Barbosa da Silva
    </div>
    """,
    unsafe_allow_html=True
)

st.write(
    "Aplicação analítica para investigar faturamento, produtos, "
    "regiões, sazonalidade, canais de venda, logística e "
    "comportamento dos clientes entre 2015 e 2024."
)


# ============================================================
# FILTROS
# ============================================================

st.sidebar.header("🔎 Filtros interativos")

anos = st.sidebar.multiselect(
    "Ano",
    sorted(df.ano.unique()),
    default=sorted(df.ano.unique())
)

meses = st.sidebar.multiselect(
    "Mês",
    sorted(df.mes.unique()),
    default=sorted(df.mes.unique())
)

regioes = st.sidebar.multiselect(
    "Região",
    sorted(df.regiao.unique()),
    default=sorted(df.regiao.unique())
)

ufs = st.sidebar.multiselect(
    "Estado (UF)",
    sorted(df.uf.unique()),
    default=sorted(df.uf.unique())
)

categorias = st.sidebar.multiselect(
    "Categoria",
    sorted(df.categoria.unique()),
    default=sorted(df.categoria.unique())
)

canais = st.sidebar.multiselect(
    "Canal de venda",
    sorted(df.canal_venda.unique()),
    default=sorted(df.canal_venda.unique())
)


# ============================================================
# VALIDAÇÃO DOS FILTROS
# ============================================================

if not all([
    anos,
    meses,
    regioes,
    ufs,
    categorias,
    canais
]):

    st.warning(
        "Selecione pelo menos uma opção em cada filtro."
    )

    st.stop()


# ============================================================
# APLICAÇÃO DOS FILTROS
# ============================================================

f = df[
    df.ano.isin(anos)
    & df.mes.isin(meses)
    & df.regiao.isin(regioes)
    & df.uf.isin(ufs)
    & df.categoria.isin(categorias)
    & df.canal_venda.isin(canais)
].copy()


if f.empty:

    st.error(
        "Nenhum registro encontrado para os filtros selecionados."
    )

    st.stop()


# ============================================================
# CÁLCULO DOS KPIs
# ============================================================

fat = f.faturamento.sum()

luc = f.lucro.sum()

ticket = (
    fat / f.quantidade.sum()
    if f.quantidade.sum()
    else 0
)

produto = (
    f.groupby("produto")["quantidade"]
    .sum()
    .idxmax()
)

categoria_lucrativa = (
    f.groupby("categoria")["lucro"]
    .sum()
    .idxmax()
)

regiao_lider = (
    f.groupby("regiao")["faturamento"]
    .sum()
    .idxmax()
)

margem = (
    luc / fat * 100
    if fat
    else 0
)

avaliacao = f.avaliacao_cliente.mean()

prazo = f.prazo_entrega.mean()


# ============================================================
# KPIs
# ============================================================

st.subheader("📌 KPIs")

c = st.columns(7)

c[0].metric(
    "Faturamento total",
    moeda(fat)
)

c[1].metric(
    "Lucro total",
    moeda(luc)
)

c[2].metric(
    "Ticket médio",
    moeda(ticket)
)

c[3].metric(
    "Produto mais vendido",
    produto
)

c[4].metric(
    "Categoria mais lucrativa",
    categoria_lucrativa
)

c[5].metric(
    "Região maior faturamento",
    regiao_lider
)

c[6].metric(
    "Margem",
    f"{margem:.2f}%"
)


# ============================================================
# ABAS
# ============================================================

st.divider()

aba1, aba2, aba3, aba4, aba5 = st.tabs([
    "📈 Evolução temporal",
    "🌎 Regiões e estados",
    "🛍️ Produtos e categorias",
    "🚚 Logística e clientes",
    "📊 Sazonalidade e dados"
])


# ============================================================
# ABA 1 — EVOLUÇÃO TEMPORAL
# ============================================================

with aba1:

    st.subheader(
        "Linha temporal — evolução das vendas"
    )

    mensal = (
        f.groupby("data", as_index=False)
        .agg(
            faturamento=("faturamento", "sum"),
            lucro=("lucro", "sum")
        )
        .sort_values("data")
    )

    fig, ax = plt.subplots(figsize=(12, 5))

    ax.plot(
        mensal["data"],
        mensal["faturamento"],
        label="Faturamento",
        linewidth=2
    )

    ax.plot(
        mensal["data"],
        mensal["lucro"],
        label="Lucro",
        linewidth=2
    )

    ax.set_title(
        "Evolução do faturamento e lucro"
    )

    ax.set_xlabel("Data")
    ax.set_ylabel("R$")

    ax.legend()

    plt.xticks(rotation=30)

    plt.tight_layout()

    st.pyplot(fig)

    plt.close(fig)


    # --------------------------------------------------------
    # RESUMO ANUAL
    # --------------------------------------------------------

    anual = (
        f.groupby("ano")
        .agg(
            faturamento=("faturamento", "sum"),
            lucro=("lucro", "sum"),
            quantidade=("quantidade", "sum")
        )
    )

    anual["margem"] = (
        anual["lucro"]
        / anual["faturamento"]
        * 100
    )

    st.subheader("Resumo anual")

    st.dataframe(
        anual.style.format({
            "faturamento": moeda,
            "lucro": moeda,
            "quantidade": "{:,.0f}",
            "margem": "{:.2f}%"
        }),
        use_container_width=True
    )


# ============================================================
# ABA 2 — REGIÕES E ESTADOS
# ============================================================

with aba2:

    st.subheader(
        "Barras por estado — comparação regional"
    )

    estado = (
        f.groupby("uf", as_index=False)
        .agg(
            faturamento=("faturamento", "sum"),
            lucro=("lucro", "sum"),
            quantidade=("quantidade", "sum")
        )
        .sort_values(
            "faturamento",
            ascending=False
        )
    )

    fig, ax = plt.subplots(figsize=(12, 7))

    sns.barplot(
        data=estado,
        x="faturamento",
        y="uf",
        ax=ax
    )

    ax.set_title(
        "Faturamento por estado"
    )

    ax.set_xlabel(
        "Faturamento (R$)"
    )

    ax.set_ylabel("UF")

    plt.tight_layout()

    st.pyplot(fig)

    plt.close(fig)


    # --------------------------------------------------------
    # REGIÕES
    # --------------------------------------------------------

    st.subheader(
        "Comparação entre regiões"
    )

    reg = (
        f.groupby("regiao", as_index=False)
        .agg(
            faturamento=("faturamento", "sum"),
            lucro=("lucro", "sum"),
            quantidade=("quantidade", "sum")
        )
    )

    reg["ticket_medio"] = (
        reg["faturamento"]
        / reg["quantidade"]
    )

    fig, ax = plt.subplots(figsize=(10, 5))

    sns.barplot(
        data=reg.sort_values(
            "faturamento",
            ascending=False
        ),
        x="faturamento",
        y="regiao",
        ax=ax
    )

    ax.set_title(
        "Faturamento por região"
    )

    ax.set_xlabel("R$")

    ax.set_ylabel("")

    plt.tight_layout()

    st.pyplot(fig)

    plt.close(fig)

    st.dataframe(
        reg.style.format({
            "faturamento": moeda,
            "lucro": moeda,
            "quantidade": "{:,.0f}",
            "ticket_medio": moeda
        }),
        use_container_width=True
    )


# ============================================================
# ABA 3 — PRODUTOS E CATEGORIAS
# ============================================================

with aba3:

    st.subheader(
        "Barras por categoria — comparação de faturamento"
    )

    cat = (
        f.groupby("categoria", as_index=False)
        .agg(
            faturamento=("faturamento", "sum"),
            lucro=("lucro", "sum"),
            quantidade=("quantidade", "sum")
        )
        .sort_values(
            "faturamento",
            ascending=False
        )
    )

    fig, ax = plt.subplots(figsize=(11, 5))

    sns.barplot(
        data=cat,
        x="faturamento",
        y="categoria",
        ax=ax
    )

    ax.set_title(
        "Faturamento por categoria"
    )

    ax.set_xlabel("R$")

    ax.set_ylabel("")

    plt.tight_layout()

    st.pyplot(fig)

    plt.close(fig)


    # --------------------------------------------------------
    # PRODUTOS
    # --------------------------------------------------------

    st.subheader(
        "Ranking de produtos por volume de vendas"
    )

    prod = (
        f.groupby("produto", as_index=False)
        .agg(
            quantidade=("quantidade", "sum"),
            faturamento=("faturamento", "sum"),
            lucro=("lucro", "sum"),
            avaliacao=("avaliacao_cliente", "mean")
        )
        .sort_values(
            "quantidade",
            ascending=False
        )
    )

    st.dataframe(
        prod.style.format({
            "quantidade": "{:,.0f}",
            "faturamento": moeda,
            "lucro": moeda,
            "avaliacao": "{:.2f}"
        }),
        use_container_width=True
    )


    # --------------------------------------------------------
    # CATEGORIA MAIS LUCRATIVA
    # --------------------------------------------------------

    st.subheader(
        "Categoria mais lucrativa"
    )

    cat_l = cat.sort_values(
        "lucro",
        ascending=False
    )

    st.dataframe(
        cat_l.style.format({
            "faturamento": moeda,
            "lucro": moeda,
            "quantidade": "{:,.0f}"
        }),
        use_container_width=True
    )


# ============================================================
# ABA 4 — LOGÍSTICA E CLIENTES
# ============================================================

with aba4:

    st.subheader(
        "Dispersão — lucro × faturamento"
    )

    lf = (
        f.groupby(
            ["uf", "regiao"],
            as_index=False
        )
        .agg(
            faturamento=("faturamento", "sum"),
            lucro=("lucro", "sum")
        )
    )

    fig, ax = plt.subplots(
        figsize=(11, 6)
    )

    sns.scatterplot(
        data=lf,
        x="faturamento",
        y="lucro",
        hue="regiao",
        s=100,
        ax=ax
    )

    ax.set_title(
        "Relação entre faturamento e lucro por estado"
    )

    ax.set_xlabel(
        "Faturamento (R$)"
    )

    ax.set_ylabel(
        "Lucro (R$)"
    )

    plt.tight_layout()

    st.pyplot(fig)

    plt.close(fig)


    # --------------------------------------------------------
    # AVALIAÇÃO E PRAZO
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Avaliação média",
            f"{avaliacao:.2f}/5"
        )

    with col2:

        st.metric(
            "Prazo médio de entrega",
            f"{prazo:.1f} dias"
        )


    # --------------------------------------------------------
    # RELAÇÃO AVALIAÇÃO × VENDAS
    # --------------------------------------------------------

    st.subheader(
        "Relação entre avaliação e vendas"
    )

    av = (
        f.groupby("uf", as_index=False)
        .agg(
            avaliacao=("avaliacao_cliente", "mean"),
            quantidade=("quantidade", "sum"),
            prazo=("prazo_entrega", "mean")
        )
    )

    fig, ax = plt.subplots(
        figsize=(10, 5)
    )

    sns.scatterplot(
        data=av,
        x="quantidade",
        y="avaliacao",
        size="prazo",
        hue="prazo",
        sizes=(60, 300),
        ax=ax
    )

    ax.set_title(
        "Volume de vendas × avaliação média por estado"
    )

    ax.set_xlabel(
        "Quantidade vendida"
    )

    ax.set_ylabel(
        "Avaliação"
    )

    plt.tight_layout()

    st.pyplot(fig)

    plt.close(fig)


    # --------------------------------------------------------
    # ANÁLISE LOGÍSTICA
    # --------------------------------------------------------

    st.subheader(
        "Análise logística"
    )

    log = (
        f.groupby("regiao", as_index=False)
        .agg(
            prazo_medio=("prazo_entrega", "mean"),
            avaliacao=("avaliacao_cliente", "mean"),
            quantidade=("quantidade", "sum")
        )
    )

    st.dataframe(
        log.style.format({
            "prazo_medio": "{:.2f} dias",
            "avaliacao": "{:.2f}",
            "quantidade": "{:,.0f}"
        }),
        use_container_width=True
    )


# ============================================================
# ABA 5 — SAZONALIDADE E DADOS
# ============================================================

with aba5:

    st.subheader(
        "Heatmap mensal — sazonalidade"
    )

    heat = f.pivot_table(
        index="ano",
        columns="mes",
        values="faturamento",
        aggfunc="sum",
        fill_value=0
    )

    fig, ax = plt.subplots(
        figsize=(13, 6)
    )

    sns.heatmap(
        heat,
        annot=True,
        fmt=".0f",
        cmap="YlGnBu",
        ax=ax
    )

    ax.set_title(
        "Heatmap de faturamento por ano e mês"
    )

    ax.set_xlabel("Mês")

    ax.set_ylabel("Ano")

    plt.tight_layout()

    st.pyplot(fig)

    plt.close(fig)


    # --------------------------------------------------------
    # TABELA DINÂMICA
    # --------------------------------------------------------

    st.subheader(
        "Tabela dinâmica"
    )

    pivot = f.pivot_table(
        index="categoria",
        columns="canal_venda",
        values="faturamento",
        aggfunc="sum",
        fill_value=0
    )

    st.dataframe(
        pivot.style.format(moeda),
        use_container_width=True
    )


    # --------------------------------------------------------
    # DADOS DETALHADOS
    # --------------------------------------------------------

    st.subheader(
        "Dados detalhados"
    )

    st.dataframe(
        f.sort_values(
            "data",
            ascending=False
        ),
        use_container_width=True
    )


    # --------------------------------------------------------
    # DOWNLOAD
    # --------------------------------------------------------

    st.download_button(
        "⬇️ Baixar dados filtrados",
        f.to_csv(
            index=False
        ).encode("utf-8"),
        "ecommerce_filtrado.csv",
        "text/csv"
    )


# ============================================================
# INTERPRETAÇÃO DOS RESULTADOS
# ============================================================

st.divider()

st.subheader(
    "🧠 Interpretação dos resultados"
)

st.markdown(
    f"""
- **Categoria de maior faturamento:** {f.groupby("categoria").faturamento.sum().idxmax()}.
- **Categoria mais lucrativa:** {categoria_lucrativa}.
- **Produto com maior volume vendido:** {produto}.
- **Estado com maior faturamento:** {f.groupby("uf").faturamento.sum().idxmax()}.
- **Região com maior faturamento:** {regiao_lider}.
- **Canal com maior faturamento:** {f.groupby("canal_venda").faturamento.sum().idxmax()}.
- **Ticket médio:** {moeda(ticket)} por unidade vendida.
- **Margem de lucro:** {margem:.2f}%.
- **Avaliação média:** {avaliacao:.2f}/5.
- **Prazo médio:** {prazo:.1f} dias.
"""
)


# ============================================================
# CONCLUSÃO EXECUTIVA
# ============================================================

st.subheader(
    "🎯 Conclusão executiva"
)

st.write(
    "A análise combina desempenho financeiro, volume de vendas, "
    "localização, canais, sazonalidade e indicadores logísticos. "
    "Os filtros permitem investigar diferentes segmentos e apoiar "
    "decisões sobre produtos, regiões, canais e eficiência operacional."
)


# ============================================================
# RODAPÉ
# ============================================================

st.divider()

st.markdown(
    """
    <div style="
        text-align: center;
        color: #8295aa;
        padding: 15px;
    ">

        <strong>Projeto acadêmico — G1</strong>
        <br>

        Vendas em E-commerce no Brasil
        <br><br>

        <strong>Disciplina:</strong>
        Linguagens de Programação
        <br>

        <strong>Professor:</strong>
        Alexandre Neves Louzada
        <br>

        <strong>Aluno:</strong>
        Felipe Barbosa da Silva
        <br><br>

        Python + Pandas + NumPy + Matplotlib +
        Seaborn + Streamlit + SQLAlchemy + SQLite

    </div>
    """,
    unsafe_allow_html=True
)
```
