import streamlit as st
from utils.common import common_data, common_dash
from utils.plots import plot_df_fc, df2plot, plot_comp
from utils.pre_processing import get_day_diff


if __name__ == '__main__':
    st.set_page_config(
        page_icon="👋",
        page_title='PronostiCER',
        layout='wide',
        initial_sidebar_state='auto')
    option_uva_cer, option_delta_years, option_days_ahead, option_origin = common_dash()
    cer_df, uva_df, cer_df_fc, uva_df_fc, today, dolar_blue_df, dolar_blue_df_fc = \
        common_data(option_delta_years, option_days_ahead, option_origin)

    with st.expander(label="Comparación UVA vs Dólar Blue", expanded=True):
        st.subheader('Comparación UVA vs Dólar Blue')
        uva_df_plot, uva_df_fc_plot = df2plot(uva_df, uva_df_fc)
        dolar_blue_df_plot, dolar_blue_df_fc_plot = df2plot(dolar_blue_df,
                                                            dolar_blue_df_fc)
        fig = plot_comp(uva_df_plot, uva_df_fc_plot, today, dolar_blue_df_plot, dolar_blue_df_fc_plot)
        fig.add_vline(x=today)
        fig.add_annotation(x=today, y=1, text=f'hoy UVA={round(uva_df_plot.loc[today]["y"])}, '
                                              f'dólar blue={round(dolar_blue_df_plot.loc[today]["y"])}')
        st.plotly_chart(fig, use_container_width=True)

    st.header(f"Datos pronosticados de {option_uva_cer}")
    with st.expander(label="Valores", expanded=True):
        st.subheader('Valores')
        df_plot, df_fc_plot = df2plot(cer_df if option_uva_cer == 'CER' else uva_df,
                                      cer_df_fc if option_uva_cer == 'CER' else uva_df_fc)
        fig_val = plot_df_fc(df_plot=df_plot, dffc_plot=df_fc_plot)
        fig_val.add_vline(x=today)
        fig_val.add_annotation(x=today, y=df_plot.loc[today]['y'], text='hoy')
        st.plotly_chart(fig_val, use_container_width=True)

    with st.expander(label="Variación diaria", expanded=False):
        st.subheader('Variación diaria')
        df_plot, df_fc_plot = df2plot(get_day_diff(cer_df) if option_uva_cer == 'CER' else get_day_diff(uva_df),
                                      get_day_diff(cer_df_fc) if option_uva_cer == 'CER' else get_day_diff(uva_df_fc))
        fig_day = plot_df_fc(df_plot=df_plot, dffc_plot=df_fc_plot)
        fig_day.add_vline(x=today)
        fig_day.add_annotation(x=today, y=df_plot.loc[today]['y'], text='hoy')
        st.plotly_chart(fig_day, use_container_width=True)

    st.header(f"Datos pronosticados de Dólar Blue")
    with st.expander(label="Valores", expanded=True):
        st.subheader('Valores')
        df_plot, df_fc_plot = df2plot(dolar_blue_df,
                                      dolar_blue_df_fc)
        fig_val = plot_df_fc(df_plot=df_plot, dffc_plot=df_fc_plot)
        fig_val.add_vline(x=today)
        fig_val.add_annotation(x=today, y=df_plot.loc[today]['y'], text='hoy')
        st.plotly_chart(fig_val, use_container_width=True)

    with st.expander(label="Variación diaria", expanded=False):
        st.subheader('Variación diaria')
        df_plot, df_fc_plot = df2plot(get_day_diff(dolar_blue_df),
                                      get_day_diff(dolar_blue_df_fc))
        fig_day = plot_df_fc(df_plot=df_plot, dffc_plot=df_fc_plot)
        fig_day.add_vline(x=today)
        fig_day.add_annotation(x=today, y=df_plot.loc[today]['y'], text='hoy')
        st.plotly_chart(fig_day, use_container_width=True)

    with st.expander(label="Acerca de...", expanded=True):
        st.subheader("Acerca de...")
        st.text("Desarrollado por Hernán Garrido, 261 15 3636206, carloshernangarrido@gmail.com"
                "\nDatos de CER/UVA tomados de: http://www.bcra.gov.ar"
                "\nDatos de dólar blue tomados de: https://www.ambito.com/"
                "\nPronosticado con Facebook Prophet")


