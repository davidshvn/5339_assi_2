import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import paho.mqtt.client as mqtt
from streamlit_autorefresh import st_autorefresh
from streamlit.components.v1 import html

st.set_page_config(layout="wide")

# config
BROKER = "test.mosquitto.org"
TOPIC = "streamlit/demo/data"
CENTER_START = [-33.8688, 151.2093]  # Sydney center

market_data = ["92", "94", "97"]

brands = {
    "shell": "https://upload.wikimedia.org/wikipedia/en/thumb/e/e8/Shell_logo.svg/150px-Shell_logo.svg.png",
    "711": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/40/7-eleven_logo.svg/272px-7-eleven_logo.svg.png",
    "coles": "https://upload.wikimedia.org/wikipedia/en/thumb/4/4e/Ampol_Logo_May_2020.svg/109px-Ampol_Logo_May_2020.svg.png"
}

# track selected market in a global variable
if "selected_market" not in st.session_state:
    st.session_state["selected_market"] = "92"

# ui dropdown to select market
selected_market = st.selectbox("Fuel", market_data, index=0)

if selected_market != st.session_state["selected_market"]:
    st.session_state["selected_market"] = selected_market
    st.session_state["markers"] = []

if "markers" not in st.session_state:
    st.session_state["markers"] = []

if "center" not in st.session_state:
    st.session_state["center"] = CENTER_START

if "zoom" not in st.session_state:
    st.session_state["zoom"] = 9

# mqtt callback
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        lat = payload.get("lat")
        lon = payload.get("lon")
        brand = payload.get("brand")
        prices = payload.get("prices")

        fuel_type = st.session_state.get("selected_market", "92")
        number = next((d["price"] for d in prices if d["fuel"] == fuel_type), None)

        if lat is not None and lon is not None:
            image_url = brands[brand]
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
            rows = """
                <tr>
                    <td style="padding: 4px;"><b>Fuel</b></td>
                    <td style="padding: 4px;"><b>Price</b></td>
                    <td style="padding: 4px;"><b>Last updated</b></td>
                </tr>
            """

            for p in prices:
                rows += f"""
                    <tr>
                        <td style="padding: 4px;"><b>{p.get("fuel")}</b></td>
                        <td style="padding: 4px;">{p.get("price")}</td>
                        <td style="padding: 4px;">{p.get("update_time")}</td>
                    </tr>
                """

            popup_html = f"""
                <div style="display: inline-block; padding: 4px;">
                    <table style="border-collapse: collapse;">
                        {rows}
                    </table>
                </div>
            """
            popup = folium.Popup(popup_html, max_width=None)

            marker = folium.Marker(
                location=[lat, lon],
                icon=folium.DivIcon(
                    icon_size=(40, 40),
                    icon_anchor=(20, 20),
                    html=html
                ),
                popup=popup
            )
            st.session_state["markers"].append(marker)

    except Exception as e:
        print("MQTT error:", e)


st_autorefresh(interval=10000, key="autorefresh")

m = folium.Map(location=st.session_state["center"], zoom_start=st.session_state["zoom"])
fg = folium.FeatureGroup(name="Markers")
for marker in st.session_state["markers"]:
    fg.add_child(marker)

st_folium(
    m,
    center=st.session_state["center"],
    zoom=st.session_state["zoom"],
    key="nsw_map",
    feature_group_to_add=fg,
    height=600,
    width=1200,
)

# Debugging
st.write(f"Markers shown: {len(st.session_state['markers'])}")

# suscribing
client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER, 1883, 60)
client.subscribe(TOPIC)
client.loop_forever()