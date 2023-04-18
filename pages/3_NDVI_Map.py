import streamlit as st
import leafmap.foliumap as leafmap
import ee
st.set_page_config(layout="wide")

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

m = leafmap.Map(center=(-43.525650, 172.639847), zoom=6.25)
# m.split_map(
#     left_layer='ESA WorldCover 2020 S2 FCC', right_layer='ESA WorldCover 2020'
# )
# m.add_legend(title='ESA Land Cover', builtin_legend='ESA_WorldCover')



# Map = geemap.Map()

image = (
    ee.ImageCollection('MODIS/MCD43A4_006_NDVI')
    .filter(ee.Filter.date('2018-04-01', '2018-05-01'))
    .select("NDVI")
    .first()
)

vis_params = {
    'min': 0.0,
    'max': 1.0,
    'palette': [
        'FFFFFF',
        'CE7E45',
        'DF923D',
        'F1B555',
        'FCD163',
        '99B718',
        '74A901',
        '66A000',
        '529400',
        '3E8601',
        '207401',
        '056201',
        '004C00',
        '023B01',
        '012E01',
        '011D01',
        '011301',
    ],
}
# m.setCenter(-7.03125, 31.0529339857, 2)
m.addLayer(image, vis_params, 'MODIS NDVI')

# countries = geemap.shp_to_ee("../data/countries.shp")
# style = {"color": "00000088", "width": 1, "fillColor": "00000000"}
# Map.addLayer(countries.style(**style), {}, "Countries")

ndvi = image.visualize(**vis_params)
# blend = ndvi.blend(countries.style(**style))

m.addLayer(ndvi, {}, "NDVI")

m.to_streamlit(height=700)