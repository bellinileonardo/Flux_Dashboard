-----

# 🚀 Flux Dashboard: Inteligência de Varejo com Agentes de IA
#### [Acessar Versão Online](https://frontfluxdashboard.streamlit.app/)

O Flux Dashboard não é apenas um painel de visualização; é uma plataforma de Inteligência Operacional que integra dados reais de ERP com uma camada de raciocínio baseada em IA Generativa. Ele foi desenhado para eliminar o abismo entre o dado bruto e a decisão estratégica.

# 🤖 A Inteligência por trás do Flux
O grande diferencial do projeto é o ecossistema de Agentes de IA Personalizados. Não utilizamos apenas um chat genérico; implementamos uma estrutura de consultoria técnica:

** Agentes de Setor: Prompts especializados para as verticais de Vendas, Estoque e Financeiro. Cada agente possui um "System Prompt" que define seu comportamento, métricas de sucesso e tom de voz.

** Consultor de IA Contextual: Utiliza RAG (Retrieval-Augmented Generation) para analisar os dados que estão em tela. Se você filtrar uma queda em março, o agente "lê" o DataFrame e explica a causa raiz.

** Orquestração: Baseado em LangChain e alimentado pelo Google Gemini, garantindo respostas rápidas e precisas com foco em varejo.

# 📊 Visualizações Claras e Intuitivas
Mergulhe em gráficos e tabelas que simplificam a compreensão de seus **Key Performance Indicators (KPIs)** de varejo mais importantes. Entenda, de forma instantânea, o que está funcionando e o que precisa de atenção.
    <img width="1833" height="865" alt="image" src="https://github.com/user-attachments/assets/4b856603-9f5e-428b-a5e7-80d7150b8943" />,
    <img width="1879" height="851" alt="Screenshot_6" src="https://github.com/user-attachments/assets/e779ffab-3a19-4c67-b182-0057e55ebcc1" />
    <img width="1898" height="794" alt="Screenshot_3" src="https://github.com/user-attachments/assets/9b2256fe-4141-42f4-bdef-4a55af7c8429" />
    <img width="1829" height="824" alt="Screenshot_5" src="https://github.com/user-attachments/assets/d0fc9f39-4658-497b-914e-9009dee5b24d" />
    <img width="1878" height="789" alt="Screenshot_4" src="https://github.com/user-attachments/assets/b6eb9a55-76a0-415c-9bae-d4f94d4b0171" />



# ✨ Funcionalidades Core
##📊 BI & KPIs em Tempo Real
Visualizações dinâmicas integradas a sistemas de origem (ERP). Transformamos transações complexas em KPIs claros como Ticket Médio, Taxa de Ruptura e Margem de Contribuição.

## 🔎 Flux IA (Análise Profunda)
Nossa IA analisa o comportamento das vendas no período e gera um relatório de Otimização de Resultados e Eficiência Operacional. É o fim do "eu acho" e o início do "os dados mostram".

## 📈 Predição & Prevenção
Projeções de Vendas: Algoritmos que identificam sazonalidade e tendências.

Análise de Ruptura: Identificação inteligente de falhas no estoque antes que elas afetem o faturamento.

## 🛠️ Stack Técnica
Linguagem: Python

Interface: Streamlit

IA/LLM: Google Gemini API / LangChain (Agentes)

Dados: Pandas (ETL & Manipulação), NumPy

Visualização: Plotly / Altair

## ⚙️ Arquitetura e Engenharia de Contexto

Diferente de soluções de chat genéricas, o Flux Dashboard utiliza um pipeline de dados inteligente:

- **Data Sourcing:** Extração automatizada via `SQLAlchemy`.
- **Contextual Switching:** O sistema monitora o estado da sessão no Streamlit. Ao navegar entre as abas (Home, Vendas, RH), o motor de IA troca automaticamente o conjunto de dados (DataFrame) e o "System Prompt" do consultor.
- **RAG Adaptativo:** O Agente de Chat recebe um `chunk` dos dados processados no Pandas, permitindo que ele execute análises estatísticas em tempo real sobre os filtros aplicados pelo usuário.

-----
