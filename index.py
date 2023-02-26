from streamlit_option_menu import option_menu
import main,campaign
from ui import setUI
import streamlit.components.v1 as components
import snowflake.connector as sf
import streamlit as st

@st.cache_resource(ttl=1000)
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


page = option_menu("Piano-Adverity-Snowflake", ["Home", "Campaigns"],
                   icons=['house', 'binoculars-fill', "list-task",'door-open'],
                   menu_icon="search", default_index=0, orientation="horizontal",
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
if page == 'Home':
    main.getPage(getSession())
if page == 'Campaigns':
    campaign.getPage(getSession())    