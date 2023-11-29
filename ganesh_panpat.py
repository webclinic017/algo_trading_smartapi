import streamlit as st
st.set_page_config(page_title="Algo App",layout="wide",initial_sidebar_state="expanded",)
st.markdown("""
        <style>
               .block-container {
                    padding-top: 0.5rem;
                    padding-bottom: 0rem;
                    padding-left: 2rem;
                    padding-right: 5rem;
                }
        </style>
        """, unsafe_allow_html=True)
if 'user_name' not in st.session_state:
   st.session_state['user_name']="Guest"
   st.session_state['login_time']="Guest"
from SmartApi import SmartConnect
from SmartApi import SmartWebSocket
import threading
import pandas as pd
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
warnings.filterwarnings('ignore')
NoneType = type(None)
def get_user_pwd(user):
  if user=='Ganesh': username = 'G93179'; pwd = '4789'; apikey = 'CjOKjC5g'; token='U4EAZJ3L44CNJHNUZ56R22TPKI'
  elif user=='Kalyani': username = 'K205244'; pwd = '4789'; apikey = 'lzC7yJmt'; token='YDV6CJI6BEU3GWON7GZTZNU3RM'
  elif user=="Akshay": username='A325394'; pwd='1443'; apikey='OeSllszj'; token='G4OKBQKHXPS67EN2WMVP3TZ7X4'
  return username,pwd,apikey,token,user
username,pwd,apikey,token,user=get_user_pwd("Kalyani")
obj=SmartConnect(api_key=apikey)
if st.session_state['user_name']=="Guest":
   try:
      FEED_TOKEN = None;TOKEN_MAP = None;SMART_API_OBJ = None
      global user_name
      now=datetime.datetime.now(tz=gettz('Asia/Kolkata')).replace(tzinfo=None)
      data = obj.generateSession(username,pwd,pyotp.TOTP(token).now())
      refreshToken= data['data']['refreshToken']
      feedToken=obj.getfeedToken()
      userProfile= obj.getProfile(refreshToken)
      aa= userProfile.get('data')
      st.session_state['user_name']=aa.get('name').title()
      st.session_state['login_time']=datetime.datetime.now(tz=gettz('Asia/Kolkata')).replace(microsecond=0,tzinfo=None)
      user=aa.get('name').title().split(' ')[0]
      st.session_state['refreshToken']=refreshToken
      st.session_state['feedToken']=feedToken
   except Exception as e:
      st.write("Unable to login")
      st.write(e)
st.write(obj.getProfile(refreshToken).get('data')) 
st.write(feedToken)
@st.cache_resource
def get_token_df():
  global symbolDf,token_df
  url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
  d = requests.get(url).json()
  token_df = pd.DataFrame.from_dict(d)
  token_df['expiry'] = pd.to_datetime(token_df['expiry']).apply(lambda x: x.date())
  token_df = token_df.astype({'strike': float})
  return token_df
token_df=get_token_df()
st.header(f"Welcome {st.session_state['user_name']}")
st.write(f"Last Login {st.session_state['login_time']}")
nf_ce_btn=st.button(label="NIFTY CE")
if nf_ce_btn:
  odrbook=obj.orderBook()
  st.write(odrbook)
