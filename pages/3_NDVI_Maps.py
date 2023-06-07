import streamlit as st
# import geemap
import geemap.foliumap as geemap
import ee
import geopandas as gpd
from shapely.geometry import Polygon
import warnings
import fiona
import geopandas as gpd
from datetime import date, timedelta, datetime
# import datetime
from dateutil.rrule import rrule, MONTHLY
from dateutil.relativedelta import relativedelta # to add days or years
import pandas as pd
import calendar
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
  return image.updateMask(mask)


def ee_authenticate(token_name="EARTHENGINE_TOKEN"):
    geemap.ee_initialize(token_name=token_name)
def getNDVI(image):
    
    # Normalized difference vegetation index (NDVI)
    ndvi = image.normalizedDifference(['B8','B4']).rename("NDVI")
    image = image.addBands(ndvi)

    return(image)
def calculate_ndvi(image):
    ndvi = image.normalizedDifference(['B8', 'B4'])
    return ndvi.rename('NDVI').copyProperties(image, ['system:time_start'])



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
labels = ['One', 'Two', 'Three', 'Four', 'Five']
# color can be defined using either hex code or RGB (0-255, 0-255, 0-255)
colors = ['#8DD3C7', '#FFFFB3', '#BEBADA', '#FB8072', '#80B1D3']
# # colors = [(255, 0, 0), (127, 255, 0), (127, 18, 25), (36, 70, 180), (96, 68, 123)]

# labels = ['-0.2', '-.2 - 0', '0 - .1', '.1 - .2', '.2 - .3', '.3 - .4', '.4 - .5', '.5 - .6', '.6 - .7', '.7 - .8', '.8 - .9', '.9 - 1.0']
# labels = ['NDVI < -0.2', '-.2 < NDVI ≤ 0', '0 < NDVI ≤ .1', '.1 < NDVI ≤ .2', '.2 < NDVI ≤ .3', '.3 < NDVI ≤ .4', '.4 < NDVI ≤ .5', '.5 < NDVI ≤ .6', '.6 < NDVI ≤ .7', '.7 < NDVI ≤ .8', '.8 < NDVI ≤ .9', '.9 < NDVI ≤ 1.0']
# colors = ['	#000000', '#a50026', '#d73027', '#f46d43', '#fdae61', '#fee08b', '#ffffbf','#d9ef8b','#a6d96a', '#66bd63','#1a9850','#006837']

map1.add_legend(labels= labels,draggable=True)
# labels=labels, colors=colors, position='bottomright'
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
cols1,_ = st.columns((1,2)) 
row1_col1, row1_col2 = st.columns([2, 1])
start_date = '2022-01-01'
end_date = '2022-12-31'

with row1_col2:
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

start_date = sd.strftime("%Y-%m-%d") + "T" 
end_date = ed.strftime("%Y-%m-%d") + "T" 
months = [dt.strftime("%m-%Y") for dt in rrule(MONTHLY, dtstart=sd, until=ed)]

with row1_col1:

    sample_roi = st.selectbox(
        "Select a existing ROI or upload a GeoJSON file:",
        roi_options,
        index=0,
    )
    if sample_roi != "Uploaded GeoJSON":
        gdf = gpd.GeoDataFrame(
            index=[0], crs=crs, geometry=[landsat_rois[sample_roi]]
        )
        # map1.add_gdf(gdf, "ROI")
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
            st.write(":red[No Region of Interest (ROI) has been selected yet.]")
            aoi = []
            # aoi = ee.FeatureCollection("FAO/GAUL/2015/level1").filter(ee.Filter.eq('ADM1_NAME','Canterbury')).geometry()
    
    agree = st.checkbox('Select a month between ' + str(sd) + ' and '+ str(ed))
    if agree:
        # st.write('Great!')
        mo = st.select_slider(
            'Select a month',
            options=months
            )
        st.write('Selected month:', mo)
        # Convert month string to datetime object
        month_date = datetime.strptime(mo, "%m-%Y")

        # Extract year and month from the datetime object
        year = month_date.year
        month = month_date.month

        # Create start_date and end_date based on the given month
        start_date = datetime(year, month, 1).strftime("%Y-%m-%d")
        last_day = calendar.monthrange(year, month)[1]
        # Create the end date for the month
        end_date = datetime(year, month, last_day).strftime("%Y-%m-%d")
        # st.write('Dates between', start_date ,' and ', end_date)
        ####
        
        adate = st.checkbox('Select a date between ' + str(start_date) + ' and '+ str(end_date))
        collect_date = ee.ImageCollection('COPERNICUS/S2_SR').filterDate(start_date, end_date).filterBounds(aoi)
        image_ids = collect_date.aggregate_array('system:index').getInfo()
        dates = [image_id.split('_')[0][:8] for image_id in image_ids]
        listdates = [date[:4] + '-' + date[4:6] + '-' + date[6:] for date in dates]

        if adate:
            # st.write('Great!')
            ad = st.select_slider(
                'Select a date',
                options=listdates
                )
            st.write('Selected date:', ad)
           
            start_date = datetime.strptime(ad, "%Y-%m-%d")
 
            next_date = start_date + timedelta(days=1)
            end_date = next_date.strftime("%Y-%m-%d")+"T"
           
if aoi != []:

    map1.add_gdf(gdf, "ROI")
    aoi = geemap.gdf_to_ee(gdf, geodesic=False)

    NDVI_data = ee.ImageCollection('COPERNICUS/S2_SR').filterDate(start_date, end_date).filterBounds(aoi).filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE",90)).map(maskCloudAndShadows).map(getNDVI).map(addDate).median()
    NDVI_plot = ee.ImageCollection('COPERNICUS/S2_SR').filterDate(start_date, end_date).filterBounds(aoi).filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE",90)).map(maskCloudAndShadows).map(calculate_ndvi).map(addDate)
    # st.write(start_date, end_date)
    # areas = geemap.ee_to_gdf(aoi)

    # # Calculate the area of the polygon
    # area = areas.geometry.area.item()
    # st.write('Area: ', round(area*10**4,1),' Square Kilometers.')

    graph_ndvi = st.checkbox('Show NDVI graph')
    if graph_ndvi:    
        image_ids = NDVI_plot.aggregate_array('system:index').getInfo()
        # image_ids
        dates = []
        ndvi_values = []
        # Iterate over the image IDs
        for image_id in image_ids:
            # Get the image by ID
            image = NDVI_plot.filter(ee.Filter.eq('system:index', image_id)).first()   
            
            # Get the image date and NDVI value
            date = image.date().format('yyyy-MM-dd')
            # print(date)
            # ndvi_value = image.reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10).get('NDVI').getInfo()
            try:
                st.session_state["ndvi_value"] = ndvi_value = image.reduceRegion(reducer=ee.Reducer.mean(), geometry=aoi, scale=10).get('NDVI').getInfo()
            except Exception as e:
                st.error("Please select smaller polygon!")
                st.error(e)
                

            # Add the date and NDVI value to the lists
            dates.append(date.getInfo())
            ndvi_values.append(ndvi_value)

        # # Create a pandas DataFrame from the lists
        df = pd.DataFrame({'Date': dates, 'NDVI': ndvi_values})
        
        st.bar_chart(df, y="NDVI", x="Date", use_container_width=True)
 

    map1.centerObject(aoi)
    try:
        st.session_state["ndvi"] = map1.addLayer(NDVI_data.clip(aoi).select('NDVI'), pallete, "NDVI")

    except Exception as e:
        # st.error(e)
        st.error("Too much cloud on this day.")
        st.error("Please select additional dates!")



map1.addLayerControl()

map1.to_streamlit(height=700)