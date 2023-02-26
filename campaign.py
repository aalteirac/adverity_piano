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

@st.cache_data(show_spinner=False)
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
        domain=[0.12, 0.88]),height=610, title='Impressions, Clicks & CTR(%)')
    st.plotly_chart(fig, theme="streamlit",use_container_width=True)

def getKPIByMonth(df):
    return df.groupby(['MONTH']).agg({'IMPRESSIONS':'sum',
                                      'CLICKS':'sum',
                                      'CTR':"mean"}).reset_index()

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
 