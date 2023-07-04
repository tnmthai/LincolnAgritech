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
startDate = '2021-01-20'
endDate = '2021-01-21'
rgb = ['B4','B3','B2']
rgbViza = {"min":0.0, "max":0.7,"bands":rgb}
aoi = ee.FeatureCollection("FAO/GAUL/2015/level0").filter(ee.Filter.eq('ADM0_NAME','New Zealand')).geometry()
se2a = ee.ImageCollection('COPERNICUS/S2_SR').filterDate(startDate,endDate).filterBounds(aoi).filter(
    ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE",90)).median().divide(10000)#.clip(aoi)
Map.centerObject(aoi)
Map.addLayer(se2a, rgbViza, "S2 original")
Map.to_streamlit(height=700)
