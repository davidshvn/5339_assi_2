import streamlit as st
import pandas as pd

# Sample data: 3 locations
data = pd.DataFrame({
    'lat': [37.7749, 34.0522, 40.7128],
    'lon': [-122.4194, -118.2437, -74.0060]
})

# Show the map
st.title("📍 Basic Map in Streamlit")
st.map(data)