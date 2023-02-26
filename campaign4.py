import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import pycountry
import geopandas
import leafmap.foliumap as leafmap



session=None
def alpha3code(column):
    CODE=[]
    for country in column:
        try:
            code=pycountry.countries.get(name=country).alpha_3
           # .alpha_3 means 3-letter country code 
           # .alpha_2 means 2-letter country code
            CODE.append(code)
        except:
            if country=='Bolivia':
                CODE.append('BOL')
            if country=='Venezuela':
                CODE.append('VEN')    
    return CODE

@st.cache_data(show_spinner=False)
def getRawCampaign():
    queryAll=f'''
    SELECT *,to_date(TO_VARCHAR(DAY, 'yyyy-MM-01')) as MONTH,coalesce((clicks/NULLIF(impressions,0))*100,0) as CTR,coalesce(((clicks + likes + shares)/NULLIF(impressions,0))*100,0) as ER from adverity.adverity."Marketing_Data";
    '''
    df = pd.read_sql(queryAll, session)
    return df

def getGeoFromIso(df):
    world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
    world.columns=['pop_est', 'continent', 'name', 'CODE', 'gdp_md_est', 'geometry']
    merge=pd.merge(world,df,on='CODE')
    location=pd.read_csv('https://raw.githubusercontent.com/melanieshi0120/COVID-19_global_time_series_panel_data/master/data/countries_latitude_longitude.csv')
    merge=merge.merge(location,on='name').reset_index()
    return merge

def getMapConversion(df,metric):
    df=df[['geometry','longitude','latitude',metric]]
    m = leafmap.Map(center=(40, -100),zoom=5,draw_control=False,
        measure_control=False,
        fullscreen_control=False,
        attribution_control=True
    )
    m.add_data(
        df, column=metric, scheme='Quantiles', cmap='Blues', legend_title=metric
    )
    # m.zoom_to_bounds([-9.0882278, -55.3228175, 68.2249543, 72.2460938])
    # m = leafmap.Map(center=[15, -40], zoom=3 ,tiles="stamentonerbackground")
    # df=df[['longitude','latitude',metric]]
    # df[metric]=round(df[metric],2)
    # m.add_points_from_xy(df, x="longitude", y="latitude")
    # m.add_labels(
    #     df,
    #     metric,
    #     font_size="9pt",
    #     font_color="red",
    #     font_family="arial",
    #     font_weight="bold",
    # )
    # m.add_heatmap(
    #     data=df,
    #     latitude="latitude",
    #     longitude="longitude",
    #     value=metric,
    #     name="Heat map",
    #     radius=33,
    #     blur=22
    # )
    m.to_streamlit(height=350)
    # world_map= folium.Map(tiles="cartodbpositron")
    # marker_cluster = MarkerCluster().add_to(world_map)
    # #for each coordinate, create circlemarker of user percent
    # for i in range(len(df)):
    #         lat = df.iloc[i]['latitude']
    #         long = df.iloc[i]['longitude']
    #         radius=5
    #         popup_text = """Country : {}<br>
    #                     %of Users : {}<br>"""
    #         popup_text = popup_text.format(df.iloc[i]['name'],
    #                                 df.iloc[i]['CONVERSIONS']
    #                                 )
    #         folium.CircleMarker(location = [lat, long], radius=radius, popup= popup_text, fill =True).add_to(marker_cluster)

def getVideoForMap(df):
    df=df[['COUNTRY_NAME','VIDEO_COMPLETION_RATE', 'CONVERSIONS']]
    df=df.groupby(['COUNTRY_NAME']).agg({'VIDEO_COMPLETION_RATE':'mean','CONVERSIONS':'sum'}).reset_index()
    df['CODE']=alpha3code(df.COUNTRY_NAME)
    df=getGeoFromIso(df)
    return df

def getKPIByCountry(df):
    df=df.groupby(['COUNTRY_NAME','CAMPAIGN','AD_TYPE','AD_NAME']).agg({
                                      'CTR':"mean",
                                      'VIDEO_COMPLETIONS':'sum',
                                      'VIDEO_COMPLETION_RATE':'mean'
                                      }).reset_index()
    df['VIDEO_COMPLETION_RATE']=df['VIDEO_COMPLETION_RATE']*100
    return df

def getPercentRenderer():
    rd = JsCode('''
        function(params) {
            var color='green';
            if(params.value<1)
                color="red";
            if(params.value>1 && params.value<1.1)
                color="#ffc700";    
            return '<span style="color:'+color + '">' + parseFloat(params.value).toFixed(2) + '%</span>'}
    ''') 
    return rd
  
def getPercentRendererComp():
    rd = JsCode('''
        function(params) {
            var color='green';
            if(params.value<25)
                color="red";
            if(params.value>25 && params.value<30)
                color="#ffc700";    
            return '<span style="color:'+color + '">' + parseFloat(params.value).toFixed(2) + '%</span>'}
    ''') 
    return rd   

def getTableCountryPerf(df):
    ob = GridOptionsBuilder.from_dataframe(df)
    ob.configure_column('COUNTRY_NAME', rowGroup=True,hide= True)
    ob.configure_column('CAMPAIGN', rowGroup=True,hide= True)
    ob.configure_column('AD_TYPE', rowGroup=True,hide= True)
    ob.configure_column('CTR', aggFunc='avg',header_name='CTR(%)',cellRenderer= getPercentRenderer())
    ob.configure_column('VIDEO_COMPLETIONS', aggFunc='sum', header_name='VIDEO COMPLETIONS')
    ob.configure_column('VIDEO_COMPLETION_RATE', aggFunc='avg',header_name='VIDEO COMPLETION RATE(%)',cellRenderer= getPercentRendererComp())
    
    ob.configure_grid_options(suppressAggFuncInHeader = True)
    custom_css = {
        ".ag-watermark":{
            "display":"none!important"
        },
        ".ag-root-wrapper":{
             "margin-top":"28px",
             "border-bottom": "2px",
             "border-bottom-color": "#b9b5b5",
             "border-bottom-style": "double"
             }
        }
    gripOption=ob.build()
    gripOption["autoGroupColumnDef"]= {
    "headerName": 'COUNTRY/CAMPAIGN/AD_TYPE',
    "cellRendererParams": {
      "suppressCount": True,
        },
    }
    AgGrid(df, gripOption, enable_enterprise_modules=True,fit_columns_on_grid_load=True,height=342,custom_css=custom_css,allow_unsafe_jscode=True,)

def getPage(sess):
    global session 
    session = sess
    colMap1,colMap2=st.columns(2)
    with colMap1:
        getMapConversion(getVideoForMap(getRawCampaign()),'CONVERSIONS') 
    with colMap2:
        getMapConversion(getVideoForMap(getRawCampaign()),'VIDEO_COMPLETION_RATE')     
    getTableCountryPerf(getKPIByCountry(getRawCampaign()))
    # st.write(getKPIByCountry(getRawCampaign()))