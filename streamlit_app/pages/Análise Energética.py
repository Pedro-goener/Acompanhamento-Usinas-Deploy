import pandas as pd
import streamlit as st
import plotly.express as px
from PIL import Image
import os
import numpy as np
import sys
# Adicione o diretório 'utils' ao caminho de importação
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../Utils')))
from interacao_db import load_and_prepare_data,db_config,usinas_dict
from plotagem import plot_time_series
#Encontra diretório atual
current_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
#Achando o caminho do icone
icon_path = os.path.join(current_dir,'.streamlit','Logo_azul_quadrada.PNG')
st.set_page_config(page_title="Análise Energética", layout="wide",page_icon=icon_path)
#Achando o caminho da logo
img_path = os.path.join(current_dir,'.streamlit','Logo_goener_colorida.png')
img = Image.open(img_path)
# Redimensionar a imagem (alterando a altura e mantendo a proporção)
img = img.resize((int(img.width * (50 / img.height)), 50))  # Altura = 30 pixels
# Exibir a imagem redimensionada
st.image(img)
st.title('Análise Energética')
#Filtros iniciais
usina = st.selectbox('Selecione a Usina',usinas_dict.keys())
query = f'SELECT * FROM energy_data WHERE "Usina_id" = {usinas_dict[usina]}'
#Leitura do arquivo
df = load_and_prepare_data(db_config,query)
# Filtro Temporal
data_selecionada = st.date_input('Selecione o intervalo temporal', value=(df['Data'].min(), df['Data'].max()))
if len(data_selecionada) == 2:
    ini, fim = (data_selecionada[0], data_selecionada[1])
    df_filtrado = df[(df['Data'].dt.date >= ini) & (df['Data'].dt.date <= fim)]
else:
    data_unica = pd.to_datetime(data_selecionada[0]).date()
    mask = df['Data'] == data_unica
    df_filtrado = df[mask]

fig = px.bar(df_filtrado,x='Data',y='energia_diaria')
fig.update_traces(marker=dict(color='#009F98'))
st.plotly_chart(fig)

