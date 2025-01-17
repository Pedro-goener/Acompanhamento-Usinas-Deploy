import pandas as pd
import streamlit as st
import plotly.express as px
from PIL import Image
import numpy as np
import os
from streamlit_plotly_events import plotly_events
import sys

# Adicione o diretório 'utils' ao caminho de importação
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../Utils')))
from interacao_db import load_and_prepare_data,db_config
#Encontra diretório atual
current_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
#Achando o caminho do icone
icon_path = os.path.join(current_dir,'.streamlit','Logo_azul_quadrada.PNG')
st.set_page_config(page_title="Dispersão Real X Esperado", layout="wide",page_icon=icon_path)
#Achando o caminho da logo e carregando com pillow
img_path = os.path.join(current_dir,'.streamlit','Logo_goener_colorida.png')
img = Image.open(img_path)
# Redimensionar a imagem (alterando a altura e mantendo a proporção)
img = img.resize((int(img.width * (50 / img.height)), 50))  # Altura = 30 pixels

# Exibir a imagem redimensionada
st.image(img)
#Puxar dados diretamente do banco de dados
df = load_and_prepare_data(db_config,'SELECT * FROM "Performance_data"')
df['Tempo'] = pd.to_datetime(df['Tempo'])
#Leitura do arquivo
st.title('Dispersão Real X Esperado')
#Filtro Temporal
data_selecionada = st.date_input('Selecione o intervalo temporal',value=(df['Tempo'].min(), df['Tempo'].max()))
if len(data_selecionada) == 2:
    ini, fim = map(pd.to_datetime, data_selecionada)
    df_filtrado = df[(df['Tempo'] >= ini) & (df['Tempo'] <= fim)]
else:
    data_unica = pd.to_datetime(data_selecionada[0])  # Pegue apenas a primeira data
    mask = df['Tempo'].dt.date == data_unica.date()  # Compare as datas
    df_filtrado = df[mask]
fig = px.scatter(df_filtrado,x='Potencia Ativa(kW)',y='Potencia Ativa(kW) prevista')
# Adicionar a reta esperada
x_line = np.linspace(df['Potencia Ativa(kW)'].min(), df['Potencia Ativa(kW)'].max(), 500)  # Definir os pontos da reta
fig.add_scatter(x=x_line, y=x_line, mode='lines', name='Esperado', line=dict(color='black', dash='dash',width=3))

st.plotly_chart(fig)