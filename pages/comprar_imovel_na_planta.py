import numpy as np
import pandas as pd
import streamlit as st

# Page Config
st.set_page_config(page_title="house me - comprar na planta", page_icon="house_with_garden", layout="wide", initial_sidebar_state="auto")


# Initial State
if 'valor_imovel' not in st.session_state:
    st.session_state['valor_imovel'] = 500000

if 'metros_quadrados' not in st.session_state:
    st.session_state['metros_quadrados'] = 48

if 'tempo_construcao' not in st.session_state:
    st.session_state['tempo_construcao'] = 36

if 'taxa_anual_incc' not in st.session_state:
    st.session_state['taxa_anual_incc'] = 8.0

if 'taxa_anual_aplicacao' not in st.session_state:
    st.session_state['taxa_anual_aplicacao'] = 14.0


# Header
# st.title(":house_with_garden: House me!")
st.header(":seedling: Simulação de Compra de Imovel na Planta")
st.markdown("**Vale a pena comprar seu imóvel na planta? Vamos simular!**")
st.markdown("---")


# Sidebar
st.sidebar.title("Parâmetros Iniciais") 
st.session_state['valor_imovel'] = st.sidebar.number_input("Valor do imóvel", value=float(st.session_state['valor_imovel']))
st.session_state['metros_quadrados'] = st.sidebar.number_input("Metros quadrados", value=st.session_state['metros_quadrados'])
st.session_state['tempo_construcao'] = st.sidebar.number_input("Tempo de construção (meses)", value=st.session_state['tempo_construcao'])
valor_entrada_planta = st.sidebar.number_input("Valor da entrada", value=0.1 * st.session_state['valor_imovel'])
valor_total_mensal_planta = st.sidebar.number_input("Valor para mensais", value=0.12 * st.session_state['valor_imovel'])
valor_total_anual_planta = st.sidebar.number_input("Valor para anuais", value=0.08 * st.session_state['valor_imovel'])

valor_mensal_planta = valor_total_mensal_planta / st.session_state['tempo_construcao']
valor_anual_planta = valor_total_anual_planta / int(st.session_state['tempo_construcao'] / 12)

valor_total_planta = valor_entrada_planta + valor_total_mensal_planta + valor_total_anual_planta
valor_financiamento = st.session_state['valor_imovel'] - valor_entrada_planta - valor_total_mensal_planta - valor_total_anual_planta


# Ficha com os valores do imóvel
col_into_1, col_into_2 = st.columns(2)
col_into_1.subheader(":arrow_forward: Resumo do Imóvel")
col_into_1.write(f"- **Valor do imóvel:** R$ {st.session_state['valor_imovel']:,.2f}")
col_into_1.write(f"- **Metros quadrados:** {st.session_state['metros_quadrados']} m²")
col_into_1.write(f"- **Valor do metro quadrado:** R$ {st.session_state['valor_imovel'] / st.session_state['metros_quadrados']:,.2f}")
col_into_1.write(f"- **Tempo de construção:** {st.session_state['tempo_construcao']} meses")
col_into_1.write(f"- **Entrada:** R$ {valor_entrada_planta:,.2f} | {valor_entrada_planta / st.session_state['valor_imovel']:.1%}")
col_into_1.write(f"- **Valor total mensal:** R$ {valor_total_mensal_planta:,.2f} | {valor_total_mensal_planta / st.session_state['valor_imovel']:.1%} | {st.session_state['tempo_construcao']} x {valor_mensal_planta:,.2f}")
col_into_1.write(f"- **Valor total anual:** R$ {valor_total_anual_planta:,.2f} | {valor_total_anual_planta / st.session_state['valor_imovel']:.1%} | {int(st.session_state['tempo_construcao'] / 12)} x {valor_anual_planta:,.2f}")
col_into_1.write(f"- **Valor total pago durante a construção:** R$ {valor_total_planta:,.2f} | {valor_total_planta / st.session_state['valor_imovel']:.1%}")
col_into_1.write(f"- **Valor a ser financiado:** R$ {valor_financiamento:,.2f} | {valor_financiamento / st.session_state['valor_imovel']:.1%}")

# Fluxo de Pagamento
col_into_2.subheader(":arrow_forward: Fluxo de Pagamento na Fase de Construção")

data = {'mes': [], 'entrada': [], 'mensalidade': [], 'anualidade': []}
for i in range(1, st.session_state['tempo_construcao'] + 1):
    data['mes'].append(i)
    data['entrada'].append(valor_entrada_planta if i == 1 else 0)
    data['mensalidade'].append(valor_mensal_planta)
    data['anualidade'].append(valor_anual_planta if i % 12 == 0 else 0)

