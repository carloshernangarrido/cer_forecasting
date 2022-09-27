import datetime
import pandas as pd
import pytz


def get_uva_df(cer_df):
    def cer2uva(cer):
        return 14.05 * (cer / 5.5636)

    df = cer_df.copy(deep=True)
    df.rename(columns={'cer': 'uva'}, inplace=True)
    df['uva'] = cer2uva(df['uva'])
    if 'cer_lower' in df.columns:
        df.rename(columns={'cer_lower': 'uva_lower'}, inplace=True)
        df['uva_lower'] = cer2uva(df['uva_lower'])
    if 'cer_upper' in df.columns:
        df.rename(columns={'cer_upper': 'uva_upper'}, inplace=True)
        df['uva_upper'] = cer2uva(df['uva_upper'])
    return df


def resample_df(df: pd.DataFrame):
    df = df.sort_index(ascending=True)
    now = datetime.datetime.today()
    today = pytz.timezone('America/Argentina/Mendoza').\
        localize(pytz.datetime.datetime(year=now.year, month=now.month, day=now.day))
    print(today)
    try:
        _ = df.loc[today]
    except KeyError:
        df.loc[today] = df.iloc[-1]
    df = df.groupby(df.index).mean()
    df = df.drop_duplicates(keep='last').resample(rule='D').ffill()
    return df


def get_day_diff(df):
    df_diff_day = df.diff(1)
    return df_diff_day


def get_month_diff(df):
    return df.resample('M').last().diff(1)
