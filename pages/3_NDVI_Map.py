import streamlit as st
# import geemap
import geemap.foliumap as geemap
import ee
import geopandas as gpd
from shapely.geometry import Polygon
import warnings
# st.set_page_config(layout="wide")
st.set_page_config(layout="wide")
warnings.filterwarnings("ignore")
@st.cache_data
def ee_authenticate(token_name="EARTHENGINE_TOKEN"):
    geemap.ee_initialize(token_name=token_name)
def getNDVI(image):
    
    # Normalized difference vegetation index (NDVI)
    ndvi = image.normalizedDifference(['B8','B4']).rename("NDVI")
    image = image.addBands(ndvi)

    return(image)

def addDate(image):
    img_date = ee.Date(image.date())
    img_date = ee.Number.parse(img_date.format('YYYYMMdd'))
    return image.addBands(ee.Image(img_date).rename('date').toInt())


st.title("NDVI Map")
ee_authenticate(token_name="EARTHENGINE_TOKEN")

# import geopandas as gpd
# shp = gpd.read_file("data/nzshp/Canterbury.shp")
# gdf = shp.to_crs({'init': 'epsg:4326'}) 

# can = []
# for index, row in gdf.iterrows():
#     for pt in list(row['geometry'].exterior.coords): 
#         can.append(list(pt))
# aoi = {
#     "Canterbury": Polygon(can),
# }
aoi = ee.FeatureCollection("FAO/GAUL/2015/level1").filter(ee.Filter.eq('ADM1_NAME','Canterbury')).geometry()

NDVI_data = ee.ImageCollection('COPERNICUS/S2_SR').filterDate("2022-03-01","2022-03-31").filterBounds(aoi) \
    .map(getNDVI).map(addDate).median()

color = ['FFFFFF', 'CE7E45', 'DF923D', 'F1B555', 'FCD163', '99B718',
               '74A901', '66A000', '529400', '3E8601', '207401', '056201',
               '004C00', '023B01', '012E01', '011D01', '011301']
pallete = {"min":0, "max":1, 'palette':color}
# initialize our map
map1 = geemap.Map()
map1.centerObject(aoi, 7)
map1.addLayer(NDVI_data.clip(aoi).select('NDVI'), pallete, "NDVI")

map1.addLayerControl()
map1

map1.to_streamlit(height=700)

