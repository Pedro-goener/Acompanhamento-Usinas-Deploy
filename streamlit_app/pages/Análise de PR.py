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
from interacao_db import load_and_prepare_data,db_config,usinas_dict
from plotagem import plot_time_series
from filtros import filtro_temporal
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
#Filtros de usinas
usina = st.selectbox('Selecione a Usina',usinas_dict.keys())

#Leitura do Arquivo e conversão para datetime
query = f'SELECT * FROM pr_diario WHERE "Usina_id" = {usinas_dict[usina]} '
df_diario = load_and_prepare_data(db_config,query)
df_diario['Tempo'] = pd.to_datetime(df_diario['Tempo'])
df_diario['Ano_mes'] = df_diario['Tempo'].dt.to_period('M')
df_filtrado = filtro_temporal(df_diario)
#Plotagem dos inversores
fig0 = px.line(df_filtrado,x='Tempo',y='PR diario',color='Inversor')
st.plotly_chart(fig0)
inversor = st.selectbox('Selecione o inversor',[1,2,3,4,5,6,7,8,9,10])
df_filtrado = df_filtrado[df_filtrado['Inversor'] == inversor]
# # Agrupamento DataFrame por Mês
# df_mensal = df_diario.groupby('Ano_mes', as_index=False)[['Potencia Ativa(kW) prevista', 'Potencia Ativa(kW)']].sum()
# df_mensal['PR mensal'] = df_mensal['Potencia Ativa(kW)'] / df_mensal['Potencia Ativa(kW) prevista']


# # Gráfico de barras do PR diário
# fig1 = px.bar(df_filtrado, x='Tempo', y='PR diario')
# fig1.update_layout(
#     shapes=[
#         dict(
#             type="line",
#             x0=df_filtrado['Tempo'].min(), x1=df_filtrado['Tempo'].max(),
#             y0=1, y1=1,
#             line=dict(color="black", width=2, dash="dash"),
#         )
#     ]
# )
# fig1.update_traces(marker=dict(color='#009F98'))

# Exibindo gráfico interativo
selected_points = plotly_events(fig0)

# Se houver clique em uma barra
if selected_points:
    data_selecionada = pd.to_datetime(selected_points[0]['x']).date()
    df_temporal = load_and_prepare_data(db_config,f'SELECT * FROM performance_data WHERE "Inversor" = {inversor} AND "Usina_id" = {usinas_dict[usina]}')
    df_temporal['Tempo'] = pd.to_datetime(df_temporal['Tempo'])
    df_temporal = df_temporal[df_temporal['Tempo'].dt.date == data_selecionada]
    plot_time_series(df_temporal)

# # Gráfico do PR mensal
# df_mensal['Ano_mes'] = df_mensal['Ano_mes'].astype(str)
# fig2 = px.bar(df_mensal, x='Ano_mes', y='PR mensal')
# fig2.update_traces(marker=dict(color='#009F98'))
# st.plotly_chart(fig2)