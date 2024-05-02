import streamlit as st
from streamlit.logger import get_logger
import yfinance as yf
import datetime
import time
from dateutil.tz import gettz
import pandas as pd
import pandas_ta as pdta
from SmartApi import SmartConnect
LOGGER = get_logger(__name__)
st.set_page_config(page_title="Algo App",layout="wide",initial_sidebar_state="expanded",)
st.markdown("""
  <style>
    .block-container {padding-top: 0.5rem;padding-bottom: 0rem;padding-left: 2rem;padding-right: 5rem;}
  </style>
  """, unsafe_allow_html=True)
st.write("# Welcome to My Algo!")
username = 'G93179'
pwd = '4789'
apikey = 'Rz6IiOsd'
token='U4EAZJ3L44CNJHNUZ56R22TPKI'
obj = SmartConnect(apikey)
try:totp = pyotp.TOTP(token).now()
except Exception as e:
  time.sleep(2)
  logger.error("Invalid Token: The provided token is not valid.")
  raise e
correlation_id = "abcde"
data = obj.generateSession(username, pwd, totp)
if data['status'] == False:logger.error(data)
else:
  authToken = data['data']['jwtToken']
  refreshToken = data['data']['refreshToken']
  feedToken = obj.getfeedToken()
  res = obj.getProfile(refreshToken)
  obj.generateToken(refreshToken)
  userProfile= obj.getProfile(refreshToken)
  aa= userProfile.get('data')
  st.write(f"Welcome {aa.get('name').title()}")
