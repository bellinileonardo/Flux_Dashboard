import streamlit as st
from datetime import datetime
import models as mdls
import pandas as pd
import locale
import streamlit_shadcn_ui as ui
import google.generativeai as genai # Para integração com Gemini
import os # Para acessar a chave da API
#from streamlit_extras.customize_running import center_running
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px






# --- Configuração da Página ---
with st.container():
    st.set_page_config(page_title="Flux Dash - IA",                   
                    page_icon=":robot:",                   
                    layout="wide",                   
                    initial_sidebar_state="expanded"                   
                    )
    mdls.menu_top_page()

    # --- Configuração de Localização (Locale) ---
    try:
        # Tenta configurar para Português do Brasil (Linux/macOS)
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        st.session_state['use_currency_fallback'] = False
    except locale.Error:
        try:
            # Fallback para Windows
            locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
            st.session_state['use_currency_fallback'] = False
        except locale.Error:
            st.warning("Não foi possível definir o locale para pt_BR. Usando formatação padrão para moeda.")
            st.session_state['use_currency_fallback'] = True

    # --- Fallback manual para moeda ---
    def format_currency_fallback(value, grouping=False):
        try:
            amount = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            return f"R$ {amount}"
        except (ValueError, TypeError):
            amount = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            return f"R$ {amount}"

    # --- Função auxiliar para formatar moeda ---
    def format_currency(value, grouping=True):
            try:
                return locale.currency(value, grouping=grouping, symbol='R$')  # type: ignore
            except (ValueError, TypeError):
                return locale.currency(value, grouping=grouping, symbol='R$')  # type: ignore



    # --- Estilização CSS (Comentado por padrão) ---
    #url_background_app = "https://i.pinimg.com/originals/7c/0a/38/7c0a3899b0d94b18e49e445678c01a82.jpg"
    page_home = f"""
            <style>
                [data-testid="stAppViewContainer"] {{
                    background-color: withesmoke;
                    background-opacity: 6;
                    background-position: center;
                    background-repeat: no-repeat;
                    background-size: cover;
                }}
                [data-testid="stToolbar"]{{
                    background-color: rgb(17, 63, 103)
                }}
                [data-testid="stSidebarContent"]{{
                    background-color: rgba(17, 63, 103, 0.2)
                }}
                [data-testid="stIconMaterial"]{{
                    color:white;
                }}
            </style>
            """
    st.markdown(page_home, unsafe_allow_html=True)

# --- Configuração da API Gemini ---
with st.container():
    gemini_api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY"))
    if gemini_api_key is None:
        st.sidebar.subheader("Chave API GEMINI")
        gemini_api_key = st.sidebar.text_input("Digite Sua Chave e pressione ENTER", key="chave_api_gemini_home")
    gemini_client = None
    if gemini_api_key:
        try:
            genai.configure(api_key=gemini_api_key) # type: ignore
            # Escolha o modelo Gemini apropriado (ex: gemini-1.5-flash, gemini-pro)
            gemini_client = genai.GenerativeModel('gemini-1.5-flash') # type: ignore # Ou outro modelo
            # Teste simples (opcional) - pode gerar custo mínimo
            # gemini_client.generate_content("Teste")
        except Exception as e:
            st.warning(f"Não foi possível inicializar a API do Gemini. A funcionalidade de IA estará desativada. Erro: {e}", icon="🤖")
            gemini_client = None
    else:
        st.info("Chave da API Gemini não configurada. Use o menu lateral para adicionar sua chave ao sistema.", icon="ℹ️")

