import streamlit as st
import pandas as pd

session=None


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
                                      'CTR':"mean"})

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


def getPage(sess):
    global session 
    session = sess
    st.write(getGlobalKPI( getRawCampaign(),'IMPRESSIONS','sum'))
    st.write(getGlobalKPI( getRawCampaign(),'CLICKS','sum'))
    st.write(getGlobalKPI( getRawCampaign(),'CTR','mean'))
    st.write(getKPIByMonth(getRawCampaign()))
    st.write(getCTRByGenderByAge(getRawCampaign()))
    st.write(getCTRByDevice(getRawCampaign()))
    st.write(getKPIByCampaignAds(getRawCampaign()))
    st.write(getTopBottomAds(getRawCampaign()))
    st.write(getTopBottomAds(getRawCampaign(),True))
    st.write(getVideoFunnel(getRawCampaign()))
    st.write(getVideoKPI(getRawCampaign()))
    st.write(getVideoCompletionDrillDown(getRawCampaign()))