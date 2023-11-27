import streamlit as st
import datetime
import time
st.set_page_config(page_title="Algo App",layout="wide",initial_sidebar_state="expanded", )
st.header("Welcome Ganesh Panpat")
current_time=st.empty()
col1, col2 = st.columns(2)
with col1:
   st.header("A cat")
with col2:
   st.header("A dog")
for i in range(60):
  current_time.text(datetime.datetime.now().replace(microsecond=0))
  time.sleep(1)