# Layout topo da pagina
with st.container():
    # --- Definição de Datas Padrão - Datas não dinamicas somente na versão de apresentação, devida limitação dos dados. ---
    data_agora = datetime.now()
    data_inicio_dados = "2025-03-01"
    data_inicio_padrao = "2025-07-15" 
    data_fim_padrao = "2025-07-28"

    col_date_top = st.columns([4,1,1,1.8,1.8], vertical_alignment="center")
    with col_date_top[0]: # Titulo Pagina
        # Titulo Front Flux
        st.subheader("📊 Flux Dashboard - Integrado com IA")
        st.caption("Este dashboard tem uma visão completa do desempenho de vendas.")
    with col_date_top[1]: # Pass
        pass
    with col_date_top[2]: # Botão Selecionar Fonte de Dados
        btn_select_fonte_dados = False
    with col_date_top[3]: # Data Inicio
        data_inicio = st.date_input(
        "Data Inicial",
        value=data_inicio_padrao,
        min_value=data_inicio_dados, # Data inicial não pode ser no futuro
        max_value=data_fim_padrao, # Data final não pode ser no futuro
        key="data_inicio_home",
        format="DD/MM/YYYY")
    with col_date_top[4]: # Data Fim
        data_fim = st.date_input(
            "Data Final",
            key="data_fim_home",
            value=data_fim_padrao,
            min_value=data_inicio, # Data final não pode ser antes da inicial
            max_value=data_fim_padrao, # Data final não pode ser no futuro
            format="DD/MM/YYYY"
        )

    # Garante que data_fim seja pelo menos igual a data_inicio
    if data_fim < data_inicio:
        st.warning("A data final não pode ser anterior à data inicial.")
        data_fim = data_inicio # Corrige automaticamente

    # Adiciona hora ao fim do dia para incluir todas as vendas do último dia
    data_fim_query = datetime.combine(data_fim, datetime.max.time())
#st.write(st.session_state)
# --- Consulta Principal ao Banco de Dados (CSV) ---
with st.container():
    # Carrega os dados usando a nova função centralizada
    df_vendas_filtrado = mdls.carregar_dados(      
        file_csv="dados_export.csv",  
        data_inicio=data_inicio,
        data_fim_query=data_fim_query
    )
    #st.dataframe(df_vendas_filtrado)

    df_vw_resumo_venda_itens = mdls.carregar_dados_extras(      
        file_csv="dados_export2.csv",  
        data_inicio=data_inicio,
        data_fim_query=data_fim_query
    )
    #st.dataframe(df_vw_resumo_venda_itens)

