import streamlit as st
import datetime as dt
from utils.common import cached_forecast_cer_prophet, common_dash, common_data
from utils.plots import df2plot, plot_df_fc
from utils.pre_processing import get_uva_df, get_day_diff


if __name__ == '__main__':
    option_uva_cer, option_delta_years, option_days_ahead, option_origin = common_dash()
    cer_df, uva_df, cer_df_fc, uva_df_fc, today = common_data(option_delta_years, option_days_ahead, option_origin)

    date_val = (today - dt.timedelta(days=option_days_ahead))
    cer_df_val = cer_df[:date_val]
    uva_df_val = get_uva_df(cer_df_val)
    cer_df_fc_val = cached_forecast_cer_prophet(df_actual=cer_df_val, days_ahead=option_days_ahead)
    uva_df_fc_val = get_uva_df(cer_df_fc_val)

    st.header(f"Validación de pronóstico de {option_uva_cer}")
    with st.expander(label="Valores", expanded=True):
        st.subheader('Valores')
        df_plot, df_fc_plot = df2plot(cer_df if option_uva_cer == 'CER' else uva_df,
                                      cer_df_fc_val if option_uva_cer == 'CER' else uva_df_fc_val)
        fig_val_val = plot_df_fc(df_plot=df_plot, dffc_plot=df_fc_plot)
        fig_val_val.add_vline(x=date_val)
        fig_val_val.add_annotation(x=date_val, y=df_plot.loc[date_val]['y'], text='hoy - horizonte')
        st.plotly_chart(fig_val_val, use_container_width=True)

    with st.expander(label="Variación diaria", expanded=True):
        st.subheader('Variación diaria')
        df_plot, df_fc_plot = df2plot(get_day_diff(cer_df) if option_uva_cer == 'CER' else get_day_diff(uva_df),
                                      get_day_diff(cer_df_fc_val) if option_uva_cer == 'CER' else get_day_diff(uva_df_fc_val))
        fig_day_val = plot_df_fc(df_plot=df_plot, dffc_plot=df_fc_plot)
        fig_day_val.add_vline(x=date_val)
        fig_day_val.add_vline(x=date_val)
        fig_day_val.add_annotation(x=date_val, y=df_plot.loc[date_val]['y'], text='hoy - horizonte')
        st.plotly_chart(fig_day_val, use_container_width=True)