import streamlit as st
import folium
from streamlit_folium import st_folium

# Use Sydney (NSW) as starting center
CENTER_START = [-33.8688, 151.2093]  # Sydney, NSW

# Initialize session state
if "markers" not in st.session_state:
    st.session_state["markers"] = []

if "center" not in st.session_state:
    st.session_state["center"] = CENTER_START

if "zoom" not in st.session_state:
    st.session_state["zoom"] = 7  # suitable for regional NSW view

st.title("NSW Market Map")
st.subheader("Add New Market Locations")

# User form to add a new market
with st.form("marker_form"):
    lat = st.number_input("Latitude", value=st.session_state["center"][0], format="%.6f")
    lon = st.number_input("Longitude", value=st.session_state["center"][1], format="%.6f")
    label = st.text_input("Label", "New Market")
    submitted = st.form_submit_button("Add Market")

# Add marker if form was submitted
if submitted:
    marker = folium.Marker(location=[lat, lon], popup=label)
    st.session_state["markers"].append(marker)
    st.session_state["center"] = [lat, lon]

# Create map and add markers
m = folium.Map(location=st.session_state["center"], zoom_start=st.session_state["zoom"])
fg = folium.FeatureGroup(name="Markers")
for marker in st.session_state["markers"]:
    fg.add_child(marker)

# Display the map
st_data = st_folium(
    m,
    center=st.session_state["center"],
    zoom=st.session_state["zoom"],
    key="nsw_map",
    feature_group_to_add=fg,
    height=500,
    width=800,
)