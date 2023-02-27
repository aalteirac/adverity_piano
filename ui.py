import streamlit as st


def setUI():
    st.markdown('''
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
''', unsafe_allow_html=True)