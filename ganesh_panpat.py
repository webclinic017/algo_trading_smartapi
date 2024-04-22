import streamlit as st
st.set_page_config(page_title="Algo App",layout="wide",initial_sidebar_state="expanded",)
st.markdown("""
  <style>
    .block-container {padding-top: 0.5rem;padding-bottom: 0rem;padding-left: 2rem;padding-right: 5rem;}
  </style>
  """, unsafe_allow_html=True)
from SmartApi import SmartConnect
import pyotp
from logzero import logger
api_key = 'Rz6IiOsd'
username = 'G93179'
pwd = '4789'
smartApi = SmartConnect(api_key)
try:
    token = "U4EAZJ3L44CNJHNUZ56R22TPKI"
    totp = pyotp.TOTP(token).now()
except Exception as e:
    logger.error("Invalid Token: The provided token is not valid.")
    raise e
correlation_id = "abcde"
data = smartApi.generateSession(username, pwd, totp)
if data['status'] == False:logger.error(data)
else:
  # login api call
  # logger.info(f"You Credentials: {data}")
  authToken = data['data']['jwtToken']
  refreshToken = data['data']['refreshToken']
  # fetch the feedtoken
  feedToken = smartApi.getfeedToken()
  # fetch User Profile
  res = smartApi.getProfile(refreshToken)
  smartApi.generateToken(refreshToken)
  res=res['data']['exchanges']
  userProfile= obj.getProfile(refreshToken)
  aa= userProfile.get('data')
  print(f"Welcome {aa.get('name').title()}...")
st.write(aa.get('name').title())
  
