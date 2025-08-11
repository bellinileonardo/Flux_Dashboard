import streamlit as st
import pandas as pd
import plotly.express as px

################## Engine Banco de Dados ####################

# Cria pagina mais interativa para o Top Itens (Func. Gerada pelo Gemini)(Estudo)
def exibir_aba_top20(data):
    """
    Renderiza a aba "Top 20", transformando-a em uma ferramenta de análise interativa.

    Esta função encapsula toda a lógica da aba, incluindo:
    1. Carregamento de dados com cache para performance.
    2. Filtros interativos na barra lateral.
    3. Exibição de KPIs (Key Performance Indicators) dinâmicos.
    4. Um gráfico de barras interativo com Plotly.
    5. Uma tabela de dados detalhada e estilizada dentro de um expander.
    """
    st.header("Análise de Performance dos Produtos Principais")
    st.markdown(
        "Use os filtros na barra lateral para explorar os produtos com melhor desempenho."
    )

    # --- 1. Carregamento e Cache de Dados ---
    # @st.cache_data garante que os dados sejam carregados apenas uma vez,
    # melhorando a performance da aplicação.


    df_principal = data
    #st.dataframe(data)
    with st.sidebar.expander("Filtros TOP Itens"):
        # --- 2. Filtros Interativos na Barra Lateral ---
        st.header("Filtros da Análise Top 20")
        top_n = st.slider(
            'Selecione o número de produtos (Top N):',
            min_value=5,
            max_value=20,
            value=10,  # Valor padrão
            help="Defina quantos produtos do topo do ranking você deseja visualizar."
        )

        categorias_disponiveis = df_principal['desc_setor'].unique()
        categorias_selecionadas = st.multiselect(
            'Filtre por Categoria:',
            options=categorias_disponiveis,
            default=categorias_disponiveis,
            help="Selecione uma ou mais categorias para a análise."
        )

    # --- 3. Lógica de Filtragem e Preparação dos Dados ---
    # Aplica os filtros selecionados pelo usuário
    df_filtrado = df_principal[df_principal['desc_setor'].isin(categorias_selecionadas)]
    df_top_n = df_filtrado.sort_values('quantidade', ascending=False).head(top_n)

    # --- 4. Exibição de KPIs (Métricas de Destaque) ---
    st.subheader(f"💡 Insights Rápidos do Top {top_n}")

    if df_top_n.empty:
        st.warning("Nenhum dado encontrado para os filtros selecionados.")
    else:
        # Calcula as métricas com base nos dados filtrados
        receita_total = df_top_n['total_liquido_item'].sum()
        vendas_totais = df_top_n['quantidade'].sum()
        produto_campeao = df_top_n.iloc[0]['nome_item']

        # Organiza os KPIs em colunas para um layout limpo
        col1, col2, col3 = st.columns(3)
        col1.metric("🏆 Produto #1", produto_campeao)
        col2.metric("💰 Receita Total (🏆)", f"R$ {receita_total:,.2f}")
        col3.metric("📦 Unidades Vendidas (🏆)", f"{vendas_totais:,}")

    st.divider()

    # --- 5. Gráfico de Barras Interativo Aprimorado ---
    st.subheader(f"📊 Ranking Top {top_n} por Receita de Vendas")
    if not df_top_n.empty:
        # Ordena o DataFrame pela receita (total_liquido_item) para uma visualização mais intuitiva
        df_sorted = df_top_n.sort_values('quantidade', ascending=True).head(top_n)
        st.dataframe(df_sorted)


        fig = px.bar(
            df_sorted,
            x='total_liquido_item',
            y='nome_item',
            orientation='v',
            # Exibe o valor da receita na barra, formatado como moeda
            text='total_liquido_item',
            # A cor continua representando a quantidade, adicionando uma dimensão extra de informação
            color='quantidade',
            labels={
                'nome_item': 'Produto',
                'quantidade': 'Unidades Vendidas',
                'total_liquido_item': 'Receita'
            }
            # A altura dinâmica é uma ótima prática e foi mantida
            #eight=max(400, top_n * 35)
        )

        # Atualiza a formatação do texto e a aparência geral do gráfico
        fig.update_traces(
            # Formata o texto como moeda brasileira e posiciona fora da barra
            texttemplate='R$ %{x:,.2f}',
            textposition='outside',
            # Personaliza as informações exibidas ao passar o mouse
            hovertemplate=(
                "<b>%{y}</b><br>" +
                "Receita: %{x:R$,.2f}<br>" +
                "Unidades Vendidas: %{customdata[0]:,}<extra></extra>"
            ),
            customdata=df_sorted[['quantidade']] # Adiciona 'quantidade' aos dados do hover
        )


        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("O gráfico não pode ser exibido pois não há dados.")


    # --- 6. Tabela de Dados Detalhada (em um Expander) ---
    with st.expander(f"Ver tabela de dados detalhada do Top {top_n}", expanded=False):
        if not df_top_n.empty:
            st.dataframe(
                df_top_n.style
                .background_gradient(cmap='Greens', subset=['quantidade'])
                .background_gradient(cmap='Blues', subset=['total_liquido_item'])
                .format({'total_liquido_item': 'R$ {:,.2f}', 'total_liquido_item': '{:+.2f}%'})
                .bar(subset=['total_liquido_item'], align='zero', color=['#d65f5f', '#5fba7d']),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("Tabela vazia devido aos filtros aplicados.")


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
                .format({'Unidades Vendidas': '{:,.0f}', 'Receita Total': 'R$ {:,.2f}','Descontos': 'R$ {:,.2f}'})
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
            st.page_link("Home.py", label="Home", help='Pagina Principal - Graficos - KPI´s - Top itens - Ruptura de Estoque', icon="🏠", use_container_width=True)
        with col_top_menu[1]:
            st.page_link("pages/flux_ia.py", label="FLUXO - A IA do Varejo ", help="Avaliação Inteligente para os dados visualizados.", icon="🤖", use_container_width=True)
        with col_top_menu[2]:
            st.page_link("http://www.google.com", label="Flux SoftHouse", help='Sua Casa de Softwares e Automações', icon="ℹ️", use_container_width=True)
        with col_top_menu[3]:
            st.page_link("http://www.google.com", label="Google", help='Abra a pagina do Google', icon="🌎", use_container_width=True)