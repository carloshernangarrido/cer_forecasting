from typing import Union
from prophet import Prophet, make_holidays
import pandas as pd


def forecast_cer_prophet(df_actual: pd.DataFrame, days_ahead: int = 1, dump: bool = True,
                         dolar_blue_df_fc: Union[None, pd.DataFrame] = None, holidays_flag: bool = False):
    """
Uses prophet to forecast df a number of days ahead.
    :param dump: flag to decide if dump df into a pickle
    :param df_actual: data frame containing actual data
    :param days_ahead: Number of days to forecast.
    :param dolar_blue_df_fc: pre forecasted dolar blue to be used as an addition regressor. If None, it is not used.
    :return: data frame containing actual and forecasted data
    :param holidays_flag: include or not holidays
    """
    cer_cap = 1000.0
    df = df_actual.copy(deep=True)
    df.insert(0, column='ds', value=df.index.map(lambda x: x.replace(tzinfo=None)))
    df.insert(0, column='y', value=df.cer)
    day15_of_month = [date for date in df['ds'] if date.day == 15]
    df['cap'] = cer_cap
    m = Prophet(changepoints=day15_of_month, growth='logistic')
    if holidays_flag:
        m.add_country_holidays(country_name='Argentina')
    if isinstance(dolar_blue_df_fc, pd.DataFrame):
        df['dolar_blue'] = dolar_blue_df_fc['venta']
        df.dropna(inplace=True)
        m.add_regressor('dolar_blue')
    m.fit(df)
    future = m.make_future_dataframe(periods=days_ahead)
    if isinstance(dolar_blue_df_fc, pd.DataFrame):
        future['dolar_blue'] = dolar_blue_df_fc['venta'].values[0:len(future)]
    future['cap'] = cer_cap
    df_future = m.predict(future)
    cer_df_fc = pd.DataFrame(data=None, columns=df_actual.columns,
                             index=df_future['ds'].map(lambda x: x.replace(tzinfo=df_actual.index[0].tzinfo)))
    cer_df_fc.index.freq, cer_df_fc.index.name = 'D', 'date'
    cer_df_fc['cer'] = df_future['yhat'].values
    cer_df_fc.insert(1, column='cer_lower', value=df_future['yhat_lower'].values)
    cer_df_fc.insert(2, column='cer_upper', value=df_future['yhat_upper'].values)
    if dump:
        cer_df_fc.to_pickle('cer_df_fc.pickle')
    return cer_df_fc


def forecast_dolar_blue_prophet(df_actual: pd.DataFrame, days_ahead: int = 1, dump: bool = True,
                                holidays_flag: bool = False):
    """
Uses prophet to forecast df a number of days ahead.
    :param dump: flag to decide if dump df into a pickle
    :param df_actual: data frame containing actual data
    :param days_ahead: Number of days to forecast.
    :param holidays_flag: include or not holidays
    :return: data frame containing actual and forecasted data
    """
    dolar_blue_cap = 1000.0
    df = df_actual.copy(deep=True)
    df.insert(0, column='ds', value=df.index.map(lambda x: x.replace(tzinfo=None)))
    df.insert(0, column='y', value=df.venta)
    df['cap'] = dolar_blue_cap
    m = Prophet(growth='logistic')
    if holidays_flag:
        m.add_country_holidays(country_name='Argentina')
    m.fit(df)
    future = m.make_future_dataframe(periods=days_ahead)
    future['cap'] = dolar_blue_cap
    df_future = m.predict(future)
    dolar_blue_df_fc = pd.DataFrame(data=None, columns=df_actual.columns,
                                    index=df_future['ds'].map(lambda x: x.replace(tzinfo=df_actual.index[0].tzinfo)))
    dolar_blue_df_fc.index.freq, dolar_blue_df_fc.index.name = 'D', 'date'
    dolar_blue_df_fc['venta'] = df_future['yhat'].values
    dolar_blue_df_fc.insert(1, column='venta_lower', value=df_future['yhat_lower'].values)
    dolar_blue_df_fc.insert(2, column='venta_upper', value=df_future['yhat_upper'].values)
    if dump:
        dolar_blue_df_fc.to_pickle('dolar_blue_df_fc.pickle')
    return dolar_blue_df_fc
