import datetime
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="SupplyHub - Dashboard Automático", page_icon="⚡", layout="wide"
)

# Estilização visual limpa
st.markdown(
    """
    <style>
    .main-title { font-size: 2.4rem; color: #1E3A8A; font-weight: 800; }
    .sub-title { font-size: 1.1rem; color: #4B5563; }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    '<p class="main-title">⚡ SupplyHub - Portal Auto-Dashboard</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="sub-title">Suba qualquer planilha Excel e o sistema gerará'
    " instantaneamente os indicadores e gráficos correspondentes.</p>",
    unsafe_allow_html=True,
)

# Sidebar para Upload
st.sidebar.header("📁 Upload de Excel")
uploaded_file = st.sidebar.file_uploader(
    "Envie seu arquivo Excel (.xlsx / .xls)", type=["xlsx", "xls"]
)

# Usar arquivo padrão se nenhum for enviado
if uploaded_file is None:
  try:
    default_path = "GRV 28-09- TESTE.xlsx"
    xls = pd.ExcelFile(default_path)
    st.sidebar.info(
        "📌 Usando arquivo de exemplo padrão (`GRV 28-09- TESTE.xlsx`). Envie o"
        " seu arquivo acima para substituir."
    )
  except Exception as e:
    xls = None
    st.sidebar.error("Nenhum arquivo encontrado. Por favor, envie um Excel.")
else:
  try:
    xls = pd.ExcelFile(uploaded_file)
    st.sidebar.success(
        f"Arquivo carregado com sucesso! Abas encontradas: {len(xls.sheet_names)}"
    )
  except Exception as e:
    st.sidebar.error(f"Erro ao ler o arquivo Excel: {e}")
    xls = None

if xls is not None:
  # Seletor de Abas caso o Excel tenha múltiplas abas
  aba_selecionada = st.sidebar.selectbox(
      "Selecione a Aba do Excel para visualizar:", xls.sheet_names
  )

  # Carregar dados da aba escolhida
  df = pd.read_excel(xls, sheet_name=aba_selecionada)

  # Limpar nomes das colunas (remover espaços extras)
  df.columns = df.columns.astype(str).str.strip()

  # Exibir metadados rápidos
  st.divider()
  col_info1, col_info2, col_info3 = st.columns(3)
  with col_info1:
    st.metric("Aba Visualizada", aba_selecionada)
  with col_info2:
    st.metric("Total de Linhas (Registros)", len(df))
  with col_info3:
    st.metric("Total de Colunas", len(df.columns))

  # Separar colunas numéricas e de texto automaticamente
  colunas_numericas = df.select_dtypes(
      include=[np.number]
  ).columns.tolist()
  colunas_texto = df.select_dtypes(include=["object", "category"]).columns.tolist()

  # KPIs Automáticos baseados nas colunas numéricas disponíveis
  if colunas_numericas:
    st.subheader("📊 Indicadores Automáticos (KPIs)")
    kpi_cols = st.columns(min(len(colunas_numericas), 4))
    for i, col_num in enumerate(colunas_numericas[:4]):
      soma_val = df[col_num].sum()
      with kpi_cols[i]:
        st.metric(label=f"Soma de {col_num}", value=f"{soma_val:,.2f}")

  st.divider()

  # Filtro e Pesquisa Global na Tabela
  st.subheader("🔍 Pesquisa e Exploração de Dados")
  termo_pesquisa = st.text_input(
      "Digite qualquer termo para buscar em tempo real na tabela:"
  )

  df_exibicao = df.copy()
  if termo_pesquisa:
    mask = df_exibicao.astype(str).apply(
        lambda x: x.str.contains(termo_pesquisa, case=False, na=False)
    ).any(axis=1)
    df_exibicao = df_exibicao[mask]

  # Exibir Tabela Interativa
  st.dataframe(df_exibicao, use_container_width=True)

  st.divider()

  # Geração Automática de Gráficos Dinâmicos
  st.subheader("📈 Gráficos e Análises Visuais Gerados Automaticamente")

  if colunas_texto and colunas_numericas:
    c_graf1, c_graf2 = st.columns(2)

    with c_graf1:
      st.markdown("##### Distribuição / Agrupamento")
      cat_col = st.selectbox(
          "Escolha a coluna de Categoria / Texto:", colunas_texto, key="cat1"
      )
      num_col = st.selectbox(
          "Escolha a coluna Numérica para métrica:", colunas_numericas, key="num1"
      )

      if cat_col and num_col:
        df_agrupado = (
            df.groupby(cat_col)[num_col]
            .sum()
            .reset_index()
            .sort_values(by=num_col, ascending=False)
            .head(15)
        )
        fig_bar = px.bar(
            df_agrupado,
            x=cat_col,
            y=num_col,
            title=f"Top 15: {num_col} por {cat_col}",
            color=num_col,
            color_continuous_scale="Blues",
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with c_graf2:
      st.markdown("##### Participação / Composição")
      if len(colunas_texto) > 1:
        cat_col2 = st.selectbox(
            "Segunda coluna de Categoria:", colunas_texto, index=1, key="cat2"
        )
      else:
        cat_col2 = cat_col

      if cat_col2 and num_col:
        df_pie = (
            df.groupby(cat_col2)[num_col]
            .sum()
            .reset_index()
            .sort_values(by=num_col, ascending=False)
            .head(10)
        )
        fig_pie = px.pie(
            df_pie,
            names=cat_col2,
            values=num_col,
            title=f"Participação de {num_col} por {cat_col2}",
            hole=0.4,
        )
        st.plotly_chart(fig_pie, use_container_width=True)
  else:
    st.info(
        "A aba selecionada precisa conter colunas de texto e numéricas para"
        " gerar gráficos automáticos."
    )

else:
  st.warning("Envie um arquivo Excel para iniciar.")
