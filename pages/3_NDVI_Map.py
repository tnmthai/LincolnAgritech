import streamlit as st
# import geemap
import geemap.foliumap as geemap
import ee
import geopandas as gpd
from shapely.geometry import Polygon
import warnings
import fiona
# st.set_page_config(layout="wide")
st.set_page_config(layout="wide")
warnings.filterwarnings("ignore")
@st.cache_data

def uploaded_file_to_gdf(data):
    import tempfile
    import os
    import uuid

    _, file_extension = os.path.splitext(data.name)
    file_id = str(uuid.uuid4())
    file_path = os.path.join(tempfile.gettempdir(), f"{file_id}{file_extension}")

    with open(file_path, "wb") as file:
        file.write(data.getbuffer())

    if file_path.lower().endswith(".kml"):
        fiona.drvsupport.supported_drivers["KML"] = "rw"
        gdf = gpd.read_file(file_path, driver="KML")
    else:
        gdf = gpd.read_file(file_path)

    return gdf

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
data = st.file_uploader(
    "Upload a GeoJSON file to use as an ROI. Customize timelapse parameters and then click the Submit button.",
    type=["geojson", "kml", "zip"],
)
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
map1.addLayer(NDVI_data.clip(aoi).select('NDVI'), pallete, "NDVI-Canterbury")

map1.addLayerControl()

map1.to_streamlit(height=700)

