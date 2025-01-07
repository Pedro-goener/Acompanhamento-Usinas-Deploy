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

#Leitura do Arquivo, conversão para datetime e criação da data e mês
file_path = os.path.join(current_dir,'Dados_ocorrencias','Tabela_ocorrencias_att.csv')
df = pd.read_csv(file_path)
df['Tempo'] = pd.to_datetime(df['Tempo'])
df['Data'] = df['Tempo'].dt.date
df['Ano_mes'] = df['Tempo'].dt.to_period('M')
#Agrupamendo DataFrame por Data
df_diario = df.groupby('Data',as_index=False)[['Potencia Ativa(kW) prevista','Potencia Ativa(kW)']].sum()
df_diario['PR diário'] = df_diario['Potencia Ativa(kW)']/df_diario['Potencia Ativa(kW) prevista']
#Agrupamento DataFrame por Mês
df_mensal = df.groupby('Ano_mes', as_index=False)[['Potencia Ativa(kW) prevista', 'Potencia Ativa(kW)']].sum()
df_mensal['PR mensal'] = df_mensal['Potencia Ativa(kW)']/df_mensal['Potencia Ativa(kW) prevista']
st.title('PR diário')
#Filtro Temporal
data_selecionada = st.date_input('Selecione o intervalo temporal',value=(df['Tempo'].min(), df['Tempo'].max()))
if len(data_selecionada) == 2:
    ini, fim = (data_selecionada[0], data_selecionada[1])
    df_filtrado = df_diario[(df_diario['Data'] >= ini) & (df_diario['Data'] <= fim)]
else:
    data_unica = pd.to_datetime(data_selecionada[0]).date()  # Converte para datetime.date se necessário
    mask = df['Data'] == data_unica  # Compare as datas
    df_filtrado = df_diario[mask]

fig1 = px.bar(df_filtrado,x='Data',y='PR diário')

fig1.update_layout(
    shapes=[
        dict(
            type="line",
            x0=df_filtrado['Data'].min(),x1=df_filtrado['Data'].max(),  # Fim do eixo x
            y0=1,y1=1,  # Posição no eixo y
            line=dict(color="black",width=2,dash="dash"),
            )
        ]
    )
fig1.update_traces(marker=dict(color='#009F98'))
st.plotly_chart(fig1)
df_mensal['Ano_mes'] = df_mensal['Ano_mes'].astype(str)  # Converte para string
fig2 = px.bar(df_mensal,x='Ano_mes',y='PR mensal')
fig2.update_traces(marker=dict(color='#009F98'))
st.plotly_chart(fig2)