import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------
# Configuração da página
# --------------------------------
st.set_page_config(
    page_title="Dashboard de Salários em Dados",
    page_icon="📊",
    layout="wide"
)

# --------------------------------
# Carregar dados
# --------------------------------
@st.cache_data
def carregar_dados():
    url = "https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv"
    return pd.read_csv(url)

df = carregar_dados()

# --------------------------------
# Barra lateral
# --------------------------------
st.sidebar.header("🔎 Filtros")

anos = sorted(df["ano"].unique())
anos_sel = st.sidebar.multiselect("Ano", anos, default=anos)

senioridade = sorted(df["senioridade"].unique())
senioridade_sel = st.sidebar.multiselect("Senioridade", senioridade, default=senioridade)

contrato = sorted(df["contrato"].unique())
contrato_sel = st.sidebar.multiselect("Tipo de contrato", contrato, default=contrato)

empresa = sorted(df["tamanho_empresa"].unique())
empresa_sel = st.sidebar.multiselect("Tamanho da empresa", empresa, default=empresa)

# --------------------------------
# Filtrar dados
# --------------------------------
df_filtrado = df[
    (df["ano"].isin(anos_sel)) &
    (df["senioridade"].isin(senioridade_sel)) &
    (df["contrato"].isin(contrato_sel)) &
    (df["tamanho_empresa"].isin(empresa_sel))
]

# --------------------------------
# Título
# --------------------------------
st.title("📊 Dashboard de Salários na Área de Dados")
st.markdown("Explore os dados salariais da área de dados usando os filtros à esquerda.")

# --------------------------------
# Métricas
# --------------------------------
st.subheader("📌 Métricas gerais")

if not df_filtrado.empty:

    salario_medio = df_filtrado["usd"].mean()
    salario_max = df_filtrado["usd"].max()
    total = df_filtrado.shape[0]

    if not df_filtrado["cargo"].mode().empty:
        cargo_freq = df_filtrado["cargo"].mode()[0]
    else:
        cargo_freq = "N/A"

else:
    st.warning("Nenhum dado encontrado com os filtros selecionados.")

    salario_medio = 0
    salario_max = 0
    total = 0
    cargo_freq = "Nenhum"

col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Salário médio", f"${salario_medio:,.0f}")
col2.metric("🏆 Salário máximo", f"${salario_max:,.0f}")
col3.metric("📄 Total de registros", f"{total:,}")
col4.metric("💼 Cargo mais frequente", cargo_freq)

# --------------------------------
# Gráficos principais
# --------------------------------
st.subheader("📊 Análises Visuais")

col1, col2 = st.columns(2)

# Top cargos
with col1:
    if not df_filtrado.empty:

        top_cargos = (
            df_filtrado
            .groupby("cargo")["usd"]
            .mean()
            .nlargest(10)
            .sort_values()
            .reset_index()
        )

        fig = px.bar(
            top_cargos,
            x="usd",
            y="cargo",
            orientation="h",
            title="Top 10 cargos por salário médio",
            color="usd",
            color_continuous_scale="blues"
        )

        st.plotly_chart(fig, use_container_width=True)

# Histograma
with col2:
    if not df_filtrado.empty:

        fig2 = px.histogram(
            df_filtrado,
            x="usd",
            nbins=30,
            title="Distribuição de salários",
            color_discrete_sequence=["#636EFA"]
        )

        st.plotly_chart(fig2, use_container_width=True)

# --------------------------------
# Segunda linha
# --------------------------------
col3, col4 = st.columns(2)

# Tipos de trabalho
with col3:
    if not df_filtrado.empty:

        remoto = df_filtrado["remoto"].value_counts().reset_index()
        remoto.columns = ["tipo", "quantidade"]

        fig3 = px.pie(
            remoto,
            names="tipo",
            values="quantidade",
            hole=0.5,
            title="Proporção dos tipos de trabalho"
        )

        st.plotly_chart(fig3, use_container_width=True)

# Mapa mundial
with col4:
    if not df_filtrado.empty:

        df_ds = df_filtrado[df_filtrado["cargo"] == "Data Scientist"]

        mapa = (
            df_ds
            .groupby("residencia_iso3")["usd"]
            .mean()
            .reset_index()
        )

        fig4 = px.choropleth(
            mapa,
            locations="residencia_iso3",
            color="usd",
            title="Salário médio de Cientista de Dados por país",
            color_continuous_scale="RdYlGn"
        )

        st.plotly_chart(fig4, use_container_width=True)

# --------------------------------
# NOVO gráfico 1
# Evolução salarial por ano
# --------------------------------
st.subheader("📈 Evolução dos salários ao longo dos anos")

if not df_filtrado.empty:

    evolucao = (
        df_filtrado
        .groupby("ano")["usd"]
        .mean()
        .reset_index()
    )

    fig5 = px.line(
        evolucao,
        x="ano",
        y="usd",
        markers=True,
        title="Salário médio por ano"
    )

    st.plotly_chart(fig5, use_container_width=True)

# --------------------------------
# NOVO gráfico 2
# Salário por senioridade
# --------------------------------
st.subheader("🧠 Salários por nível de senioridade")

if not df_filtrado.empty:

    senioridade_salario = (
        df_filtrado
        .groupby("senioridade")["usd"]
        .mean()
        .sort_values()
        .reset_index()
    )

    fig6 = px.bar(
        senioridade_salario,
        x="senioridade",
        y="usd",
        color="usd",
        color_continuous_scale="viridis",
        title="Salário médio por senioridade"
    )

    st.plotly_chart(fig6, use_container_width=True)

# --------------------------------
# Tabela final
# --------------------------------
st.subheader("📋 Dados detalhados")

st.dataframe(df_filtrado, use_container_width=True)