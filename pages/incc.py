import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="house me - incc", page_icon="house_with_garden", layout='wide', initial_sidebar_state="auto")
# st.title(":house_with_garden: House me!")
st.header(":chart_with_upwards_trend: INCC - Índice Nacional de Custo da Construção")

# Sidebar
st.sidebar.title("Parâmetros")
group_viz_data = st.sidebar.selectbox("Visualizar dados por:", options=["mes", "ano"], index=0)
filter_year = st.sidebar.slider("Filtrar por ano:", min_value=1944, max_value=2024, value=(1998, 2024))

# Gráficos da Série Histórica do INCC
st.subheader(":arrow_forward: Série Histórica do INCC")
df = pd.read_parquet("data/incc.parquet") \
       .reset_index() \
       .rename(columns={'date': 'data', 'year': 'ano', 'month': 'mes', 'day': 'dia'})

df_filtered = df[(df['ano'] >= filter_year[0]) & (df['ano'] <= filter_year[1])]
if group_viz_data == "ano":
    df_filtered['incc_corrected'] = df_filtered['incc'] / 100 + 1
    df_filtered = df_filtered \
        .groupby('ano') \
        .incc_corrected \
        .prod() \
        .sub(1) \
        .mul(100) \
        .reset_index() \
        .rename(columns={'ano': 'data', 'incc_corrected': 'incc'})


chart_col_1, chart_col_2 = st.columns(2, gap='large')
mean_incc = df_filtered['incc'].mean()
median_incc = df_filtered['incc'].median()

fig_line = px.line(df_filtered, x='data', y="incc")
fig_line.add_hline(y=mean_incc, line_dash="dot", line_color="red", annotation_text=f"Média: {mean_incc:.2f}")
fig_line.add_hline(y=median_incc, line_dash="dot", line_color="green", annotation_text=f"Mediana: {median_incc:.2f}")
chart_col_1.plotly_chart(fig_line, use_container_width=True)

fig_hist = px.histogram(df_filtered, x='incc', nbins=50)
fig_hist.add_vline(x=mean_incc, line_dash="dot", line_color="red", annotation_text=f"Média: {mean_incc:.2f}")
fig_hist.add_vline(x=median_incc, line_dash="dot", line_color="green", annotation_text=f"Mediana: {median_incc:.2f}")
chart_col_2.plotly_chart(fig_hist, use_container_width=True)

# Tabela com os dados estatísticos
st.subheader(":arrow_forward: Dados Estatísticos")
st.write(f"- **Média:** {mean_incc:.2f}")
st.write(f"- **Mediana:** {median_incc:.2f}")
st.write(f"- **Desvio Padrão:** {df_filtered['incc'].std():.2f}")
st.write(f"- **Mínimo:** {df_filtered['incc'].min():.2f}")
st.write(f"- **Máximo:** {df_filtered['incc'].max():.2f}")