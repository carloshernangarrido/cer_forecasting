from prophet import Prophet
import pandas as pd


def forecast_cer_prophet(df_actual: pd.DataFrame, days_ahead: int = 1):
    """
Uses prophet to forecast df a number of days ahead.
    :param df_actual: data frame containing actual data
    :param days_ahead: Number of days to forecast.
    :return: data frame containing actual and forecasted data
    """
    df = df_actual.copy(deep=True)
    df.insert(0, column='ds', value=df.index.map(lambda x: x.replace(tzinfo=None)))
    df.insert(0, column='y', value=df.cer)
    m = Prophet(changepoint_range=.95)
    m.fit(df)
    df_future = m.predict(m.make_future_dataframe(periods=days_ahead))
    cer_df_fc = pd.DataFrame(data=None, columns=df_actual.columns,
                             index=df_future['ds'].map(lambda x: x.replace(tzinfo=df_actual.index[0].tzinfo)))
    cer_df_fc.index.freq, cer_df_fc.index.name = 'D', 'date'
    cer_df_fc['cer'] = df_future['yhat'].values
    cer_df_fc.insert(1, column='cer_lower', value=df_future['yhat_lower'].values)
    cer_df_fc.insert(2, column='cer_upper', value=df_future['yhat_upper'].values)
    return cer_df_fc
