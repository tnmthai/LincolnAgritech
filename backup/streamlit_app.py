import streamlit as st
import leafmap.foliumap as leafmap

st.set_page_config(layout="wide")

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

# Customize page title
st.title("Lincoln Agritech Geospatial Applications")

st.markdown(
    """
    An online interactive mapping tool to display basic vegetative metrics available over Canterbury.
    """
)



m = leafmap.Map(minimap_control=True, center=(-43.525650, 172.639847), zoom=6.25)
m.add_basemap("OpenTopoMap")
m.to_streamlit(height=500)
