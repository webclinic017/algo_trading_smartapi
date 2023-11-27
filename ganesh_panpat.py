import streamlit as st
import datetime
import time
st.header("Welcome Ganesh Panpat")
current_time=st.empty()
for i in range(60):
  current_time.text(datetime.datetime.now().replace(microsecond=0))
  time.sleep(1)
