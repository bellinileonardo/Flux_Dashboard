import streamlit as st
import google.generativeai as genai # Para integração com Gemini
import os # Para acessar a chave da API
import Home as hm
import models as mdls


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

mdls.menu_top_page()
st.subheader("📊 Flux Dashboard - Seu Varejo Integrado com IA")
st.caption("Esta analise usa a interface GEMINI do Google para analisar suas vendas.")
#st.dataframe(df_vendas_filtrado)
if gemini_client:
    #st.info("Faça uma pergunta sobre os dados filtrados atualmente exibidos.", icon="❓")
    #pergunta_cliente_para_gemini = st.text_area("Sua pergunta:", key="ia_question_gemini", placeholder="Ex: Quais foram os 5 produtos menos vendidos neste período? Qual o dia com maior lucro?")
    data_para_ia = hm.df_vw_resumo_venda_itens.copy()
    data_para_ia = data_para_ia.head(789)
    #st.dataframe(data_para_ia)
    with st.popover("Ver dados Enviados a IA", use_container_width=True):
        st.dataframe(data_para_ia, use_container_width=True, hide_index=True)
        #st.write(data_para_ia.columns)
    if st.button("Analisar com IA", key="ia_button_gemini_flux", type="primary", use_container_width=True):
        
            with st.spinner("Consultando a IA... Por favor, aguarde."):
                try:
                    dados_coletados_dfvendas = data_para_ia.to_csv(index=False)


                    # Descrever as colunas para dar contexto à IA
                    column_description = ", ".join(data_para_ia.columns)

                    # Construir o prompt
                    prompt = f"""
                        # MISSÃO
                        Sua missão é realizar uma análise de consultoria completa sobre os dados de vendas de varejo fornecidos, identificando insights acionáveis para aumentar a lucratividade
                        e a eficiência operacional.

                        # PERSONA
                        Você é um Consultor de Negócios Sênior, especialista em Inteligência de Varejo. Sua comunicação é direta, objetiva e focada em resultados financeiros.

                        # CONTEXTO
                        Os dados a seguir representam uma amostra de transações de vendas, em formato CSV, extraídos diretamente dos Pontos de Venda (PDVs).

                        ## Schema dos Dados (Colunas disponíveis: {column_description})
                        - **dfnumero_loja**: Código que identifica a loja. 
                        - **dfdata_movimento**: Data em que a venda foi registrada.
                        - **dfnumero_pdv**: Número do Ponto de Venda (caixa) onde a transação ocorreu.
                        - **dfcodigo_operador**: Identificação do operador de caixa.
                        - **dfnome_operador**: Nome completo do operador de caixa.
                        - **dfnumero_nfce**: Número da Nota Fiscal de Consumidor Eletrônica.
                        - **dfdata_abertura_cupom**: Data e hora de início da transação.
                        - **dfdata_fechamento_cupom**: Data e hora de encerramento da transação.
                        - **dfcupom_cancelado**: Indica se o cupom fiscal foi cancelado (True/False).
                        - **dfmotivo_cancelamento_cupom**: Razão pela qual o cupom foi cancelado.
                        - **dfsupervisor_cancelamento_cupom**: Supervisor responsável pelo cancelamento do cupom.
                        - **dfcodigo_item**: Código único do produto.
                        - **dfdescricao_item**: Nome ou descrição detalhada do produto.
                        - **dfitem_cancelado**: Indica se o item específico foi cancelado da venda (True/False).
                        - **dfmotivo_cancelamento_item**: Motivo para o cancelamento do item.
                        - **dfquantidade_vendida_item**: Quantidade do item vendido na transação.
                        - **dftotal_desconto_item**: Valor total de desconto aplicado ao item.
                        - **dfvalor_liquido_vendido_item**: Valor final do item após os descontos.
                        - **departamento**: Departamento ao qual o produto pertence.
                        - **tributacao**: Tipo de regime tributário do produto.
                        - **unidade**: Unidade de medida do produto (ex: Kg, Un, L).
                        - **preco**: Preço de venda do produto.
                        - **precocusto**: Custo do produto para a loja.
                        - **estoque**: Quantidade de unidades do produto em estoque.
                        - **ncm**: Nomenclatura Comum do Mercosul, código de identificação do produto.
                        - **desc_setor**: Descrição do setor do produto.
                        - **desc_secao**: Descrição da seção do produto.
                        - **desc_categoria**: Descrição da categoria do produto.

                        ## Dados para Análise
                        ```json
                        {dados_coletados_dfvendas}
                        ```

                        # TAREFA
                        Realize uma análise aprofundada dos dados fornecidos, seguindo as etapas abaixo.

                        ## 1. Análise Interna (Foco nos Dados Fornecidos)
                        Concentre-se exclusivamente nos dados do JSON para extrair os principais indicadores de desempenho (KPIs). Sua análise deve, no mínimo, abordar:
                        - **Performance de Produtos**: Quais são os produtos mais e menos vendidos (em volume e em valor)? Qual a margem de lucro por produto (preco - precocusto)?
                        - **Performance Operacional**: Qual o desempenho por operador de caixa e por PDV? Existem discrepâncias significativas?
                        - **Padrões Temporais**: Identifique padrões de vendas por hora do dia ou dia da semana.
                        - **Impacto dos Descontos**: Qual o volume de descontos concedidos e como eles impactam a receita e o lucro?
                        - **Análise de Cancelamentos**: Quais as taxas e os principais motivos de cancelamento (de cupons e de itens)? Identifique possíveis perdas de receita ou necessidade de treinamento.
                        - **Eficiência da Transação**: Calcule o tempo médio de atendimento por transação (dfdata_fechamento_cupom - dfdata_abertura_cupom).

                        ## 2. Enriquecimento com Contexto de Mercado (Opcional e Sinalizado)
                        Se, e somente se, a sua análise interna puder ser significativamente enriquecida, você pode, de forma proativa, correlacionar os achados com dados públicos e atuais sobre o varejo brasileiro.
                        - **Obrigatório**: Sempre que usar dados externos, **cite a fonte e o dado específico**.
                        - **Exemplos**:
                        - **Sazonalidade**: "O aumento nas vendas do 'Produto X' em Junho pode estar relacionado às festas juninas, uma tendência sazonal forte no varejo de alimentos."
                        - **Indicadores Econômicos**: "A queda no ticket médio pode refletir o atual índice de confiança do consumidor divulgado pelo IBGE."

                        # FORMATO DA RESPOSTA
                        Estruture sua resposta de forma clara, profissional e acionável, usando o seguinte formato em Markdown:

                        ### Sumário Executivo
                        Comece com um parágrafo conciso que resume os achados mais críticos e o potencial de impacto financeiro.

                        ### Principais Observações
                        Apresente os dados e padrões mais importantes que sustentam sua análise, usando bullet points para clareza. Use negrito para destacar valores e KPIs.

                        ### Análise e "Viés Lucrativo"
                        Traduza os dados em insights de negócio. O que esses números significam em termos de dinheiro? Onde a empresa está ganhando ou perdendo mais?

                        ### Recomendações Estratégicas
                        Finalize com 1 a 3 ações práticas e priorizadas que a gestão pode tomar para aumentar o lucro, reduzir custos ou melhorar a eficiência.

                        # DIRETRIZES FINAIS
                        - Seja analítico e orientado a dados.
                        - Foque em insights que levem a resultados financeiros positivos.
                        - Entregue uma análise de alto nível, como um verdadeiro consultor de negócios.
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
    st.warning("A funcionalidade de Análise Inteligente está desativada. Verifique a configuração da chave da API no menu lateral.", icon="🤖")