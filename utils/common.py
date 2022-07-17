import streamlit as st
from utils.data_ingestion import get_cer_df
from utils.forecasting import forecast_cer_prophet
from utils.pre_processing import get_uva_df, resample_df


@st.cache
def cached_get_cer_df(**kwargs):
    return get_cer_df(url=kwargs['url'] if 'url' in kwargs.keys() else None,
                      delta_years=kwargs['delta_years'])


@st.cache
def cached_resample_df(**kwargs):
    return resample_df(cer_df=kwargs['cer_df'])


@st.cache
def cached_forecast_cer_prophet(**kwargs):
    return forecast_cer_prophet(df_actual=kwargs['df_actual'], days_ahead=kwargs['days_ahead'])


def common_dash():
    # st.markdown(""" <style>
    # #MainMenu {visibility: hidden;}
    # footer {visibility: hidden;}
    # </style> """, unsafe_allow_html=True)
    st.markdown(""" <style>
    footer {visibility: hidden;}
    </style> """, unsafe_allow_html=True)

    st.title("Visualizador y pronosticador de CER y UVA")

    with st.sidebar:
        st.header("Parámetros")
        option_uva_cer = st.selectbox('¿CER o UVA?', ('CER', 'UVA'))
        option_delta_years = st.selectbox('Años hacia atrás', range(1, 10), index=0)
        option_days_ahead = st.select_slider('Días hacia adelante', options=range(1, 366), value=90)

    return option_uva_cer, option_delta_years, option_days_ahead


def common_data(option_delta_years, option_days_ahead):
    cer_df_ = cached_get_cer_df(delta_years=option_delta_years)
    cer_df_ = cer_df_.copy(deep=True)
    cer_df = resample_df(cer_df=cer_df_)
    uva_df = get_uva_df(cer_df)

    cer_df_fc = forecast_cer_prophet(df_actual=cer_df, days_ahead=option_days_ahead)
    uva_df_fc = get_uva_df(cer_df_fc)
    today = cer_df.index[-1]
    return cer_df, uva_df, cer_df_fc, uva_df_fc, today
