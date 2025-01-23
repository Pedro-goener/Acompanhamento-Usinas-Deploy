import plotly.express as px
import pandas as pd
import numpy as np
import streamlit as st
def plot_time_series(df):
    # Cálculo das energias real e prevista
    energia_real = float(np.trapezoid(df['Potencia Ativa(kW)'], df['Tempo'])) / (3.6 * 1e12)
    energia_prevista = float(np.trapezoid(df['Potencia Ativa(kW) prevista'], df['Tempo'])) / (
            3.6 * 1e12)

    st.markdown(f"<h3>Energia real: {energia_real:.2f} kWh</h3>", unsafe_allow_html=True)
    st.markdown(f"<h3>Energia prevista: {energia_prevista:.2f} kWh</h3>", unsafe_allow_html=True)

    # Gráfico da série temporal
    df = df.sort_values(by='Tempo')
    fig_temporal = px.line(df, x='Tempo', y=['Potencia Ativa(kW) prevista', 'Potencia Ativa(kW)'])
    fig_temporal.update_layout(
        yaxis_title='Potência Ativa (kW)',
    )
    fig_temporal.update_traces(
        line=dict(color='#808000'),
        selector=dict(name='Potencia Ativa(kW)')
    )
    fig_temporal.update_traces(
        line=dict(color='#009F98', dash='dash'),
        selector=dict(name='Potencia Ativa(kW) prevista')
    )
    st.plotly_chart(fig_temporal)