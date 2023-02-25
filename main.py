import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np
import hydralit_components as hc
import snowflake.connector as sf
import random
import string
import leafmap.foliumap as leafmap


session=None

metrics=['Mobile Data Usage Per Mobile Broadband Subscription, Gb Per Month',
        'Fixed Broadband - All Subscriptions Per 100 Inhabitants',
        'Fixed Broadband - Fibre/Lan Subscriptions Per 100 Inhabitants',
        'Fixed Broadband - Cable Subscriptions Per 100 Inhabitants',
        'Fixed Broadband - DSL Subscriptions Per 100 Inhabitants',
        'Fixed Broadband - Satellite Subscriptions Per 100 Inhabitants',
        'Fixed Broadband - Terrestrial Fixed Wireless Subscriptions Per 100 Inhabitants'
        ]
metricsLabels=[
        'Mobile Data (Gb/m)',
        'All Access',
        'Fibre/Lan ',
        'Cable',
        'DSL',
        'Satellite',
        'Terrestrial Wireless'
        ]
metricsIcons=['fa fa-mobile',
        'fa fa-globe',
        'fa fa-network-wired',
        'fa fa-server',
        'fa fa-ethernet',
        'fa fa-satellite-dish',
        'fa fa-wifi'
        ]   

def getCard(text,val,icon, compare=False):
    letters = string.ascii_lowercase
    key = ''.join(random.choice(letters) for i in range(8))
    pgcol='green'
    if '-' in text:
        pgcol='red'
    if compare==False:
        pgcol='darkgrey'
    style={'icon': icon,'icon_color':'darkgrey','progress_color':pgcol}
    icoSize="20vw"
    hc.info_card(key=key,title=val, title_text_size="16vw",content=str(text),content_text_size="10vw",icon_size=icoSize,theme_override=style,bar_value=100)

@st.cache_data
def getBroadband():
    queryAll=f'''
    SELECT "Country Name","Variable Name" as metric, "Date" as date, "Value" FROM "TELECOMMUNICATION_DATA_ATLAS"."TELECOMMUNICATION"."BROADBAND_DB" WHERE 
        "Variable Name" IN ({', '.join(['"{}"'.format(value) for value in metrics]).replace('"',"'")}) and "Date" ='2021-01-01'
        AND "Frequency" = 'A';
    '''
    df = pd.read_sql(queryAll, session)
    return df

@st.cache_data
def getViewsByCity():
    queryAll=f'''
    select count(distinct av_session_id) as cnt, adverity.adverity.campaign() as CAMPAIGN, geo_country, geo_city,geo_latitude as lat,geo_longitude as lon    
    FROM ATIDEMO.stream.events
    Where av_session_id is not null and av_show is not null and
        to_date(EVENT_TIME) BETWEEN '2022-10-02' AND to_date(CURRENT_DATE())
    group by geo_country, geo_city,geo_latitude,geo_longitude
    '''
    df = pd.read_sql(queryAll, session)
    return df

def getAllViews():
    queryAll=f'''
        SELECT  site_id,src_campaign,av_session_id,event_time,geo_city,geo_country,geo_latitude as lat,geo_longitude as lon,av_show, av_episode
        FROM ATIDEMO.stream.events
        Where av_session_id is not null and av_show is not null and
        to_date(EVENT_TIME) BETWEEN '2020-01-02' AND '2020-06-02';
         '''
    df = pd.read_sql(queryAll, session)
    return df


def getWorldwideKPI(worldwide):
    st.subheader("Wordlwide High Speed Broadband Metrics (Marketplace)")
    cols=st.columns(len(metrics))
    for index,c in enumerate(cols):
        with cols[index]:
            if 'metrics[index]' not in st.session_state:
                dfW=worldwide[worldwide.METRIC==metrics[index]]
                fbnb=dfW['Value'].iloc[0]
                st.session_state[metrics[index]]=fbnb
            unit="%"
            if 'Gb' in metrics[index]:
                unit="Gb"
            getCard(metricsLabels[index],str(round(st.session_state[metrics[index]],2)) + unit, metricsIcons[index])

def getCountrySelectionBox(raw):
    return st.selectbox(
        'Compare with:',
    np.insert(raw['Country Name'].unique(),0,['Select Country...']),0)

