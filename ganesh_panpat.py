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
apikey = 'Rz6IiOsd'
username = 'G93179'
pwd = '4789'
token='U4EAZJ3L44CNJHNUZ56R22TPKI'

for attempt in range(3):
  try:
    print(f"Login attempt {attempt}")
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
      print(f"Welcome {aa.get('name').title()}")
      userProfile= obj.getProfile(refreshToken)
      aa= userProfile.get('data')
      print(f"Welcome {aa.get('name').title()}...")
      st.write(aa.get('name').title())
      break
  except Exception as e:
    time.sleep(2)
    print(f"Unable to login error in angel_login {e}")
