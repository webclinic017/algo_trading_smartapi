import streamlit as st
import datetime
import time
st.set_page_config(page_title="Algo App",layout="wide",initial_sidebar_state="expanded", )
st.header("Welcome Ganesh Panpat")
current_time=st.empty()
col1,col2=st.columns(2,[0.05,0.95])
with col1:
  st.button("HI")
with col2:
  st.button("Ganesh")
for i in range(60):
  current_time.text(datetime.datetime.now().replace(microsecond=0))
  time.sleep(1)
