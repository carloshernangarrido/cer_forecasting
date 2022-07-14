import streamlit as st
from utils.data_ingestion import get_cer_df
from utils.forecasting import forecast_cer_prophet
from utils.pre_processing import get_uva_df, resample_df, get_day_diff, get_month_diff
from pytz import datetime as dt
import plotly.express as px
import plotly.graph_objects as go


@st.cache
def cached_get_cer_df(**kwargs):
    return get_cer_df(url=kwargs['url'] if 'url' in kwargs.keys() else None,
                      delta_years=kwargs['delta_years'])


@st.cache
def cached_resample_df(**kwargs):
    return resample_df(cer_df=kwargs['cer_df'])


if __name__ == '__main__':
    st.set_page_config(page_title='PronostiCER', layout='wide',
                       initial_sidebar_state='auto')
    st.title("Visualizador y pronosticador de CER y UVA")
    with st.sidebar:
        st.header("Parámetros")
        option_uva_cer = st.selectbox('¿CER o UVA?', ('CER', 'UVA'))
        option_delta_years = st.selectbox('Años hacia atrás', range(10), index=3)
        option_days_ahead = st.select_slider('días adelante', options=range(365), value=10)
    cer_df = cached_get_cer_df(delta_years=option_delta_years)
    cer_df = cached_resample_df(cer_df=cer_df)
    cer_df = cer_df.copy(deep=True)
    uva_df = get_uva_df(cer_df)

    cer_df_fc = forecast_cer_prophet(cer_df, days_ahead=option_days_ahead)
    uva_df_fc = get_uva_df(cer_df_fc)

    # st.header("Datos actuales")
    # st.subheader(option_uva_cer)
    # with st.expander(label="Gráfico"):
    #     st.header('Valores')
    #     fig_val = px.scatter(cer_df if option_uva_cer == 'CER' else uva_df,
    #                          x=cer_df.index, y=option_uva_cer.lower())
    #     st.plotly_chart(fig_val, use_container_width=True)
    #
    #     st.header('Variación diaria')
    #     fig_day = px.scatter(get_day_diff(cer_df) if option_uva_cer == 'CER' else get_day_diff(uva_df),
    #                          x=get_day_diff(cer_df).index, y=option_uva_cer.lower())
    #     st.plotly_chart(fig_day, use_container_width=True)
    #
    #     st.header('Variación mensual')
    #     fig_month = px.scatter(get_month_diff(cer_df) if option_uva_cer == 'CER' else get_month_diff(uva_df),
    #                            x=get_month_diff(cer_df).index, y=option_uva_cer.lower())
    #     st.plotly_chart(fig_month, use_container_width=True)
    # with st.expander(label="Tabla"):
    #     st.header('Tabla')
    #     df_table = cer_df.copy(deep=True) if option_uva_cer == 'CER' else uva_df.copy(deep=True)
    #     df_table.index = df_table.index.map(dt.datetime.date)
    #     st.dataframe(df_table)

    st.header("Datos pronosticados")
    st.subheader(option_uva_cer)
    with st.expander(label="Gráfico", expanded=True):
        st.header('Valores')
        fig_val_fc = go.Figure()
        fig_val_fc.update_layout(legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))

        fig_val_fc.add_scatter(x=cer_df.index if option_uva_cer == 'CER' else uva_df.index,
                               y=cer_df.cer if option_uva_cer == 'CER' else uva_df.uva,
                               name='actual')
        fig_val_fc.add_scatter(x=cer_df_fc.index if option_uva_cer == 'CER' else uva_df_fc.index,
                               y=cer_df_fc.cer if option_uva_cer == 'CER' else uva_df_fc.uva,
                               name='pronosticado')
        fig_val_fc.add_scatter(x=cer_df_fc.index if option_uva_cer == 'CER' else uva_df_fc.index,
                               y=cer_df_fc.cer_lower if option_uva_cer == 'CER' else uva_df_fc.uva_lower,
                               name='pronosticado menor', line={'color': 'green', 'dash': 'dot'})
        fig_val_fc.add_scatter(x=cer_df_fc.index if option_uva_cer == 'CER' else uva_df_fc.index,
                               y=cer_df_fc.cer_upper if option_uva_cer == 'CER' else uva_df_fc.uva_upper,
                               name='pronosticado mayor', line={'color': 'green', 'dash': 'dot'})
        st.plotly_chart(fig_val_fc, use_container_width=True)

        st.header('Variación diaria')
        df_plot = get_day_diff(cer_df) if option_uva_cer == 'CER' else get_day_diff(uva_df)
        if 'cer' in df_plot.columns:
            df_plot.rename(columns={'cer': 'y'}, inplace=True)
        elif 'uva' in df_plot.columns:
            df_plot.rename(columns={'uva': 'y'}, inplace=True)
        else:
            raise ValueError
        df_fc_plot = get_day_diff(cer_df_fc) if option_uva_cer == 'CER' else get_day_diff(uva_df_fc)
        if 'cer' in df_fc_plot.columns:
            df_fc_plot.rename(columns={'cer': 'yhat',
                                       'cer_upper': 'yhat_upper',
                                       'cer_lower': 'yhat_lower'}, inplace=True)
        elif 'uva' in df_fc_plot.columns:
            df_fc_plot.rename(columns={'uva': 'yhat',
                                       'uva_upper': 'yhat_upper',
                                       'uva_lower': 'yhat_lower'}, inplace=True)
        else:
            raise ValueError
        fig_day = go.Figure()
        fig_day.update_layout(legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
        fig_day.add_scatter(x=df_plot.index,
                            y=df_plot.y,
                            name='actual')
        fig_day.add_scatter(x=df_fc_plot.index,
                            y=df_fc_plot.yhat,
                            name='pronosticado')
        fig_day.add_scatter(x=df_fc_plot.index,
                            y=df_fc_plot.yhat_lower,
                            name='pronosticado menor', line={'color': 'green'})
        fig_day.add_scatter(x=df_fc_plot.index,
                            y=df_fc_plot.yhat_upper,
                            name='pronosticado mayor', line={'color': 'green'})
        st.plotly_chart(fig_day, use_container_width=True)
        # fig_day = px.scatter(get_day_diff(cer_df_fc) if option_uva_cer == 'CER' else get_day_diff(uva_df_fc),
        #                      x=get_day_diff(cer_df_fc).index, y=option_uva_cer.lower())
        # st.plotly_chart(fig_day, use_container_width=True)
        #
        # st.header('Variación mensual')
        # fig_month = px.scatter(get_month_diff(cer_df_fc) if option_uva_cer == 'CER' else get_month_diff(uva_df_fc),
        #                        x=get_month_diff(cer_df_fc).index, y=option_uva_cer.lower())
        # st.plotly_chart(fig_month, use_container_width=True)
