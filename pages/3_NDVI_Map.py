import streamlit as st
# import leafmap.foliumap as leafmap
import geemap.foliumap as geemap
import ee
import geopandas as gpd
# st.set_page_config(layout="wide")

# st.sidebar.info(
#     """
#     - Web App URL: <https://streamlit.geemap.org>
#     - GitHub repository: <https://github.com/giswqs/streamlit-geospatial>
#     """
# )

# st.sidebar.title("Contact")
# st.sidebar.info(
#     """
#     Qiusheng Wu: <https://wetlands.io>
#     [GitHub](https://github.com/giswqs) | [Twitter](https://twitter.com/giswqs) | [YouTube](https://www.youtube.com/c/QiushengWu) | [LinkedIn](https://www.linkedin.com/in/qiushengwu)
#     """
# )

st.title("NDVI Map")

m = geemap.Map(center=(-43.525650, 172.639847), zoom=6.25)

shp = gpd.read_file("data/nzshp/Canterbury.shp")
gdf = shp.to_crs({'init': 'epsg:4326'}) 

# m.add_gdf(gdf, "Canterbury")


start_date = '2022-01-01'
end_date = '2022-12-31'

# features = []
# for i in range(shp.shape[0]):
#     geom = shp.iloc[i:i+1,:] 
#     jsonDict = eval(geom.to_json()) 
#     geojsonDict = jsonDict['features'][0] 
#     features.append(ee.Feature(geojsonDict)) 

# roi = ee.FeatureCollection(features)

l8 = (
    ee.ImageCollection('LANDSAT/LC08/C02/T1_TOA') 
    # .filterBounds(roi)
    .filterDate(start_date, end_date)
)
median = l8.median()

visParams = {
    'bands': ['B4', 'B3', 'B2'],
    'min': 0,
    'max': 0.4,
}

m.add_landsat_ts_gif(label= 'Pucallpa, Peru', bands=['SWIR1', 'NIR', 'Red'], nd_bands=['NIR', 'Red'], nd_palette=['black', 'green'], nd_threshold=0.3, start_year=2000, start_date='01-01', end_date='12-31', frames_per_second=5)

# m.addLayer(median, {}, 'l8')


def addNDVI(image):
    ndvi = image.normalizedDifference(['B5', 'B4']).rename('NDVI')
    return image.addBands(ndvi)

def addDate(image):
    img_date = ee.Date(image.date())
    img_date = ee.Number.parse(img_date.format('YYYYMMdd'))
    return image.addBands(ee.Image(img_date).rename('date').toInt())

def addMonth(image):
    img_date = ee.Date(image.date())
    img_doy = ee.Number.parse(img_date.format('M'))
    return image.addBands(ee.Image(img_doy).rename('month').toInt())

def addDOY(image):
    img_date = ee.Date(image.date())
    img_doy = ee.Number.parse(img_date.format('D'))
    return image.addBands(ee.Image(img_doy).rename('doy').toInt())

# withNDVI = l8.map(addNDVI).map(addDate).map(addMonth).map(addDOY)

# greenest = withNDVI.qualityMosaic('NDVI')

# ndvi = greenest.select('NDVI')
# # palette = [
# #     '#d73027',
# #     '#f46d43',
# #     '#fdae61',
# #     '#fee08b',
# #     '#d9ef8b',
# #     '#a6d96a',
# #     '#66bd63',
# #     '#1a9850',
# # ]
# # m.addLayer(ndvi, {'palette': palette}, 'NDVI')
# m.addLayer(ndvi, {}, 'NDVI')
m.to_streamlit(height=700)