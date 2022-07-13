import streamlit as st
import plotly.express as px
from utils.data_ingestion import get_cer_df
from utils.pre_processing import get_uva_df, resample_df, get_day_diff, get_month_diff
from pytz import datetime as dt


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
        option_uva_cer = st.selectbox(
            '¿CER o UVA?',
            ('CER', 'UVA'))
        option_delta_years = st.selectbox(
            'Años hacia atrás',
            (1, 2, 3, 4, 5, 6, 7, 8, 9, 10))
    cer_df = cached_get_cer_df(delta_years=option_delta_years)
    cer_df = cached_resample_df(cer_df=cer_df)
    cer_df = cer_df.copy(deep=True)

    uva_df = get_uva_df(cer_df)

    st.header("Datos actuales")
    st.subheader(option_uva_cer)
    with st.expander(label="Gráfico"):
        st.header('Valores')
        fig_val = px.scatter(cer_df if option_uva_cer == 'CER' else uva_df,
                             x=cer_df.index, y=option_uva_cer.lower())
        st.plotly_chart(fig_val, use_container_width=True)

        st.header('Variación diaria')
        fig_day = px.scatter(get_day_diff(cer_df) if option_uva_cer == 'CER' else get_day_diff(uva_df),
                             x=get_day_diff(cer_df).index, y=option_uva_cer.lower())
        st.plotly_chart(fig_day, use_container_width=True)

        st.header('Variación mensual')
        fig_month = px.scatter(get_month_diff(cer_df) if option_uva_cer == 'CER' else get_month_diff(uva_df),
                               x=get_month_diff(cer_df).index, y=option_uva_cer.lower())
        st.plotly_chart(fig_month, use_container_width=True)
    with st.expander(label="Tabla"):
        st.header('Tabla')
        df_table = cer_df.copy(deep=True) if option_uva_cer == 'CER' else uva_df.copy(deep=True)
        df_table.index = df_table.index.map(dt.datetime.date)
        st.dataframe(df_table)
