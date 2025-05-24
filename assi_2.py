import streamlit as st
import folium
import random
from streamlit_folium import st_folium

# NSW center (Sydney)
CENTER_START = [-33.8688, 151.2093]

# Sydney bounding box
LAT_MIN, LAT_MAX = -34.25, -33.35
LON_MIN, LON_MAX = 150.75, 151.15

# Initialize session state
if "markers" not in st.session_state:
    st.session_state["markers"] = []

if "center" not in st.session_state:
    st.session_state["center"] = CENTER_START

if "zoom" not in st.session_state:
    st.session_state["zoom"] = 10

#st.title("Random Market Generator in NSW")

markets = ["92", "94", "97"]
default_index = markets.index("92")
selected_market = st.selectbox("Fuel", markets, index=default_index)

if st.button("Add Random Markers"):
    
    lat = random.uniform(LAT_MIN, LAT_MAX)
    lon = random.uniform(LON_MIN, LON_MAX)
    number = random.randint(100, 999)

    # Custom image + number marker
    image_url = "https://upload.wikimedia.org/wikipedia/en/thumb/e/e8/Shell_logo.svg/150px-Shell_logo.svg.png"
    html = f"""
    <div style="position: relative; width: 40px; height: 40px;">
        <img src="{image_url}" style="width: 100%; height: 100%; border-radius: 50%;">
        <div style="
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 14px;
            font-weight: bold;
            color: white;
            text-shadow:
            -1px -1px 0 black,
            1px -1px 0 black,
            -1px  1px 0 black,
            1px  1px 0 black;
        ">{number}</div>
    </div>
    """

    marker = folium.Marker(
        location=[lat, lon],
        icon=folium.DivIcon(
            icon_size=(40, 40),
            icon_anchor=(20, 20),
            html=html
        ),
        popup=f"Market #{number}"
    )
    st.session_state["markers"].append(marker)

# Draw the map
m = folium.Map(location=st.session_state["center"], zoom_start=st.session_state["zoom"])
fg = folium.FeatureGroup(name="Markers")

for marker in st.session_state["markers"]:
    fg.add_child(marker)

st_folium(
    m,
    center=st.session_state["center"],
    zoom=st.session_state["zoom"],
    key="nsw_random",
    feature_group_to_add=fg,
    height=600,
    width=800,
)