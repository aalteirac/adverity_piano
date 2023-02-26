import streamlit as st
import pandas as pd
import hydralit_components as hc
import random
import string
import plotly.graph_objects as go
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode, GridUpdateMode

session=None

def getCard(text,val,icon, compare=False):
    letters = string.ascii_lowercase
    key = ''.join(random.choice(letters) for i in range(8))
    pgcol='green'
    if '-' in text:
        pgcol='red'
    if compare==False:
        pgcol='darkgrey'
    style={'icon': icon,'icon_color':'darkgrey','progress_color':pgcol}
    icoSize="10vw"
    hc.info_card(key=key,title=str(val), title_text_size="10vw",content=str(text),content_text_size="8vw",icon_size=icoSize,theme_override=style)

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
    df['RATIO_VIDEO_QUARTILE_25_VIEWS']=(df['VIDEO_QUARTILE_25_VIEWS']/df['QUARTILE SUM'])*100
    df['RATIO_VIDEO_QUARTILE_50_VIEWS']=(df['VIDEO_QUARTILE_50_VIEWS']/df['QUARTILE SUM'])*100
    df['RATIO_VIDEO_QUARTILE_75_VIEWS']=(df['VIDEO_QUARTILE_75_VIEWS']/df['QUARTILE SUM'])*100
    df['RATIO_VIDEO_COMPLETIONS']=(df['VIDEO_COMPLETIONS']/df['QUARTILE SUM'])*100
    df['RATIO_VIDEO']=(df['VIEWS']/df['QUARTILE SUM'])*100
    return df[['RATIO_VIDEO_QUARTILE_25_VIEWS', 'RATIO_VIDEO_QUARTILE_50_VIEWS','RATIO_VIDEO_QUARTILE_75_VIEWS','RATIO_VIDEO_COMPLETIONS','RATIO_VIDEO']].mean()

def getVideoKPI(df):
    col_list= ['VIEWS','VIDEO_QUARTILE_25_VIEWS','VIDEO_QUARTILE_50_VIEWS','VIDEO_QUARTILE_75_VIEWS','VIDEO_COMPLETIONS']
    return getGlobalKPI(df,col_list)

def getVideoCompletionDrillDown(df):
    return df.groupby(['CAMPAIGN','AD_NAME']).agg({'VIDEO_COMPLETIONS':'mean'}).sort_values(by=['VIDEO_COMPLETIONS'],ascending=False)

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
    fig.update_layout(height=430,title=prefix+' Performing Ads by ER(%)') #yaxis_range=[1.2,1.25]
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

def getTableCampaignPerf(df):
    ob = GridOptionsBuilder.from_dataframe(df)
    ob.configure_column('CAMPAIGN', rowGroup=True,hide= True)
    ob.configure_column('AD_TYPE', rowGroup=True,hide= True)
    ob.configure_column('IMPRESSIONS', aggFunc='sum',header_name='IMPRESSIONS')
    ob.configure_column('CLICKS', aggFunc='sum', header_name='CLICKS')
    ob.configure_column('CTR', aggFunc='avg',header_name='CTR')
    ob.configure_grid_options(autoGroupColumnDef={'headerName':'CAMPAIGN/AD_TYPE'},suppressAggFuncInHeader = True)
    custom_css = {
        ".ag-root-wrapper":{
             "margin-top":"30px",
             "border-bottom": "2px",
             "border-bottom-color": "#b9b5b5",
             "border-bottom-style": "double"
             }
        }
    AgGrid(df, ob.build(), enable_enterprise_modules=True,fit_columns_on_grid_load=True,height=345,custom_css=custom_css)

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
    col1, col2,col3 = st.columns(3)
    with col1:
        getCard("Impressions","{:,}".format(getGlobalKPI( getRawCampaign(),'IMPRESSIONS','sum')),'fa fa-print')
    with col2:
        getCard("Clicks","{:,}".format(getGlobalKPI( getRawCampaign(),'CLICKS','sum')),'fa fa-hand-pointer')
    with col3:
        getCard("CTR (%)",str(  round(getGlobalKPI( getRawCampaign(),'CTR','mean'),2)) +"%",'fa fa-money-bill')
    getChartClickCTR(getKPIByMonth(getRawCampaign()))
   
    
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

    
    # st.write(getVideoFunnel(getRawCampaign()))
    # st.write(getVideoKPI(getRawCampaign()))
    # st.write(getVideoCompletionDrillDown(getRawCampaign()))