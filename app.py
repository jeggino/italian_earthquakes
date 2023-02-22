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
    0, 644, (0, 644))
    
    magnitudo_mask = ((df_raw["magnitudo_score"]>=values_magnitudo[0]) & (df_raw["magnitudo_score"]<=values_magnitudo[1]))
    deepness_mask = ((df_raw["Profondità"]>=values_deepness[0]) & (df_raw["Profondità"]<=values_deepness[1]))
    
    filtered_data = df_raw[magnitudo_mask & deepness_mask]
    
    return filtered_data

@st.cache_data() 
def get_heatmap():
    df_raw = pd.read_csv('earthquakes Italy 1985-2020.csv')
    df_raw['Data e Ora (ITItalia)'] = df_raw['Data e Ora (ITItalia)'].replace({'\xa0':' '}, regex=True)
    form = "%Y-%m-%d %H:%M:%S"
    df_raw['date_time'] = pd.to_datetime(df_raw['Data e Ora (ITItalia)'], format=form)
    df_raw['magnitudo_score']=df_raw['Magnitudo'].str.split('\xa0',expand=True)[1].astype(float)
    df_raw = df_raw.drop(['Data e Ora (ITItalia)','Magnitudo','Zona'],axis=1)
    df_municipalities = gpd.read_file('https://raw.githubusercontent.com/openpolis/geojson-italy/master/geojson/limits_IT_municipalities.geojson')
    df_municipalities = df_municipalities[['name','prov_name','reg_name','geometry']].rename(columns={'name':'mun_name'})
    geometry = [Point(xy) for xy in zip(df_raw.Longitudine, df_raw.Latitudine,)]
    geo_df = gpd.GeoDataFrame(df_raw, geometry=geometry,crs="EPSG:4326")

    pointInPoly_municipalities = gpd.sjoin(geo_df, df_municipalities, op='within').reset_index(drop=True).drop_duplicates()
    pointInPoly_municipalities['date'] = pointInPoly_municipalities['date_time'].dt.date
    df_HeatMap = pointInPoly_municipalities[['date', 'Latitudine', 'Longitudine']].sort_values('date').reset_index(drop=True)
    df_HeatMap['date'] = df_HeatMap['date'].astype(str)
    lat_long_list = []
    for i in df_HeatMap.date.unique():
        temp=[]
        for index, instance in df_HeatMap[df_HeatMap['date'] == i].iterrows():
            temp.append([instance['Latitudine'],instance['Longitudine']])
        lat_long_list.append(temp)
        
    # create a map
    centroid = df_municipalities.centroid


    m = folium.Map(location=[centroid.y.mean(), centroid.x.mean()], zoom_start=6,  
                   tiles='cartodbdark_matter',
                   attr='&copy'
                  )

    # define map dimensions
    fig=Figure(width=700,height=700)
    fig.add_child(m)

    HeatMapWithTime(lat_long_list,
                    index=df_HeatMap.date.unique().tolist(),
                    name='heatmap',
                    overlay=False,
                    radius=15,
                    auto_play=True,
                    speed_step=1,
                    position='bottomright',
                    display_index=True
    ).add_to(m)

    #fullscreen
    folium.plugins.Fullscreen(position='topleft', title='Full Screen', title_cancel='Exit Full Screen', force_separate_button=True,).add_to(m)

    return m



st.dataframe(data=get_data(), use_container_width=True)

st_folium(get_heatmap())



