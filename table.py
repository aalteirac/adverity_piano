import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode, GridUpdateMode
import pandas as pd
import numpy as np


df = pd.DataFrame({
    'Name': ['Alice','Alice', 'Bob','Bob'],
    'Day': ['Monday','Tuesday','Monday','Tuesday'],
    'Miles': [2.1,4,1.2,4.3]
})

ob = GridOptionsBuilder.from_dataframe(df)
ob.configure_column('Name', rowGroup=True)
ob.configure_column('Day', rowGroup=True)
ob.configure_column('Miles', aggFunc='sum')


st.markdown('# AgGrid')
AgGrid(df, ob.build(), enable_enterprise_modules=True)