import streamlit as st
import datetime as dt
from utils.common import forecast_dolar_blue_prophet, common_dash, common_data
from utils.plots import df2plot, plot_df_fc
from utils.pre_processing import get_uva_df, get_day_diff

if __name__ == '__main__':
    option_uva_cer, option_delta_years, option_days_ahead, option_origin, holidays_flag = common_dash()
    cer_df, uva_df, cer_df_fc, uva_df_fc, today, dolar_blue_df, dolar_blue_df_fc = \
        common_data(option_delta_years, option_days_ahead, option_origin, forecast=False, dump=False,
                    holidays_flag=holidays_flag)

    date_val = (today - dt.timedelta(days=option_days_ahead))
    dolar_blue_df_val = dolar_blue_df[:date_val]
    dolar_blue_df_fc_val = forecast_dolar_blue_prophet(df_actual=dolar_blue_df_val,
                                                       days_ahead=option_days_ahead, dump=False)

    st.header(f"Validación de pronóstico de dólar blue")
    with st.expander(label="Valores", expanded=True):
        st.subheader('Valores')
        df_plot, df_fc_plot = df2plot(dolar_blue_df, dolar_blue_df_fc_val)
        fig_val_val = plot_df_fc(df_plot=df_plot, dffc_plot=df_fc_plot)
        fig_val_val.add_vline(x=date_val)
        fig_val_val.add_annotation(x=date_val, y=df_plot.loc[date_val]['y'], text='hoy - horizonte')
        st.plotly_chart(fig_val_val, use_container_width=True)

    with st.expander(label="Variación diaria", expanded=False):
        st.subheader('Variación diaria')
        df_plot, df_fc_plot = df2plot(get_day_diff(dolar_blue_df), get_day_diff(dolar_blue_df_fc_val))
        fig_day_val = plot_df_fc(df_plot=df_plot, dffc_plot=df_fc_plot)
        fig_day_val.add_vline(x=date_val)
        fig_day_val.add_vline(x=date_val)
        fig_day_val.add_annotation(x=date_val, y=df_plot.loc[date_val]['y'], text='hoy - horizonte')
        st.plotly_chart(fig_day_val, use_container_width=True)
