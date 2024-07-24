import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import plotly.express as px  # type: ignore

# Carregar a base de dados
@st.cache_data
def load_data():
    return pd.read_csv("campeonato-brasileiro-full.csv")

tabela_limpa = load_data()

# Processar os dados
def process_data(df):
    jogos_mandante = df['mandante'].value_counts()
    jogos_visitante = df['visitante'].value_counts()
    jogos = jogos_mandante.add(jogos_visitante, fill_value=0).sort_values(ascending=False)

    vencedores = df['vencedor'].value_counts()

    perdedores_mandante = df[df['vencedor'] != '-'].groupby('visitante').size()
    perdedores_visitante = df[df['vencedor'] != '-'].groupby('mandante').size()
    perdedores = perdedores_mandante.add(perdedores_visitante, fill_value=0).sort_values(ascending=False)

    # Atualizando o cálculo das derrotas
    derrotas_mandante = df[df['vencedor'] != '-'][df['vencedor'] != df['mandante']].groupby('mandante').size()
    derrotas_visitante = df[df['vencedor'] != '-'][df['vencedor'] != df['visitante']].groupby('visitante').size()
    derrotas = derrotas_mandante.add(derrotas_visitante, fill_value=0).sort_values(ascending=False)

    gols_feitos_mandante = df.groupby('mandante')['mandante_Placar'].sum()
    gols_feitos_visitante = df.groupby('visitante')['visitante_Placar'].sum()
    gols_feitos = gols_feitos_mandante.add(gols_feitos_visitante, fill_value=0).sort_values(ascending=False)

    gols_levados_mandante = df.groupby('mandante')['visitante_Placar'].sum()
    gols_levados_visitante = df.groupby('visitante')['mandante_Placar'].sum()
    gols_levados = gols_levados_mandante.add(gols_levados_visitante, fill_value=0).sort_values(ascending=False)

    empates_mandante = df[df['vencedor'] == '-'].groupby('mandante').size()
    empates_visitante = df[df['vencedor'] == '-'].groupby('visitante').size()
    empates = empates_mandante.add(empates_visitante, fill_value=0).sort_values(ascending=False)

    pontos_vitorias = df.groupby('vencedor').size() * 3
    pontos_empates_mandante = df[df['vencedor'] == '-'].groupby('mandante').size()
    pontos_empates_visitante = df[df['vencedor'] == '-'].groupby('visitante').size()
    pontos_empates = pontos_empates_mandante.add(pontos_empates_visitante, fill_value=0)
    pontos = pontos_vitorias.add(pontos_empates, fill_value=0).sort_values(ascending=False)

    return jogos, vencedores, perdedores, derrotas, gols_feitos, gols_levados, empates, pontos

# Função para criar gráficos com Plotly
def plot_graph(data, title):
    data = data.drop(labels='-', errors='ignore')  # Remover o time "-"
    fig = px.bar(data, title=title)
    fig.update_layout(xaxis_title='Times', yaxis_title='Quantidade')
    st.plotly_chart(fig)

# Função para criar a tabela consolidada
def create_consolidated_table(jogos, vencedores, perdedores, derrotas, gols_feitos, gols_levados, empates, pontos):
    tabela = pd.DataFrame({
        'Jogos': jogos,
        'Vitórias': vencedores,
        'Empates': empates,
        'Derrotas': derrotas,
        'Gols Feitos': gols_feitos,
        'Gols Levados': gols_levados,
        'Pontos': pontos
    }).fillna(0).astype(int)

    # Remover o time "-"
    tabela = tabela.drop(labels='-', errors='ignore')

    return tabela

