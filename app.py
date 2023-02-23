import streamlit as st
from streamlit_option_menu import option_menu

import folium
from folium.plugins import Fullscreen,HeatMapWithTime,MiniMap
from streamlit_folium import st_folium

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

import datetime
from datetime import date

import altair as alt

import pydeck as pdk

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
    try:
        starttime = st.date_input("Start time", value=datetime.date(2022, 7, 6), min_value=None, max_value=None, key=None, help=None, on_change=None, args=None, kwargs=None, disabled=False, label_visibility="visible")
        endtime = st.date_input("End time", value=None, min_value=None, max_value=None, key=None, help=None, on_change=None, args=None, kwargs=None, disabled=False, label_visibility="visible")
        df_raw = pd.read_csv(f"https://webservices.ingv.it/fdsnws/event/1/query?starttime={str(starttime)}T00%3A00%3A00&{str(endtime)}=2023-02-23T23%3A59%3A59&minmag=2&maxmag=10&mindepth=-10&maxdepth=1000&minlat=35&maxlat=49&minlon=5&maxlon=20&minversion=100&orderby=time-asc&format=text&limit=10000",
                            sep="|")[['Time', 'Latitude', 'Longitude', 'Depth/Km', 'Magnitude']]
        df_raw["Time"] = df_raw["Time"].str.split("T",expand=True)[0]
        df_raw["Magnitude"] = df_raw["Magnitude"].astype("float")
        df_raw["Depth/Km"] = df_raw["Depth/Km"].astype("int")
        
        df_municipalities = gpd.read_file('https://raw.githubusercontent.com/openpolis/geojson-italy/master/geojson/limits_IT_municipalities.geojson')
        df_municipalities = df_municipalities[['name','prov_name','reg_name','geometry']].rename(columns={'name':'mun_name'})
        
        #zip the coordinates into a point object and convert to a GeoData Frame
        geometry = [Point(xy) for xy in zip(df_raw.Longitude, df_raw.Latitude,)]
        geo_df = gpd.GeoDataFrame(df_raw, geometry=geometry,crs="EPSG:4326")

        pointInPoly_municipalities = gpd.sjoin(geo_df, df_municipalities, op='within').reset_index(drop=True).drop_duplicates()

        return  pointInPoly_municipalities[['Time', 'Latitude', 'Longitude', 'Depth/Km', 'Magnitude','mun_name','prov_name','reg_name']]
    except:
        st.error('Date input error', icon="🚨")
        st.stop()
        
# st.dataframe(get_data())

left,  center, right = st.columns([2,3,3], gap="large")

with left: 
    df = get_data()
    
with right:

    values_magnitude = st.slider('Magnitude',int(df.Magnitude.min()), int(df.Magnitude.max()), (int(df.Magnitude.min()), int(df.Magnitude.max())))
    
with center:
    values_deepness = st.slider('Depth/Km',int(df["Depth/Km"].min()), int(df["Depth/Km"].max()), (int(df["Depth/Km"].min()), int(df["Depth/Km"].max())))    

    magnitudo_mask = ((df["Magnitude"]>=values_magnitude[0]) & (df["Magnitude"]<=values_magnitude[1]))
    deepness_mask = ((df["Depth/Km"]>=values_deepness[0]) & (df["Depth/Km"]<=values_deepness[1]))

    filtered_data = df[magnitudo_mask & deepness_mask]
    
left_2,  right_2 = st.columns([2,3], gap="large")

with left_2:
    
    source = filtered_data.groupby("reg_name",as_index=False).size()
    chart = alt.Chart(source).mark_bar().encode(
        x=alt.X('size:Q', axis=None),
        y=alt.Y('reg_name:N', sort='-x', axis=None)
    )

    st.altair_chart(chart, use_container_width=True, theme="streamlit")
    
# with center: 
    
        
    

with right_2:
    try:
        tooltip = {
           "html": "<b>Region:</b> {reg_name} <br /><b>Province:</b> {prov_name} <br /><b>Municipality:</b> {mun_name} <br /><b>Date:</b> {Time} <br /><b>Magnitude:</b> {Magnitude} <br /><b>Depth:</b> {Depth/Km} Km",
           "style": {
                "backgroundColor": "steelblue",
                "color": "white"
           }
        }
        st.pydeck_chart(pdk.Deck(
            map_provider="mapbox", 
            map_style=pdk.map_styles.SATELLITE,
            tooltip=tooltip,
            initial_view_state=pdk.ViewState(
                latitude=filtered_data["Latitude"].mean(),
                longitude=filtered_data["Longitude"].mean(),
                zoom=4,
                pitch=50,
            ),
            layers=[
                pdk.Layer(
                    "ScatterplotLayer",
                    data=filtered_data,
                    pickable=True,
                    opacity=0.3,
                    stroked=True,
                    filled=True,
                    radius_scale=10,
                    radius_min_pixels=10,
                    radius_max_pixels=100,
                    line_width_min_pixels=1,
                    get_position='[Longitude, Latitude]',
                    get_radius="Magnitude",
                    get_fill_color=[255, 140, 0],
                    get_line_color=[0, 0, 0],

                )
            ],
        ))
        
        
    except:
        st.error('No data', icon="🚨")
        st.stop()
        

