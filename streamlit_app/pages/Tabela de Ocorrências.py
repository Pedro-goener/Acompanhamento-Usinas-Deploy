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
from interacao_db import load_and_prepare_data,db_config,usinas_dict
from plotagem import plot_time_series
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
#Explicação perdas
st.markdown(f"<h6>Perda total: No mínimo 10 minutos com Potencia Ativa nula durante o dia ou PR<0.1 </h6>", unsafe_allow_html=True)
st.markdown(f"<h6>Perda dissipada: 3 dias seguidos com PR < 0.95 </h6>", unsafe_allow_html=True)
st.markdown(f"<h6>Dados faltantes: No mínimo 1 dia sem dados </h6>", unsafe_allow_html=True)
#Tabela inicial de usinas
st.markdown(f"<h3>Selecione a Usina </h3>", unsafe_allow_html=True)
usina_df = load_and_prepare_data(db_config,'SELECT * FROM tabela_usinas')
#Exibição dataframe interativo
gb = GridOptionsBuilder.from_dataframe(usina_df)
gb.configure_selection('single')
grid_options = gb.build()
# Exibindo o dataframe interativo
usina_response = AgGrid(
    usina_df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    theme='streamlit',
    height=200,
    width='100%',
)
#Exibir tabela da usina selecionada
if usina_response['selected_rows'] is not None:
    usina = usina_response['selected_rows']['Usina'][0]
    inversor = st.selectbox('Selecione o inversor',[1,2,3,4,5,6,7,8,9,10])
    #Leitura do Arquivo e conversão para datetime
    query = f'SELECT * FROM tabela_ocorrencias WHERE "Inversor" = {inversor} AND "Usina_id"::INTEGER = {usinas_dict[usina]}'
    df = load_and_prepare_data(db_config,query)
    df['Inicio'] = pd.to_datetime(df['Inicio'])
    df['Fim'] = pd.to_datetime(df['Fim'])
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
    #Criação dataframe interativo
    gb = GridOptionsBuilder.from_dataframe(df_filtrado)
    gb.configure_selection('single')
    grid_options = gb.build()

    response = AgGrid(
        df_filtrado,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        theme='streamlit',
        height=300,
        width='100%',
    )

    #Caso selecione uma linha, exibir série temporal
    if not response['selected_rows'] is None:
        df_p = load_and_prepare_data(db_config,f'SELECT * FROM performance_data WHERE "Inversor" = {inversor} AND "Usina_id"::INTEGER = {usinas_dict[usina]}')
        ini = pd.to_datetime(response['selected_rows']['Inicio']).dt.date[0]
        fim = pd.to_datetime(response['selected_rows']['Fim']).dt.date[0]
        if ini < fim:
            df_p_filtrado = df_p[(df_p['Tempo'].dt.date >= ini) & (df_p['Tempo'].dt.date <= fim)]
        elif ini == fim:
            mask = df_p['Tempo'].dt.date == ini
            df_p_filtrado = df_p[mask]

        plot_time_series(df_p_filtrado)
