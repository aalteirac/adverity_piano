from streamlit_option_menu import option_menu
import main,campaign, campaign2,campaign3, campaign4
from ui import setUI
import streamlit.components.v1 as components
import snowflake.connector as sf
import streamlit as st
import hydralit_components as hc
import time


@st.cache_resource(ttl=2500)
def getSession():
    session = sf.connect(**st.secrets.snow)
    return session

page = option_menu("Piano-Adverity-Snowflake", ["Home", "Campaigns Overview","Ads Performance","Video Deep Dive","Country Performance"],
                   icons=['house', 'binoculars-fill', "list-task",'camera-reels','map'],
                   menu_icon="window", default_index=0, orientation="horizontal",
                   styles={
                       "container": {"max-width": "100%!important","--primary-color":"#4a4d4f","--text-color":"#30333f"},
                       "nav-link": {"font-weight": "600"},
                       "menu-title" :{"font-weight": "600"},
                       "nav-link": {"font-size": "1.14vw","font-weight": "600"}
                       # "margin":"0px", "--hover-color": "#eee"}
                       # "container": {"padding": "0!important", "background-color": "#fafafa"}, "icon": {"color":
                       # "orange", "font-size": "25px"}, "nav-link": {"font-size": "25px", "text-align": "left",
                       # "margin":"0px", "--hover-color": "#eee"}, "nav-link-selected": {"background-color": "green"},
                   }
                   )

emp=st.empty()

setUI()
emp.markdown('<p class="big-font">🕜</p>', unsafe_allow_html=True)
if page == 'Home':
    main.getPage(getSession())
if page == 'Campaigns Overview':
    campaign.getPage(getSession())    
if page == 'Ads Performance':
    campaign2.getPage(getSession()) 
if page == 'Video Deep Dive':
    campaign3.getPage(getSession())      
if page == 'Country Performance':
    campaign4.getPage(getSession())        
emp.empty()
# menu_data = [
#     {'id':'Home','icon':"🐙",'label':"Home"},
#     {'id':'Campaigns','icon': "💀", 'label':"Campaigns"},
# ]
# over_theme = {'txc_inactive': '#FFFFFF'}
# menu_id = hc.nav_bar(
#     menu_definition=menu_data,
#     override_theme=over_theme,
#     hide_streamlit_markers=False, #will show the st hamburger as well as the navbar now!
#     sticky_nav=True, #at the top or not
#     sticky_mode='pinned', #jumpy or not-jumpy, but sticky or pinned
# )
# if menu_id=='Home':
#     main.getPage(getSession())
# if menu_id=='Campaigns':
#     campaign.getPage(getSession())     