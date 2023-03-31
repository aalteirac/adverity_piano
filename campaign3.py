import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from math import log, floor
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode, GridUpdateMode
from streamlit_kpi import streamlit_kpi
import numbers


session=None

@st.cache_data(show_spinner=False,ttl=5000)
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

def getCard(text,val,icon, key,compare=False,titleTextSize="16vw",content_text_size="10vw",unit="%",height='100',iconLeft=95,iconTop=90,backgroundColor='#f0f2f6'):
    pgcol='green'
    if isinstance(val, numbers.Number):
        if val<0:
            pgcol='red'
    if compare==False:
        pgcol='darkgrey'
    style={'icon': icon,'icon_color':'#535353','progress_color':pgcol}
    icoSize="20vw"
    if compare==False:
        streamlit_kpi(key=key+"_n",height=height,title=text,value=val,icon=icon,unit=unit,iconLeft=iconLeft,showProgress=False,iconTop=iconTop,backgroundColor=backgroundColor)
    else:
        streamlit_kpi(key=key+"_n",height=height,title=text,value=val,icon=icon,progressValue=100,unit=unit,iconLeft=iconLeft,showProgress=True,progressColor=pgcol,iconTop=iconTop,backgroundColor=backgroundColor)  
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
        height=500,
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
        height=470,
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
    fig.update_layout(yaxis_range=[df['VIDEO_COMPLETIONS'].min() - (df['VIDEO_COMPLETIONS'].min()/20),df['VIDEO_COMPLETIONS'].max()]) #yaxis_range=[1.2,1.25]
    st.plotly_chart(fig,config=config, theme="streamlit",use_container_width=True)

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

def getEuroRendererCPV():
    rd = JsCode('''
        function(params) { 
            var color='red';
            if(params.value<=0.15)
                color="green";
            if(params.value>0.15 && params.value<0.20)
                color="#ffc700";  
            return '<span style="color:'+color + '">' + parseFloat(params.value).toFixed(2) + '€</span>'}
    ''') 
    return rd  

def getEuroRendererCPCV():
    rd = JsCode('''
        function(params) { 
            var color='red';
            if(params.value<=2)
                color="green";
            if(params.value>2 && params.value<3)
                color="#ffc700";  
            return '<span style="color:'+color + '">' + parseFloat(params.value).toFixed(2) + '€</span>'}
    ''') 
    return rd  

def customAggCPV():
    rd=JsCode('''
    function(params) {
                if (params.node.data){
                    return params.node.data.COSTS/params.node.data.VIEWS;
                }
                return params.node.aggData.COSTS/params.node.aggData.VIEWS;
            }
    ''')
    return rd

def customAggCPCV():
    rd=JsCode('''
    function(params) {
                if (params.node.data){
                    return params.node.data.COSTS/params.node.data.VIDEO_COMPLETIONS;
                }
                return params.node.aggData.COSTS/params.node.aggData.VIDEO_COMPLETIONS;
            }
    ''')
    return rd

def getTableCountryPerf(df):
    ob = GridOptionsBuilder.from_dataframe(df)
    ob.configure_column('COUNTRY_NAME', rowGroup=True,hide= True,sortable=True,showRowGroup= 'country', cellRenderer= 'agGroupCellRenderer')
    ob.configure_column('CAMPAIGN', rowGroup=True,hide= True)
    ob.configure_column('AD_TYPE', rowGroup=True,hide= True)
    ob.configure_column('AD_NAME',rowGroup=True,hide= True)
    ob.configure_column('CTR', aggFunc='avg',header_name='CTR(%)',cellRenderer= getPercentRenderer())
    ob.configure_column('VIEWS', aggFunc='sum', header_name='VIDEO VIEWS')
    ob.configure_column('COSTS', aggFunc='sum', header_name='COSTS',hide= True)
    ob.configure_column('CPVMANUAL',valueGetter=customAggCPV(),header_name='COST PER VIDEO VIEW',cellRenderer=getEuroRendererCPV())
    ob.configure_column('CPCVMANUAL', valueGetter=customAggCPCV(),header_name='COST PER VIDEO COMPLETED',cellRenderer=getEuroRendererCPCV())
    ob.configure_column('VIDEO_COMPLETIONS', aggFunc='sum', header_name='VIDEO COMPLETIONS')    
    ob.configure_grid_options(suppressAggFuncInHeader = True)
    custom_css = {
        ".ag-row-level-3 .ag-group-expanded, .ag-row-level-3 .ag-group-contracted":{
            "display":"none!important",
        },
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
    # "cellRendererSelector":getRenderLeaf(),
    "cellRendererParams": {
        "suppressDoubleClickExpand": True,  
        "suppressCount": True,
    },
    }
    AgGrid(df, gripOption, enable_enterprise_modules=True,fit_columns_on_grid_load=True,height=342,custom_css=custom_css,allow_unsafe_jscode=True, update_mode=GridUpdateMode.NO_UPDATE )

def divide_two_cols(df_sub):
    df_sub['CPVMANUAL']=df_sub['COSTS'].sum() / df_sub['VIEWS'].sum()
    return df_sub

def getKPIByCountry(df):
    df=df.groupby(['COUNTRY_NAME', 'CAMPAIGN','AD_TYPE', 'AD_NAME']).agg({
                            'VIDEO_COMPLETIONS':'sum',
                            'VIEWS':'sum',
                            'COSTS':'sum',
                            'CTR':"mean",
                            }).reset_index()
    df['CPVMANUAL']=0
    df['CPCVMANUAL']=0
    df= df[['COUNTRY_NAME', 'CAMPAIGN','AD_TYPE', 'AD_NAME','CTR', 'VIEWS','COSTS','CPVMANUAL','VIDEO_COMPLETIONS','CPCVMANUAL']].sort_values(['COUNTRY_NAME'])
    return df

def getPage(sess):
    global session 
    session = sess
    df=getVideoKPI(getRawCampaign())
    vws=df[df["index"] == "VIEWS"][0].iloc[0]
    vws25=df[df["index"] == "VIDEO_QUARTILE_25_VIEWS"][0].iloc[0]
    vws50=df[df["index"] == "VIDEO_QUARTILE_50_VIEWS"][0].iloc[0]
    vws75=df[df["index"] == "VIDEO_QUARTILE_75_VIEWS"][0].iloc[0]
    vwsComp=df[df["index"] == "VIDEO_COMPLETIONS"][0].iloc[0]
    colMain1,colMain2=st.columns([2,3])
    with colMain1:
        getChartVideoFunnel(getVideoFunnel(getRawCampaign()))
    with colMain2:    
        col1,col2,col3,col4,col5=st.columns(5)
        with col1:
            getCard("TOTAL VIEWED",str(formatBigNumber(vws)), "fa fa-video",key='one')
        with col2:
            getCard("25% VIEWED",str(formatBigNumber(vws25)), "",key='two')
        with col3:
            getCard("50% VIEWED",str(formatBigNumber(vws50)), "",key='three')
        with col4:
            getCard("75% VIEWED",str(formatBigNumber(vws75)), "",key='four')
        with col5:
            getCard("COMPLETE VIEW",str(formatBigNumber(vwsComp)), "fa fa-film",key='five')                
        getChartVideoByCampaign(getVideoCompletionDrillDown(getRawCampaign()))
    getTableCountryPerf(getKPIByCountry(getRawCampaign()))
