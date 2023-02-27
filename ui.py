import streamlit as st
import streamlit.components.v1 as components

def setUI():
    style=''' 
        <style>
            .stApp header{
                display:none;
            }
            .big-font {
                font-size:34vw !important;
                color:"darkgrey";
                opacity:0.1;
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
        </style>
        '''
    hvar='''
        <script>
            function debounce(func, wait, immediate) {
                // 'private' variable for instance
                // The returned function will be able to reference this due to closure.
                // Each call to the returned function will share this common timer.
                var timeout;

                // Calling debounce returns a new anonymous function
                return function() {
                    // reference the context and args for the setTimeout function
                    var context = this,
                    args = arguments;

                    // Should the function be called now? If immediate is true
                    //   and not already in a timeout then the answer is: Yes
                    var callNow = immediate && !timeout;

                    // This is the basic debounce behaviour where you can call this 
                    //   function several times, but it will only execute once 
                    //   [before or after imposing a delay]. 
                    //   Each time the returned function is called, the timer starts over.
                    clearTimeout(timeout);

                    // Set the new timeout
                    timeout = setTimeout(function() {

                    // Inside the timeout function, clear the timeout variable
                    // which will let the next execution run when in 'immediate' mode
                    timeout = null;

                    // Check if the function already ran with the immediate flag
                    if (!immediate) {
                        // Call the original function with apply
                        // apply lets you define the 'this' object as well as the arguments 
                        //    (both captured before setTimeout)
                        func.apply(context, args);
                    }
                    }, wait);

                    // Immediate mode and no wait timer? Execute the function..
                    if (callNow) func.apply(context, args);
                }
                }
            function hide(){
                //console.log("HIDE")
                window.parent.document.querySelector(".main").scrollTop = 0;
                window.parent.document.querySelector(".main").style.overflow="hidden";
               
            }
            window.parent.document.addEventListener("DOMNodeInserted", 
                debounce((e) => {
                    //if (e.target && e.target.classList && e.target.classList.contains("element-container")  ){
                        hide();
                    //}    
                    setTimeout(()=>{
                            window.parent.document.querySelector(".main").style.overflow="auto";
                            window.parent.document.querySelector(".main").scrollTop = 0;
                            setTimeout(()=>{
                                toHide=window.parent.document.querySelectorAll('iframe[height="0"]')
                                for (const iframe of toHide) {
                                    
                                    iframe.parentElement.style.display="none"
                                }
                            },5000)
                        }
                    ,2000)
                },500,true)
                , true);      
        </script>
        '''
    st.markdown(style, unsafe_allow_html=True)
    components.html(hvar, height=0, width=0)
