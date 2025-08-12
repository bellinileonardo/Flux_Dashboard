import streamlit as st
import pandas as pd
import plotly.express as px


def exibir_ranking_top_produtos(df_top_n: pd.DataFrame, top_n: int):
    st.subheader(f"📊 Ranking Top {top_n} Produtos por Receita de Vendas")

    if df_top_n.empty:
        st.info("O gráfico não pode ser exibido pois não há dados disponíveis para os filtros aplicados.")
        return

    # Ordena pelos produtos com maior receita (do maior para o menor)
    df_sorted = df_top_n.sort_values('total_liquido_item', ascending=False).head(top_n)
    df_sorted = df_sorted.rename(columns={
        'nome_item': 'Produto',
        'quantidade': 'Unidades Vendidas',
        'estoque_item': 'Estoque',
        'total_liquido_item': 'Receita Total',
        'setor_item': 'Setor',
        'categoria_item': 'Categoria',
        'desconto_liquido_item': 'Descontos'

    })

    ranking_top_coluna = st.columns(2)
    with ranking_top_coluna[0]:
        # --- 1. Identificação de Produtos com Baixa Quantidade (possível ruptura) ---
        with st.container(border=True):
            st.subheader("Rank de Produtos por Setor")
            st.plotly_chart(px.bar(df_sorted['Setor'].value_counts(),
                                   labels={
                                       'index': 'Setor',
                                       'value': 'Quantidade de Produtos'
                                   },
                                   color=df_sorted['Setor'].value_counts().index,
                                   #title="Rank de Produtos por Setor"
                                   )
                            )

    with ranking_top_coluna[1]:
    # --- 3. Tabela Detalhada com Estilo ---
        with st.container(border=True):
            df_sorted = df_sorted.drop(['Setor', 'Categoria'], axis=1)

            styled_df = df_sorted.style \
                .background_gradient(cmap='Greens', subset=['Unidades Vendidas']) \
                .background_gradient(cmap='Reds', subset=['Descontos']) \
                .background_gradient(cmap='Blues', subset=['Receita Total']) \
                .background_gradient(cmap='Oranges', subset=['Estoque']) \
                .format({'Unidades Vendidas': '{:,.0f}','Estoque':'{:,.0f}', 'Receita Total': 'R$ {:,.2f}','Descontos': 'R$ {:,.2f}'})
            st.subheader("Produtos por Receita de Vendas")
            st.dataframe(styled_df, use_container_width=True, hide_index=True)

# Primeira função de carregamento de dados, mais pesada(Estudo)
@st.cache_data(ttl=6000, show_spinner="Fabricando dados solicitados... Aguarde...")
def carregar_dados(file_csv,data_inicio, data_fim_query):
    # =================================================================================
    # FUNÇÕES DE LÓGICA E EXIBIÇÃO
    # =================================================================================
    """Carrega os dados de um arquivo CSV."""

    try:
        df_file_csv = pd.read_csv(f"./{file_csv}", sep=",", decimal='.', encoding="UTF-8")
        df_file_csv["dh_emissao"] = pd.to_datetime(df_file_csv["dh_emissao"], errors='coerce')
        # Filtra o dataframe do CSV pelo período selecionado na UI
        df_filtrado_csv = df_file_csv[df_file_csv["dh_emissao"].between(pd.to_datetime(data_inicio), pd.to_datetime(data_fim_query))]
        if df_filtrado_csv.empty:
            st.warning("Nenhum dado de venda foi encontrado para o período selecionado no arquivo CSV.", icon="📅")
            st.stop()
        return df_filtrado_csv
    except FileNotFoundError:
        st.error("O arquivo 'dados_export_ue.csv' não foi encontrado na pasta do projeto.")
        st.info("Por favor, faça o upload do arquivo CSV para continuar ou selecione a opção de consulta direta ao banco de dados.")
        st.file_uploader("Enviar CSV", type=['csv'])
        st.stop()
    except Exception as e:
        st.error(f"Ocorreu um erro ao ler o arquivo CSV: {e}")
        st.stop()

# Segunda função de carregamento de dados, csv menos dados(Estudo)
@st.cache_data(ttl=6000, show_spinner="Fabricando dados solicitados... Aguarde...")
def carregar_dados_extras(file_csv,data_inicio, data_fim_query):
    # =================================================================================
    # FUNÇÕES DE LÓGICA E EXIBIÇÃO
    # =================================================================================
    """Carrega os dados de um arquivo CSV."""

    try:
        df_file_csv = pd.read_csv(f"./{file_csv}", sep=",", decimal='.', encoding="UTF-8")
        df_file_csv["dfdata_movimento"] = pd.to_datetime(df_file_csv["dfdata_movimento"], errors='coerce')
        # Filtra o dataframe do CSV pelo período selecionado na UI
        df_filtrado_csv = df_file_csv[df_file_csv["dfdata_movimento"].between(pd.to_datetime(data_inicio), pd.to_datetime(data_fim_query))]
        if df_filtrado_csv.empty:
            st.warning("Nenhum dado de venda foi encontrado para o período selecionado no arquivo CSV.", icon="📅")
            st.stop()
        return df_filtrado_csv
    except FileNotFoundError:
        st.error("O arquivo 'dados_export_ue.csv' não foi encontrado na pasta do projeto.")
        st.info("Por favor, faça o upload do arquivo CSV para continuar ou selecione a opção de consulta direta ao banco de dados.")
        st.file_uploader("Enviar CSV", type=['csv'])
        st.stop()
    except Exception as e:
        st.error(f"Ocorreu um erro ao ler o arquivo CSV: {e}")
        st.stop()

# Menu TOP para paginas do app
def menu_top_page():
    with st.container():
        col_top_menu = st.columns(4)
        with col_top_menu[0]:
            st.page_link("Home.py", label="Home", help='Pagina Principal - Gráficos - KPI´s - Top itens - Ruptura de Estoque', icon="🏠", use_container_width=True)
        with col_top_menu[1]:
            st.page_link("pages/Fluxo_IA.py", label="FLUXO - A IA do Varejo ", help="Avaliação Inteligente para os dados visualizados.", icon="🤖", use_container_width=True)
        with col_top_menu[2]:
            st.page_link("http://www.google.com", label="Flux SoftHouse", help='Sua Casa de Softwares e Automações', icon="ℹ️", use_container_width=True)
        with col_top_menu[3]:
            st.page_link("http://www.google.com", label="Google", help='Abra a pagina do Google', icon="🌎", use_container_width=True)