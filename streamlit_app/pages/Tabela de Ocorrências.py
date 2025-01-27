import pandas as pd
import streamlit as st
from PIL import Image
from pygments.lexer import default
from sqlalchemy.orm.sync import update
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import plotly.express as px
import numpy as np
import os
import sys
# Adicione o diretório 'utils' ao caminho de importação
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../Utils')))
from interacao_db import load_and_prepare_data,db_config,usinas_dict,update_data
from plotagem import plot_time_series
from filtros import filtro_temporal
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
    usina = usina_response['selected_rows']['Usina'].iloc[0]
    inversor = st.selectbox('Selecione o inversor',[1,2,3,4,5,6,7,8,9,10])
    #Leitura do Arquivo e conversão para datetime
    check = st.checkbox('Exibir histórico?')
    if check:
        query = f'SELECT * FROM tabela_ocorrencias WHERE "Inversor" = {inversor} AND "Usina_id"::INTEGER = {usinas_dict[usina]}'
    else:
        query = f'SELECT * FROM tabela_ocorrencias WHERE "Inversor" = {inversor} AND "Usina_id"::INTEGER = {usinas_dict[usina]} AND "Verificado" = FALSE'
    df = load_and_prepare_data(db_config,query)
    df['Inicio'] = pd.to_datetime(df['Inicio'])
    df['Fim'] = pd.to_datetime(df['Fim'])
    #Filtro de status
    status = df['Status'].unique()
    status_selecionados = st.multiselect('Selecione o tipo de ocorrência',status,default=df['Status'].unique())
    df_filtrado  = df[df['Status'].isin(status_selecionados)]
    #Filtro Temporal
    data_selecionada = st.date_input('Selecione o intervalo temporal', value=(df['Inicio'].min(), df['Inicio'].max()))
    if isinstance(data_selecionada, tuple) and len(data_selecionada) == 2:
        # Converter as datas selecionadas para datetime para realizar a comparação
        ini, fim = map(pd.to_datetime, data_selecionada)
        # Filtrar o DataFrame pelo intervalo de datas
        df_filtrado = df_filtrado[(df_filtrado['Inicio'] >= ini) & (df_filtrado['Inicio'] <= fim)]

    else:
        data_unica = pd.to_datetime(data_selecionada[0])  # Pegue apenas a primeira data
        mask = df_filtrado['Inicio'].dt.date == data_unica.date()  # Compare as datas
        df_filtrado = df_filtrado[mask]

    # Inicializando o session_state
    if 'df_filtrado' not in st.session_state:
        # Inicializa o DataFrame filtrado apenas na primeira vez
        st.session_state.df_filtrado = df_filtrado

    #Criação dataframe interativo
    gb = GridOptionsBuilder.from_dataframe(df_filtrado)
    gb.configure_selection('single')
    gb.configure_column('Verificado',editable = True)
    gb.configure_column('Usina_id',hide=True)
    gb.configure_column('Inversor',hide=True)
    gb.configure_column('index', hide=True)
    grid_options = gb.build()
    #Exibição da tabela
    response = AgGrid(
        df_filtrado,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        theme='streamlit',
        height=300,
        width='100%',
    )
    #Interação usuário
    observacao = st.text_input('Observação da ocorrência',max_chars=300,placeholder='Digite aqui...',
                               value=st.session_state.get('observacao', ''))
    submit = st.button('Enviar atualização')
    #Atualizar tabela
    if submit:
        if response['data'] is not None:
            novo_df = response['data'].reset_index()
            df_filtrado = df_filtrado.reset_index()
            id_update = novo_df.loc[novo_df['Verificado'] != df_filtrado['Verificado'],'index'].iloc[0]
            update_data(db_config,id_update,observacao)
            st.session_state.observacao = observacao
            st.success('Atualização enviada com sucesso!')

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
