import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# =================== CONFIGURAÇÕES INICIAIS ===================
st.set_page_config(
    page_title="DASHBOARD DE RH 👥",
    layout="wide"
)

# Função auxiliar para formatar valores numéricos
def formata_numero(valor, prefixo=''):
    for unidade in ['', 'mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'


# =================== CARREGAMENTO E TRATAMENTO DE DADOS ===================
@st.cache_data
def carregar_dados():
    # Lê o Excel da pasta data/ (caminho relativo, funciona em qualquer computador)
    caminho = Path(__file__).parent / "data" / "BaseFuncionarios.xlsx"
    df = pd.read_excel(caminho)

    hoje = pd.to_datetime("today").normalize()

    # Tratamento de datas
    df['Data de Nascimento'] = pd.to_datetime(df['Data de Nascimento'], errors='coerce').dt.normalize()
    df['Data de Contratacao'] = pd.to_datetime(df['Data de Contratacao'], errors='coerce').dt.normalize()
    df['Data de Demissao'] = pd.to_datetime(df['Data de Demissao'], errors='coerce').dt.normalize()

    # Colunas adicionais
    df["Tempo de Casa"] = ((hoje - df['Data de Contratacao']).dt.days) // 365
    df["Sexo"] = df["Sexo"].map({"M": "Masculino", "F": "Feminino"})
    df[['Cidade', 'Estado']] = df['Endereço'].str.extract(r',\s*([^,]+)\s*-\s*([A-Z]{2})')
    df['Status'] = df['Data de Demissao'].apply(lambda x: 'Desativado' if pd.notna(x) else 'Ativo')

    # Conversões numéricas
    df["Salario Base"] = pd.to_numeric(df["Salario Base"], errors="coerce")
    df["Horas Extras"] = pd.to_numeric(df["Horas Extras"], errors="coerce")
    df["Ferias Acumuladas"] = pd.to_numeric(df["Ferias Acumuladas"], errors="coerce")

    # Ajuste de colunas de data para exibição
    df['Data de Nascimento'] = pd.to_datetime(df['Data de Nascimento'], errors="coerce").dt.date
    df['Data de Contratacao'] = pd.to_datetime(df['Data de Contratacao'], errors="coerce").dt.date
    df['Data de Demissao'] = pd.to_datetime(df['Data de Demissao'], errors="coerce").dt.date

    return df, hoje


# Chamada
df, hoje = carregar_dados()


# =================== FUNÇÕES DE VISUALIZAÇÃO ===================
def mostrar_overview(df, hoje):
    st.subheader("Visão Geral 🔑")
    st.markdown("""
    Este painel apresenta uma **visão geral** da força de trabalho da empresa,
    destacando os principais indicadores de **pessoas** e **produtividade**.
    """)

    # --- Pessoas ---
    st.subheader("📊 Pessoas")
    st.markdown("A empresa conta atualmente com os seguintes números de colaboradores:")

    df["Idade"] = ((hoje - pd.to_datetime(df["Data de Nascimento"], errors="coerce")).dt.days / 365).round()
    df["Tempo de Casa"] = ((hoje - pd.to_datetime(df["Data de Contratacao"], errors="coerce")).dt.days / 365).round()

    total_funcionarios = df.shape[0]
    ativos = df[df["Status"] == "Ativo"].shape[0]
    desligados = df[df["Status"] == "Desativado"].shape[0]
    perc_ativos = (ativos / total_funcionarios) * 100 if total_funcionarios > 0 else 0
    perc_desligados = (desligados / total_funcionarios) * 100 if total_funcionarios > 0 else 0
    idade_media = df["Idade"].mean()
    tempo_medio_casa = round(df["Tempo de Casa"].mean())
    media_salarial = df["Salario Base"].mean()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Funcionários", total_funcionarios)
    col2.metric("Ativos", f"{ativos}")
    col3.metric("Desligados", f"{desligados}")
    col4.metric("Média Salarial", formata_numero(media_salarial, "R$"))

    st.markdown(f"""
    Atualmente, **{perc_ativos:.1f}%** da força de trabalho está ativa, enquanto **{perc_desligados:.1f}%** já foi desligada.  
    A **idade média** dos colaboradores é de **{round(idade_media)} anos**, e o **tempo médio de casa** é de **{tempo_medio_casa} anos**.
    """)

    st.markdown("---")

    # --- Produtividade ---
    st.subheader("⚖️ Produtividade")
    st.markdown("A produtividade pode ser observada pelo acúmulo de férias e pelas horas extras realizadas:")

    media_horas_extras = round(df["Horas Extras"].mean())
    media_ferias = round(df["Ferias Acumuladas"].mean())

    col5, col6 = st.columns(2)
    col5.metric("Média de Horas Extras", f"{media_horas_extras}h")
    col6.metric("Média de Férias Acumuladas", f"{media_ferias} dias")

    st.markdown(f"""
    Em média, cada colaborador acumula **{media_horas_extras} horas extras**
    e **{media_ferias} dias de férias**.  
    Esses números podem indicar tanto **dedicação além da carga horária**
    quanto **acúmulo de passivos trabalhistas**.
    """)


def mostrar_graficos(df):
    st.subheader("📈 Gráficos")

    # --- Prepara datasets auxiliares ---
    df_estado = df.groupby("Estado").size().reset_index(name="Qtd Funcionários")
    media_salarial_area = df.groupby("Área")["Salario Base"].mean().sort_values(ascending=False).reset_index()
    tempo_area = df.groupby("Área")["Tempo de Casa"].mean().reset_index()
    status_estado = df.groupby(["Estado", "Status"]).size().reset_index(name="Qtd")
    genero = df["Sexo"].value_counts().reset_index()
    genero.columns = ["Sexo", "Qtd"]

    # --- Contratações por ano ---
    df['Ano Contratacao'] = pd.to_datetime(df['Data de Contratacao'], errors='coerce').dt.year
    contratacoes_ano = df.groupby("Ano Contratacao").size().reset_index(name="Qtd Contratações")

    # --- Distribuição por nível ---
    nivel = df["Nível"].value_counts().reset_index()
    nivel.columns = ["Nível", "Qtd"]

    # --- Gráficos existentes ---
    geojson_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
    fig_mapa = px.choropleth(
        df_estado,
        geojson=geojson_url,
        locations="Estado",
        featureidkey="properties.sigla",
        color="Qtd Funcionários",
        color_continuous_scale="Blues",
        scope="south america",
        title="Funcionários por Estado"
    )
    fig_mapa.update_geos(scope="south america", projection_type="mercator")

    fig_status_estado = px.bar(
        status_estado,
        x="Estado",
        y="Qtd",
        color="Status",
        barmode="stack",
        title="Funcionários Ativos x Desligados por Estado",
        color_discrete_map={
            "Ativo": "#3B82F6",
            "Desativado": "#F87171"
        }
    )

    fig_media_salarial_area = px.line(
    media_salarial_area,
    x='Área',
    y='Salario Base',
    markers=True,
    title='💼 Média Salarial por Área',
    color_discrete_sequence=["#3B82F6"]  # Azul vibrante
)

    fig_media_salarial_area.update_traces(
    line=dict(width=3),
    marker=dict(size=8, symbol="circle", color="#1E40AF"),
    hovertemplate='<b>%{x}</b><br>Salário: R$ %{y:,.2f}<extra></extra>'
)

    fig_tempo_area = px.bar(
        tempo_area,
        x="Área",
        y="Tempo de Casa",
        title="Tempo Médio de Casa por Área"
    )

    # --- Novos gráficos ---
    top5_salarios = df.nlargest(5, "Salario Base")[["Nome Completo", "Salario Base"]]
    fig_top5_salarios = px.bar(
        top5_salarios,
        x="Salario Base",
        y="Nome Completo",
        orientation="h",
        title="Top 5 Salários por Funcionário",
        color="Salario Base",
        color_continuous_scale="Blues"
    )

    fig_genero = px.pie(
        genero,
        values="Qtd",
        names="Sexo",
        title="Funcionários por Gênero",
        hole=0.3,  # transforma em rosca
        color_discrete_sequence=["#3B82F6", "#F87171"]
    )

    fig_contratacoes = px.line(
    contratacoes_ano,
    x="Ano Contratacao",
    y="Qtd Contratações",
    title="Contratações por Ano",
    markers=True,
    color_discrete_sequence=["#60A5FA"]
)

    fig_contratacoes.update_traces(
    line=dict(width=3),  # Linha mais grossa
    marker=dict(size=8, symbol="circle", color="#1D4ED8")  # Marcadores mais visíveis
)
    
    fig_nivel = px.pie(
    nivel,
    values="Qtd",
    names="Nível",
    title="Funcionários por Nível",
    hole=0.4,  # Rosca mais elegante
    color_discrete_sequence=["#1E3A8A", "#3B82F6", "#1D4ED8", "#93C5FD", "#BFDBFE"]
)

    # --- Organiza em duas colunas ---
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(fig_mapa, width="stretch")
        st.plotly_chart(fig_media_salarial_area, width="stretch")
        st.plotly_chart(fig_top5_salarios, width="stretch")
        st.plotly_chart(fig_contratacoes, width="stretch")

    with col2:
        st.plotly_chart(fig_status_estado, width="stretch")
        st.plotly_chart(fig_tempo_area, width="stretch")
        st.plotly_chart(fig_genero, width="stretch")
        st.plotly_chart(fig_nivel, width="stretch")


def mostrar_dados(df):
    st.subheader("📂 Dados Tratados")
    st.dataframe(df)

    # Botão de download CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar dados em CSV",
        data=csv,
        file_name="dados_tratados.csv",
        mime="text/csv"
    )


# =================== DASHBOARD PRINCIPAL ===================
st.title('DASHBOARD DE RH 👥')

aba1, aba2, aba3 = st.tabs(['🔑 Overview', '📈 Gráficos', '📂 Dados Tratados'])

with aba1:
    mostrar_overview(df, hoje)

with aba2:
    mostrar_graficos(df)

with aba3:
    mostrar_dados(df)
