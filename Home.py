import streamlit as st
import leafmap.foliumap as leafmap

st.set_page_config(layout="wide")

st.sidebar.title("About")
st.sidebar.info(
    """
    - Web App URL: https://lincolnagritech.streamlit.app/
   
    """
)

st.sidebar.title("Contact")
st.sidebar.info(
    """
    Thai Tran: Thai.Tran@
    """
)

st.title("Lincoln Agritech Geospatial Applications")

st.markdown(
    """
    An online interactive mapping tool to display basic vegetative metrics available over New Zealand.
    """
)

st.info("Click on the left sidebar menu to navigate to the different apps.")

st.subheader("Timelapse of Satellite Imagery")
st.markdown(
    """
    The following timelapse animations were created using the Timelapse web app. Click `Timelapse` on the left sidebar menu to create your own timelapse for any location around the globe.
"""
)

row1_col1, row1_col2, row1_col3 = st.columns(3)
with row1_col1:
    st.image("data/can.gif")
    st.markdown("""Canterbury Region""")
    
with row1_col2:
    st.image("data/urewera.gif")
    
with row1_col3:
    st.image("data/mitimiti.gif")
