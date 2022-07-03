import pandas as pd


def get_uva_df(cer_df):
    df = cer_df.copy(deep=True)
    df.rename(columns={'cer': 'uva'}, inplace=True)
    df['uva'] = 14.05*(df['uva']/5.5636)
    return df
