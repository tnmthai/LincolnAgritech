import streamlit as st
import geemap.foliumap as leafmap
import ee
import geemap
import os

Map = leafmap.Map(
    basemap="HYBRID",
    plugin_Draw=True,
    Draw_export=True,
    # locate_control=True,
    plugin_LatLngPopup=False, center=(-43.525650, 172.639847), zoom=6.25,
)

st.set_page_config(layout="wide")

st.title("Marker Cluster")
# Add Earth Engine dataset
dem = ee.Image('USGS/SRTMGL1_003')

# Set visualization parameters.
dem_vis = {
    'min': 0,
    'max': 4000,
    'palette': ['006633', 'E5FFCC', '662A00', 'D8D8D8', 'F5F5F5'],
}

# Add Earth Engine DEM to map
Map.addLayer(dem, dem_vis, 'SRTM DEM')

# Add Landsat data to map
landsat = ee.Image('LANDSAT/LE7_TOA_5YEAR/1999_2003')

landsat_vis = {'bands': ['B4', 'B3', 'B2'], 'gamma': 1.4}
Map.addLayer(landsat, landsat_vis, "LE7_TOA_5YEAR/1999_2003")


Map.to_streamlit(height=700)
