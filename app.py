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
@st.cache_data(experimental_allow_widgets=True)  # 👈 Set the parameter
def get_data():
    
    df_raw = pd.read_csv("eartquakes_italy.csv")
    values_magnitudo = st.slider(
    'Magnitudo',
    0.0, 6.2, (2.0, 5.0))
    
    values_deepness = st.slider(
    'Deepness',
    0.0, 6.2, (2.0, 5.0))
    
    magnitudo_mask = ((df_raw["magnitudo_score"]>=values_magnitudo[0]) & (df_raw["magnitudo_score"]<=values_magnitudo[1]))
    deepness_mask = ((df_raw["Profondità"]>=values_deepness[0]) & (df_raw["Profondità"]<=values_deepness[1]))
    
    filtered_data = data[magnitudo_mask & deepness_mask]
    
    return filtered_data

# data = get_data()
# values = st.slider(
#     'Select a range of values',
#     0.0, 6.2, (2.0, 5.0))
# st.write('Values:', values)
# magnitudo_mask = ((data["magnitudo_score"]>=values[0]) & (data["magnitudo_score"]<=values[1]))
# filtered_data = data[magnitudo_mask]

st.dataframe(data=get_data(), use_container_width=True)



