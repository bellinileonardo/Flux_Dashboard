import streamlit as st
from datetime import datetime, timedelta
import models as mdls
import pandas as pd
import streamlit_shadcn_ui as ui
import locale
import google.generativeai as genai # Para integração com Gemini
import os # Para acessar a chave da API
from streamlit_extras.customize_running import center_running



center_running()
# --- Configuração da Página ---
st.set_page_config(page_title="Flux Dash - IA",                   page_icon=":robot:",                   layout="wide",                   initial_sidebar_state="expanded"                   )

# --- Configuração de Localização (Locale) ---
try:
    # Tenta configurar para Português do Brasil (Linux/macOS)
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    try:
        # Fallback para Windows
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    except locale.Error:
        st.warning("Não foi possível definir o local para pt_BR. Usando formatação padrão para moeda.")
        # Define um formatador manual simples como fallback se tudo falhar
        def format_currency_fallback(value, grouping=False):
             # Simples fallback, pode não ser perfeito para todos os casos
            try:
                amount = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                return f"R$ {amount}"
            except (ValueError, TypeError):
                return "R$ N/A" # Retorna N/A se a conversão falhar
        # Sobrescreve a função de moeda apenas se a configuração falhar
        # Usar locale.format_string é geralmente mais robusto se o locale foi definido parcialmente
        # Mas vamos usar o fallback simples para garantir que algo funcione.
        st.session_state['currency_formatter'] = format_currency_fallback

# Função auxiliar para formatar moeda, usando o fallback se necessário
def format_currency(value, grouping=True):
    if 'currency_formatter' in st.session_state:
        return st.session_state['currency_formatter'](value, grouping=grouping)
    else:
        try:
            # Tenta usar a função locale.currency padrão
            return locale.currency(value, grouping=grouping, symbol='R$')# type: ignore
        except (ValueError, TypeError):
             return "R$ N/A" # Retorna N/A se a conversão falhar

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
        gemini_api_key = st.sidebar.text_input("Digite Sua Chave e pressione ENTER", key="chave_api_gemini")
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

# --- Consulta Principal ao Banco de Dados (Parametrizada) ---
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

