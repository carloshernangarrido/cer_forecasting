import streamlit as st
import plotly.express as px
from utils.data_ingestion import get_cer_df
from utils.pre_processing import get_uva_df


if __name__ == '__main__':
    @st.cache
    def cached_get_cer_df(**kwargs):
        return get_cer_df(url=kwargs['url'] if 'url' in kwargs.keys() else None,
                          delta_years=kwargs['delta_years'])

    cer_df = cached_get_cer_df(delta_years=1)
    uva_df = get_uva_df(cer_df)
    st.title("Visualizador y pronosticador de CER y UVA")
    with st.sidebar:
        st.header("Parámetros")

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.header("CER")
            # st.table(cer_df)
            fig = px.line(cer_df, x='fecha', y="CER")
            st.plotly_chart(fig, use_container_width=True)
            #
            # (x=cer_df['date'], y=cer_df['cer'])
        with col2:
            st.header("UVA")
            st.table(uva_df)
