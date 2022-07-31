import pathlib

import streamlit as st

import const
import pandas as pd
import datetime as dt
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
        option_delta_years = st.selectbox('Años hacia atrás', range(1, 10), index=const.YEARS_BEHIND-1)
        option_days_ahead = st.select_slider('Días hacia adelante', options=range(1, 366), value=const.DAYS_AHEAD)
        option_origin = st.selectbox('Origen de los datos', ('auto', 'ingest', 'local'))

    return option_uva_cer, option_delta_years, option_days_ahead, option_origin


def ingest(option_delta_years):
    cer_df_ = cached_get_cer_df(delta_years=option_delta_years)
    cer_df_ = cer_df_.copy(deep=True)
    cer_df = cached_resample_df(cer_df=cer_df_)
    cer_df.to_pickle('cer_df.pickle')
    return cer_df


def common_data(option_delta_years, option_days_ahead, origin):
    print('***')
    if origin == 'ingest':
        print(f'>> ingesting because user required')
        cer_df = ingest(option_delta_years)
    elif origin == 'local':
        print('>> reading local because user required')
        cer_df = pd.read_pickle('cer_df.pickle')
    elif origin == 'auto':
        try:
            local_date = dt.datetime.fromtimestamp(pathlib.Path('cer_df.pickle').stat().st_mtime)
            print(local_date.date(), dt.datetime.today().date())
            if local_date.date() == dt.datetime.today().date():
                print('>> reading local')
                cer_df = pd.read_pickle('cer_df.pickle')
                if cer_df.index[-1].year - cer_df.index[0].year != option_delta_years:
                    print(f'>> ingesting because delta_years_local = {cer_df.index[-1].year - cer_df.index[0].year}, '
                          f'and option_delta_years = {option_delta_years}')
                    cer_df = ingest(option_delta_years)
            else:
                print('>> ingesting because file is old')
                cer_df = ingest(option_delta_years)
        except FileNotFoundError:
            print('>> ingesting because file was not found')
            cer_df = ingest(option_delta_years)
    else:
        raise ValueError('origin must be ingest, local, or auto')

    today = cer_df.index[-1]
    uva_df = get_uva_df(cer_df)
    cer_df_fc = forecast_cer_prophet(df_actual=cer_df, days_ahead=option_days_ahead)
    uva_df_fc = get_uva_df(cer_df_fc)
    return cer_df, uva_df, cer_df_fc, uva_df_fc, today