# Função para criar o quadro de honra
def create_hall_of_fame(df):
    campeoes_wikipedia = {
        1959: "Bahia", 1960: "Palmeiras", 1961: "Santos", 1962: "Santos", 1963: "Santos", 1964: "Santos",
        1965: "Santos", 1966: "Cruzeiro", 1967: "Palmeiras", 1968: "Botafogo", 1969: "Palmeiras", 1970: "Fluminense",
        1971: "Atlético Mineiro", 1972: "Palmeiras", 1973: "Palmeiras", 1974: "Vasco da Gama", 1975: "Internacional",
        1976: "Internacional", 1977: "São Paulo", 1978: "Guarani", 1979: "Internacional", 1980: "Flamengo",
        1981: "Grêmio", 1982: "Flamengo", 1983: "Flamengo", 1984: "Fluminense", 1985: "Coritiba", 1986: "São Paulo",
        1987: "Sport Recife", 1988: "Bahia", 1989: "Vasco da Gama", 1990: "Corinthians", 1991: "São Paulo",
        1992: "Flamengo", 1993: "Palmeiras", 1994: "Palmeiras", 1995: "Botafogo", 1996: "Grêmio", 1997: "Vasco da Gama",
        1998: "Corinthians", 1999: "Corinthians", 2000: "Vasco da Gama", 2001: "Atlético Paranaense", 2002: "Santos",
        2003: "Cruzeiro", 2004: "Santos", 2005: "Corinthians", 2006: "São Paulo", 2007: "São Paulo", 2008: "São Paulo",
        2009: "Flamengo", 2010: "Fluminense", 2011: "Corinthians", 2012: "Fluminense", 2013: "Cruzeiro", 2014: "Cruzeiro",
        2015: "Corinthians", 2016: "Palmeiras", 2017: "Corinthians", 2018: "Palmeiras", 2019: "Flamengo",
        2020: "Flamengo", 2021: "Atlético Mineiro", 2022: "Palmeiras", 2023: "Botafogo"
    }

    # Transformar o dicionário em um DataFrame
    campeoes_df = pd.DataFrame(list(campeoes_wikipedia.items()), columns=['ano', 'time'])

    # Contar os títulos totais por time
    campeoes_totais = campeoes_df['time'].value_counts()

    return campeoes_totais

# Construir o aplicativo Streamlit
st.title("Análise do Campeonato Brasileiro")

# Tabs para navegação
aba_selecionada = st.tabs(["Ano Específico", "Geral", "Quadro de Honra"])

with aba_selecionada[0]:
    # Seleção de parâmetros
    anos = sorted(tabela_limpa['data'].str.split('/').str[-1].unique())
    ano_selecionado = st.selectbox("Selecione o Ano", anos)

    # Filtrar dados por ano selecionado
    dados_ano = tabela_limpa[tabela_limpa['data'].str.endswith(ano_selecionado)]

    # Processar dados para o ano selecionado
    jogos, vencedores, perdedores, derrotas, gols_feitos, gols_levados, empates, pontos = process_data(dados_ano)

    # Criar tabela consolidada para o ano selecionado
    tabela_consolidada_ano = create_consolidated_table(jogos, vencedores, perdedores, derrotas, gols_feitos, gols_levados, empates, pontos)

    # Exibir tabela
    st.header(f"Estatísticas do Ano {ano_selecionado}")
    st.subheader("Tabela Consolidada")
    st.dataframe(tabela_consolidada_ano)

    # Exibir gráficos
    col1, col2 = st.columns(2)
    with col1:
        plot_graph(vencedores, "Times com mais vitórias")
        plot_graph(gols_feitos, "Times com mais Gols Feitos")
        plot_graph(empates, "Times com mais Empates")

    with col2:
        plot_graph(derrotas, "Times com mais Derrotas")
        plot_graph(gols_levados, "Times com mais Gols Levados")
        plot_graph(pontos, "Times com mais Pontos")

with aba_selecionada[1]:
    # Processar dados para todos os anos
    jogos, vencedores, perdedores, derrotas, gols_feitos, gols_levados, empates, pontos = process_data(tabela_limpa)

    # Criar tabela consolidada para todos os anos
    tabela_consolidada_geral = create_consolidated_table(jogos, vencedores, perdedores, derrotas, gols_feitos, gols_levados, empates, pontos)

    # Exibir tabela
    st.header("Estatísticas Gerais")
    st.subheader("Tabela Consolidada")
    st.dataframe(tabela_consolidada_geral)

    # Exibir gráficos
    col1, col2 = st.columns(2)
    with col1:
        plot_graph(jogos, "Times com mais Jogos")
        plot_graph(vencedores, "Times com mais vitórias")
        plot_graph(gols_feitos, "Times com mais Gols Feitos")
        plot_graph(empates, "Times com mais Empates")

    with col2:
        plot_graph(derrotas, "Times com mais Derrotas")
        plot_graph(gols_levados, "Times com mais Gols Levados")
        plot_graph(pontos, "Times com mais Pontos")

with aba_selecionada[2]:
    # Criar o quadro de honra
    st.header("Quadro de Honra")
    campeoes = create_hall_of_fame(tabela_limpa)
    
    # Exibir tabela
    st.subheader("Times com mais Títulos desde 1959")
    st.dataframe(campeoes)
    
    # Exibir gráfico
    plot_graph(campeoes, "Times com mais Títulos")
