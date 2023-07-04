import streamlit as st
# import leafmap.foliumap as leafmap
import geemap.foliumap as geemap
import ee
import geopandas as gpd
# st.set_page_config(layout="wide")
@st.cache_data
def ee_authenticate(token_name="EARTHENGINE_TOKEN"):
    geemap.ee_initialize(token_name=token_name)
def maskCloudAndShadows(image):
  cloudProb = image.select('MSK_CLDPRB')
  snowProb = image.select('MSK_SNWPRB')
  cloud = cloudProb.lt(5)
  snow = snowProb.lt(5)
  scl = image.select('SCL')
  shadow = scl.eq(3); # 3 = cloud shadow
  cirrus = scl.eq(10); # 10 = cirrus
  # Cloud probability less than 5% or cloud shadow classification
  mask = (cloud.And(snow)).And(cirrus.neq(1)).And(shadow.neq(1))
  return image.updateMask(mask).divide(10000)
st.title("Sentinel 2 Bands and Combinations")
ee_authenticate(token_name="EARTHENGINE_TOKEN")
# geemap.ee_initialize()
Map = geemap.Map(center=(-43.525650, 172.639847))
startDate = '2022-01-01'
endDate = '2022-03-31'
RGB = st.selectbox(
    "Select an RGB band combination:",
    [
    "Natural Color (B4,B3,B2)",
    "Color Infrared (B8,B4,B3)",
    "Short-Wave Infrared (B12,B8,B4)",
    "Agriculture (B11,B8,B2)",
    "Geology (B12,B11,B2)",
    "Bathymetric (B4,B3,B1)",
    "Healthy Vegetation (B8,B11,B2)",
    "Land/Water (B8,B11,B4)",
    "Natural Colors with Atmospheric Removal (B12,B8,B3)",
    "Vegetation Analysis (B11,B8,B4)"
    ],
    index=0,
    )
start_index = RGB.find("(") + 1
end_index = RGB.find(")")

values = RGB[start_index:end_index]
band = values.split(",")

rgbViza = {"min":0.0, "max":0.7,"bands":band}
aoi = ee.FeatureCollection("FAO/GAUL/2015/level0").filter(ee.Filter.eq('ADM0_NAME','New Zealand')).geometry()
se2a = ee.ImageCollection('COPERNICUS/S2_SR').filterDate(startDate,endDate).filterBounds(aoi).filter(
    ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE",60)).median().divide(10000)#.clip(aoi)
se2c = ee.ImageCollection('COPERNICUS/S2_SR').filterDate(
    startDate,endDate).filterBounds(aoi).filter(
    ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE",90)).map(maskCloudAndShadows).median().clip(aoi)
Map.centerObject(aoi,7)
Map.addLayer(se2c, rgbViza, "Sentinel 2")
Map.to_streamlit(height=700)
