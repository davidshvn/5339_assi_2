import streamlit as st
import folium
from streamlit_folium import st_folium
import random
import json
import threading
import paho.mqtt.client as mqtt
from streamlit_autorefresh import st_autorefresh

# NSW center (Sydney)
CENTER_START = [-33.8688, 151.2093]

# Initialize session state
import queue

if "marker_queue" not in st.session_state:
    st.session_state["marker_queue"] = queue.Queue()

if "markers" not in st.session_state:
    st.session_state["markers"] = []

if "center" not in st.session_state:
    st.session_state["center"] = CENTER_START

if "zoom" not in st.session_state:
    st.session_state["zoom"] = 10

if "mqtt_started" not in st.session_state:
    st.session_state["mqtt_started"] = False

# Dropdown
markets = ["92", "94", "97"]
selected_market = st.selectbox("Fuel", markets, index=0)

# MQTT Setup
BROKER = "test.mosquitto.org"
TOPIC = "streamlit/demo/data"

# MQTT callback
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        lat = payload.get("lat")
        lon = payload.get("lon")
        brand = payload.get("brand", "Brand")
        number = payload.get(selected_market, "?")  # Use the selected market

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
            #st.session_state["markers"].append(marker)
            st.session_state["marker_queue"].put(marker)

    except Exception as e:
        print("MQTT Error:", e)

# Start MQTT thread once
#if not st.session_state["mqtt_started"]:
#    threading.Thread(target=mqtt_thread, daemon=True).start()
st.session_state["mqtt_started"] = True


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

st.write(f"Markers shown: {len(st.session_state['markers'])}")

# Refresh every 2000ms (2 seconds)
st_autorefresh(interval=2000, key="datarefresh")

# Transfer new markers from the queue to the session state
while not st.session_state["marker_queue"].empty():
    st.session_state["markers"].append(st.session_state["marker_queue"].get())

# MQTT background thread
#def mqtt_thread():
client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER, 1883, 60)
client.subscribe(TOPIC)
client.loop_forever()