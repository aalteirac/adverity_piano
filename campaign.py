import streamlit as st
import pandas as pd
import hydralit_components as hc
import random
import string
import plotly.graph_objects as go
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode, GridUpdateMode
import pycountry
import geopandas
import leafmap.foliumap as leafmap
import time


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

def getCard(text,val,icon, compare=False):
    letters = string.ascii_lowercase
    key = ''.join(random.choice(letters) for i in range(8))
    pgcol='green'
    if '-' in text:
        pgcol='red'
    if compare==False:
        pgcol='darkgrey'
    style={'icon': icon,'icon_color':'darkgrey','progress_color':pgcol}
    icoSize="15vw"
    hc.info_card(key=key,title=str(val), title_text_size="12vw",content=str(text),content_text_size="8vw",icon_size=icoSize,theme_override=style)

@st.cache_data
def getRawCampaign():
    queryAll=f'''
    SELECT *,to_date(TO_VARCHAR(DAY, 'yyyy-MM-01')) as MONTH,coalesce((clicks/NULLIF(impressions,0))*100,0) as CTR,coalesce(((clicks + likes + shares)/NULLIF(impressions,0))*100,0) as ER from adverity.adverity."Marketing_Data";
    '''
    df = pd.read_sql(queryAll, session)
    return df

def getGlobalKPI(dt,kpi,op='sum'):
    if op=='sum':
        return dt[kpi].sum()
    if op=='mean':
        return dt[kpi].mean()

def getKPIByMonth(df):
    return df.groupby(['MONTH']).agg({'IMPRESSIONS':'sum',
                                      'CLICKS':'sum',
                                      'CTR':"mean"}).reset_index()

def getCTRByGenderByAge(df):
    return df.groupby(['GENDER','AGE_RANGE']).agg({'CTR':'mean'}).reset_index()

def getKPIByCampaignAds(df):
    return df.groupby(['CAMPAIGN','AD_TYPE','AD_NAME']).agg({'IMPRESSIONS':'sum',
                                      'CLICKS':'sum',
                                      'CTR':"mean"}).reset_index()

def getCTRByDevice(df):
    return df.groupby(['DEVICE_TYPE']).agg({'CTR':'mean'}).reset_index()

def getTopBottomAds(df,bottom=False,n=3):
    return df.groupby(['AD_NAME']).agg({'ER':'mean'}).sort_values(by=['ER'],ascending=bottom).reset_index().head(n)

def getVideoFunnel(df):
    col_list= ['VIEWS','VIDEO_QUARTILE_25_VIEWS','VIDEO_QUARTILE_50_VIEWS','VIDEO_QUARTILE_75_VIEWS','VIDEO_COMPLETIONS']
    df['QUARTILE SUM'] = df[col_list].sum(axis=1)
    df['25% VIEWED']=(df['VIDEO_QUARTILE_25_VIEWS']/df['QUARTILE SUM'])*100
    df['50% VIEWED']=(df['VIDEO_QUARTILE_50_VIEWS']/df['QUARTILE SUM'])*100
    df['75% VIEWED']=(df['VIDEO_QUARTILE_75_VIEWS']/df['QUARTILE SUM'])*100
    df['COMPLETED']=(df['VIDEO_COMPLETIONS']/df['QUARTILE SUM'])*100
    df['VIEWED']=(df['VIEWS']/df['QUARTILE SUM'])*100
    return df[['25% VIEWED', '50% VIEWED','75% VIEWED','COMPLETED','VIEWED']].mean().reset_index()

def getVideoKPI(df):
    col_list= ['VIEWS','VIDEO_QUARTILE_25_VIEWS','VIDEO_QUARTILE_50_VIEWS','VIDEO_QUARTILE_75_VIEWS','VIDEO_COMPLETIONS']
    return getGlobalKPI(df,col_list).reset_index()

def getVideoCompletionDrillDown(df):
    return df.groupby(['CAMPAIGN','AD_TYPE']).agg({'VIDEO_COMPLETIONS':'mean'}).sort_values(by=['VIDEO_COMPLETIONS'],ascending=False).reset_index()

