import ee
import geemap
import streamlit as st

# Initialize Earth Engine
ee.Initialize()

# Create a Streamlit app
st.title("Draw Polygon with geemap and Streamlit")

# Create a map using geemap
Map = geemap.Map(center=[40, -100], zoom=4)

# Enable drawing control
Map.add_draw_control()

# Display the map in Streamlit
Map.to_streamlit()

# Get the drawn features
drawn_features = Map.user_roi

# Check if any features are drawn
if drawn_features is not None:
    # Convert the drawn features to an Earth Engine Geometry object
    aoi = geemap.geopandas_to_ee(drawn_features, geodesic=False)

    # Add the Earth Engine Geometry object as a layer to the map
    Map.addLayer(aoi, {}, "Drawn Polygon")

# Display the map with the drawn polygon
Map.to_streamlit()