# --- Processamento Inicial de Dados --- #
with st.container(): 
    progresso_tratamento_dados = st.progress(0, text="Iniciando Tratamento de Dados Solicitados")
    # Converte colunas numéricas após carregamento, tratando erros
    numeric_cols = ['preco_venda', 'preco_custo', 'quantidade', 'estoque', 'total_liquido_item']
    for col in numeric_cols:
        df_vendas_filtrado[col] = pd.to_numeric(df_vendas_filtrado[col], errors='coerce')
    progresso_tratamento_dados.progress(10, text="Tratando Dados Numericos")
    # Converte coluna de data/hora
    df_vendas_filtrado['dh_emissao'] = pd.to_datetime(df_vendas_filtrado['dh_emissao'], errors='coerce')
    progresso_tratamento_dados.progress(50, text="Removendo Linhas Vazias")
    # Remove linhas onde a conversão numérica ou de data falhou (opcional, mas recomendado)
    df_vendas_filtrado.dropna(subset=numeric_cols + ['dh_emissao'], inplace=True)
    progresso_tratamento_dados.progress(80, text="Calculando Valores")
    # Calcula o custo total por item (preço de custo * quantidade)
    # Trata casos onde preco_custo pode ser nulo/inválido
    progresso_tratamento_dados.progress(90, text="Calculando o custo total por item (preço de custo * quantidade)")
    df_vendas_filtrado['custo_total_item'] = df_vendas_filtrado['preco_custo'].fillna(0) * df_vendas_filtrado['quantidade']
    progresso_tratamento_dados.progress(100, text="Concluido")
    progresso_tratamento_dados.empty()

    # --- Cálculos de KPIs (Baseados no DataFrame Filtrado) ---
    df_itens_nfce_cancelados = df_vw_resumo_venda_itens.loc[df_vw_resumo_venda_itens["dfitem_cancelado"] == True]
    df_itens_nfce_vendidos = df_vw_resumo_venda_itens.loc[df_vw_resumo_venda_itens["dfitem_cancelado"] == False]
    #st.dataframe(df_itens_nfce_cancelados)
    # Considera apenas itens não cancelados para cálculos de receita, lucro, etc.
    df_validos = df_vendas_filtrado[df_vendas_filtrado["cancelado"] == False].copy()
    df_validos_colunas = list(df_validos.columns)

    df_forma_pagamento = df_validos['nome'].unique()

    total_tributos_pagos = df_validos["total_tributos"].unique()
    total_tributos_pagos_soma = total_tributos_pagos.sum()
    total_tributos_pagos = float(total_tributos_pagos[0])

    total_itens_cancelados = len(df_itens_nfce_cancelados)
    total_itens_vendidos = len(df_itens_nfce_vendidos)
    #total_itens_vendidos = int(df_validos["quantidade"].sum()) # Soma das quantidades válidas
    total_atendimentos = df_validos["numero"].nunique() # NFC-es únicas válidas

    vlr_total_descontos_aplicados = (df_validos["desconto"].sum())
    vlr_total_descontos_aplicados = vlr_total_descontos_aplicados if vlr_total_descontos_aplicados is not None else 0
    vlr_total_descontos_aplicados = float(vlr_total_descontos_aplicados)

    vlr_total_vendas = df_validos["total_liquido_item"].sum()
    vlr_total_custo = df_validos["custo_total_item"].sum() # Usa a coluna calculada
    vlr_total_lucro = vlr_total_vendas - vlr_total_custo - float(total_tributos_pagos_soma) - vlr_total_descontos_aplicados

    # Evita divisão por zero
    vlr_ticket_medio = vlr_total_vendas / total_atendimentos if total_atendimentos > 0 else 0
    perc_margem_bruta = (vlr_total_lucro / vlr_total_vendas * 100) if vlr_total_vendas > 0 else 0
    itens_por_transacao = total_itens_vendidos / total_atendimentos if total_atendimentos > 0 else 0

    # --- NOVOS KPIs ---
    # 1. Lucro por Atendimento: Mede o lucro médio gerado a cada transação.
    lucro_por_atendimento = vlr_total_lucro / total_atendimentos if total_atendimentos > 0 else 0

    # 2. Taxa de Itens com Desconto: Percentual de itens vendidos com algum desconto.
    itens_com_desconto = df_validos[df_validos['desconto'] > 0].shape[0]
    taxa_itens_desconto = (itens_com_desconto / total_itens_vendidos * 100) if total_itens_vendidos > 0 else 0

    # 3. Giro de Estoque: Mede a eficiência do estoque (versão simplificada com base nos itens vendidos no período).
    df_estoque_valor = df_validos.drop_duplicates(subset=['nome_item'])
    valor_total_estoque_atual = (df_estoque_valor['estoque'] * df_estoque_valor['preco_custo']).sum()
    giro_estoque = vlr_total_custo / valor_total_estoque_atual if valor_total_estoque_atual > 0 else 0

# Cards de KPI

