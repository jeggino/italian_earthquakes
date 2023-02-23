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
    
    df_raw = pd.read_csv("https://webservices.ingv.it/fdsnws/event/1/query?starttime=2020-02-16T00%3A00%3A00&endtime=2023-02-23T23%3A59%3A59&minmag=2&maxmag=10&mindepth=-10&maxdepth=1000&minlat=35&maxlat=49&minlon=5&maxlon=20&minversion=100&orderby=time-asc&format=text&limit=10000",
                        sep="|")[['Time', 'Latitude', 'Longitude', 'Depth/Km', 'Magnitude']]
    df_raw["Time"] = df_raw["Time"].str.split("T",expand=True)[0]
    df_raw["Magnitude"] = df_raw["Magnitude"].astype("float")
    df_raw["Depth/Km"] = df_raw["Depth/Km"].astype("int")
    
    return  df_raw 

left, right = st.columns([1,3],gap="large")

with left: 
    df = get_data()

    values_magnitude = st.slider('Magnitude',float(df.Magnitude.min()), float(df.Magnitude.max()), (float(df.Magnitude.min()), float(df.Magnitude.max())))
    values_deepness = st.slider('Depth/Km',int(df["Depth/Km"].min()), int(df["Depth/Km"].max()), (int(df["Depth/Km"].min()), int(df["Depth/Km"].max())))

    magnitudo_mask = ((df["Magnitude"]>=values_magnitude[0]) & (df["Magnitude"]<=values_magnitude[1]))
    deepness_mask = ((df["Depth/Km"]>=values_deepness[0]) & (df["Depth/Km"]<=values_deepness[1]))

    filtered_data = df[magnitudo_mask & deepness_mask]

with right:
    st.pydeck_chart(pdk.Deck(
        map_style=None,
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

# @st.cache_data() 
# def get_municipalities():
#     df_municipalities = gpd.read_file('https://raw.githubusercontent.com/openpolis/geojson-italy/master/geojson/limits_IT_municipalities.geojson')
#     df_municipalities = df_municipalities[['name','prov_name','reg_name','geometry']].rename(columns={'name':'mun_name'})
#     return df_municipalities

# @st.cache_data() 
# def get_dataset_2():
#     df_raw = pd.read_csv('Italian_Catalogue.csv')
#     form = "%Y-%m-%d %H:%M:%S"
#     df_raw['Time'] = pd.to_datetime(df_raw['Time'], format=form)
#     geometry = [Point(xy) for xy in zip(df_raw.Longitude, df_raw.Latitude)]
#     geo_df = gpd.GeoDataFrame(df_raw, geometry=geometry,crs="EPSG:4326")
    
#     return geo_df
    

# @st.cache_data() 
# def get_pointInPoly_municipalities():
#     pointInPoly_municipalities = gpd.sjoin(get_dataset_2(), get_municipalities(), op='within').reset_index(drop=True).drop_duplicates()
#     pointInPoly_municipalities['date'] = pointInPoly_municipalities['Time'].dt.date
#     return pointInPoly_municipalities
    
# @st.cache_data() 
# def get_heatmap():    
    
#     df_HeatMap = get_pointInPoly_municipalities()[['date', 'Latitude', 'Longitude']].sort_values('date').reset_index(drop=True)
#     df_HeatMap['date'] = df_HeatMap['date'].astype(str)
#     lat_long_list = []
#     for i in df_HeatMap.date.unique():
#         temp=[]
#         for index, instance in df_HeatMap[df_HeatMap['date'] == i].iterrows():
#             temp.append([instance['Latitude'],instance['Longitude']])
#         lat_long_list.append(temp)
        
#     # create a map
#     centroid = get_municipalities().centroid


#     m = folium.Map(location=[centroid.y.mean(), centroid.x.mean()], zoom_start=6,  
#                    tiles='cartodbdark_matter',
#                    attr='&copy'
#                   )



#     HeatMapWithTime(lat_long_list,
#                     index=df_HeatMap.date.unique().tolist(),
#                     name='heatmap',
#                     overlay=False,
#                     radius=15,
#                     auto_play=True,
#                     speed_step=1,
#                     position='bottomright',
#                     display_index=True
#     ).add_to(m)

#     #fullscreen
#     folium.plugins.Fullscreen(position='topleft', title='Full Screen', title_cancel='Exit Full Screen', force_separate_button=True,).add_to(m)

#     return m



# st.dataframe(data=get_data(), use_container_width=True)
# st.dataframe(data=get_pointInPoly_municipalities(), use_container_width=True)
# st_folium(get_heatmap())



