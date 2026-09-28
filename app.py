import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Configuração da página para celular
st.set_page_config(page_title="SupplyHub - Portal de Suprimentos", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .main-title { font-size: 22px; font-weight: bold; color: #1E3A8A; margin-bottom: 0px; }
    .sub-text { font-size: 14px; color: #4B5563; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">⚡ SupplyHub - Portal de Cotações e Suprimentos</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">Faça o upload da sua planilha Excel de compras para gerar os comparativos instantaneamente.</p>', unsafe_allow_html=True)

# Upload do arquivo Excel
uploaded_file = st.file_uploader("📂 Envie sua planilha Excel (.xlsx)", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        # Lê a planilha
        df = pd.read_excel(uploaded_file)
        
        # Limpa espaços nos nomes das colunas
        df.columns = df.columns.astype(str).str.strip()
        
        st.success("Planilha carregada com sucesso!")
        
        # Exibe métricas gerais
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total de Linhas / Itens", len(df))
        with col2:
            st.metric("Total de Colunas", len(df.columns))
            
        with st.expander("👁️ Ver Dados Completos da Planilha"):
            st.dataframe(df, use_container_width=True)
            
        st.markdown("---")
        st.markdown("### 📊 Gráficos e Comparativos Automáticos")
        
        # Identifica automaticamente colunas numéricas e de texto
        # Converte colunas que parecem números para formato numérico
        for col in df.columns:
            # Tenta converter para numérico se tiver símbolos de moeda ou texto misturado
            if df[col].dtype == 'object':
                temp_col = df[col].astype(str).str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).str.strip()
                converted = pd.to_numeric(temp_col, errors='coerce')
                if converted.notna().sum() > len(df) * 0.2: # Se mais de 20% forem números
                    df[col] = converted

        colunas_numericas = df.select_dtypes(include=['number']).columns.tolist()
        colunas_texto = df.select_dtypes(include=['object']).columns.tolist()
        
        if colunas_numericas:
            # Se houver várias colunas numéricas (como os vários fornecedores e valor unitário)
            if len(colunas_numericas) > 1 and colunas_texto:
                # Cria um gráfico comparando as colunas numéricas por item (usando a primeira coluna de texto como base, ex: descrição ou PN)
                col_base = colunas_texto[0]
                
                # Seletor para escolher qual coluna numérica visualizar ou ver todas
                opcoes_grafico = ["Todas as colunas numéricas (Comparativo Geral)"] + colunas_numericas
                escolha_metrica = st.selectbox("Selecione a métrica ou fornecedor para visualizar:", opcoes_grafico)
                
                if escolha_metrica == "Todas as colunas numéricas (Comparativo Geral)":
                    df_melted = pd.melt(df, id_vars=[col_base], value_vars=colunas_numericas, var_name='Métrica / Fornecedor', value_name='Valor')
                    df_melted['Valor'] = pd.to_numeric(df_melted['Valor'], errors='coerce')
                    df_melted = df_melted.dropna(subset=['Valor'])
                    
                    if not df_melted.empty:
                        fig = px.bar(df_melted, x=col_base, y='Valor', color='Métrica / Fornecedor',
                                     title="Comparativo entre Colunas / Fornecedores por Item",
                                     barmode='group')
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Não há valores numéricos suficientes para exibir no gráfico.")
                else:
                    fig = px.bar(df, x=col_base, y=escolha_metrica, color=col_base,
                                 title=f"Análise de {escolha_metrica}")
                    st.plotly_chart(fig, use_container_width=True)
            elif colunas_numericas and colunas_texto:
                fig = px.bar(df, x=colunas_texto[0], y=colunas_numericas[0],
                             title=f"Gráfico de {colunas_numericas[0]} por {colunas_texto[0]}")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("A planilha possui dados numéricos, mas faltam colunas de texto para associar aos gráficos.")
        else:
            st.warning("Não foram encontradas colunas com valores numéricos nesta aba da planilha. Verifique se os preços/quantidades estão salvos como números.")

        # Pesquisa rápida
        st.markdown("---")
        st.markdown("### 🔍 Pesquisa Rápida na Planilha")
        termo_busca = st.text_input("Digite o nome da peça, código PN ou fornecedor:")
        
        if termo_busca:
            mask = df.astype(str).apply(lambda x: x.str.contains(termo_busca, case=False, na=False)).any(axis=1)
            resultado_busca = df[mask]
            st.write(f"Encontrados {len(resultado_busca)} registros:")
            st.dataframe(resultado_busca, use_container_width=True)
        else:
            st.caption("Dica: Digite parte do código PN ou descrição para filtrar instantaneamente.")

    except Exception as e:
        st.error(f"Erro ao processar a planilha: {e}")
else:
    st.info("Envie um arquivo Excel para iniciar.")
