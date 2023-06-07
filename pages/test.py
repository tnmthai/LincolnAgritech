import ee
import geemap
import streamlit as st

# Initialize Earth Engine
ee.Initialize()

# Set geemap configuration
geemap.set_plotting_options(image_thumb_width=400, dataFrameSerialization='arrow')

# Create a Streamlit app
st.title("Draw Polygon with geemap and Streamlit")

# Create a map using geemap
Map = geemap.Map(center=[40, -100], zoom=4)

# Enable drawing control
Map.add_draw_control()

# Display the map in Streamlit
st.write(Map.to_streamlit())

# Get the drawn features
drawn_features = Map.user_roi

# Check if any features are drawn
if drawn_features is not None:
    # Convert the drawn features to an Earth Engine Geometry object
    aoi = geemap.geopandas_to_ee(drawn_features, geodesic=False)

    # Calculate the area of the drawn polygons
    area = aoi.geometry().area()

    # Get the area value
    area_value = area.getInfo()

    # Display the area
    st.write("Total area:", area_value, "square meters")

# Display the map with the drawn polygon
st.write(Map.to_streamlit())
