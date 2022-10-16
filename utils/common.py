import pathlib
import streamlit as st
import const
import pandas as pd
import datetime as dt
from utils.data_ingestion import get_cer_df, get_dolar_blue_df
from utils.forecasting import forecast_cer_prophet, forecast_dolar_blue_prophet
from utils.pre_processing import get_uva_df, resample_df


def common_dash():
    st.markdown(""" <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style> """, unsafe_allow_html=True)
    st.markdown(""" <style>
    footer {visibility: hidden;}
    </style> """, unsafe_allow_html=True)

    st.title("Visualizador y pronosticador de CER, UVA y Dólar Blue")

    with st.sidebar:
        st.header("Parámetros")
        option_uva_cer = st.selectbox('¿CER o UVA?', ('CER', 'UVA'))
        option_delta_years = st.selectbox('Años hacia atrás', range(1, 10), index=const.YEARS_BEHIND - 1)
        option_days_ahead = st.select_slider('Días hacia adelante', options=range(1, 366), value=const.DAYS_AHEAD)
        option_origin = st.selectbox('Origen de los datos', ('auto', 'ingest', 'local'))
        option_holidays = st.selectbox('¿incluir feriados?', ('SI', 'NO'))
        holidays_flag = True if option_holidays == 'SI' else False

    return option_uva_cer, option_delta_years, option_days_ahead, option_origin, holidays_flag


def ingest_cer(option_delta_years, dump: bool):
    cer_df_ = get_cer_df(delta_years=option_delta_years)
    cer_df_ = cer_df_.copy(deep=True)
    cer_df = resample_df(df=cer_df_)
    if dump:
        cer_df.to_pickle('cer_df.pickle')
    return cer_df


def ingest_dolar_blue(option_delta_years, dump: bool):
    dolar_blue_df_ = get_dolar_blue_df(delta_years=option_delta_years)
    dolar_blue_df_ = dolar_blue_df_.copy(deep=True)
    dolar_blue_df = resample_df(df=dolar_blue_df_)
    if dump:
        dolar_blue_df.to_pickle('dolar_blue_df.pickle')
    return dolar_blue_df


