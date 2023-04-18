import streamlit as st
import leafmap.foliumap as leafmap
import geemap.foliumap as geemap
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

m = geemap.Map(center=(-43.525650, 172.639847), zoom=6.25)
# m.split_map(
#     left_layer='ESA WorldCover 2020 S2 FCC', right_layer='ESA WorldCover 2020'
# )
# m.add_legend(title='ESA Land Cover', builtin_legend='ESA_WorldCover')

import geopandas as gpd
shp = gpd.read_file("data/nzshp/Canterbury.shp")
gdf = shp.to_crs({'init': 'epsg:4326'}) 

m.add_gdf(gdf, "Canterbury")

m.to_streamlit(height=700)