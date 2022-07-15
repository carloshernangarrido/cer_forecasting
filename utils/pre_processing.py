import pandas as pd


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


def resample_df(cer_df):
    cer_df = cer_df.drop_duplicates(keep='first').resample(rule='D').ffill()
    return cer_df


def get_day_diff(df):
    df_diff_day = df.diff(1)
    return df_diff_day


def get_month_diff(df):
    return df.resample('M').last().diff(1)
