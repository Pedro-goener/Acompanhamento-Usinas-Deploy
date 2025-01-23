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
st.set_page_config(page_title="Séries Temporais", layout="wide",page_icon=icon_path)
#Achando o caminho da logo
img_path = os.path.join(current_dir,'.streamlit','Logo_goener_colorida.png')
img = Image.open(img_path)
# Redimensionar a imagem (alterando a altura e mantendo a proporção)
img = img.resize((int(img.width * (50 / img.height)), 50))  # Altura = 30 pixels
# Exibir a imagem redimensionada
st.image(img)
st.title('Séries Temporais')
#Filtros iniciais
usina = st.selectbox('Selecione a Usina',usinas_dict.keys())

inversor = st.selectbox('Selecione o inversor',[1,2,3,4,5,6,7,8,9,10])
#Leitura do Arquivo e conversão para datetime
query = f'SELECT * FROM performance_data WHERE "Inversor" = {inversor} AND "Usina_id" = {usinas_dict[usina]}'
df = load_and_prepare_data(db_config,query)
df['Tempo'] = pd.to_datetime(df['Tempo'])
#Filtro Temporal
data_selecionada = st.date_input('Selecione o intervalo temporal',value=(df['Tempo'].min(), df['Tempo'].max()))
if len(data_selecionada) == 2:
    ini, fim = map(pd.to_datetime, data_selecionada)
    df_filtrado = df[(df['Tempo'] >= ini) & (df['Tempo'] <= fim)]
else:
    data_unica = pd.to_datetime(data_selecionada[0])  # Pegue apenas a primeira data
    mask = df['Tempo'].dt.date == data_unica.date()  # Compare as datas
    df_filtrado = df[mask]

plot_time_series(df_filtrado)