def common_data(option_delta_years, option_days_ahead, origin, forecast=True, dump=True, holidays_flag=True):
    print('\n*** CER / UVA ***')
    if origin == 'ingest':
        print(f'>> ingesting because user required')
        cer_df = ingest_cer(option_delta_years, dump)
        print(f'>> forecasting because user required')
        if forecast:
            cer_df_fc = forecast_cer_prophet(df_actual=cer_df, days_ahead=option_days_ahead,
                                             holidays_flag=holidays_flag)
            uva_df_fc = get_uva_df(cer_df_fc)
        else:
            cer_df_fc = None
            uva_df_fc = None
    elif origin == 'local':
        print('>> reading local because user required')
        try:
            cer_df = pd.read_pickle('cer_df.pickle')
            cer_df_fc = pd.read_pickle('cer_df_fc.pickle')
            uva_df_fc = get_uva_df(cer_df_fc)
        except FileNotFoundError():
            print('>> ingesting because file was not found')
            cer_df = ingest_cer(option_delta_years, dump)
            print('>> forecasting because file was not found')
            if forecast:
                cer_df_fc = forecast_cer_prophet(df_actual=cer_df, days_ahead=option_days_ahead,
                                                 holidays_flag=holidays_flag)
                uva_df_fc = get_uva_df(cer_df_fc)
            else:
                cer_df_fc = None
                uva_df_fc = None
    elif origin == 'auto':
        try:
            local_date = dt.datetime.fromtimestamp(pathlib.Path('cer_df.pickle').stat().st_mtime)
            if local_date.date() == dt.datetime.today().date():
                print('>> reading local')
                cer_df = pd.read_pickle('cer_df.pickle')
                cer_df_fc = pd.read_pickle('cer_df_fc.pickle')
                uva_df_fc = get_uva_df(cer_df_fc)
                if cer_df.index[-1].year - cer_df.index[0].year != option_delta_years:
                    print(f'>> ingesting because delta_years_local = {cer_df.index[-1].year - cer_df.index[0].year}, '
                          f'and option_delta_years = {option_delta_years}')
                    cer_df = ingest_cer(option_delta_years, dump)
                    print(f'>> forecasting because delta_years_local = {cer_df.index[-1].year - cer_df.index[0].year}, '
                          f'and option_delta_years = {option_delta_years}')
                    if forecast:
                        cer_df_fc = forecast_cer_prophet(df_actual=cer_df, days_ahead=option_days_ahead,
                                                         holidays_flag=holidays_flag)
                        uva_df_fc = get_uva_df(cer_df_fc)
                    else:
                        cer_df_fc = None
                        uva_df_fc = None
            else:
                print('>> ingesting because file is old')
                cer_df = ingest_cer(option_delta_years, dump)
                print(f'>> forecasting because because file is old')
                if forecast:
                    cer_df_fc = forecast_cer_prophet(df_actual=cer_df, days_ahead=option_days_ahead,
                                                     holidays_flag=holidays_flag)
                    uva_df_fc = get_uva_df(cer_df_fc)
                else:
                    cer_df_fc = None
                    uva_df_fc = None
        except FileNotFoundError:
            print('>> ingesting because file was not found')
            cer_df = ingest_cer(option_delta_years, dump)
            print(f'>> forecasting because file was not found')
            if forecast:
                cer_df_fc = forecast_cer_prophet(df_actual=cer_df, days_ahead=option_days_ahead,
                                                 holidays_flag=holidays_flag)
                uva_df_fc = get_uva_df(cer_df_fc)
            else:
                cer_df_fc = None
                uva_df_fc = None
    else:
        raise ValueError('origin must be ingest_cer, local, or auto')

    print('\n*** Dólar Blue ***')
    if origin == 'ingest':
        print(f'>> ingesting because user required')
        dolar_blue_df = ingest_dolar_blue(option_delta_years, dump)
        print(f'>> forecasting because user required')
        if forecast or forecast == 'dolar_blue':
            dolar_blue_df_fc = forecast_dolar_blue_prophet(df_actual=dolar_blue_df, days_ahead=option_days_ahead)
        else:
            dolar_blue_df_fc = None
    elif origin == 'local':
        print('>> reading local because user required')
        try:
            dolar_blue_df = pd.read_pickle('dolar_blue_df.pickle')
            dolar_blue_df_fc = pd.read_pickle('dolar_blue_df_fc.pickle')
        except FileNotFoundError():
            print('>> ingesting because file was not found')
            dolar_blue_df = ingest_dolar_blue(option_delta_years, dump)
            print('>> forecasting because file was not found')
            if forecast or forecast == 'dolar_blue':
                dolar_blue_df_fc = forecast_dolar_blue_prophet(df_actual=dolar_blue_df, days_ahead=option_days_ahead)
            else:
                dolar_blue_df_fc = None
    elif origin == 'auto':
        try:
            local_date = dt.datetime.fromtimestamp(pathlib.Path('dolar_blue_df.pickle').stat().st_mtime)
            if local_date.date() == dt.datetime.today().date():
                print('>> reading local')
                dolar_blue_df = pd.read_pickle('dolar_blue_df.pickle')
                dolar_blue_df_fc = pd.read_pickle('dolar_blue_df_fc.pickle')
                if dolar_blue_df.index[-1].year - dolar_blue_df.index[0].year != option_delta_years:
                    print(f'>> ingesting because delta_years_local = '
                          f'{dolar_blue_df.index[-1].year - dolar_blue_df.index[0].year}, '
                          f'and option_delta_years = {option_delta_years}')
                    dolar_blue_df = ingest_dolar_blue(option_delta_years, dump)
                    print(f'>> forecasting because delta_years_local = '
                          f'{dolar_blue_df.index[-1].year - dolar_blue_df.index[0].year}, '
                          f'and option_delta_years = {option_delta_years}')
                    if forecast or forecast == 'dolar_blue':
                        dolar_blue_df_fc = forecast_dolar_blue_prophet(df_actual=dolar_blue_df,
                                                                       days_ahead=option_days_ahead)
                    else:
                        dolar_blue_df_fc = None
            else:
                print('>> ingesting because file is old')
                dolar_blue_df = ingest_dolar_blue(option_delta_years, dump)
                print('>> forecasting because file is old')
                if forecast or forecast == 'dolar_blue':
                    dolar_blue_df_fc = forecast_dolar_blue_prophet(df_actual=dolar_blue_df,
                                                                   days_ahead=option_days_ahead)
                else:
                    dolar_blue_df_fc = None
        except FileNotFoundError:
            print('>> ingesting because file was not found')
            dolar_blue_df = ingest_dolar_blue(option_delta_years, dump)
            print('>> forecasting because file was not found')
            if forecast or forecast == 'dolar_blue':
                dolar_blue_df_fc = forecast_dolar_blue_prophet(df_actual=dolar_blue_df, days_ahead=option_days_ahead)
            else:
                dolar_blue_df_fc = None
    else:
        raise ValueError('origin must be ingest_cer, local, or auto')

    uva_df = get_uva_df(cer_df)
    today_cer, today_dolar_blue = cer_df.index[-1], dolar_blue_df.index[-1]
    if today_cer < today_dolar_blue:
        today = today_cer
    else:
        today = today_dolar_blue
    print(f'{today_cer=}, {today_dolar_blue=}, {today=}')
    return cer_df, uva_df, cer_df_fc, uva_df_fc, today, dolar_blue_df, dolar_blue_df_fc
