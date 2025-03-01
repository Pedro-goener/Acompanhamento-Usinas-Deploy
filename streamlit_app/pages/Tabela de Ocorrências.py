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
st.markdown(f"<h6>Perda total: No mínimo 1 hora com Potencia Ativa nula durante o dia ou PR<0.1 </h6>", unsafe_allow_html=True)
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

#Exibir tabela de inversores da usina selecionada
if usina_response['selected_rows'] is not None:
    usina = usina_response['selected_rows']['Usina'].iloc[0]
    #Exibição tabela de inversores
    inv_df = load_and_prepare_data(db_config, f"SELECT * FROM tabela_inversores WHERE \"Usina\" = '{usina}'")
    gb = GridOptionsBuilder.from_dataframe(inv_df)
    gb.configure_selection('single')
    grid_options = gb.build()
    # Exibindo o dataframe interativo
    inv_response = AgGrid(
        inv_df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        theme='streamlit',
        height=200,
        width='100%',
    )


    # Encapsulando conteudo dinamico
    def load_dynamic_content():
        inversor = inv_response['selected_rows']['Inversor'].iloc[0]
        check = st.checkbox('Exibir histórico?', key='history_checkbox')
        if check:
            query = f'SELECT * FROM tabela_ocorrencias WHERE "Inversor" = {inversor} AND "Usina_id"::INTEGER = {usinas_dict[usina]}'
        else:
            query = f'SELECT * FROM tabela_ocorrencias WHERE "Inversor" = {inversor} AND "Usina_id"::INTEGER = {usinas_dict[usina]} AND "Verificado" = FALSE'

        df = load_and_prepare_data(db_config, query)
        df['Inicio'] = pd.to_datetime(df['Inicio'])
        df['Fim'] = pd.to_datetime(df['Fim'])

        status = df['Status'].unique()
        status_selecionados = st.multiselect('Selecione o tipo de ocorrência', status, default=df['Status'].unique(),
                                             key='status_multiselect')
        df_filtrado = df[df['Status'].isin(status_selecionados)]

        data_selecionada = st.date_input('Selecione o intervalo temporal',
                                         value=(df['Inicio'].min(), df['Inicio'].max()),
                                         key='date_input')

        if isinstance(data_selecionada, tuple) and len(data_selecionada) == 2:
            ini, fim = map(pd.to_datetime, data_selecionada)
            df_filtrado = df_filtrado[(df_filtrado['Inicio'] >= ini) & (df_filtrado['Inicio'] <= fim)]
        else:
            data_unica = pd.to_datetime(data_selecionada[0])
            mask = df_filtrado['Inicio'].dt.date == data_unica.date()
            df_filtrado = df_filtrado[mask]

        columns_to_hide = ['Inversor', 'Usina_id', 'index']
        edited_df = df_filtrado.drop(columns=columns_to_hide)
        disabled_columns = [col for col in edited_df.columns if col != "Verificado"]

        edited_df = st.data_editor(
            edited_df,
            column_config={"Verificado": st.column_config.CheckboxColumn("Verificado")},
            disabled=disabled_columns,
            use_container_width=True,
            key='data_editor'
        )

        st.session_state.edited_df = pd.concat([edited_df, df_filtrado[columns_to_hide]], axis=1)

        observacao = st.text_input('Observação da ocorrência',
                                   max_chars=300,
                                   placeholder='Digite aqui...',
                                   key='observacao_input')

        if st.button('Enviar atualização', key='submit_button'):
            if edited_df is not None:
                novo_df = pd.concat([edited_df, df_filtrado[columns_to_hide]], axis=1)
                id_update = novo_df.loc[novo_df['Verificado'] != df_filtrado['Verificado'], 'index'].iloc[0]
                update_data(db_config, id_update, observacao)
                st.success('Atualização enviada com sucesso!')
                st.session_state.needs_rerun = True
                st.rerun()

        selected_row_index = st.selectbox(
            "Linha selecionada (índice):",
            options=[None] + list(edited_df.index),
            key="row_selector"
        )

        if selected_row_index is not None:
            df_p = load_and_prepare_data(db_config,
                                         f'SELECT * FROM performance_data WHERE "Inversor" = {inversor} AND "Usina_id"::INTEGER = {usinas_dict[usina]}')
            ini = pd.to_datetime(edited_df.loc[selected_row_index, 'Inicio']).date()
            fim = pd.to_datetime(edited_df.loc[selected_row_index, 'Fim']).date()
            df_p['Tempo'] = pd.to_datetime(df_p['Tempo'])
            if ini < fim:
                df_p_filtrado = df_p[(df_p['Tempo'].dt.date >= ini) & (df_p['Tempo'].dt.date <= fim)]
            elif ini == fim:
                mask = df_p['Tempo'].dt.date == ini
                df_p_filtrado = df_p[mask]

            plot_time_series(df_p_filtrado)


    # Executar o conteúdo dinâmico
    if inv_response['selected_rows'] is not None:
        load_dynamic_content()
