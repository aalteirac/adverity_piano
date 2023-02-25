import streamlit as st
import pandas as pd
import hydralit_components as hc
import random
import string
import plotly.express as px
import plotly.graph_objects as go

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
    return df.groupby(['GENDER','AGE_RANGE']).agg({'CTR':'mean'})

def getKPIByCampaignAds(df):
    return df.groupby(['CAMPAIGN','AD_NAME']).agg({'IMPRESSIONS':'sum',
                                      'CLICKS':'sum',
                                      'CTR':"mean"})

def getCTRByDevice(df):
    return df.groupby(['DEVICE_TYPE']).agg({'CTR':'mean'})

def getTopBottomAds(df,bottom=False,n=3):
    return df.groupby(['AD_NAME']).agg({'ER':'mean'}).sort_values(by=['ER'],ascending=bottom).head(n)

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
        domain=[0.12, 0.88]),height=430)
    st.plotly_chart(fig, theme="streamlit",use_container_width=True)


def getPage(sess):
    global session 
    session = sess
    # st.write(getGlobalKPI( getRawCampaign(),'IMPRESSIONS','sum'))
    # st.write(getGlobalKPI( getRawCampaign(),'CLICKS','sum'))
    # st.write(getGlobalKPI( getRawCampaign(),'CTR','mean'))
    col1, col2,col3 = st.columns(3)
    with col1:
        getCard("Impressions","{:,}".format(getGlobalKPI( getRawCampaign(),'IMPRESSIONS','sum')),'fa fa-print')
    with col2:
        getCard("Clicks","{:,}".format(getGlobalKPI( getRawCampaign(),'CLICKS','sum')),'fa fa-hand-pointer')
    with col3:
        getCard("CTR (%)",str(  round(getGlobalKPI( getRawCampaign(),'CTR','mean'),2)) +"%",'fa fa-money-bill')
    # with col2:    
        # st.write(getKPIByMonth(getRawCampaign()))
    getChartClickCTR(getKPIByMonth(getRawCampaign()))
    # st.write(getCTRByGenderByAge(getRawCampaign()))
    # st.write(getCTRByDevice(getRawCampaign()))
    # st.write(getKPIByCampaignAds(getRawCampaign()))
    # st.write(getTopBottomAds(getRawCampaign()))
    # st.write(getTopBottomAds(getRawCampaign(),True))
    # st.write(getVideoFunnel(getRawCampaign()))
    # st.write(getVideoKPI(getRawCampaign()))
    # st.write(getVideoCompletionDrillDown(getRawCampaign()))