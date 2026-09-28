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
st.markdown('<p class="sub-text">Faça o upload da sua planilha Excel de compras e acompanhe os comparativos por fornecedor.</p>', unsafe_allow_html=True)

# Upload do arquivo Excel
uploaded_file = st.file_uploader("📂 Envie sua planilha Excel (.xlsx)", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        # Lê a planilha
        df = pd.read_excel(uploaded_file)
        
        # Normaliza os nomes das colunas (remove espaços extras e padroniza maiúsculas/minúsculas)
        df.columns = df.columns.astype(str).str.strip()
        
        st.success("Planilha carregada com sucesso!")
        
        # Exibe métricas gerais
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total de Itens (PNs)", len(df))
        with col2:
            st.metric("Total de Colunas", len(df.columns))
            
        with st.expander("👁️ Ver Dados da Planilha"):
            st.dataframe(df, use_container_width=True)
            
        # Identificação automática ou por mapeamento das colunas fornecidas pelo usuário
        # Colunas esperadas: 
        # A: Descrição do item, B: Número da peça do fabricante, C: Quantidade, 
        # D a K: Fornecedores (Crones, Draco, Erycla, Idealmak, ATI Brasil, Coppermetal, DNA Vedações, etc.)
        # L: Valor unitário
        
        st.markdown("---")
        st.markdown("### 📊 Comparativo de Fornecedores e Custos")
        
        # Lista dos fornecedores conhecidos baseados nas suas colunas
        fornecedores_colunas = [
            'fornecedor original crones', 'fornecedor draco', 'fornecedor erycla', 
            'fornecedor idealmak', 'fornecedor a t i brasil', 'fornecedor coppermetal', 
            'fornecedor dna vedações', 'crones', 'draco', 'erycla', 'idealmak', 
            'a t i brasil', 'coppermetal', 'dna vedações'
        ]
        
        # Encontra quais colunas no Excel correspondem aos fornecedores
        cols_encontradas = []
        for col in df.columns:
            col_lower = col.lower()
            if any(f in col_lower for f in ['crones', 'draco', 'erycla', 'idealmak', 'brasil', 'coppermetal', 'vedações']):
                cols_encontradas.append(col)
                
        if cols_encontradas:
            # Prepara dados para gráfico de preços médios/totais por fornecedor
            df_melted = pd.melt(df, id_vars=[c for c in df.columns if c not in cols_encontradas],
                                value_vars=cols_encontradas, 
                                var_name='Fornecedor', value_name='Valor')
            
            # Limpa valores nulos e converte para numérico
            df_melted['Valor'] = pd.to_numeric(df_melted['Valor'], errors='coerce')
            df_melted = df_melted.dropna(subset=['Valor'])
            
            if not df_melted.empty:
                # Gráfico de barras comparando os fornecedores
                fig = px.bar(df_melted, x='Fornecedor', y='Valor', color='Fornecedor',
                             title="Comparativo de Valores por Fornecedor",
                             labels={'Valor': 'Preço / Valor (R$)', 'Fornecedor': 'Fornecedor'})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("As colunas de fornecedores foram identificadas, mas os campos de valores estão vazios ou não numéricos.")
        else:
            # Procura qualquer coluna numérica para gerar gráfico genérico caso os nomes exatos variem
            colunas_numericas = df.select_dtypes(include=['number']).columns.tolist()
            colunas_texto = df.select_dtypes(include=['object']).columns.tolist()
            
            if colunas_numericas and colunas_texto:
                fig = px.bar(df, x=colunas_texto[0], y=colunas_numericas[0],
                             title=f"Análise de {colunas_numericas[0]} por {colunas_texto[0]}")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Envie uma planilha contendo valores numéricos nas colunas para gerar os gráficos automáticos.")

        # Pesquisa rápida por PN ou Descrição
        st.markdown("---")
        st.markdown("### 🔍 Pesquisa Rápida de Peças (PN) ou Descrição")
        termo_busca = st.text_input("Digite o nome da peça, código PN ou fornecedor:")
        
        if termo_busca:
            # Filtra o dataframe com base no termo digitado em qualquer coluna de texto
            mask = df.astype(str).apply(lambda x: x.str.contains(termo_busca, case=False, na=False)).any(axis=1)
            resultado_busca = df[mask]
            st.write(p := f"Encontrados {len(resultado_busca)} registros:")
            st.dataframe(resultado_busca, use_container_width=True)
        else:
            st.caption("Dica: Digite parte do código PN ou nome do item acima para filtrar instantaneamente.")

    except Exception as e:
        st.error(f"Erro ao processar a planilha: {e}")
else:
    st.info("Envie um arquivo Excel para iniciar.")
