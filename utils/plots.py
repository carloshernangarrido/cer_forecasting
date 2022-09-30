import plotly.graph_objects as go


def df2plot(df, dffc):
    df_plot = df.copy()
    dffc_plot = dffc.copy()
    if 'cer' in df_plot.columns:
        df_plot.rename(columns={'cer': 'y'}, inplace=True)
    elif 'uva' in df.columns:
        df_plot.rename(columns={'uva': 'y'}, inplace=True)
    elif 'venta' in df.columns:
        df_plot.rename(columns={'venta': 'y'}, inplace=True)
    else:
        raise ValueError
    if 'cer' in dffc_plot.columns:
        dffc_plot.rename(columns={'cer': 'yhat',
                                  'cer_upper': 'yhat_upper',
                                  'cer_lower': 'yhat_lower'}, inplace=True)
    elif 'uva' in dffc_plot.columns:
        dffc_plot.rename(columns={'uva': 'yhat',
                                  'uva_upper': 'yhat_upper',
                                  'uva_lower': 'yhat_lower'}, inplace=True)
    elif 'venta' in dffc_plot.columns:
        dffc_plot.rename(columns={'venta': 'yhat',
                                  'venta_upper': 'yhat_upper',
                                  'venta_lower': 'yhat_lower'}, inplace=True)
    else:
        raise ValueError
    return df_plot, dffc_plot


def plot_df_fc(df_plot, dffc_plot):
    fig = go.Figure()
    fig.update_layout(legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
    fig.add_scatter(x=dffc_plot.index,
                    y=dffc_plot.yhat_lower,
                    name='pronosticado menor', line={'color': 'pink'})
    fig.add_scatter(x=dffc_plot.index,
                    y=dffc_plot.yhat_upper,
                    name='pronosticado mayor', line={'color': 'lightgreen'})
    fig.add_scatter(x=df_plot.index,
                    y=df_plot.y,
                    name='actual', line={'color': 'blue'})
    fig.add_scatter(x=dffc_plot.index,
                    y=dffc_plot.yhat,
                    name='pronosticado', line={'color': 'red'})
    fig.update_layout(legend=dict(
        yanchor="bottom",
        y=0.01,
        xanchor="left",
        x=0.01
    ))
    return fig


def plot_comp(uva_df_plot, uva_df_fc_plot, today, dolar_blue_df_plot, dolar_blue_df_fc_plot):
    fig = go.Figure()
    fig.update_layout(legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))

    fig.add_scatter(x=uva_df_fc_plot.index,
                    y=uva_df_fc_plot.yhat_lower / uva_df_fc_plot.yhat[today],
                    name='uva incertidumbre', line={'color': 'pink'})
    fig.add_scatter(x=uva_df_fc_plot.index,
                    y=uva_df_fc_plot.yhat_upper / uva_df_fc_plot.yhat[today],
                    name='uva pronosticado mayor', line={'color': 'pink'}, showlegend=False)
    fig.add_scatter(x=uva_df_plot.index,
                    y=uva_df_plot.y / uva_df_fc_plot.yhat[today],
                    name='uva actual', line={'color': 'red'})
    fig.add_scatter(x=uva_df_fc_plot.index,
                    y=uva_df_fc_plot.yhat / uva_df_fc_plot.yhat[today],
                    name='uva pronosticado', line={'color': 'orange'})

    fig.add_scatter(x=dolar_blue_df_fc_plot.index,
                    y=dolar_blue_df_fc_plot.yhat_lower / dolar_blue_df_fc_plot.yhat[today],
                    name='dólar blue incertidumbre', line={'color': 'GreenYellow'})
    fig.add_scatter(x=dolar_blue_df_fc_plot.index,
                    y=dolar_blue_df_fc_plot.yhat_upper / dolar_blue_df_fc_plot.yhat[today],
                    name='dólar blue pronosticado mayor', line={'color': 'GreenYellow'}, showlegend=False)
    fig.add_scatter(x=dolar_blue_df_plot.index,
                    y=dolar_blue_df_plot.y / dolar_blue_df_fc_plot.yhat[today],
                    name='dólar blue actual', line={'color': 'green'})
    fig.add_scatter(x=dolar_blue_df_fc_plot.index,
                    y=dolar_blue_df_fc_plot.yhat / dolar_blue_df_fc_plot.yhat[today],
                    name='dólar blue pronosticado', line={'color': 'LightGreen'})
    #
    # fig.update_layout(legend=dict(
    #     yanchor="bottom",
    #     y=0.01,
    #     xanchor="left",
    #     x=0.01
    # ))
    return fig
