import pandas as pd
import streamlit as st
import plotly.express as px
from PIL import Image
import os
import numpy as np
from streamlit_plotly_events import plotly_events
import sys

# Adicione o diretório 'utils' ao caminho de importação
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../Utils')))
from interacao_db import load_and_prepare_data,db_config
# Encontra diretório atual
current_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# Achando o caminho do icone
icon_path = os.path.join(current_dir, '.streamlit', 'Logo_azul_quadrada.PNG')
st.set_page_config(page_title="PR diário", layout="wide", page_icon=icon_path)

# Achando o caminho da logo e carregando com pillow
img_path = os.path.join(current_dir, '.streamlit', 'Logo_goener_colorida.png')
img = Image.open(img_path)
# Redimensionar a imagem
img = img.resize((int(img.width * (50 / img.height)), 50))
st.image(img)



#------------------------------------------------------------------#
st.title('PR diário')
#Filtros iniciais
usina = st.selectbox('Selecione a Usina',['Betânia','Porteiras'])
performance_usinas = {
    'Betânia':'performance_data_bet',
    'Porteiras':'performance_data_por'
}
inversor = st.selectbox('Selecione o inversor',[1,2,3,4,5,6,7,8,9,10])
#Leitura do Arquivo e conversão para datetime
query = f'SELECT * FROM {performance_usinas[usina]} WHERE "Inversor" = {inversor}'
df = load_and_prepare_data(db_config,query)
df['Tempo'] = pd.to_datetime(df['Tempo'])
df['Data'] = df['Tempo'].dt.date
df['Ano_mes'] = df['Tempo'].dt.to_period('M')
# Agrupamento DataFrame por Data
df_diario = df.groupby('Data', as_index=False)[['Potencia Ativa(kW) prevista', 'Potencia Ativa(kW)']].sum()
df_diario['PR diário'] = df_diario['Potencia Ativa(kW)'] / df_diario['Potencia Ativa(kW) prevista']

# Agrupamento DataFrame por Mês
df_mensal = df.groupby('Ano_mes', as_index=False)[['Potencia Ativa(kW) prevista', 'Potencia Ativa(kW)']].sum()
df_mensal['PR mensal'] = df_mensal['Potencia Ativa(kW)'] / df_mensal['Potencia Ativa(kW) prevista']

# Filtro Temporal
data_selecionada = st.date_input('Selecione o intervalo temporal', value=(df['Tempo'].min(), df['Tempo'].max()))
if len(data_selecionada) == 2:
    ini, fim = (data_selecionada[0], data_selecionada[1])
    df_filtrado = df_diario[(df_diario['Data'] >= ini) & (df_diario['Data'] <= fim)]
else:
    data_unica = pd.to_datetime(data_selecionada[0]).date()
    mask = df['Data'] == data_unica
    df_filtrado = df_diario[mask]

# Gráfico de barras do PR diário
fig1 = px.bar(df_filtrado, x='Data', y='PR diário')
fig1.update_layout(
    shapes=[
        dict(
            type="line",
            x0=df_filtrado['Data'].min(), x1=df_filtrado['Data'].max(),
            y0=1, y1=1,
            line=dict(color="black", width=2, dash="dash"),
        )
    ]
)
fig1.update_traces(marker=dict(color='#009F98'))

# Exibindo gráfico interativo
selected_points = plotly_events(fig1)

# Se houver clique em uma barra
if selected_points:
    data_selecionada = pd.to_datetime(selected_points[0]['x']).date()
    df_temporal = df[df['Tempo'].dt.date == data_selecionada]

    # Cálculo das energias real e prevista
    energia_real = float(np.trapezoid(df_temporal['Potencia Ativa(kW)'], df_temporal['Tempo'])) / (3.6 * 1e12)
    energia_prevista = float(np.trapezoid(df_temporal['Potencia Ativa(kW) prevista'], df_temporal['Tempo'])) / (
                3.6 * 1e12)

    st.markdown(f"<h3>Energia real: {energia_real:.2f} kWh</h3>", unsafe_allow_html=True)
    st.markdown(f"<h3>Energia prevista: {energia_prevista:.2f} kWh</h3>", unsafe_allow_html=True)

    # Gráfico da série temporal
    df_temporal = df_temporal.sort_values(by='Tempo')
    fig_temporal = px.line(df_temporal, x='Tempo', y=['Potencia Ativa(kW) prevista', 'Potencia Ativa(kW)'])
    fig_temporal.update_layout(
        yaxis_title='Potência Ativa (kW)',
    )
    fig_temporal.update_traces(
        line=dict(color='#808000'),
        selector=dict(name='Potencia Ativa(kW)')
    )
    fig_temporal.update_traces(
        line=dict(color='#009F98', dash='dash'),
        selector=dict(name='Potencia Ativa(kW) prevista')
    )
    st.plotly_chart(fig_temporal)

# Gráfico do PR mensal
df_mensal['Ano_mes'] = df_mensal['Ano_mes'].astype(str)
fig2 = px.bar(df_mensal, x='Ano_mes', y='PR mensal')
fig2.update_traces(marker=dict(color='#009F98'))
st.plotly_chart(fig2)