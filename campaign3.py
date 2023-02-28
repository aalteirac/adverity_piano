import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import string
import random
import hydralit_components as hc
from math import log, floor


session=None

@st.cache_data(show_spinner=False)
def getRawCampaign():
    queryAll=f'''
    SELECT *,to_date(TO_VARCHAR(DAY, 'yyyy-MM-01')) as MONTH,coalesce((clicks/NULLIF(impressions,0))*100,0) as CTR,coalesce(((clicks + likes + shares)/NULLIF(impressions,0))*100,0) as ER from adverity.adverity."Marketing_Data";
    '''
    df = pd.read_sql(queryAll, session)
    return df

def formatBigNumber(number):
    units = ['', 'K', 'M', 'G', 'T', 'P']
    k = 1000.0
    magnitude = int(floor(log(number, k)))
    return '%.2f%s' % (number / k**magnitude, units[magnitude])

def getCard(text,val,icon, compare=False):
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
        return hc.info_card(key=key,title=val, title_text_size="16vw",content=str(text),content_text_size="10vw",icon_size=icoSize,theme_override=style)
    else:
        return hc.info_card(key=key,title=val, title_text_size="16vw",content=str(text),content_text_size="10vw",icon_size=icoSize,theme_override=style,bar_value=100)    

def getGlobalKPI(dt,kpi,op='sum'):
    if op=='sum':
        return dt[kpi].sum()
    if op=='mean':
        return dt[kpi].mean()

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
        height=640,
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
            st.metric(label=row['index'].replace('_',' ').replace('VIDEO QUARTILE','').replace('VIEWS','% VIEWED'), value='{:,}'.format(row[0]))

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
        height=650,
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

def getPage(sess):
    global session 
    session = sess
    df=getVideoKPI(getRawCampaign())
    vws=df[df["index"] == "VIEWS"][0].iloc[0]
    vws25=df[df["index"] == "VIDEO_QUARTILE_25_VIEWS"][0].iloc[0]
    vws50=df[df["index"] == "VIDEO_QUARTILE_50_VIEWS"][0].iloc[0]
    vws75=df[df["index"] == "VIDEO_QUARTILE_75_VIEWS"][0].iloc[0]
    vwsComp=df[df["index"] == "VIDEO_COMPLETIONS"][0].iloc[0]
    col1,col2,col3,col4,col5=st.columns(5)
    with col1:
        getCard("TOTAL VIEWED",str(formatBigNumber(vws)), "fa fa-video")
    with col2:
        getCard("25% VIEWED",str(formatBigNumber(vws25)), "")
    with col3:
        getCard("50% VIEWED",str(formatBigNumber(vws50)), "")
    with col4:
        getCard("75% VIEWED",str(formatBigNumber(vws75)), "")
    with col5:
        getCard("COMPLETE VIEW",str(formatBigNumber(vwsComp)), "fa fa-film")                

    colF,colK=st.columns([3,3])
    with colF:
        getChartVideoFunnel(getVideoFunnel(getRawCampaign()))
    with colK:
        getChartVideoByCampaign(getVideoCompletionDrillDown(getRawCampaign()))