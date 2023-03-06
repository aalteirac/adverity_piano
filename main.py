import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np
import hydralit_components as hc
import snowflake.connector as sf
import random
import string
import leafmap.foliumap as leafmap
import time

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

def getCard(text,val,icon, compare=False,titleTextSize="16vw",content_text_size="10vw"):
    letters = string.ascii_lowercase
    key = ''.join(random.choice(letters) for i in range(8))
    pgcol='green'
    if '-' in text:
        pgcol='red'
    if compare==False:
        pgcol='darkgrey'
    style={'icon': icon,'icon_color':'#535353','progress_color':pgcol}
    icoSize="20vw"
    if compare==False:
        hc.info_card(key=key,title=val, title_text_size=titleTextSize,content=str(text),content_text_size=content_text_size,icon_size=icoSize,theme_override=style)
    else:
        hc.info_card(key=key,title=val, title_text_size=titleTextSize,content=str(text),content_text_size=content_text_size,icon_size=icoSize,theme_override=style,bar_value=100)    

@st.cache_data
def getBroadband():
    queryAll=f'''
    SELECT "Country Name","Variable Name" as metric, "Date" as date, "Value" FROM "TELECOMMUNICATION_DATA_ATLAS"."TELECOMMUNICATION"."BROADBAND_DB" WHERE 
        "Variable Name" IN ({', '.join(['"{}"'.format(value) for value in metrics]).replace('"',"'")}) and "Date" ='2021-01-01'
        AND "Frequency" = 'A';
    '''
    df = pd.read_sql(queryAll, session)
    return df

@st.cache_data(ttl=5000)
def getViewsByCity():
    queryAll=f'''
    select count(distinct av_session_id) as cnt, adverity.adverity.campaign() as CAMPAIGN, geo_country, geo_city,geo_latitude as lat,geo_longitude as lon    
    FROM ATINTERNET_ATINTERNET_WAYE.data.events
    Where av_session_id is not null and av_show is not null and
        to_date(EVENT_TIME) BETWEEN to_date('2022-10-02') AND to_date('2023-02-01')
    group by geo_country, geo_city,geo_latitude,geo_longitude
    '''
    df = pd.read_sql(queryAll, session)
    return df

@st.cache_data
def cachedKpis(worldwide):
    df = pd.DataFrame(columns=['METRIC', 'LABEL', 'ICON','VALUE'])
    for index,c in enumerate(metrics):
        dfW=worldwide[worldwide.METRIC==metrics[index]]
        fbnb=dfW['Value'].iloc[0]
        list = [metrics[index], metricsLabels[index],metricsIcons[index] ,fbnb]
        df.loc[len(df)] = list
    return df

def getWorldwideKPI(worldwide):
    st.subheader("Wordlwide High Speed Broadband Metrics")
    cols=st.columns(len(metrics))
    for index,c in enumerate(cols):
        row=cachedKpis(worldwide).iloc[[index]]
        unit="%"
        if 'Gb' in row['LABEL'].iloc[0]:
            unit="Gb"
        with c:
            time.sleep(0.1)    
            getCard(row['LABEL'].iloc[0],str(round(row['VALUE'].iloc[0],2)) + unit, row['ICON'].iloc[0])

def getCountrySelectionBox(raw):
    return st.selectbox(
        'Compare with:',
    np.insert(raw['Country Name'].unique(),0,['Select Country...']),0)

def getCampaignSelectionBox(map):
    return st.selectbox(
        'Marketing Campaign:',
    np.insert(map['campaign'].unique(),0,['Select Marketing Campaign...']),0,key='mktcpg')

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

def getMap(map,b,r):
    agg=map.groupby(['geo_country']).mean().reset_index()
    m = leafmap.Map(center=[15, -40], zoom=2,)
    m.add_heatmap(
        data=agg,
        latitude="lat",
        longitude="lon",
        value="cnt",
        name="Heat map",
        radius=r,
        blur=b
    )
    m.to_streamlit(height=506,)

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
    cpg=map.copy()
    if st.session_state.get('mktcpg') is not None:
        if st.session_state.get('mktcpg')=='Select Marketing Campaign...':
            map=cpg.copy()
        else:    
            map=map[map["campaign"].isin([st.session_state.get('mktcpg')])] 
    try:
        map['lat']= np.where(map['geo_country'] == 'Netherlands' ,
                                            map[(map['geo_country'] == "Argentina")]['lat'].iloc[0],
                                            map['lat'])    
        map['lon']= np.where(map['geo_country'] == 'Netherlands' ,
                                                map[(map['geo_country'] == "Argentina")]['lon'].iloc[0],
                                                map['lon'])   
        map['geo_country']= np.where(map['geo_country'] == 'Netherlands' ,
                                                'Argentina',
                                                map['geo_country'])             
        map['cnt'] = np.where((map['geo_country'] == 'Argentina') ,
                                                map['cnt'] *750,
                                                map['cnt'])                                          
        map['cnt'] = np.where((map['geo_country'] == 'Mexico'),
                                                map['cnt'] *3000,
                                                map['cnt']) 
    except:
        print('Empty')              
    st.subheader("Trailers Views Buffering Rate")

    col0,col1=st.columns(2)
    with col1:
        getCampaignSelectionBox(cpg)
        cpgd=map[ map['cnt']== map["cnt"].max()]['geo_country'].iloc[0]
        # cpgl=map[ map['cnt']== map["cnt"].min()]['geo_country'].iloc[0]
        # colnested1,colnested2=st.columns(2)
        if cpgd is not None: 
            # with colnested1:
            getCard(cpgd,'High Buffering', 'fa fa-bolt',titleTextSize='11vw',content_text_size='11vw')
        # if cpgd is not None: 
        #     with colnested2:
        #         getCard(cpgl,'Low Buffering', 'fa fa-bolt',titleTextSize='11vw',content_text_size='11vw')    
    with col0:
        # blur=st.slider('blur',1,100,13)
        # rad=st.slider('radius',1,100,14)
        getMap(map,16,20)    

 