with st.expander("Quadro de KPI´s", expanded=True): # Cards de KPI
    # --- Cards de Métricas ---
    col_kpi_01 = st.columns(6)
    with col_kpi_01[0]: # Lucro Liquido
        ui.metric_card(title="Lucro Liquido",
        content=format_currency(vlr_total_lucro),
        description=f"Lucro liquido",
        key="card_lucro_liquido_soma")
    with col_kpi_01[1]: # Imposto Pago
        ui.metric_card(title="Imposto Pago",
        content=format_currency(total_tributos_pagos_soma),
        description=f"Impostos Pagos",
        key="card_tributo_pago_soma")
    with col_kpi_01[2]: # Descontos Aplicados
        ui.metric_card(title="Descontos Aplicados",
        content=format_currency(vlr_total_descontos_aplicados),
        description=f"Descontos Aplicados",
        key="card_desconto_aplicado_nfce")
    with col_kpi_01[3]: # Lucro por Atendimento
        ui.metric_card(title="Lucro / Atendimento",
        content=format_currency(lucro_por_atendimento),
        description="Lucro médio por transação",
        key="card_lucro_atendimento")
    with col_kpi_01[4]: # Itens com Desconto
        ui.metric_card(title="Itens com Desconto",
        content=f"{taxa_itens_desconto:.2f}%",
        description=f"{itens_com_desconto} de {total_itens_vendidos} itens",
        key="card_taxa_itens_desconto")
    with col_kpi_01[5]: # Giro de Estoque
        ui.metric_card(title="Giro de Estoque",
        content=f"{giro_estoque:.2f}",
        description="CMV / Estoque (Período)",
        key="card_giro_estoque")

    col_kpi_02 = st.columns(6) # Adicionado mais uma coluna para os novos KPIs
    with col_kpi_02[0]: # Vendas Liquidas
        ui.metric_card(title="Vendas Líquidas",
        content=format_currency(vlr_total_vendas),
        description=f" ",
        key="card_vendas")
    with col_kpi_02[1]: # Custo Mercadoria
        ui.metric_card(title="Custo Mercadoria (CMV)",
        content=format_currency(vlr_total_custo),
        description="Custo dos itens vendidos",
        key="card_custo")
    with col_kpi_02[2]: # Itens Vendidos
        ui.metric_card(title="Itens Vendidos",
                    content=f"{total_itens_vendidos}",
                    description=f"Itens Cancelados: {total_itens_cancelados} ",
                    key="card_itens")
    with col_kpi_02[3]: # Ticket Medio
            ui.metric_card(title="Ticket Médio",
                        content=format_currency(vlr_ticket_medio),
                        description=f"{total_atendimentos} Atendimentos",
                        key="card_ticket_medio")
    with col_kpi_02[4]: # Margem Bruta
        ui.metric_card(title="Margem Bruta",
        content=f"{perc_margem_bruta:.2f}%",
        description="((Venda - Custo) / Venda)",
        key="card_margem")
    with col_kpi_02[5]: # Itens/transação
        ui.metric_card(title="Itens / Transação",
        content=f"{itens_por_transacao:.2f}",
        description="Média de itens por venda",
        key="card_itens_transacao")


