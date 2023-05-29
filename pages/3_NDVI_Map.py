import streamlit as st
# import geemap
import geemap.foliumap as geemap
import ee
import geopandas as gpd
from shapely.geometry import Polygon
import warnings
import fiona
import geopandas as gpd
from datetime import date, timedelta
import datetime
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

color = ['FFFFFF', 'CE7E45', 'DF923D', 'F1B555', 'FCD163', '99B718',
               '74A901', '66A000', '529400', '3E8601', '207401', '056201',
               '004C00', '023B01', '012E01', '011D01', '011301']
pallete = {"min":0, "max":1, 'palette':color}
st.title("NDVI Map")
ee_authenticate(token_name="EARTHENGINE_TOKEN")
ee.Initialize()
map1 = geemap.Map(
    basemap="HYBRID",
    plugin_Draw=True,
    Draw_export=True,
    locate_control=True,
    plugin_LatLngPopup=False, center=(-43.525650, 172.639847), zoom=6.25,
)
# map1.add_basemap("ROADMAP")



shp = gpd.read_file("data/nzshp/Canterbury.shp")
gdf = shp.to_crs({'init': 'epsg:4326'}) 

can = []
for index, row in gdf.iterrows():
    for pt in list(row['geometry'].exterior.coords): 
        can.append(list(pt))


shp = gpd.read_file("data/nzshp/Mitimiti.shp")
gdf = shp.to_crs({'init': 'epsg:4326'}) 

Mitimiti = []
for index, row in gdf.iterrows():
    for pt in list(row['geometry'].exterior.coords): 
        Mitimiti.append(list(pt))

shp = gpd.read_file("data/nzshp/Urewera.shp")
gdf = shp.to_crs({'init': 'epsg:4326'}) 

Urewera = []
for index, row in gdf.iterrows():
    for pt in list(row['geometry'].exterior.coords): 
        Urewera.append(list(pt))


landsat_rois = {
    "Canterbury":Polygon (can),
    "Mitimiti": Polygon(  Mitimiti  ),
    "Te Urewera": Polygon(  Urewera  ),

}

roi_options = ["Uploaded GeoJSON"] + list(landsat_rois.keys())
crs = "epsg:4326"

row1_col1, row1_col2 = st.columns([2, 1])
start_date = '2022-01-01'
end_date = '2022-12-31'

with row1_col1:

    sample_roi = st.selectbox(
        "Select a existing ROI or upload a GeoJSON file:",
        roi_options,
        index=0,
    )
with row1_col2:
    today = date.today()

    default_date_yesterday = today - timedelta(days=1)


    sd = st.date_input(
        "Start date",
        date(2022, 1, 1))
    # st.write('start:', sd.strftime("%Y-%m-%d") )
    ed = st.date_input(
        "End date",
        default_date_yesterday)       
    # start_date = ee.Date(sd.strftime("%Y-%m-%d"))
    end_date = ee.Date(ed.strftime("%Y-%m-%d"))
    # st.write('start2:', start_date )
    st.write('Your dates between', ee.Date(sd.strftime("%Y-%m-%d")) ,' and ', end_date)
    end_date = '2022-12-31'
if sample_roi != "Uploaded GeoJSON":
    gdf = gpd.GeoDataFrame(
        index=[0], crs=crs, geometry=[landsat_rois[sample_roi]]
    )
    map1.add_gdf(gdf, "ROI")
    aoi = geemap.gdf_to_ee(gdf, geodesic=False)
elif sample_roi == "Uploaded GeoJSON":
    data = st.file_uploader(
        "Upload a GeoJSON file to use as an ROI. Customize timelapse parameters and then click the Submit button.",
        type=["geojson", "kml", "zip"],
    )
    if data:
        gdf = uploaded_file_to_gdf(data)
        st.session_state["aoi"] = geemap.gdf_to_ee(gdf, geodesic=False)    
        map1.add_gdf(gdf, "ROI")
    else:
        aoi = ee.FeatureCollection("FAO/GAUL/2015/level1").filter(ee.Filter.eq('ADM1_NAME','Canterbury')).geometry()
aoi = geemap.gdf_to_ee(gdf, geodesic=False)
# else:
    # aoi = ee.FeatureCollection("FAO/GAUL/2015/level1").filter(ee.Filter.eq('ADM1_NAME','Canterbury')).geometry()

NDVI_data = ee.ImageCollection('COPERNICUS/S2_SR').filterDate(start_date, end_date).filterBounds(aoi) \
.map(getNDVI).map(addDate).median()

map1.centerObject(aoi)
map1.addLayer(NDVI_data.clip(aoi).select('NDVI'), pallete, "NDVI")

map1.addLayerControl()

map1.to_streamlit(height=700)

