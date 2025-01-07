import pandas as pd

def adicionar_status_perda(df):
    # Ajuste das configurações do pandas para exibir todas as colunas
    pd.set_option('display.max_columns', None)

    # Remover colunas irrelevantes
    df_rf = df.drop(columns=['lag_1', 'lag_2', 'Potencia Ativa Prevista (kNN)',
                             'velocidade do vento', 'humidade',
                             'irradiancia inclinada', 'temperatura ambiente'])

    # Garantir que a coluna 'Tempo' seja convertida para datetime e configurada como índice
    df_rf['Tempo'] = pd.to_datetime(df_rf['Tempo'])
    df_rf.set_index('Tempo', inplace=True)

    # Calcular a razão PR (Potencia Ativa Prevista / Potencia Ativa Real)
    df_rf['PR'] = df_rf['Potencia Ativa Prevista (Random Forest)'] / df_rf['Potencia Ativa(kW)']

    # Função para verificar o status da potência
    def check_power_status(tempo):
        mask = df_rf.index.floor('10min') == tempo
        sub_df = df_rf[mask]

        # Verificar perda total
        if (sub_df['PR'] <= 0.1).any() or (sub_df['Potencia Ativa Prevista (Random Forest)'] <= 0.1).any():
            return pd.Series('Perda Total', index=sub_df.index)

        # Verificar perda instantânea (1 hora = 6 períodos de 10min)
        hora_atual = tempo
        mask_1h = (df_rf.index.floor('10min') >= hora_atual - pd.Timedelta(hours=1)) & (
                df_rf.index.floor('10min') <= hora_atual)
        dados_1h = df_rf[mask_1h]

        if ((dados_1h['PR'] > 0.1) & (dados_1h['PR'] < 0.95)).all() and len(dados_1h) >= 6:
            return pd.Series('Perda Instantanea', index=sub_df.index)

        # Verificar perda dissolvida
        dia_atual = tempo.floor('D')
        dados_dia = df_rf[df_rf.index.floor('D') == dia_atual]

        if (dados_dia['PR'] < 0.95).mean() > 0.5:  # Mais da metade dos PRs abaixo de 0.95
            if (sub_df['PR'] < 0.95).any() and (sub_df['Potencia Ativa Prevista (Random Forest)'] > 100).any():
                return pd.Series('Perda Dissolvida', index=sub_df.index)

        return pd.Series('Normal', index=sub_df.index)

    # Aplicar a função check_power_status a cada valor único de tempo (de 10min)
    windows = df_rf.index.floor('10min').unique()
    df_rf['Status'] = pd.concat([check_power_status(tempo) for tempo in windows])

    return df_rf