with st.container(): # --- Processamento Inicial de Dados --- #
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
with st.container(): # Graficos - Tabela top itens - Gemini
        # --- Gráficos e Análises Gerais (se houver dados filtrados) ---
        tab_graficos, tab_top20, tab_ia = st.tabs(["📈 Gráficos", "🎖️ TOP 20", "🤖 Análise Inteligente"])
        with tab_graficos:
            st.subheader("Visualizações Gráficas")
            col_graph1, col_graph2= st.columns(2, border=True, vertical_alignment="top")
            with col_graph1:
                # Vendas Líquidas por Dia
                st.markdown("**Vendas Líquidas por Dia**")
                df_vendas_dia = df_validos.groupby(df_validos['dh_emissao'].dt.date)['total_liquido_item'].sum()
                if not df_vendas_dia.empty:
                    st.line_chart(df_vendas_dia, y="total_liquido_item", color="#FFBC4C", y_label="Total Liquido", use_container_width=True)
                else:
                    st.caption("Sem dados de vendas válidas para o gráfico diário.")

                # Vendas por Setor
                st.markdown("**Itens Vendidos por Setor**")
                df_vendas_setor = df_validos['desc_setor'].value_counts()
                #st.table(df_vendas_setor)
                if not df_vendas_setor.empty:
                    st.bar_chart(df_vendas_setor, x_label="Setor", y_label="Quantidade", color="#58A0C8", use_container_width=True)
                else:
                    st.caption("Sem dados de setor para exibir.")
                # Vendas por Forma de Pagamento
                st.markdown("**Itens Vendidos por Forma de Pagamento**")
                df_vendas_forma_pagamento = df_validos['nome'].value_counts()
                st.bar_chart(df_vendas_forma_pagamento, color="#FFBC4C", horizontal=True, use_container_width=True)

                # Cancelamentos por Supervisor
                st.markdown("**Cancelamentos por Supervisor**")
                st.bar_chart(df_vw_resumo_venda_itens["dfsupervisor_cancelamento_cupom"].value_counts(), color="#58A0C8", horizontal=True, use_container_width=True)

            with col_graph2:
                # Vendas por Categoria
                st.markdown("**Itens Vendidos por Categoria**")
                df_vendas_categoria = df_validos['desc_categoria'].value_counts().head(15) # Top 15
                if not df_vendas_categoria.empty:
                    st.bar_chart(df_vendas_categoria, color="#58A0C8", use_container_width=True)
                else:
                    st.caption("Sem dados de categoria para exibir.")
                # Vendas por PDV (Série) - Só mostra se 'Todas' as séries estiverem selecionadas
                st.markdown("**Itens Vendidos por Série (PDV)**")
                df_vendas_pdv = df_vendas_filtrado['serie'].value_counts()
                st.bar_chart(df_vendas_pdv, color="#FFBC4C", x_label="PDV", use_container_width=True)
                # Total de Cancelamentos
                st.markdown("**Cancelamentos por Motivo**")
                st.bar_chart(df_vw_resumo_venda_itens["dfmotivo_cancelamento_cupom"].value_counts(), color="#58A0C8", horizontal=True, use_container_width=True)
                # Vendas por Colaborador
                st.markdown("**Vendas por Colaborador**")
                st.bar_chart(df_vw_resumo_venda_itens['dfnome_operador'].value_counts(), color="#FFBC4C", horizontal=True, use_container_width=True)
        with tab_top20:
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
        with tab_ia:
            st.subheader("Análise Inteligente com IA")
            #st.dataframe(df_vendas_filtrado)
            if gemini_client:
                st.info("Faça uma pergunta sobre os dados filtrados atualmente exibidos.", icon="❓")
                pergunta_cliente_para_gemini = st.text_area("Sua pergunta:", key="ia_question_gemini", placeholder="Ex: Quais foram os 5 produtos menos vendidos neste período? Qual o dia com maior lucro?")
                data_para_ia = df_vw_resumo_venda_itens.head(100)
                data_para_ia['dfdata_abertura_cupom'] = pd.to_datetime(data_para_ia['dfdata_abertura_cupom'])
                data_para_ia['dfdata_fechamento_cupom'] = pd.to_datetime(data_para_ia['dfdata_fechamento_cupom'])
                data_para_ia['tempo_venda'] =  data_para_ia['dfdata_abertura_cupom'] - data_para_ia['dfdata_fechamento_cupom']
                with st.popover("Ver dados Enviados a IA", use_container_width=True):
                    st.dataframe(data_para_ia, use_container_width=True, hide_index=True)
                if st.button("Analisar com IA", key="ia_button_gemini"):
                    if pergunta_cliente_para_gemini:
                        with st.spinner("Consultando a IA... Por favor, aguarde."):
                            try:
                                dados_coletados_dfvendas = data_para_ia.to_json(index=False) # Envia as primeiras x linhas como CSV

                                # Descrever as colunas para dar contexto à IA
                                column_description = ", ".join(data_para_ia.columns)

                                # Construir o prompt
                                prompt = f"""
                               Você é um Especialista em Inteligência de Varejo, agindo como um consultor de negócios. Seu objetivo principal é analisar dados de vendas para identificar padrões, anomalias e, mais importante, oportunidades claras para aumentar a lucratividade e a eficiência operacional. Sua comunicação deve ser direta, objetiva e focada em resultados financeiros.

                                Contexto da Análise:
                                Você receberá um conjunto de dados de vendas em formato JSON, extraído diretamente dos pontos de venda (PDVs) de uma ou mais lojas. A estrutura dos dados seguirá o schema abaixo. A sua tarefa é responder à pergunta específica do usuário sobre esses dados.

                                Schema dos Dados (Colunas disponíveis nos dados: {column_description}):

                                dfnumero_loja: Identificador da loja.

                                dfdata_movimento: Data da transação.

                                dfnumero_pdv: Identificador do caixa/ponto de venda.

                                dfcodigo_operador, dfnome_operador: Identificação do operador de caixa.

                                dfnumero_nfce: Número da nota fiscal.

                                dfdata_abertura_cupom, dfdata_fechamento_cupom: Timestamps do início e fim da venda.

                                dfcupom_cancelado, dfmotivo_cancelamento_cupom, dfsupervisor_cancelamento_cupom: Dados sobre cupons cancelados.

                                dfcodigo_item, dfdescricao_item: Identificação do produto.

                                dfitem_cancelado, dfmotivo_cancelamento_item: Dados sobre itens cancelados na venda.

                                dfquantidade_vendida_item: Quantidade de unidades do item.

                                dftotal_desconto_item: Valor total do desconto aplicado ao item.

                                dfvalor_liquido_vendido_item: Valor final do item após descontos.

                                Processo de Análise em Etapas:

                                Análise Interna (Foco nos Dados Fornecidos):

                                Primeiro, concentre-se exclusivamente nos dados do JSON para responder à pergunta do usuário.

                                Identifique os principais KPIs relevantes para a pergunta, como:

                                Produtos mais e menos vendidos (em volume e em valor).

                                Desempenho por operador ou por PDV.

                                Padrões de vendas por hora ou dia da semana.

                                Impacto dos descontos na receita.

                                Taxas e motivos de cancelamento (de cupons ou itens), identificando possíveis perdas ou necessidade de treinamento.

                                Tempo médio de transação (dfdata_fechamento_cupom - dfdata_abertura_cupom).

                                Enriquecimento com Dados Externos (Opcional e Sinalizado):

                                Se e somente se a sua análise interna puder ser significativamente enriquecida, você pode, de forma proativa, buscar e correlacionar os achados com dados públicos e atuais sobre o varejo brasileiro.

                                Sempre que usar dados externos, cite a fonte e o dado específico.

                                Exemplos de enriquecimento:

                                Sazonalidade: "O aumento nas vendas do 'Produto X' em Junho pode estar relacionado às festas juninas, uma tendência sazonal forte no varejo de alimentos."

                                Indicadores Econômicos: "A queda no ticket médio pode refletir o atual índice de confiança do consumidor divulgado pelo IBGE."

                                Taxas e Impostos: "O impacto da recente alteração na alíquota de ICMS para esta categoria de produto ainda não parece refletido nos preços."
                                Segue amostra dos dados a serem analisados para a pergunta do usuario:
                                ```json
                                {dados_coletados_dfvendas}
                                ```
                                Pergunta do Usuário:
                                {pergunta_cliente_para_gemini}

                                A Formato da Resposta, caso entenda que este formato esteja em desacordo com a sua analise, pode modificar para ser
                                o mais acertivo possivel em cima da pergunta do ususario:

                                Segue padrão, que pode ser alterado caso seja necessario, de resposta:

                                Estruture sua resposta de forma clara e acionável:

                                Primeiro uma Resposta Direta: Comece com uma resposta concisa à pergunta do usuário.

                                Depois as Principais Observações: Apresente os dados e padrões mais importantes que sustentam sua resposta, usando bullet points.


                                Efetue a Análise e "Viés Lucrativo": Traduza os dados em insights de negócio. O que esses números significam em termos de dinheiro?

                                Finalize com Oportunidades e Recomendações: Com base na análise, sugira 1 a 3 ações práticas que a gestão pode tomar para aumentar o lucro ou reduzir custos.

                                
                                Agora e com você GEMINI, faça Sua Análise e entregue o seu melhor:
                                """

                                # Chamada para a API do Gemini
                                # O Gemini geralmente não usa 'roles' (system/user) da mesma forma que OpenAI.
                                # O prompt é enviado diretamente.
                                # Você pode adicionar configurações de segurança e geração.
                                generation_config = genai.types.GenerationConfig( # type: ignore
                                    # max_output_tokens=300, # Controle de tamanho da resposta
                                    temperature=0.5 # Controle de criatividade
                                )
                                safety_settings = [ # Exemplo de configuração de segurança
                                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                                ]

                                response = gemini_client.generate_content( # type: ignore
                                    prompt, # O prompt construído anteriormente
                                    generation_config=generation_config,
                                    safety_settings=safety_settings
                                )

                                # Acessa o texto da resposta
                                # Adiciona tratamento de erro caso a resposta seja bloqueada por segurança
                                try:
                                    answer = response.text
                                    st.markdown("**Resposta da IA:**")
                                    st.success(answer)
                                except ValueError:
                                    # Se a resposta foi bloqueada, 'response.text' pode dar erro.
                                    st.error("A resposta foi bloqueada devido às configurações de segurança.", icon="🛡️")
                                    # Opcional: Mostrar detalhes do bloqueio se disponíveis
                                    if response.prompt_feedback:
                                        st.json(response.prompt_feedback)
                            except Exception as e: # Captura erros gerais da API do Google ou outros
                                st.error(f"Ocorreu um erro inesperado ao processar a análise com Gemini: {e}", icon="🚨")
                    else:
                        st.warning("Por favor, digite uma pergunta para a IA.", icon="⚠️")
            else:
                st.warning("A funcionalidade de Análise Inteligente está desativada. Verifique a configuração da chave da API no menu lateral.", icon="🤖")
