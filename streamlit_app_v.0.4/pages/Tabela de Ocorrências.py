import pandas as pd
import streamlit as st
from PIL import Image
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import plotly.express as px
import numpy as np
import os
import sys
# Adicione o diretório 'utils' ao caminho de importação
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../Utils')))
from interacao_db import load_and_prepare_data,db_config
#Encontra diretório atual principal
current_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
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
df = load_and_prepare_data(db_config,'SELECT * FROM "Tabela_ocorrencias"')
df['Inicio'] = pd.to_datetime(df['Inicio'])
df['Fim'] = pd.to_datetime(df['Fim'])
#Filtros
#Filtro de status
status = df['Status'].unique()
status_selecionados = st.multiselect('Selecione o tipo de ocorrência',status,default=df['Status'].unique())
df_filtrado  = df[df['Status'].isin(status_selecionados)]
#Filtro Temporal
data_selecionada = st.date_input('Selecione o intervalo temporal',value=(df['Inicio'].min(), df['Inicio'].max()))
if isinstance(data_selecionada,tuple) and len(data_selecionada) == 2:
    # Converter as datas selecionadas para datetime para realizar a comparação
    ini, fim = map(pd.to_datetime, data_selecionada)
    # Filtrar o DataFrame pelo intervalo de datas
    df_filtrado = df_filtrado[(df_filtrado['Inicio'] >= ini) & (df_filtrado['Inicio'] <= fim)]

else:
    data_unica = pd.to_datetime(data_selecionada[0])  # Pegue apenas a primeira data
    mask = df_filtrado['Inicio'].dt.date == data_unica.date()  # Compare as datas
    df_filtrado = df_filtrado[mask]

gb = GridOptionsBuilder.from_dataframe(df_filtrado)
gb.configure_selection('single', use_checkbox=True)  # Permite seleção única
grid_options = gb.build()

# Exibindo o dataframe interativo
response = AgGrid(
    df_filtrado,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    theme='streamlit',  # Tema
    height=300,
    width='100%',
)
#Caso selecione uma linha, exibir série temporal
if not response['selected_rows'] is None:
    df_p = load_and_prepare_data(db_config,'SELECT * FROM "Performance_data"')
    ini = pd.to_datetime(response['selected_rows']['Inicio']).dt.date[0]
    fim = pd.to_datetime(response['selected_rows']['Fim']).dt.date[0]
    if ini < fim:
        df_p_filtrado = df_p[(df_p['Tempo'].dt.date >= ini) & (df_p['Tempo'].dt.date <= fim)]
    elif ini == fim:
        mask = df_p['Tempo'].dt.date == ini
        df_p_filtrado = df_p[mask]

    # Cálculo das energias real e prevista
    energia_real = float(np.trapezoid(df_p_filtrado['Potencia Ativa(kW)'], df_p_filtrado['Tempo'])) / (3.6 * 1e12)
    energia_prevista = float(np.trapezoid(df_p_filtrado['Potencia Ativa(kW) prevista'], df_p_filtrado['Tempo'])) / (
                3.6 * 1e12)
    st.markdown(f"<h3>Energia real: {energia_real:.2f} kWh</h3>", unsafe_allow_html=True)
    st.markdown(f"<h3>Energia prevista: {energia_prevista:.2f} kWh</h3>", unsafe_allow_html=True)
    # Exiibição do gráfico
    fig = px.line(df_p_filtrado, x='Tempo', y=['Potencia Ativa(kW) prevista', 'Potencia Ativa(kW)'])
    # Atualizando o layout para adicionar um nome ao eixo Y
    fig.update_layout(
        yaxis_title='Potência Ativa (kW)',  # Nomeando o eixo Y
    )
    # Atualizando a cor da linha e tornando-a tracejada para a linha 'Potencia Ativa(kW)'
    fig.update_traces(
        line=dict(color='#808000'),  # Verde escuro
        selector=dict(name='Potencia Ativa(kW)')
    )
    fig.update_traces(
        line=dict(color='#009F98', dash='dash'),  # Azul claro
        selector=dict(name='Potencia Ativa(kW) prevista')
    )
    st.plotly_chart(fig)