def getChartClickCTR(df):
    fig = go.Figure(data=[
        go.Bar(name='IMPRESSIONS', x=df['MONTH'], y=df['IMPRESSIONS'],yaxis='y',offsetgroup=1),
        go.Bar(name='CLICKS', x=df['MONTH'], y=df['CLICKS'],yaxis='y2',offsetgroup=2),
        go.Line(name='CTR(%)',x=df['MONTH'], y=df['CTR'],yaxis='y3',offsetgroup=3)
    ],layout={
        'yaxis': {'title': 'IMPRESSIONS','showgrid':False,'showline':False},
        'yaxis2': {'title': 'CLICKS', 'overlaying': 'y', 'side': 'right','showgrid':False,'showline':False},
        'yaxis3': {'title': 'CTR(%)', 'overlaying': 'y', 'side': 'left','position':0.05,"anchor":"free",'showgrid':False,'showline':False}
    })
    # Change the bar mode
    fig.update_layout(barmode='group',xaxis=dict(
        domain=[0.12, 0.88]),height=430, title='Impressions, Clicks & CTR(%)')
    st.plotly_chart(fig, theme="streamlit",use_container_width=True)

def getChartCTRByDevice(df):
    fig = go.Figure(data=[
        go.Bar(name='IMPRESSIONS', x=df['DEVICE_TYPE'], y=df['CTR'],yaxis='y',text=df['CTR']/100)
    ],layout={
        'yaxis': {'title': 'CTR(%)','showgrid':False,'showline':False}
    })
    fig.data[0].marker.color = ('blue','green','darkgrey')
    fig.update_traces(texttemplate='%{text:.2%}', textposition='inside')
    fig.update_layout(height=430,title='CTR(%) by Device Type',yaxis_range=[df['CTR'].min() - (df['CTR'].min()/50),df['CTR'].max()]) #yaxis_range=[1.2,1.25]
    st.plotly_chart(fig, theme="streamlit",use_container_width=True)

def getChartTopAds(df,asc=True,prefix='Top'):
    df=df.sort_values(['ER'], ascending=[asc])
    fig = go.Figure(data=[
        go.Bar(name='IMPRESSIONS', y=df['AD_NAME'], x=df['ER'],text=df['ER']/100, orientation='h')
    ])
    fig.update_xaxes(visible=False, showticklabels=False)
    fig.data[0].marker.color = ('blue','green','darkgrey')
    fig.update_traces(texttemplate='%{text:.2%}', textposition='inside')
    fig.update_layout(height=430,title=prefix+' Performing Ads by ER(%)',xaxis_range=[df['ER'].min() - (df['ER'].min()/50),df['ER'].max()]) #yaxis_range=[1.2,1.25]
    st.plotly_chart(fig, theme="streamlit",use_container_width=True)    

def genSankey(df,cat_cols=[],value_cols='',title='Sankey Diagram'):
    colorPalette = ['red','#646464','#306998','#FFE873','#FFD43B']
    labelList = []
    colorNumList = []
    for catCol in cat_cols:
        labelListTemp =  list(set(df[catCol].values))
        colorNumList.append(len(labelListTemp))
        labelList = labelList + labelListTemp
        
    labelList = list(dict.fromkeys(labelList))
    
    colorList = []
    for idx, colorNum in enumerate(colorNumList):
        colorList = colorList + [colorPalette[idx]]*colorNum
        
    for i in range(len(cat_cols)-1):
        if i==0:
            sourceTargetDf = df[[cat_cols[i],cat_cols[i+1],value_cols]]
            sourceTargetDf.columns = ['source','target','count']
        else:
            tempDf = df[[cat_cols[i],cat_cols[i+1],value_cols]]
            tempDf.columns = ['source','target','count']
            sourceTargetDf = pd.concat([sourceTargetDf,tempDf])
        sourceTargetDf = sourceTargetDf.groupby(['source','target']).agg({'count':'sum'}).reset_index()
        
    sourceTargetDf['sourceID'] = sourceTargetDf['source'].apply(lambda x: labelList.index(x))
    sourceTargetDf['targetID'] = sourceTargetDf['target'].apply(lambda x: labelList.index(x))
    #OVERRIDE COLOR AS I DON'T HAVE TIME :-)
    colorList=['darkgrey','#7ce670','blue','#ebf0a8','#e3ed58','#cad622','#acd622','#7cd622','#22d69d']
    data = dict(
        type='sankey',
        node = dict(
          pad = 15,
          thickness = 20,
          line = dict(
            color = "black",
            width = 0.5
          ),
          label = labelList,
          color = colorList
        ),
        link = dict(
          source = sourceTargetDf['sourceID'],
          target = sourceTargetDf['targetID'],
          value = sourceTargetDf['count'],
        )
      )
    
    layout =  dict(
        title = title,
        font = dict(
          size = 10
        )
    )
       
    fig = dict(data=[data], layout=layout)
    st.plotly_chart(fig, theme="streamlit",use_container_width=True)

