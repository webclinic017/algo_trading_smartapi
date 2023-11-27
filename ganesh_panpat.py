import streamlit as st
import datetime
import time
import pandas as pd
import numpy as np
st.set_page_config(page_title="Algo App",layout="wide",initial_sidebar_state="expanded", )
current_time=st.empty()
c1,c2=st.columns([2,8])
with c1:
   col1, col2 = st.columns(2)
   with col1:
      nf_ce=st.button(label="NF CE")
      bnf_ce=st.button(label="BNF CE")
   with col2:
      nf_pe=st.button(label="NF PE")
      bnf_pe=st.button(label="BNF PE")
with c2:
   st.table(pd.DataFrame(np.random.randn(10, 20), columns=("col %d" % i for i in range(20))))
if 'user_name' not in st.session_state:
   st.session_state['user_name']="Guest"
   st.session_state['user_name']="Guest"
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
def get_user_pwd(user):
  if user=='Ganesh': username = 'G93179'; pwd = '4789'; apikey = 'CjOKjC5g'; token='U4EAZJ3L44CNJHNUZ56R22TPKI'
  elif user=='Kalyani': username = 'K205244'; pwd = '4789'; apikey = 'lzC7yJmt'; token='YDV6CJI6BEU3GWON7GZTZNU3RM'
  elif user=="Akshay": username='A325394'; pwd='1443'; apikey='OeSllszj'; token='G4OKBQKHXPS67EN2WMVP3TZ7X4'
  return username,pwd,apikey,token,user
username,pwd,apikey,token,user=get_user_pwd("Ganesh")
obj=SmartConnect(api_key=apikey)
def angel_login():
   try:
      FEED_TOKEN = None;TOKEN_MAP = None;SMART_API_OBJ = None
      global user_name
      data = obj.generateSession(username,pwd,pyotp.TOTP(token).now())
      refreshToken= data['data']['refreshToken']
      feedToken=obj.getfeedToken()
      userProfile= obj.getProfile(refreshToken)
      aa= userProfile.get('data')
      st.session_state['user_name']=aa.get('name').title()
      st.session_state['login_time']=datetime.datetime.now()
      print('Welcome',aa.get('name').title(),'...')
      user=aa.get('name').title().split(' ')[0]
   except Exception as e:
       print("Unable to login",e)
angel_login()
st.header(f"Welcome {st.session_state['user_name']}!!!")
