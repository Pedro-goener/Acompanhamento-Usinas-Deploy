import streamlit as st
import pandas as pd
def filtro_temporal(df):
    data_selecionada = st.date_input('Selecione o intervalo temporal',value=(df['Tempo'].min(), df['Tempo'].max()))
    if len(data_selecionada) == 2:
        ini, fim = map(pd.to_datetime, data_selecionada)
        df_filtrado = df[(df['Tempo'] >= ini) & (df['Tempo'] <= fim)]
    else:
        data_unica = pd.to_datetime(data_selecionada[0])  # Pegue apenas a primeira data
        mask = df['Tempo'].dt.date == data_unica.date()  # Compare as datas
        df_filtrado = df[mask]

    return df_filtrado