def getPercentRenderer():
    rd = JsCode('''
        function(params) {return '<span>' + parseFloat(params.value).toFixed(2) + '%</span>'}
    ''') 
    return rd   

def getTableCampaignPerf(df):
    ob = GridOptionsBuilder.from_dataframe(df)
    ob.configure_column('CAMPAIGN', rowGroup=True,hide= True)
    ob.configure_column('AD_TYPE', rowGroup=True,hide= True)
    ob.configure_column('IMPRESSIONS', aggFunc='sum',header_name='IMPRESSIONS')
    ob.configure_column('CLICKS', aggFunc='sum', header_name='CLICKS')
    ob.configure_column('CTR', aggFunc='avg',header_name='CTR',cellRenderer= getPercentRenderer())
    
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
    "headerName": 'CAMPAIGN/AD_TYPE',
    "cellRendererParams": {
      "suppressCount": True,
    },
  }
    AgGrid(df, gripOption, enable_enterprise_modules=True,fit_columns_on_grid_load=True,height=342,custom_css=custom_css,allow_unsafe_jscode=True,)

def getChartVideoFunnel(df):
    df=df.sort_values(by=[0],ascending=False)
    fig = go.Figure(go.Funnel(
        y = df['index'],
        x = round(df[0],2),
        textposition = "inside",
        textinfo = "value+label",
        texttemplate='%{value}%<br> %{label}',
        opacity = 1, 
        marker = {
        "color": ['blue','green', "teal",'darkgrey', "silver"],
        # "line": {"width": [4, 2, 2, 3, 1, 1], "color": ["wheat", "wheat", "blue", "wheat", "wheat"]}
        },
        # connector = {"line": {"color": "royalblue", "dash": "solid", "width": 3}}
        )
    )
    fig.update_yaxes(visible=False, showticklabels=False)
    fig.update_layout(
        title="Video Completion Rate",
        autosize=False,
        height=340,
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=30,
            pad=4
        ),
        # paper_bgcolor="LightSteelBlue",
    )
    config = {'displayModeBar': False}
    st.plotly_chart(fig, theme="streamlit",config = config,use_container_width=True)    

def getBarVideoKPI(df):
    cols=st.columns(len(df))
    for index, row in df.iterrows():
        with cols[index]:
            st.metric(label=row['index'].replace('_',' '), value='{:,}'.format(row[0]))

def getChartVideoByCampaign(df):
    df=df.groupby(['CAMPAIGN']).mean().reset_index()
    fig = go.Figure(data=[
        go.Bar(name='IMPRESSIONS', x=df['CAMPAIGN'], y=df['VIDEO_COMPLETIONS'],yaxis='y',text=df['VIDEO_COMPLETIONS']/100)
    ],layout={
        'yaxis': {'title': 'Video Completion Rate(%)','showgrid':False,'showline':False}
    })
    fig.data[0].marker.color = ('blue')
    config = {'displayModeBar': False}
    fig.update_layout(
        autosize=False,
        height=250,
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=0,
            pad=4
        ),
        # paper_bgcolor="LightSteelBlue",
    )
    fig.update_traces(texttemplate='%{text:.2%}', textposition='inside')
    fig.update_layout(yaxis_range=[df['VIDEO_COMPLETIONS'].min() - (df['VIDEO_COMPLETIONS'].min()/40),df['VIDEO_COMPLETIONS'].max()]) #yaxis_range=[1.2,1.25]
    st.plotly_chart(fig,config=config, theme="streamlit",use_container_width=True)

