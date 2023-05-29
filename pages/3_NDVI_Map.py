import streamlit as st
# import geemap
import geemap.foliumap as geemap
import ee
import geopandas as gpd
from shapely.geometry import Polygon
import warnings
import fiona
from datetime import date


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


# st.title("NDVI Map")
ee_authenticate(token_name="EARTHENGINE_TOKEN")

aoi = ee.FeatureCollection("FAO/GAUL/2015/level1").filter(ee.Filter.eq('ADM1_NAME','Canterbury')).geometry()

NDVI_data = ee.ImageCollection('COPERNICUS/S2_SR').filterDate("2022-03-01","2022-03-31").filterBounds(aoi) \
    .map(getNDVI).map(addDate).median()

color = ['FFFFFF', 'CE7E45', 'DF923D', 'F1B555', 'FCD163', '99B718',
               '74A901', '66A000', '529400', '3E8601', '207401', '056201',
               '004C00', '023B01', '012E01', '011D01', '011301']
pallete = {"min":0, "max":1, 'palette':color}
def app():

    today = date.today()

    st.title("Satellite Timelapse")

    row1_col1 = st.columns([1, 1])

    if st.session_state.get("zoom_level") is None:
        st.session_state["zoom_level"] = 4

    st.session_state["ee_asset_id"] = None
    st.session_state["bands"] = None
    st.session_state["palette"] = None
    st.session_state["vis_params"] = None

    with row1_col1:
        ee_authenticate(token_name="EARTHENGINE_TOKEN")
        m = geemap.Map(
            basemap="HYBRID",
            plugin_Draw=True,
            Draw_export=True,
            locate_control=True,
            plugin_LatLngPopup=False, center=(-43.525650, 172.639847), zoom=6.25,
        )
        m.add_basemap("ROADMAP")

    with row1_col1:

            # with st.expander(
            #    ""
            #     # "Steps: Draw a rectangle on the map -> Export it as a GeoJSON -> Upload it back to the app -> Click the Submit button. Expand this tab to see a demo."
            # ):
            #     video_empty = st.empty()
                # print()
            data = st.file_uploader(
                "Upload a GeoJSON file to use as an ROI. Customize timelapse parameters and then click the Submit button.",
                type=["geojson", "kml", "zip"],
            )

            crs = "epsg:4326"
            if sample_roi == "Uploaded GeoJSON":
                if data is None:
                    # st.info(
                    #     "Steps to create a timelapse: Draw a rectangle on the map -> Export it as a GeoJSON -> Upload it back to the app -> Click Submit button"
                    # )
                    if collection in [
                        "Geostationary Operational Environmental Satellites (GOES)",
                        "USDA National Agriculture Imagery Program (NAIP)",
                    ] and (not keyword):
                        m.set_center(-100, 40, 3)
                    # else:
                    #     m.set_center(4.20, 18.63, zoom=2)
            else:
                if collection in [
                    "Landsat TM-ETM-OLI Surface Reflectance",
                    "Sentinel-2 MSI Surface Reflectance",
                ]:
                    gdf = gpd.GeoDataFrame(
                        index=[0], crs=crs, geometry=[landsat_rois[sample_roi]]
                    )
                elif (
                    collection
                    == "Geostationary Operational Environmental Satellites (GOES)"
                ):
                    gdf = gpd.GeoDataFrame(
                        index=[0], crs=crs, geometry=[goes_rois[sample_roi]["region"]]
                    )
                elif collection == "MODIS Vegetation Indices (NDVI/EVI) 16-Day Global 1km":
                    gdf = gpd.GeoDataFrame(
                        index=[0], crs=crs, geometry=[modis_rois[sample_roi]]
                    )

            if sample_roi != "Uploaded GeoJSON":

                if collection in [
                    "Landsat TM-ETM-OLI Surface Reflectance",
                    "Sentinel-2 MSI Surface Reflectance",
                ]:
                    gdf = gpd.GeoDataFrame(
                        index=[0], crs=crs, geometry=[landsat_rois[sample_roi]]
                    )
                elif (
                    collection
                    == "Geostationary Operational Environmental Satellites (GOES)"
                ):
                    gdf = gpd.GeoDataFrame(
                        index=[0], crs=crs, geometry=[goes_rois[sample_roi]["region"]]
                    )
                elif collection in [
                    "MODIS Vegetation Indices (NDVI/EVI) 16-Day Global 1km",
                    "MODIS Gap filled Land Surface Temperature Daily",
                ]:
                    gdf = gpd.GeoDataFrame(
                        index=[0], crs=crs, geometry=[modis_rois[sample_roi]]
                    )
                elif collection == "MODIS Ocean Color SMI":
                    gdf = gpd.GeoDataFrame(
                        index=[0], crs=crs, geometry=[ocean_rois[sample_roi]]
                    )
                try:
                    st.session_state["roi"] = geemap.gdf_to_ee(gdf, geodesic=False)
                except Exception as e:
                    st.error(e)
                    st.error("Please draw another ROI and try again.")
                    return
                m.add_gdf(gdf, "ROI")

            elif data:
                gdf = uploaded_file_to_gdf(data)
                try:
                    st.session_state["roi"] = geemap.gdf_to_ee(gdf, geodesic=False)
                    m.add_gdf(gdf, "ROI")
                except Exception as e:
                    st.error(e)
                    st.error("Please draw another ROI and try again.")
                    return

            m.to_streamlit(height=600)
# initialize our map
    map1 = geemap.Map()
    map1.centerObject(aoi, 7)
    map1.addLayer(NDVI_data.clip(aoi).select('NDVI'), pallete, "NDVI")

    map1.addLayerControl()

    map1.to_streamlit(height=700)

