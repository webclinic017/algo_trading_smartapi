from SmartApi import SmartConnect
from SmartApi import SmartWebSocket
import threading; import pandas as pd
import pandas_ta as pdta
import json
import requests
import datetime
from dateutil.tz import gettz
import time
import math
import numpy
import warnings
import yfinance as yf
import sys
import pyotp
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import datetime
from dateutil.tz import gettz
import time
import pandas as pd
import yfinance as yf
import math
NoneType = type(None)
pd.set_option('mode.chained_assignment', None)
st.set_page_config(page_title="Algo App",layout="wide",initial_sidebar_state="expanded",)
st.markdown("""
  <style>
    .block-container {padding-top: 0.5rem;padding-bottom: 0rem;padding-left: 2rem;padding-right: 5rem;}  
  </style>
  """, unsafe_allow_html=True)
user="Ganesh"
if 'algo_state' not in st.session_state:st.session_state['algo_state']="Not Running"
if 'algo_last_run' not in st.session_state:st.session_state['algo_last_run']="Not Running"
def get_user_pwd(user):
  if user=='Ganesh': username = 'G93179'; pwd = '4789'; apikey = 'CjOKjC5g'; token='U4EAZJ3L44CNJHNUZ56R22TPKI'
  elif user=='Kalyani': username = 'K205244'; pwd = '4789'; apikey = 'lzC7yJmt'; token='YDV6CJI6BEU3GWON7GZTZNU3RM'
  elif user=="Akshay": username='A325394'; pwd='1443'; apikey='OeSllszj'; token='G4OKBQKHXPS67EN2WMVP3TZ7X4'
  return username,pwd,apikey,token
username,pwd,apikey,token=get_user_pwd(user)
if 'user_name' not in st.session_state:
    obj=SmartConnect(api_key=apikey)
    obj.generateSession(username,pwd,pyotp.TOTP(token).now())
    st.write('Login Sucess')
    feedToken=obj.getfeedToken()
    userProfile= obj.getProfile(obj.refresh_token)
    aa= userProfile.get('data')
    st.session_state['user_name']=aa.get('name')
    st.session_state['login_time']=datetime.datetime.now(tz=gettz('Asia/Kolkata')).replace(microsecond=0, tzinfo=None).time()
    st.session_state['access_token']=obj.access_token
    st.session_state['refresh_token']=obj.refresh_token
    st.session_state['feed_token']=obj.feed_token
    st.session_state['userId']=obj.userId
    st.session_state['api_key']=apikey
obj=SmartConnect(api_key=st.session_state['api_key'],access_token=st.session_state['access_token'],
                 refresh_token=st.session_state['refresh_token'],feed_token=st.session_state['feed_token'],userId=st.session_state['userId'])
st.header(f"Welcome {st.session_state['user_name']}")
last_login=st.empty()
last_login.text(f"Login: {st.session_state['login_time']} Algo: {st.session_state['algo_state']} Last run : {st.session_state['algo_last_run']}")
placeholder = st.empty()
placeholder.text("LTP")
col1,col2=st.columns([1,9])
with col1:
  st.write("Manu:")
  nf_ce=st.button("NF CE")
  bnf_ce=st.button("BNF CE")
  nf_pe=st.button("NF PE")
  bnf_pe=st.button("BNF PE")
  close_all=st.button("Close All")
  algo_state=st.checkbox("Run Algo")
with col2:
  tab1, tab2, tab3, tab4= st.tabs(["Order_Book", "Position","Algo Trade", "Settings"])
  with tab1:order_datatable=st.empty()
  with tab2:position_datatable=st.empty()
  with tab3:algo_datatable=st.empty()
  with tab4:
    buy_indicator = st.multiselect('Select Buy Indicator',['St Trade', 'ST_10_2 Trade', 'RSI MA Trade', 'RSI_60 Trade'],
                                   ['St Trade', 'ST_10_2 Trade', 'RSI MA Trade', 'RSI_60 Trade'])
    time_frame = st.multiselect('Select Time Frame',['IDX:5M', 'IDX:15M', 'OPT:5M', 'OPT:15M','IDX:1M'],
                                   ['IDX:5M', 'IDX:15M', 'OPT:5M'])
    col1_tab4,col2_tab4,col3_tab4,col4_tab4,col5_tab4=st.columns(5)
    with col1_tab4:
      banknifty_target=st.number_input(label="Bank Nifty Target",min_value=10, max_value=100, value=10, step=None)
      nifty_target=st.number_input(label="Nifty Target",min_value=5, max_value=100, value=5, step=None)
    with col2_tab4:
      banknifty_sl=st.number_input(label="Bank Nifty SL",min_value=10, max_value=100, value=10, step=None)
      nifty_sl=st.number_input(label="Nifty SL",min_value=5, max_value=100, value=5, step=None)
    with col3_tab4:
      target_order_type = st.selectbox('Target Order',('Target', 'Stop_Loss', 'NA'),1)
      lots_to_trade=st.number_input(label="Lots To Trade",min_value=1, max_value=10, value=1, step=None)
