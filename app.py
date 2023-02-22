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
    st.slider('How old are you?', 0, 130, 25)
#     magnitudo = st.slider(label="Magnitudo", min_value=0, max_value=6.2, value =(2.0, 5.0))
#     mask_magnitudo = (df_raw['magnitudo_score'] >= magnitudo[0]) & (df_raw['magnitudo_score'] <= magnitudo[1])
#     data = df_raw[mask_magnitudo]
    return df_raw

st.dataframe(data=get_data(), use_container_width=True)
df_raw = pd.read_csv("eartquakes_italy.csv")
st.write(df_raw.info())


