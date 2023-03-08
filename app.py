import streamlit as st
from streamlit_option_menu import option_menu

import folium
from folium.plugins import Fullscreen,HeatMapWithTime,MiniMap,HeatMap
from streamlit_folium import st_folium,folium_static 

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

import datetime
from datetime import date,datetime

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
            
        </style>
    ''',
    unsafe_allow_html=True
)



#---FUNCTIONS---
@st.cache_data(experimental_allow_widgets=True)  # 👈 Set the parameter
def get_data():
    try:
        df = pd.DataFrame()
        number = st.sidebar.number_input('**Download the number of years**',min_value=1, max_value=15, value=2,label_visibility="visible")

        for i in range(int(number)):
            
            a = (date.today().year-i)
            b = a - 1

            df_raw = pd.read_csv(f"https://webservices.ingv.it/fdsnws/event/1/query?starttime={str(date(b, date.today().month, date.today().day))}T00%3A00%3A00&endtime={str(date(a,  date.today().month,  date.today().day))}T23%3A59%3A59&minmag=2&maxmag=10&mindepth=-10&maxdepth=1000&minlat=35&maxlat=49&minlon=5&maxlon=20&minversion=100&orderby=time-asc&format=text&limit=10000",
                                    sep="|")[['Time', 'Latitude', 'Longitude', 'Depth/Km', 'Magnitude']]

            df = pd.concat([df, df_raw], axis=0)
            
        df = df.drop_duplicates()
        df["Time"] = df["Time"].str.split("T",expand=True)[0]
        df["Magnitude"] = df["Magnitude"].astype("float")
        df["Depth/Km"] = df["Depth/Km"].astype("int")
        
        df_municipalities = gpd.read_file('https://raw.githubusercontent.com/openpolis/geojson-italy/master/geojson/limits_IT_municipalities.geojson')
        df_municipalities = df_municipalities[['name','prov_name','reg_name','geometry']].rename(columns={'name':'mun_name'})
        
        #zip the coordinates into a point object and convert to a GeoData Frame
        geometry = [Point(xy) for xy in zip(df.Longitude, df.Latitude,)]
        geo_df = gpd.GeoDataFrame(df, geometry=geometry,crs="EPSG:4326")

        pointInPoly_municipalities = gpd.sjoin(geo_df, df_municipalities, op='within').reset_index(drop=True).drop_duplicates()

        return  pointInPoly_municipalities[['Time', 'Latitude', 'Longitude', 'Depth/Km', 'Magnitude','mun_name','prov_name','reg_name']]
    
    except:
        st.error('Date input error', icon="🚨")
        st.stop()


with st.container():
    df = get_data()    
    today = date.today()
    years10  =date(today.year - 5, today.month, today.day)
    starttime = st.sidebar.date_input("**Start time**", value=date(date.today().year, date.today().month, date.today().day-1), 
                                      min_value=datetime.strptime(df.Time.min(),'%Y-%m-%d'), 
                                      max_value=date.today(), label_visibility="visible")
    endtime = st.sidebar.date_input("**End time**", value=None, 
                                    min_value=datetime.strptime(df.Time.min(),'%Y-%m-%d'), 
                                    max_value=date.today(), label_visibility="visible")

    values_magnitude = st.sidebar.slider('**Magnitude**',int(df.Magnitude.min()), int(df.Magnitude.max()), (int(df.Magnitude.min()), int(df.Magnitude.max())))
    values_deepness = st.sidebar.slider('**Depth/Km**',int(df["Depth/Km"].min()), int(df["Depth/Km"].max()), (int(df["Depth/Km"].min()), int(df["Depth/Km"].max())))    
    
    
    time_mask = ((df['Time'] >= str(starttime) ) & (df['Time'] <= str(endtime)))
    magnitudo_mask = ((df["Magnitude"]>=values_magnitude[0]) & (df["Magnitude"]<=values_magnitude[1]))
    deepness_mask = ((df["Depth/Km"]>=values_deepness[0]) & (df["Depth/Km"]<=values_deepness[1]))
    filtered_data = df[magnitudo_mask & deepness_mask & time_mask]

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

        with st.expander("**Map** 🌍", expanded=True):
            tab1, tab2, tab3 = st.tabs(["*Points*", "*Heatmap*", "*Timelapse heatmap*"])

            tab1.pydeck_chart(pdk.Deck(
                map_provider="mapbox", 
                map_style="road",
                tooltip=tooltip,
                initial_view_state=pdk.ViewState(
                    latitude=41.902782, 
                    longitude=12.496366,
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
            
            #---HEATMAP---
            m_1 = folium.Map(location=[41.902782, 12.496366],
                            zoom_start=5)
                
            heat_data = [[row['Latitude'],row['Longitude']] for index, row in filtered_data.iterrows()]
            HeatMap(heat_data,radius=8, blur=10).add_to(m_1)
           

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
                            min_speed=2,
                            max_speed =5,
                            speed_step=1,
                            position='bottomright',
                            display_index=True
                            ).add_to(m)
            
           

            #fullscreen
            folium.plugins.Fullscreen(position='topleft', title='Full Screen', title_cancel='Exit Full Screen', force_separate_button=True,).add_to(m)
            
            with tab2:
                folium_static(m_1)
            with tab3:
                folium_static(m)
