import streamlit as st
import datetime
import time
st.set_page_config(page_title="Algo App",layout="wide",initial_sidebar_state="expanded", )
st.header("Welcome Ganesh Panpat")
current_time=st.empty()
c1,c2=st.columns[1,9]
with c1:
   col1, col2 = st.columns(2)
   with col1:
      nf_ce=st.button(label="NF CE")
      bnf_ce=st.button(label="BNF CE")
   with col2:
      nf_pe=st.button(label="NF PE")
      bnf_pe=st.button(label="BNF PE")
with c2:
   st.write("How Are you")
for i in range(60):
  current_time.text(datetime.datetime.now().replace(microsecond=0))
  time.sleep(1)
