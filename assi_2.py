import streamlit as st
import folium
from streamlit_folium import st_folium
import random
import time
import json
import threading
import queue
import paho.mqtt.client as mqtt
from streamlit_autorefresh import st_autorefresh
from streamlit.components.v1 import html

st.set_page_config(layout="wide")

# -- CONFIG --
BROKER = "test.mosquitto.org"
TOPIC = "streamlit/demo/data"
CENTER_START = [-33.8688, 151.2093]  # Sydney center

market_data = {
    "92": 178,
    "94": 182,
    "97": 191
}

brands = {
    "shell": "https://upload.wikimedia.org/wikipedia/en/thumb/e/e8/Shell_logo.svg/150px-Shell_logo.svg.png",
    "711": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/40/7-eleven_logo.svg/272px-7-eleven_logo.svg.png",
    "coles": "https://upload.wikimedia.org/wikipedia/en/thumb/4/4e/Ampol_Logo_May_2020.svg/109px-Ampol_Logo_May_2020.svg.png"
}

# Track selected market in a global variable
if "selected_market" not in st.session_state:
    st.session_state["selected_market"] = "92"

# UI dropdown to select market
selected_market = st.selectbox("Fuel", list(market_data.keys()), index=0)
#st.session_state["selected_market"] = selected_market

if selected_market != st.session_state["selected_market"]:
    st.session_state["selected_market"] = selected_market
    st.session_state["markers"] = []

# -- SESSION STATE SETUP --
if "markers" not in st.session_state:
    st.session_state["markers"] = []

if "center" not in st.session_state:
    st.session_state["center"] = CENTER_START

if "zoom" not in st.session_state:
    st.session_state["zoom"] = 10

#if "marker_queue" not in st.session_state:
#    st.session_state["marker_queue"] = queue.Queue()

# if "mqtt_started" not in st.session_state:
#     st.session_state["mqtt_started"] = False

# -- PULL FROM QUEUE INTO SESSION STATE --
# while not st.session_state["marker_queue"].empty():
#     marker = st.session_state["marker_queue"].get()
#     st.session_state["markers"].append(marker)

# -- MQTT CALLBACK --
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        lat = payload.get("lat")
        lon = payload.get("lon")
        brand = payload.get("brand")

        prices = {}
        prices["92"] = payload.get("92")
        prices["94"] = payload.get("94")
        prices["97"] = payload.get("97")

        fuel_type = st.session_state.get("selected_market", "92")
        number = prices[fuel_type]

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
            popup_html = f"""
                <div>
                    <table style="border-collapse: collapse; width: 80px;">
                        <tr>
                            <td style="padding: 4px;"><b>92</b></td>
                            <td style="padding: 4px;">{prices["92"]}</td>
                        </tr>
                        <tr>
                            <td style="padding: 4px;"><b>94</b></td>
                            <td style="padding: 4px;">{prices["94"]}</td>
                        </tr>
                        <tr>
                            <td style="padding: 4px;"><b>97</b></td>
                            <td style="padding: 4px;">{prices["97"]}</td>
                        </tr>
                    </table>
                </div>
            """
            popup = folium.Popup(popup_html, max_width=100)

            marker = folium.Marker(
                location=[lat, lon],
                icon=folium.DivIcon(
                    icon_size=(40, 40),
                    icon_anchor=(20, 20),
                    html=html
                ),
                popup=popup
            )
            # SAFELY ADD TO QUEUE
            #userdata["queue"].put(marker)
            st.session_state["markers"].append(marker)

    except Exception as e:
        print("MQTT error:", e)



# -- START THREAD ONCE --
#if not st.session_state["mqtt_started"]:
#    threading.Thread(target=mqtt_thread, args=(st.session_state["marker_queue"],), daemon=True).start()
#    st.session_state["mqtt_started"] = True

# -- AUTORERUN TO SHOW NEW MARKERS --
st_autorefresh(interval=10000, key="autorefresh")

# -- DRAW MAP --
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
    #use_container_width=True,
)

# Debugging
st.write(f"Markers shown: {len(st.session_state['markers'])}")

# -- MQTT THREAD --
#def mqtt_thread(marker_queue):
#client = mqtt.Client(userdata={"queue": marker_queue})
#client = mqtt.Client(userdata={"queue": st.session_state["marker_queue"]})
client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER, 1883, 60)
client.subscribe(TOPIC)
client.loop_forever()