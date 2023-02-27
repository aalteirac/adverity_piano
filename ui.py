import streamlit as st
import streamlit.components.v1 as components

def setUI():
    hvar='''
        <script>
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
            function hide(){
                window.parent.document.querySelector(".main").scrollTop = 0;
                window.parent.document.querySelector(".main").style.overflow="hidden";
               
            }
            window.parent.document.addEventListener("DOMNodeInserted", 
                debounce((e) => {
                    //if (e.target && e.target.classList && (e.target.classList.contains("element-container") || e.target.classList.contains("stHorizontalBlock") ) ){
                        hide();
                        //console.log('TEST')
                    //}    
                    setTimeout(()=>{
                            window.parent.document.querySelector(".main").style.overflow="auto";
                            window.parent.document.querySelector(".main").scrollTop = 0;
                            setTimeout(()=>{
                                toHide=window.parent.document.querySelectorAll('iframe[height="0"]')
                                for (const iframe of toHide) {
                                    if(iframe.hasAttribute("srcdoc"))
                                        iframe.parentElement.style.display="none"
                                }
                            },1000)
                        }
                    ,1000)
                },1000,true)
                , true);   

            var my_style= window.parent.document.createElement('style');
            my_style.innerHTML=`
                .stApp header{
                display:none;
                }
                @keyframes append-animate {
                    from {
                        transform: scale(0);
                        opacity: 0;
                    }
                    to {
                        transform: scale(1);
                        opacity: 1;	
                    }
                }
                @keyframes rotating {
                    from {
                        transform: rotate(0deg);
                    }
                    to {
                        transform: rotate(360deg);
                    }
                }
                .stMarkdown p {
                    animation: rotating 2s linear infinite;
                }
                iframe{
                    transform-origin: 50% 0;
	                animation: append-animate .9s linear;
                }
                .big-font {
                    font-size:34vw !important;
                    color:"darkgrey";
                    opacity:0.05;
                    text-align:center;
                }
                .streamlit-expanderHeader p{
                    font-size: x-large;
                }
                .main .block-container{
                    max-width: unset;
                    padding-left: 5em;
                    padding-right: 5em;
                    padding-top: 0em;
                    padding-bottom: 1em;
                    }
                [data-testid="stMetricDelta"] > div:nth-child(2){
                    justify-content: center;
                }
                        `;
                window.parent.document.head.appendChild(my_style);       
        </script>
        '''
    components.html(hvar, height=0, width=0)
