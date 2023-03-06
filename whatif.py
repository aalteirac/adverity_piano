import streamlit as st
import pandas as pd
import string
import random
import hydralit_components as hc
from math import log, floor
from sklearn.cluster import KMeans
import plotly.express as px
import numpy as np

session=None

def formatBigNumber(number):
    if number==0.0:
        return 0
    units = ['', 'K', 'M', 'G', 'T', 'P']
    k = 1000.0
    magnitude = int(floor(log(number, k)))
    return '%.3f%s' % (number / k**magnitude, units[magnitude])


def getCard(text,val,icon, compare=False):
    letters = string.ascii_lowercase
    key = ''.join(random.choice(letters) for i in range(8))
    pgcol='green'
    if '-' in text:
        pgcol='red'
    if compare==False:
        pgcol='darkgrey'
    style={'icon': icon,'icon_color':'#535353','progress_color':pgcol}
    icoSize="17vw"
    if compare==False:
        return hc.info_card(key=key,title=val, title_text_size="13vw",content=str(text),content_text_size="8vw",icon_size=icoSize,theme_override=style)
    else:
        return hc.info_card(key=key,title=val, title_text_size="13vw",content=str(text),content_text_size="10vw",icon_size=icoSize,theme_override=style,bar_value=100)    

@st.cache_data(show_spinner=False,ttl=5000)
def getRawCampaign():
    queryAll=f'''
    SELECT *,to_date(TO_VARCHAR(DAY, 'yyyy-MM-01')) as MONTH,coalesce((clicks/NULLIF(impressions,0))*100,0) as CTR,coalesce(((clicks + likes + shares)/NULLIF(impressions,0))*100,0) as ER from adverity.adverity."Marketing_Data";
    '''
    df = pd.read_sql(queryAll, session)
    return df

def getTotalCost(df):
    return df['COSTS'].sum()

def getCountrySelectionBox(raw,selec):
    raw=raw.sort_values(['COUNTRY_NAME'])
    return st.multiselect(
        'Remove Country to estimate saving:',
    raw['COUNTRY_NAME'].unique(),default=selec.sort_values(['COUNTRY_NAME'])['COUNTRY_NAME'].unique(),key="country")

def getCampaignSelectionBox(map,selec):
    return st.multiselect(
        'Remove Campaign to estimate saving:',
    map['CAMPAIGN'].unique(),default=selec.sort_values(['CAMPAIGN'])['CAMPAIGN'].unique(),key='campaign')

def reset():
    st.session_state['reset']=True


def getPage(sess):
    global session 
    session = sess
    dt=getRawCampaign()
    orig=dt.copy()
    countries=st.session_state.get('country') 
    campaings=st.session_state.get('campaign') 
    allCountries=orig['COUNTRY_NAME'].unique()
    allCampaign=orig['CAMPAIGN'].unique() 
    

    clusterSelected=st.session_state.get('clusterstore')
    if st.session_state.get('clusNum') is not None:
        kmeans = KMeans(init="random", n_clusters=st.session_state.get('clusNum'), n_init=10, random_state=1)
    else:
        kmeans = KMeans(init="random", n_clusters=5, n_init=10, random_state=1)
    clusterDF=orig.groupby(['COUNTRY_NAME']).agg({
                                    'CTR':"mean",
                                    'ER':'mean',
                                    'VIDEO_COMPLETION_RATE':'mean'
                                    }).reset_index()
    kmeans.fit(clusterDF[['CTR','ER','VIDEO_COMPLETION_RATE']])  

    clusterDF['VIDEO_COMPLETION_RATE']=clusterDF['VIDEO_COMPLETION_RATE']*100
    clusterDF['CLUSTER'] = kmeans.labels_ 
    clusterDF['CLUSTER']  = clusterDF['CLUSTER'].astype(str)
    clusterDF=clusterDF.sort_values(['CLUSTER'])

    if clusterSelected is None:
        if countries is None:
            countries=dt['COUNTRY_NAME'].unique()
            campaings=dt['CAMPAIGN'].unique()  
        else:    
            dt=dt[dt["COUNTRY_NAME"].isin(countries)]
            dt=dt[dt["CAMPAIGN"].isin(campaings)]
    elif len(clusterSelected)==0:
        dt=dt[dt["COUNTRY_NAME"].isin(countries)]
        dt=dt[dt["CAMPAIGN"].isin(campaings)]   
    elif len(clusterSelected)>0:
         dt=pd.merge(dt, clusterDF[~clusterDF['CLUSTER'].isin(list(map(str, clusterSelected)))],on=["COUNTRY_NAME"])
         countries=dt['COUNTRY_NAME'].unique()
         campaings=dt['CAMPAIGN'].unique()    


    totalcost=getTotalCost(dt)
    totalcostOrig=getTotalCost(orig)
    compared=(1-((totalcost/totalcostOrig)))*100
    colL,colR=st.columns([1,3])
    with colL:
        getCard("ORIGINAL COST",formatBigNumber(totalcostOrig),'fa fa-money-bill')  
        getCard('SAVING: '+ str(round(compared,2))+'%',formatBigNumber(totalcostOrig - totalcost), 'fa fa-piggy-bank',True)  
        st.slider('Cluster Number',2,10,value=5,key='clusNum')
        clus=st.empty()
       
       
    with colR:
        st.subheader("Estimate Saving by Canceling Campaigns in Countries"  ) 
        getCountrySelectionBox(orig,dt) 
        getCampaignSelectionBox(orig,dt)  
        st.subheader("Clustering Countries by ER, CTR and Video Completion"  )       
        clus.multiselect('Exclude Cluster (Preempts All Other Exclusions):',np.unique(kmeans.labels_),key='clusterstore')
        
        fig = px.scatter(
            clusterDF,
            y="CTR",
            size="ER",
            x='VIDEO_COMPLETION_RATE',
            color="CLUSTER",
            hover_name="COUNTRY_NAME",
            size_max=30,
            height=430
        ) 
        st.plotly_chart(fig, theme="streamlit",use_container_width=True)   