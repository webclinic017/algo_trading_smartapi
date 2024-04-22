import streamlit as st
st.set_page_config(page_title="Algo App",layout="wide",initial_sidebar_state="expanded",)
st.markdown("""
  <style>
    .block-container {padding-top: 0.5rem;padding-bottom: 0rem;padding-left: 2rem;padding-right: 5rem;}
  </style>
  """, unsafe_allow_html=True)
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
from logzero import logger
import re

username = 'G93179'; pwd = '4789'; apikey = 'Rz6IiOsd'; token='U4EAZJ3L44CNJHNUZ56R22TPKI'
obj=SmartConnect(api_key=apikey)
for attempt in range(3):
    try:
      FEED_TOKEN = None;TOKEN_MAP = None;SMART_API_OBJ = None
      global user_name,feedToken
      data = obj.generateSession(username,pwd,pyotp.TOTP(token).now())
      refreshToken= data['data']['refreshToken']
      feedToken=obj.getfeedToken()
      userProfile= obj.getProfile(refreshToken)
      aa= userProfile.get('data')
      st.user_name=aa.get('name').title()
      print(f"Welcome {aa.get('name').title()}...")
      user=aa.get('name').title().split(' ')[0]
      st.session_state['User_Name']=aa.get('name').title()
      st.session_state['login_time']=datetime.datetime.now(tz=gettz('Asia/Kolkata')).time().replace(microsecond=0)
      st.session_state['user_name']=aa.get('name').title()
      st.session_state['login_time']=datetime.datetime.now(tz=gettz('Asia/Kolkata')).replace(microsecond=0, tzinfo=None).time()
      st.session_state['access_token']=obj.access_token
      st.session_state['refresh_token']=obj.refresh_token
      st.session_state['feed_token']=obj.feed_token
      st.session_state['userId']=obj.userId
      st.session_state['api_key']=apikey
      break
    except Exception as e:
      print(f"Unable to login error in angel_login {e}")
st.header(f"Welcome {st.session_state['user_name']}")
