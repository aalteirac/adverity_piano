import streamlit as st
import pandas as pd
import string
import random
import hydralit_components as hc
from math import log, floor
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

@st.cache_data(show_spinner=False)
def getRawCampaign():
    queryAll=f'''
    SELECT *,to_date(TO_VARCHAR(DAY, 'yyyy-MM-01')) as MONTH,coalesce((clicks/NULLIF(impressions,0))*100,0) as CTR,coalesce(((clicks + likes + shares)/NULLIF(impressions,0))*100,0) as ER from adverity.adverity."Marketing_Data";
    '''
    df = pd.read_sql(queryAll, session)
    return df

def getTotalCost(df):
    return df['COSTS'].sum()

def getCountrySelectionBox(raw):
    raw=raw.sort_values(['COUNTRY_NAME'])
    return st.multiselect(
        'Compare with:',
    raw['COUNTRY_NAME'].unique(),default=raw['COUNTRY_NAME'].unique(),key="country")

def getCampaignSelectionBox(map):
    return st.multiselect(
        'Marketing Campaign:',
    map['CAMPAIGN'].unique(),default=map['CAMPAIGN'].unique(),key='campaign')

def getPage(sess):
    global session 
    session = sess
    dt=getRawCampaign()
    orig=dt.copy()
    countries=st.session_state.get('country') 
    campaings=st.session_state.get('campaign') 
    if countries is not None:
        dt=dt[dt["COUNTRY_NAME"].isin(countries)]
        dt=dt[dt["CAMPAIGN"].isin(campaings)]
    totalcost=getTotalCost(dt)
    # st.write(dt)
    colL,colR=st.columns([1,3])
    with colL:
        getCard("TOTAL COST",formatBigNumber(totalcost),'fa fa-money-bill')
    with colR:
        # st.write(dt)
        # with st.form(key='fil'):
            countr=getCountrySelectionBox(orig) 
            campaig=getCampaignSelectionBox(orig)
            # st.session_state['countries']=countries
            # if st.form_submit_button():
                # print('ok')