# Graficos - Tabela top itens - Gemini
with st.container(): 
        # --- Gráficos e Análises Gerais (se houver dados filtrados) ---
        tab_graficos, tab_top20 = st.tabs(["📈 Gráficos", "🎖️ TOP 20"])
        with tab_graficos:
            st.subheader("Visualizações Gráficas")
            col_graph1, col_graph2= st.columns(2, border=True, vertical_alignment="top")
            with col_graph1:
                with st.container(border=True):
                    # Vendas Líquidas por Dia                
                    df_vendas_dia = df_validos.groupby(df_validos['dh_emissao'].dt.date)[['total_liquido_item', 'custo_total_item', 'total_tributos', 'desconto']].sum()                      
                    if not df_vendas_dia.empty:
                        graph_venda_liquida = px.line(df_vendas_dia, 
                                                    x=df_vendas_dia.index, 
                                                    y=['desconto', 'custo_total_item', 'total_tributos','total_liquido_item' ], 
                                                    title="Vendas Líquidas por Dia",
                                                    color='variable',
                                                    labels={'dh_emissao': 'Data',
                                                            'value': 'Valor Total (R$)',
                                                            'variable': 'Totais'},
                                                            markers=True
                                                    )
                        graph_venda_liquida.for_each_trace(
                                                    lambda trace: trace.update(name=trace.name
                                                    .replace("total_liquido_item", "Total Vendas")
                                                    .replace("desconto", "Descontos")
                                                    .replace("custo_total_item", "CVM")
                                                    .replace("total_tributos", "Tributos"))
                                                    )
                        st.plotly_chart(graph_venda_liquida)
                    else:
                        st.caption("Sem dados de vendas válidas para o gráfico diário.")
                with st.container(border=True):
                    # Vendas por Setor
                    #st.markdown("**Itens Vendidos por Setor**")
                    df_vendas_setor = df_validos['desc_setor'].value_counts()
                    #st.table(df_vendas_setor)
                    if not df_vendas_setor.empty:
                        graph_venda_setor = px.bar(
                            df_vendas_setor, 
                            x=df_vendas_setor.index, 
                            y=df_vendas_setor.values, 
                            title="Itens Vendidos por Setor",
                            barmode='stack',
                            color_discrete_sequence=["#58A0C8"],
                            labels={'y': 'Quantidade', 'desc_setor': 'Setor'}
                            )
                        st.plotly_chart(graph_venda_setor)
                    else:
                        st.caption("Sem dados de setor para exibir.")
                    
                graph1_colunas = st.columns(2)
                with graph1_colunas[0]:
                    with st.container(border=True):
                        # Grafico de vendas por Forma de Pagamento   
                        df_vendas_forma_pagamento = df_validos['nome'].value_counts()
                        graph_venda_for_pagamento = px.bar(df_vendas_forma_pagamento, 
                                                    x=df_vendas_forma_pagamento.values, 
                                                    y=df_vendas_forma_pagamento.index,
                                                    color_discrete_sequence=["#FFBC4C"],
                                                    title="Itens Vendidos por Forma de Pagamento",
                                                    orientation='h',
                                                    labels={'x': 'Transações', 'nome': 'Tipos'}
                                                    )
                        st.plotly_chart(graph_venda_for_pagamento)
                with graph1_colunas[1]:
                    with st.container(border=True):
                        # Grafico de cancelamentos por Supevisor
                        df_cancel_totais_supervisor = df_vw_resumo_venda_itens["dfsupervisor_cancelamento_cupom"].value_counts()
                        graph_cancel_supervisor = px.bar(df_cancel_totais_supervisor, 
                                                    y=df_cancel_totais_supervisor.values, 
                                                    x=df_cancel_totais_supervisor.index, 
                                                    title="Cancelamentos por Supervisor",
                                                    orientation='v',
                                                    color_discrete_sequence=["#58A0C8"],
                                                    labels={'y': 'Cancelamentos', 'dfsupervisor_cancelamento_cupom': 'Fiscal'}
                                                    )
                        st.plotly_chart(graph_cancel_supervisor)
                    
            with col_graph2:
                with st.container(border=True):
                    # Vendas por Categoria                
                    df_vendas_categoria = df_validos['desc_categoria'].value_counts().head(20) # Top 20
                    if not df_vendas_categoria.empty:
                        graph_venda_categoria = px.bar(
                            df_vendas_categoria, 
                            y=df_vendas_categoria.values, 
                            x=df_vendas_categoria.index, 
                            title="Itens Vendidos por Categoria",
                            orientation='v',
                            color_discrete_sequence=["#58A0C8"],                       
                            labels={'y': 'Vendas', 'desc_categoria': 'Categoria'}
                            )
                        st.plotly_chart(graph_venda_categoria)
                        #st.bar_chart(df_vendas_categoria, color="#58A0C8", use_container_width=True)
                    else:
                        st.caption("Sem dados de categoria para exibir.")

                graph2_colunas = st.columns(2)
                with graph2_colunas[1]:
                    with st.container(border=True):
                        # Vendas por PDV (Série) - Só mostra se 'Todas' as séries estiverem selecionadas
                        df_vendas_pdv = df_vendas_filtrado['serie'].value_counts()
                        graph_vendas_pdv = px.pie(df_vendas_pdv, 
                                                values=df_vendas_pdv.values, 
                                                names=df_vendas_pdv.index, 
                                                title="Vendas por PDV",
                                                color_discrete_sequence=["#58A0C8"],
                                                hole=0.3,
                                                labels={'value': 'Vendas (R$)', 'serie': 'PDV'}
                                                )
                        st.plotly_chart(graph_vendas_pdv)
                with graph2_colunas[0]:  
                    with st.container(border=True):
                         # Total de Cancelamentos
                        df_total_motivos_cancelamentos = df_vw_resumo_venda_itens["dfmotivo_cancelamento_cupom"].value_counts()
                        graph_mot_cancelamentos_total = px.bar(
                            df_total_motivos_cancelamentos, 
                            x=df_total_motivos_cancelamentos.values, 
                            y=df_total_motivos_cancelamentos.index, 
                            title="Cancelamentos por Motivo",
                            orientation='h',
                            color_discrete_sequence=["#FFBC4C"],
                            labels={'x': 'Total Cancelamentos', 'dfmotivo_cancelamento_cupom': 'Motivos'}
                            )
                        st.plotly_chart(graph_mot_cancelamentos_total)
                with st.container(border=True):
                    
                    # Vendas por Colaborador
                    df_vendas_colaboradores = df_vw_resumo_venda_itens['dfnome_operador'].value_counts()
                    graph_vendas_colaborador = px.bar(
                        df_vendas_colaboradores, 
                        x=df_vendas_colaboradores.values, 
                        y=df_vendas_colaboradores.index, 
                        title="Vendas por Colaborador",
                        orientation='h',
                        color_discrete_sequence=["#58A0C8"],
                        labels={'x': 'Vendas (R$)', 'dfnome_operador': 'Colaborador'}
                        )
                    st.plotly_chart(graph_vendas_colaborador)
        
        with tab_top20:
            # Agrupa os dados por produto para obter os totais de vendas e quantidade.
            # Isso é necessário para que o ranking de produtos funcione corretamente,
            # ao invés de apenas pegar as primeiras 20 linhas de vendas.
            df_produtos_agregados = df_validos.groupby('nome_item').agg(
                quantidade=('quantidade', 'sum'),
                total_liquido_item=('total_liquido_item', 'sum'),
                desconto_liquido_item=('desconto', 'sum'),
                setor_item=('desc_setor', 'first'),
                categoria_item=('desc_categoria', 'first'),
                estoque_item=('estoque', 'first')
            ).reset_index()
            col_top_20_tab = st.columns(3)
            with col_top_20_tab[0]:
                pass
            with col_top_20_tab[1]:
                pass
            with col_top_20_tab[2]:
                pass
            df_top_15 = mdls.exibir_ranking_top_produtos(df_produtos_agregados, 15)
            
            '''
            col_tabela1, col_tabela2 = st.columns(2)
            
            with col_tabela1:
                # Top Itens Mais Vendidos (em quantidade)
                st.markdown("**Top 20 Itens Mais Vendidos (Quantidade)**")
                df_validos = df_validos.astype({'quantidade': 'int'})
                df_top_itens = df_validos.groupby('nome_item')['quantidade'].sum().sort_values(ascending=False).reset_index().head(20)
                df_top_itens = df_top_itens.rename(columns={'nome_item': 'Produto', 'quantidade': 'Quantidade'})
                df_top_itens = df_top_itens.style.set_properties(color="black", align="right")
                st.dataframe(df_top_itens, use_container_width=True, hide_index=True)

            with col_tabela2:
                # Itens com Maior Faturamento
                st.markdown("**Top 20 Itens por Faturamento (Venda Líquida)**")
                df_top_faturamento = df_validos.groupby('nome_item')['total_liquido_item'].sum().sort_values(ascending=False).reset_index().head(20)
                df_top_faturamento['total_liquido_item'] = df_top_faturamento['total_liquido_item'].apply(format_currency)
                df_top_faturamento = df_top_faturamento.rename(columns={'nome_item': 'Produto', 'total_liquido_item': 'Faturamento Total'})
                st.dataframe(df_top_faturamento, use_container_width=True, hide_index=True)
            '''
