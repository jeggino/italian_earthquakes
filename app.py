import streamlit as st
from streamlit_option_menu import option_menu

import folium
from folium.plugins import Draw, Fullscreen, LocateControl
from streamlit_folium import st_folium

import pandas as pd
import geopandas as gpd
import datetime
from datetime import date

st.set_page_config(
    page_title="Italian Earthquakes",
    page_icon="🌍",
    layout="wide",
    
)

st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)

#---FUNCTIONS---
@st.cache_data()  # 👈 Set the parameter
def get_data():
    df_raw = pd.read_csv("eartquakes_italy.csv")
    return df_raw

data = get_data()
values = st.slider(
    'Select a range of values',
    0.0, 6.2, (2.0, 5.0))
st.write('Values:', values)
magnitudo_mask = ((data["magnitudo_score"]>=values[0]) & (data["magnitudo_score"]<=values[1]))
filtered_data = data[magnitudo_mask]

st.dataframe(data=filtered_data, use_container_width=True)



