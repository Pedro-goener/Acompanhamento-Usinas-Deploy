import pandas as pd
import streamlit as st
import plotly.express as px
from PIL import Image
import os
#Encontra diretório atual
current_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
#Achando o caminho do icone
icon_path = os.path.join(current_dir,'.streamlit','Logo_azul_quadrada.PNG')
st.set_page_config(page_title="PR diário", layout="wide",page_icon=icon_path)
#Achando o caminho da logo e carregando com pillow
img_path = os.path.join(current_dir,'.streamlit','Logo_goener_colorida.png')
img = Image.open(img_path)
# Redimensionar a imagem (alterando a altura e mantendo a proporção)
img = img.resize((int(img.width * (50 / img.height)), 50))  # Altura = 30 pixels

# Exibir a imagem redimensionada
st.image(img)
st.title('PR diário')
#Leitura do Arquivo, conversão para datetime e criação da data
file_path = os.path.join(current_dir,'Dados_treinados','Tabela_ocorrencias.csv')
df = pd.read_csv(file_path)
df['Tempo'] = pd.to_datetime(df['Tempo'])
df['Data'] = df['Tempo'].dt.date
#Agrupamendo DataFrame por Data
df_diario = df.groupby('Data',as_index=False)['PR'].mean()
#Filtro Temporal
data_selecionada = st.date_input('Selecione o intervalo temporal',value=(df['Tempo'].min(), df['Tempo'].max()))
if isinstance(data_selecionada,tuple) and len(data_selecionada) == 2:
    # Converter as datas selecionadas para datetime para realizar a comparação
    ini, fim = map(lambda x: pd.to_datetime(x).date(), data_selecionada)
    # Filtrar o DataFrame pelo intervalo de datas
    df_filtrado = df_diario[(df_diario['Data'] >= ini) & (df_diario['Data'] <= fim)]
    fig = px.bar(df_filtrado,x='Data',y='PR')
    #Adição linha preta
    fig.update_layout(
        shapes=[
            dict(
                type="line",
                x0=df_filtrado['Data'].min(),x1=df_filtrado['Data'].max(),  # Fim do eixo x
                y0=1,y1=1,  # Posição no eixo y
                line=dict(color="black",width=2,dash="dash"),
            )
        ]
    )
    st.plotly_chart(fig)
else:
    st.warning('Selecione a data de fim')
