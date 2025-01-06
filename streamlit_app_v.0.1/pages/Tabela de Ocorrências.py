import pandas as pd
import streamlit as st
from PIL import Image
import os
#Encontra diretório atual
current_dir = os.path.dirname(os.path.abspath(__file__))
#Achando o caminho do icone
icon_path = os.path.join(current_dir,'.streamlit','Logo_azul_quadrada.PNG')
st.set_page_config(page_title="Tabela de Ocorrencias", layout="wide",page_icon=icon_path)
#Achando o caminho da logo
img_path = os.path.join(current_dir,'.streamlit','Logo_goener_colorida.png')
img = Image.open(img_path)
# Redimensionar a imagem (alterando a altura e mantendo a proporção)
img = img.resize((int(img.width * (50 / img.height)), 50))  # Altura = 30 pixels
# Exibir a imagem redimensionada
st.image(img)
st.title('Tabela de Ocorrências')
#Leitura do Arquivo e conversão para datetime
df = pd.read_csv('Dados_treinados/Tabela_ocorrencias.csv')
df['Tempo'] = pd.to_datetime(df['Tempo'])
#Filtros
#Filtro de status
status = ['Perda Total','Perda Dissolvida','Perda Instantanea','Normal']
status_selecionados = st.multiselect('Selecione o tipo de ocorrência',status,default=['Perda Total','Perda Dissolvida','Perda Instantanea'])
df_filtrado  = df[df['Status'].isin(status_selecionados)]
#Filtro Temporal
data_selecionada = st.date_input('Selecione o intervalo temporal',value=(df['Tempo'].min(), df['Tempo'].max()))
if isinstance(data_selecionada,tuple) and len(data_selecionada) == 2:
    # Converter as datas selecionadas para datetime para realizar a comparação
    ini, fim = map(pd.to_datetime, data_selecionada)
    # Filtrar o DataFrame pelo intervalo de datas
    df_filtrado = df_filtrado[(df_filtrado['Tempo'] >= ini) & (df_filtrado['Tempo'] <= fim)]

else:
    data_unica = pd.to_datetime(data_selecionada[0])  # Pegue apenas a primeira data
    mask = df_filtrado['Tempo'].dt.date == data_unica.date()  # Compare as datas
    df_filtrado = df_filtrado[mask]
st.dataframe(df_filtrado.head(50))