def getGeoFromIso(df):
    world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
    world.columns=['pop_est', 'continent', 'name', 'CODE', 'gdp_md_est', 'geometry']
    merge=pd.merge(world,df,on='CODE')
    location=pd.read_csv('https://raw.githubusercontent.com/melanieshi0120/COVID-19_global_time_series_panel_data/master/data/countries_latitude_longitude.csv')
    merge=merge.merge(location,on='name').reset_index()
    return merge


def getMapConversion(df,metric):
    df=df[['geometry','longitude','latitude',metric]]
    m = leafmap.Map(center=(40, -100),zoom=3,draw_control=False,
        measure_control=False,
        fullscreen_control=False,
        attribution_control=True
    )
    m.add_data(
        df, column=metric, scheme='Quantiles', cmap='Blues', legend_title=metric
    )
    time.sleep(1)
    m.zoom_to_bounds([-9.0882278, -55.3228175, 168.2249543, 72.2460938])
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
    m.to_streamlit(height=650)
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


def getPage(sess):
    global session 
    session = sess
    # st.write(getGlobalKPI( getRawCampaign(),'IMPRESSIONS','sum'))
    # st.write(getGlobalKPI( getRawCampaign(),'CLICKS','sum'))
    # st.write(getGlobalKPI( getRawCampaign(),'CTR','mean'))
    # st.write(getCTRByDevice(getRawCampaign()))
    # st.write(getTopBottomAds(getRawCampaign()))
    # st.write(getTopBottomAds(getRawCampaign(),True))
    # st.write(getKPIByCampaignAds(getRawCampaign()))
    # st.write(getVideoFunnel(getRawCampaign()))
    # st.write(getVideoKPI(getRawCampaign()))
    # st.write(getVideoCompletionDrillDown(getRawCampaign()))
    tab1, tab2,tab3 = st.tabs(["Overview", "Ad Performance","Video Viewing"])
   
    with tab1:
        col1, col2,col3,col4 = st.columns(4)
        with col1:
            getCard("IMPRESSIONS","{:,}".format(getGlobalKPI( getRawCampaign(),'IMPRESSIONS','sum')),'fa fa-print')
        with col2:
            getCard("CLICKS","{:,}".format(getGlobalKPI( getRawCampaign(),'CLICKS','sum')),'fa fa-hand-pointer')
        with col3:
            getCard("CTR (%)",str(  round(getGlobalKPI( getRawCampaign(),'CTR','mean'),2)) +"%",'fa fa-money-bill')
        with col4:
            getCard("ER (%)",str(  round(getGlobalKPI( getRawCampaign(),'ER','mean'),2)) +"%",'fa fa-heart')
        getChartClickCTR(getKPIByMonth(getRawCampaign()))

    with tab2:
        colL,colR=st.columns(2)
        with colR:
            genSankey(getCTRByGenderByAge(getRawCampaign()),cat_cols=['GENDER','AGE_RANGE'],value_cols='CTR',title='CTR (%) by Age Group & Gender')
        with colL:
            getChartCTRByDevice(getCTRByDevice(getRawCampaign()))
        
        colAd1,colAd2,colTable=st.columns([1,1,3])   
        with colAd1: 
            getChartTopAds(getTopBottomAds(getRawCampaign()))    
        with colAd2: 
            getChartTopAds(getTopBottomAds(getRawCampaign(),bottom=True),asc=False,prefix='Bottom')    
        with colTable:
            getTableCampaignPerf(getKPIByCampaignAds(getRawCampaign()))       

    with tab3:
        colF,colK=st.columns([5,9])
        with colF:
            getChartVideoFunnel(getVideoFunnel(getRawCampaign()))
        with colK:
            getBarVideoKPI(getVideoKPI(getRawCampaign()))
            getChartVideoByCampaign(getVideoCompletionDrillDown(getRawCampaign()))
        colMap1,colMap2=st.columns(2)
        with colMap1:
            getMapConversion(getVideoForMap(getRawCampaign()),'CONVERSIONS') 
        with colMap2:
            getMapConversion(getVideoForMap(getRawCampaign()),'VIDEO_COMPLETION_RATE')     
        # getMapConversion(getVideoForMap(getRawCampaign()),'CONVERSIONS')   