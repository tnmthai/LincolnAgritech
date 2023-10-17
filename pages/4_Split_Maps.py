import streamlit as st
import leafmap.foliumap as leafmap
import ee
import tempfile
import os
import uuid
import streamlit as st
import apps.lal as lal
import geemap.foliumap as geemap
# import geemap
import ee
import geopandas as gpd
from datetime import date, timedelta, datetime
import fiona

# Set page config
st.set_page_config(layout="wide")
st.title("Split-panel Map")

# Define utility functions (if needed)
def maskCloudAndShadows(image):
    # Your implementation here
    pass

def getNDVI(image):
    # Your implementation here
    pass

def addDate(image):
    # Your implementation here
    pass

# Define visualization parameters
bandRGB = ['B4', 'B3', 'B2']

palette = ['FFFFFF', 'CE7E45', 'DF923D', 'F1B555', 'FCD163', '99B718', '74A901', '66A000', '529400', '3E8601', '207401', '056201', '004C00', '023B01', '012E01', '011D01', '011301']

vis_params = {
    'min': 0,
    'max': 1,
    'palette': palette
}

# Create date inputs
row1_col1, row1_col2, row1_col3 = st.columns([1, 1, 1])

with row1_col2:
    today = date.today()
    default_date_yesterday = today - timedelta(days=1)

    sd = st.date_input(
        "Start date", date(2023, 1, 1), min_value=date(2015, 6, 23),
        max_value=today
    )

    ed = st.date_input(
        "End date",
        default_date_yesterday,
        min_value=date(2015, 6, 23),
        max_value=today
    )

# Process imagery
startDate = sd.strftime("%Y-%m-%d") + "T"
endDate = ed.strftime("%Y-%m-%d") + "T"

se2a = geemap.ee_tile_layer(
    geemap.ee.ImageCollection('COPERNICUS/S2_SR')
    .filterDate(startDate, endDate)
    .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 60))
    .map(maskCloudAndShadows)
    .median(),
    {"min": 0.0, "max": 0.7, "bands": bandRGB},
    'RGB'
)

ndvi_data = geemap.ee_tile_layer(
    geemap.ee.ImageCollection('COPERNICUS/S2_SR')
    .filterDate(startDate, endDate)
    .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 60))
    .map(maskCloudAndShadows)
    .map(getNDVI)
    .map(addDate)
    .median()
    .select('NDVI'),
    vis_params,
    'NDVI'
)

# Create map
m = geemap.Map(center=(-43.525650, 172.639847), zoom=6.25)
m.split_map(left_layer=se2a, right_layer=ndvi_data)

# Display the map in Streamlit
m.to_streamlit(height=700)





# import streamlit as st
# import leafmap.foliumap as leafmap
# import ee
# import tempfile
# import os
# import uuid
# import streamlit as st
# import apps.lal as lal
# import geemap.foliumap as geemap
# # import geemap
# import ee
# import geopandas as gpd
# from datetime import date, timedelta, datetime
# import fiona

# st.set_page_config(layout="wide")
# st.title("Split-panel Map")
# def maskCloudAndShadows(image):
#   cloudProb = image.select('MSK_CLDPRB')
#   snowProb = image.select('MSK_SNWPRB')
#   cloud = cloudProb.lt(5)
#   snow = snowProb.lt(5)
#   scl = image.select('SCL')
#   shadow = scl.eq(3); # 3 = cloud shadow
#   cirrus = scl.eq(10); # 10 = cirrus
#   # Cloud probability less than 5% or cloud shadow classification
#   mask = (cloud.And(snow)).And(cirrus.neq(1)).And(shadow.neq(1))
#   return image.updateMask(mask).divide(10000)
# def getNDVI(image): 
#     ndvi = image.normalizedDifference(['B8','B4']).rename("NDVI")
#     image = image.addBands(ndvi)
#     return(image)
# def calculate_ndvi(image):
#     ndvi = image.normalizedDifference(['B8', 'B4'])
#     return ndvi.rename('NDVI').copyProperties(image, ['system:time_start'])

# def addDate(image):
#     img_date = ee.Date(image.date())
#     img_date = ee.Number.parse(img_date.format('YYYYMMdd'))
#     return image.addBands(ee.Image(img_date).rename('date').toInt())


# bandRGB = ['B4','B3','B2']
# bandNIR = ['B8','B4','B3']
# palette = ['FFFFFF', 'CE7E45', 'DF923D', 'F1B555', 'FCD163', '99B718', '74A901', '66A000', '529400', '3E8601', '207401', '056201', '004C00', '023B01', '012E01', '011D01', '011301']
# # cm.palettes.ndvi

# vis_params = {
#   'min': 0,
#   'max': 1,
#   'palette': palette}
# row1_col1, row1_col2, row1_col3 = st.columns([1, 1 , 1])
# with row1_col2:
#     today = date.today()
#     default_date_yesterday = today - timedelta(days=1)

#     sd = st.date_input(
#             "Start date", date(2023, 1, 1), min_value= date(2015, 6, 23),
#             max_value= today,
#             )
#     ed = st.date_input(
#         "End date",
#         default_date_yesterday,
#         min_value= date(2015, 6, 23),max_value= today)       
#     startDate = sd.strftime("%Y-%m-%d") + "T" 
#     endDate = ed.strftime("%Y-%m-%d") + "T" 

# rgbViza = {"min":0.0, "max":0.7,"bands":bandRGB}
# rgbVizb = {"min":0.0, "max":0.7,"bands":bandNIR}

# se2a = ee.ImageCollection('COPERNICUS/S2_SR').filterDate(startDate,endDate).filter(
#     ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE",60)).map(maskCloudAndShadows).median()

# se2b = ee.ImageCollection('COPERNICUS/S2_SR').filterDate(startDate,endDate).filter(
#     ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE",60)).map(maskCloudAndShadows).median()
# ndvi_data = ee.ImageCollection('COPERNICUS/S2_SR').filterDate(startDate, endDate).filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE",60)).map(maskCloudAndShadows).map(getNDVI).map(addDate).median()

# # map1.addLayer(NDVI_data.clip(aoi).select('NDVI'), vis_params, "Median of NDVI for all selected dates")        

# s2a = geemap.ee_tile_layer(se2a, rgbViza, 'RGB') #, opacity=0.75)
# # s2b = geemap.ee_tile_layer(se2a, rgbVizb, 'NIR')#, opacity=0.75)
# s2b = geemap.ee_tile_layer(ndvi_data.select('NDVI'), vis_params, 'NDVI')#, opacity=0.75)

# m = geemap.Map(center=(-43.525650, 172.639847), zoom=6.25)
# m.split_map(
#     left_layer= s2a, right_layer=s2b
# )
# # m.add_legend(title='RGB and NIR')


# m.to_streamlit(height=700)
