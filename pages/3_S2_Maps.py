import tempfile
import os
import uuid
import streamlit as st
import apps.lal as lal
import geemap.foliumap as geemap
import ee
import geopandas as gpd
from datetime import date, timedelta, datetime
import fiona
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
def uploaded_file_to_gdf(data):
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
st.title("Sentinel 2 Bands and Combinations")
ee_authenticate(token_name="EARTHENGINE_TOKEN")
global  added_layers = {}

def add_layer(band_combination,rgbViza):
    rgb = ee.ImageCollection("COPERNICUS/S2_SR") \
        .filterDate(startDate, endDate) \
        .filterBounds(aoi) \
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 60)) \
        .median() \
        .divide(10000) \
        .clip(aoi) \
        .select(band_combination)
    
    # Generate a unique ID for the layer
    layer_id = str(len(added_layers))
    
    # Add the layer to the map
    Map.addLayer(rgb, rgbViza, "Layer " + layer_id)
    Map.centerObject(aoi)
    # Store the added layer in the dictionary
    added_layers[layer_id] = rgb
    st.write(str(len(added_layers)))

Map = geemap.Map(
    basemap="HYBRID",
    plugin_Draw=True,
    Draw_export=True,
    # locate_control=True,
    plugin_LatLngPopup=False, center=(-43.525650, 172.639847), zoom=6.25,
)

roi_options = ["Uploaded GeoJSON"] + list(lal.nz_rois.keys())
crs = "epsg:4326"
sample_roi = st.selectbox(
    "Select a existing ROI or upload a GeoJSON file:",
    roi_options,
    index=0,
)
if sample_roi != "Uploaded GeoJSON":
        gdf = gpd.GeoDataFrame(
            index=[0], crs=crs, geometry=[lal.nz_rois[sample_roi]]
        )        
        aoi = geemap.gdf_to_ee(gdf, geodesic=False)
elif sample_roi == "Uploaded GeoJSON":
    data = st.file_uploader(
        "Upload a GeoJSON file to use as an ROI. Customize timelapse parameters and then click the Submit button.",
        type=["geojson", "kml", "zip"],
    )
    if data:
        gdf = uploaded_file_to_gdf(data)
        st.session_state["aoi"] = aoi= geemap.gdf_to_ee(gdf, geodesic=False)    
        # map1.add_gdf(gdf, "ROI")
    else:
        # st.write(":red[No Region of Interest (ROI) has been selected yet.]")
        st.warning("No Region of Interest (ROI) has been selected yet!",icon="⚠️")
        aoi = [] 

today = date.today()
default_date_yesterday = today - timedelta(days=1)

sd = st.date_input(
        "Start date", date(2023, 1, 1), min_value= date(2015, 6, 23),
        max_value= today,
        )

ed = st.date_input(
    "End date",
    default_date_yesterday,
    min_value= date(2015, 6, 23),max_value= today)       
    
st.write('Dates between', sd ,' and ', ed)

startDate = sd.strftime("%Y-%m-%d") + "T" 
endDate = ed.strftime("%Y-%m-%d") + "T" 

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


# aoi = ee.FeatureCollection("FAO/GAUL/2015/level0").filter(ee.Filter.eq('ADM0_NAME','New Zealand')).geometry()
# if aoi!=[]:
#     se2a = ee.ImageCollection('COPERNICUS/S2_SR').filterDate(startDate,endDate).filterBounds(aoi).filter(
#         ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE",60)).median().divide(10000).clip(aoi)
#     se2c = ee.ImageCollection('COPERNICUS/S2_SR').filterDate(
#         startDate,endDate).filterBounds(aoi).filter(
#         ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE",90)).map(maskCloudAndShadows).median().clip(aoi)
#     Map.centerObject(aoi)
#     titlemap = "Sentinel 2: " + str(RGB[0:start_index-1])
#     Map.addLayer(se2c, rgbViza, titlemap)
def main():
    add_layer(band, rgbViza)
    
    Map.to_streamlit(height=700)
if __name__ == "__main__":
    main()