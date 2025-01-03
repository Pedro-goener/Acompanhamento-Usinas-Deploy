import pandas as pd
import streamlit as st
import plotly.express as px
from PIL import Image
icon = '.streamlit/Logo_azul_quadrada.PNG'
st.set_page_config(page_title="Séries Temporais", layout="wide",page_icon=icon)
img = Image.open('.streamlit/Logo_goener_colorida.png')
# Redimensionar a imagem (alterando a altura e mantendo a proporção)
img = img.resize((int(img.width * (50 / img.height)), 50))  # Altura = 30 pixels
# Exibir a imagem redimensionada
st.image(img)
st.title('Séries Temporais')
#Leitura do Arquivo e conversão para datetime
df = pd.read_csv('C:\\Users\\Windows\\Documents\\Pedro-Goener\\Projeto Acompanhamento Usinas\\Summer-Goener\\dados\\Dados_treinados\\Tabela_ocorrencias.csv')
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

fig = px.line(df_filtrado, x='Tempo', y=['Potencia Ativa Prevista (Random Forest)', 'Potencia Ativa(kW)'])
st.plotly_chart(fig)