def getCampaignSelectionBox(map):
    return st.selectbox(
        'Marketing Campaign:',
    np.insert(map['campaign'].unique(),0,['Select Marketing Campaign...']),0)

def getCountryKPI(country,raw,worldwide):
    if country!='Select Country...':
        filCountry=raw[(raw['Country Name']==country)]  
        merged = pd.merge(worldwide, filCountry, on="METRIC")
        merged["evol"]=round(((merged['Value_y']- merged['Value_x'] )/ merged['Value_x'])*100,0)
        cols=st.columns(len(metrics))
        for index,c in enumerate(cols):
            with c:
                try:
                    dfOne=merged[merged.METRIC==metrics[index]]
                    fbnb=dfOne['Value_y'].iloc[0]
                    evol=dfOne['evol'].iloc[0]
                    unit="%"
                    if 'Gb' in metrics[index]:
                        unit="Gb"
                    getCard(str(evol)+'%',str(round(fbnb,2)) + unit, metricsIcons[index],True)
                except:
                    getCard('Not deployed',0, metricsIcons[index])

def getMap2(map):   
    st.pydeck_chart(pdk.Deck(
            # map_style='mapbox://styles/mapbox/light-v9',
            map_style='dark_no_labels',
            tooltip=True,
            initial_view_state=pdk.ViewState(
                    latitude=08.85,
                    longitude=-20.35,
                    zoom=1.0,
                    pitch=10
                ),
            layers=[
                pdk.Layer(
                    "HeatmapLayer",
                    data=map,
                    opacity=1,
                    get_position=["lon", "lat"],
                    aggregation=pdk.types.String("SUM"),
                    # color_range=COLOR_BREWER_BLUE_SCALE,
                    threshold=0.1,
                    get_weight="cnt",
                    pickable=True,
                ),
                # pdk.Layer(
                #    'HexagonLayer',
                #    data=boostedCountry[['lon', 'lat']],
                #    get_position='[lon, lat]',
                #    radius=rad,
                #    coverage=cov/10, 
                #    bearing=bear,
                
                #    auto_highlight=True,
                #    elevation_scale=el_sc,
                #    elevation_range=[0, el_rg],
                #    pickable=True,
                #    extruded=True,
                # ),
                # pdk.Layer(
                #     'ScatterplotLayer',     # Change the `type` positional argument here
                #     data=df[['lon', 'lat']],
                #     get_position=['lon', 'lat'],
                #     auto_highlight=True,
                #     get_radius=20000,          # Radius is given in meters
                #     get_fill_color=[180, 0, 200, 140],  # Set an RGBA value for fill
                #     pickable=True)
                ],
        ))             


def getMap(map):
    agg=map.groupby(['geo_country']).mean().reset_index()
    m = leafmap.Map(center=[15, -30], zoom=3, tiles="stamentonerbackground")
    m.add_heatmap(
        data=agg,
        latitude="lat",
        longitude="lon",
        value="cnt",
        name="Heat map",
        radius=33,
        blur=22
    )
    m.to_streamlit(height=650,)

def getPage(sess):
    global session
    session=sess
    raw=getBroadband()
    raw['DATE'] = pd.to_datetime(raw['DATE'], format='%Y-%m-%d')
    worldwide=raw.groupby(['METRIC', 'DATE']).mean().reset_index()
    getWorldwideKPI(worldwide)
    
    raw['Country Name']=raw['Country Name'].replace(['Colombia'], 'Argentina')
    raw.sort_values(by=['Country Name'], inplace=True)
    country=getCountrySelectionBox(raw)

    getCountryKPI(country,raw,worldwide)

    map=getViewsByCity()
    map.rename(str.lower, axis='columns',inplace=True)
    map['cnt'] = np.where((map['geo_country'] == 'Argentina'),
                                            map['cnt'] *300,
                                            map['cnt'])                                          
    map['cnt'] = np.where((map['geo_country'] == 'Mexico'),
                                            map['cnt'] *500,
                                            map['cnt'])           
    st.subheader("Trailers Views Buffering Rate (Piano)")
  
    col0,col1=st.columns(2)
    with col1:
        campaign=getCampaignSelectionBox(map)
    with col0:
        getMap(map)    