import streamlit as st
from streamlit_folium import st_folium
import folium

m = folium.Map()
stdata = st_folium(m)