df = pd.DataFrame(data)
col_into_2.dataframe(df)


# Incidência do INCC
st.markdown("---")
st.subheader(":arrow_forward: Incidência do INCC")
col_incc_1, col_incc_2 = st.columns(2)
st.session_state['taxa_anual_incc'] = col_incc_1.number_input("Taxa da Anual do INCC (%)", value=st.session_state['taxa_anual_incc'], format="%.2f")
taxa_mensal_incc = ((1 + st.session_state['taxa_anual_incc'] / 100) ** (1 / 12) - 1) * 100

df_incc = df.copy()
df_incc['incc'] = taxa_mensal_incc
df_incc['incc_corrigido'] = df_incc['incc'] / 100 + 1
df_incc['incc_acumulado'] = df_incc['incc_corrigido'].cumprod()
df_incc['mensalidade_corrigida'] = df_incc['mensalidade'] * df_incc['incc_acumulado']
df_incc['anualidade_corrigida'] = df_incc['anualidade'] * df_incc['incc_acumulado']
df_incc['total_corrigido'] = df_incc['entrada'] + df_incc['mensalidade_corrigida'] + df_incc['anualidade_corrigida']

col_incc_1.write(f"**Taxa mensal do INCC:** {taxa_mensal_incc:.2f}%")
incc_acumulado = df_incc['incc_acumulado'].iloc[-1]
col_incc_1.write(f"**INCC acumulado no período:** {(incc_acumulado - 1) * 100:.2f}%")
col_incc_1.write(f"**Valor total mensal corrigido:** R$ {df_incc['mensalidade_corrigida'].sum():,.2f} | {df_incc['mensalidade_corrigida'].sum() / st.session_state['valor_imovel']:.1%} | {st.session_state['tempo_construcao']} x ~{df_incc['mensalidade_corrigida'].mean():,.2f}")
col_incc_1.write(f"**Valor total anual corrigido:** R$ {df_incc['anualidade_corrigida'].sum():,.2f} | {df_incc['anualidade_corrigida'].sum() / st.session_state['valor_imovel']:.1%} | {int(st.session_state['tempo_construcao'] / 12)} x ~{(df_incc['anualidade_corrigida'].sum()/int(st.session_state['tempo_construcao'] / 12)):,.2f}")
col_incc_1.write(f"**Valor total pago durante a construção corrigido:** R$ {df_incc['total_corrigido'].sum():,.2f} | {df_incc['total_corrigido'].sum() / st.session_state['valor_imovel']:.1%}")
col_incc_1.write(f"**Valor a ser financiado corrigido:** R$ {valor_financiamento * incc_acumulado:,.2f} | {valor_financiamento * incc_acumulado / st.session_state['valor_imovel']:.1%}")

st.dataframe(df_incc)


# Comparação com Aplicações
st.markdown("---")
st.subheader(":arrow_forward: Comparação com Aplicações Financeiras")
col_invest_1, col_invest_2 = st.columns(2)
st.session_state['taxa_anual_aplicacao'] = col_invest_1.number_input("Taxa da Anual da Aplicação (%)", value=14.0, format="%.2f")
taxa_mensal_aplicacao = ((1 + st.session_state['taxa_anual_aplicacao'] / 100) ** (1 / 12) - 1) * 100
col_invest_1.write(f"**Taxa mensal da aplicação:** {taxa_mensal_aplicacao:.2f}%")

df_invest = df_incc.copy()[['mes', 'total_corrigido']]
df_invest['tx_mensal'] = taxa_mensal_aplicacao
df_invest['tx_mensal_corrigida'] = df_invest['tx_mensal'].div(100).add(1)



for i in range(0, st.session_state['tempo_construcao']):
    if i == 0:
        df_invest.loc[i, 'rend_acumulado'] = df_invest.loc[i, 'total_corrigido'] * (df_invest.loc[i, 'tx_mensal_corrigida'])
    else:
        df_invest.loc[i, 'rend_acumulado'] = (df_invest.loc[i - 1, 'rend_acumulado'] + df_invest.loc[i, 'total_corrigido']) * (df_invest.loc[i, 'tx_mensal_corrigida'])

col_invest_2.dataframe(df_invest)

valor_acumulado_aplicacao = df_invest.iloc[-1]['rend_acumulado']
col_invest_1.write(f"**Valor acumulado na aplicação:** R$ {valor_acumulado_aplicacao:,.2f}")
col_invest_1.write(f"**Diferença entre o valor acumulado e o valor investido:** R$ {valor_acumulado_aplicacao - valor_total_planta:,.2f}")
col_invest_1.write(f"**Rendimento Total:** {((valor_acumulado_aplicacao - valor_total_planta) / valor_total_planta):.1%}")
