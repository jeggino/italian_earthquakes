import streamlit as st
from streamlit_option_menu import option_menu

import folium
from folium.plugins import Fullscreen,HeatMapWithTime,MiniMap
from streamlit_folium import st_folium,folium_static 

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

# st.markdown(""" <style>
# #MainMenu {visibility: hidden;}
# footer {visibility: hidden;}
# </style> """, unsafe_allow_html=True)

st.markdown(
    '''
        <style>
            .sidebar .sidebar-content {
                width: 5px;
            }
            footer {visibility: hidden;}
            #MainMenu {visibility: hidden;}
        </style>
    ''',
    unsafe_allow_html=True
)

#---FUNCTIONS---
@st.cache_data(experimental_allow_widgets=True)  # 👈 Set the parameter
def get_data():
    try:
        starttime = st.sidebar.date_input("**Start time**", value=datetime.date(2022, 7, 6), min_value=None, max_value=None, key=None, help=None, on_change=None, args=None, kwargs=None, disabled=False, label_visibility="visible")
        endtime = st.sidebar.date_input("**End time**", value=None, min_value=None, max_value=None, key=None, help=None, on_change=None, args=None, kwargs=None, disabled=False, label_visibility="visible")
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

# st.markdown("""
#     <style>
#         .stApp {
#         background: url("https://th.bing.com/th/id/R.e6b3036960aca7aa74463f3248445d4e?rik=Pa126za3CImpJQ&riu=http%3a%2f%2fgetwallpapers.com%2fwallpaper%2ffull%2f6%2f3%2fa%2f830914-earthquake-wallpapers-2197x1463-lockscreen.jpg&ehk=3qQRMr6YFUK1a%2fPHP6A6Rg0mc5y5Sm2PuIujOANK40I%3d&risl=&pid=ImgRaw&r=0");
#         background-size: cover;
#         }
#     </style>""", unsafe_allow_html=True)



df = get_data()
left_1,  right_2 = st.columns([2,2], gap="medium")

values_magnitude = st.sidebar.slider('**Magnitude**',int(df.Magnitude.min()), int(df.Magnitude.max()), (int(df.Magnitude.min()), int(df.Magnitude.max())))
values_deepness = st.sidebar.slider('**Depth/Km**',int(df["Depth/Km"].min()), int(df["Depth/Km"].max()), (int(df["Depth/Km"].min()), int(df["Depth/Km"].max())))    


magnitudo_mask = ((df["Magnitude"]>=values_magnitude[0]) & (df["Magnitude"]<=values_magnitude[1]))
deepness_mask = ((df["Depth/Km"]>=values_deepness[0]) & (df["Depth/Km"]<=values_deepness[1]))
filtered_data = df[magnitudo_mask & deepness_mask]

left,  right = st.columns([2,2], gap="medium")

with left:
    source_1 = filtered_data.groupby("reg_name",as_index=False).size()
    chart_1 = alt.Chart(source_1).mark_bar().encode(
        x=alt.X('size:Q', title="Number of earthquakes"),
        y=alt.Y('reg_name:N', sort='-x', title="Region")
    )
    
    source_2 = filtered_data.groupby("prov_name",as_index=False).size().sort_values("size",ascending=False).reset_index(drop=True)[:20]
    chart_2 = alt.Chart(source_2).mark_bar().encode(
        x=alt.X('size:Q', title="Number of earthquakes"),
        y=alt.Y('prov_name:N', sort='-x', title="Provinces")
    )
    
    sourc_3 = filtered_data.groupby("mun_name",as_index=False).size().sort_values("size",ascending=False).reset_index(drop=True)[:20]
    chart_3 = alt.Chart(sourc_3).mark_bar().encode(
        x=alt.X('size:Q', title="Number of earthquakes"),
        y=alt.Y('mun_name:N', sort='-x', title="Municipalities")
    )
    
    with st.expander("**Charts** 📊", expanded=True):
        tab1, tab2, tab3 = st.tabs(["*Regions*", "*Provinces*", "*Municipalities*"])

        tab1.altair_chart(chart_1, use_container_width=True, theme=None)
        tab2.altair_chart(chart_2, use_container_width=True, theme=None)
        tab2.caption('This is a string that explains something above.')
        tab3.altair_chart(chart_3, use_container_width=True, theme=None)
        tab3.caption('This is a string that explains something above.')
    

with right:
        
    tooltip = {
       "html": """
       <b>Region:</b> {reg_name} <br />
        <b>Province:</b> {prov_name} <br />
        <b>Municipality:</b> {mun_name} <br />
        <b>Date:</b> {Time} <br />
        <b>Magnitude:</b> {Magnitude} <br />
        <b>Depth:</b> {Depth/Km} Km
        """,
       "style": {
            "backgroundColor": "steelblue",
            "color": "white"
       }
    }
    
    with st.expander("**Map** 🗺", expanded=True):
        tab1, tab2, tab3 = st.tabs(["*Points*", "*Heatmap*", "*Timelapse heatmap*"])

        tab1.pydeck_chart(pdk.Deck(
            map_provider="mapbox", 
            map_style="road",
            tooltip=tooltip,
            initial_view_state=pdk.ViewState(
                latitude=filtered_data["Latitude"].mean(),
                longitude=filtered_data["Latitude"].mean(),
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
        ), use_container_width=True)

        tab2.pydeck_chart(pdk.Deck(
            map_provider="mapbox", 
            map_style=pdk.map_styles.SATELLITE,
            initial_view_state=pdk.ViewState(
                latitude=filtered_data["Latitude"].mean(),
                longitude=filtered_data["Longitude"].mean(),
                zoom=3,
                pitch=0,
            ),
            layers=[
                pdk.Layer(
                    "HeatmapLayer",
                    data=filtered_data,
                    opacity=1,
                    threshold=1,
                    get_position='[Longitude, Latitude]',
                    pickable=True,
                )
            ],
        ), use_container_width=True)
    
        #---TIMELAPSE---
        df_HeatMap = filtered_data[['Time', 'Latitude', 'Longitude']].sort_values('Time').reset_index(drop=True)
        df_HeatMap['Time'] = df_HeatMap['Time'].astype(str)

        lat_long_list = []
        for i in df_HeatMap.Time.unique():
            temp=[]
            for index, instance in df_HeatMap[df_HeatMap['Time'] == i].iterrows():
                temp.append([instance['Latitude'],instance['Longitude']])
            lat_long_list.append(temp)

        m = folium.Map(location=[41.902782, 12.496366],
                       zoom_start=5)


        HeatMapWithTime(lat_long_list,
                        index=df_HeatMap.Time.unique().tolist(),
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
        
        with tab3:
            folium_static(m)
    
    
                             
                             

        
