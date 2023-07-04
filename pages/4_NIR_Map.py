import streamlit as st
# import leafmap.foliumap as leafmap
import geemap.foliumap as geemap
import ee
import geopandas as gpd
# st.set_page_config(layout="wide")
@st.cache_data
def ee_authenticate(token_name="EARTHENGINE_TOKEN"):
    geemap.ee_initialize(token_name=token_name)


st.title("NIR Map")
ee_authenticate(token_name="EARTHENGINE_TOKEN")
# geemap.ee_initialize()
Map = geemap.Map(center=(-43.525650, 172.639847), zoom=6.25)



Map.to_streamlit(height=700)
