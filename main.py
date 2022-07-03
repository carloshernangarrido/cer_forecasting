import streamlit as st
import plotly.express as px
from utils.data_ingestion import get_cer_df
from utils.pre_processing import get_uva_df


@st.cache
def cached_get_cer_df(**kwargs):
    return get_cer_df(url=kwargs['url'] if 'url' in kwargs.keys() else None,
                      delta_years=kwargs['delta_years'])


if __name__ == '__main__':
    st.title("Visualizador y pronosticador de CER y UVA")
    with st.sidebar:
        st.header("Parámetros")
        option_uva_cer = st.selectbox(
            '¿CER o UVA?',
            ('CER', 'UVA'))
        option_delta_years = st.selectbox(
            'Años hacia atrás',
            (1, 2, 3, 4, 5, 6, 7, 8, 9, 10))
    cer_df = cached_get_cer_df(delta_years=option_delta_years)
    uva_df = get_uva_df(cer_df)

    with st.expander(label="Datos actuales"):
        st.header(option_uva_cer)
        col1, col2 = st.columns(2)
        with col1:
            st.header('Gráfico')
            fig_cer = px.line(cer_df if option_uva_cer == 'CER' else uva_df,
                              x='date', y=option_uva_cer.lower())
            st.plotly_chart(fig_cer, use_container_width=True)
        with col2:
            st.header('Tabla')
            st.table(cer_df if option_uva_cer == 'CER' else uva_df)
