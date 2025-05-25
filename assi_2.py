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

# -- CONFIG --
BROKER = "test.mosquitto.org"
TOPIC = "streamlit/demo/data"
CENTER_START = [-33.8688, 151.2093]  # Sydney center

# -- SESSION STATE SETUP --
if "markers" not in st.session_state:
    st.session_state["markers"] = []

if "center" not in st.session_state:
    st.session_state["center"] = CENTER_START

if "zoom" not in st.session_state:
    st.session_state["zoom"] = 10

if "marker_queue" not in st.session_state:
    st.session_state["marker_queue"] = queue.Queue()

if "mqtt_started" not in st.session_state:
    st.session_state["mqtt_started"] = False

# -- PULL FROM QUEUE INTO SESSION STATE --
while not st.session_state["marker_queue"].empty():
    marker = st.session_state["marker_queue"].get()
    st.session_state["markers"].append(marker)

# -- MQTT CALLBACK --
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        lat = payload.get("lat")
        lon = payload.get("lon")
        brand = payload.get("brand")
        number = payload.get("94")

        if lat is not None and lon is not None:
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
                popup=f"{brand} #{number}"
            )
            # SAFELY ADD TO QUEUE
            userdata["queue"].put(marker)

    except Exception as e:
        print("MQTT error:", e)

# -- MQTT THREAD --
def mqtt_thread(marker_queue):
    client = mqtt.Client(userdata={"queue": marker_queue})
    client.on_message = on_message
    client.connect(BROKER, 1883, 60)
    client.subscribe(TOPIC)
    client.loop_forever()

# -- START THREAD ONCE --
if not st.session_state["mqtt_started"]:
    threading.Thread(target=mqtt_thread, args=(st.session_state["marker_queue"],), daemon=True).start()
    st.session_state["mqtt_started"] = True

# -- AUTORERUN TO SHOW NEW MARKERS --
st_autorefresh(interval=3000, key="autorefresh")

# -- DROPDOWN (NOT FILTERING IN THIS DEMO) --
markets = ["92", "94", "97"]
st.selectbox("Fuel", markets, index=0)

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
    width=800,
)

# Debugging
st.write(f"Markers shown: {len(st.session_state['markers'])}")