import pandas as pd


def get_uva_df(cer_df):
    df = cer_df.copy(deep=True)
    df.rename(columns={'cer': 'uva'}, inplace=True)
    df['uva'] = 14.05*(df['uva']/5.5636)
    return df


def resample_df(cer_df):
    cer_df = cer_df.resample(rule='D').ffill()
    return cer_df


def get_day_diff(df):
    df_diff_day = df.diff(1)
    return df_diff_day


def get_month_diff(df):
    return df.resample('M').last().diff(1)
