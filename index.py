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

setUI()
hvar = """  <script>
                function debounce(func, wait, immediate) {
                    var timeout;
                    return function() {
                        var context = this,
                        args = arguments;
                        var callNow = immediate && !timeout;
                        clearTimeout(timeout);
                        timeout = setTimeout(function() {
                            timeout = null;
                            if (!immediate) {
                                func.apply(context, args);
                            }
                        }, wait);
                        if (callNow) func.apply(context, args);
                    }
                }

                function fade(e){
                    e.style.transition = "opacity 0s";
                    e.style.opacity="0.01";
                    //window.parent.document.body.style.transition = "opacity 0s";
                    //window.parent.document.body.style.opacity="0.01";
                    setTimeout(()=>{
                        e.style.transition = "opacity 0.4s";
                        e.style.opacity="1";
                        //window.parent.document.body.style.position="static";
                        //window.parent.document.body.style.left="0px";
                        load=false;
                    },800)
                }
                var load;
                 window.parent.document.addEventListener("DOMNodeInserted", function (e) {
                                if (e.target && e.target.classList && (e.target.classList.contains("element-container") || e.target.classList.contains("stHorizontalBlock")))
                                    fade(e.target)
                                //debounce(fade,1000,true)
                                }
                              , true);      
                var my_awesome_script = window.parent.document.createElement('script');
                my_awesome_script.innerHTML=`
                        var load;
                        document.addEventListener("DOMNodeInserted", function (event) {
                            
                        }, false);`;
                //window.parent.document.head.appendChild(my_awesome_script);

    
            </script> """


page = option_menu("Piano-Adverity-Snowflake", ["Home", "Campaigns Overview","Ads Performance","Video Deep Dive","Country Performance"],
                   icons=['house', 'binoculars-fill', "list-task",'camera-reels','map'],
                   menu_icon="window", default_index=0, orientation="horizontal",
                   styles={
                       "container": {"max-width": "100%!important","--primary-color":"#4a4d4f","--text-color":"#30333f"},
                       "nav-link": {"font-weight": "600"},
                       "menu-title" :{"font-weight": "600"}
                       # "container": {"padding": "0!important", "background-color": "#fafafa"}, "icon": {"color":
                       # "orange", "font-size": "25px"}, "nav-link": {"font-size": "25px", "text-align": "left",
                       # "margin":"0px", "--hover-color": "#eee"}, "nav-link-selected": {"background-color": "green"},
                   }
                   )
# components.html(hvar, height=0, width=0)


emp=st.empty()
st.markdown("""
<style>
.big-font {
    font-size:30vw !important;
    color:"darkgrey";
}
</style>
""", unsafe_allow_html=True)
emp.markdown('<p class="big-font">LOAD...</p>', unsafe_allow_html=True)
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