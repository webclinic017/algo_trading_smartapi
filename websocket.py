from SmartApi import SmartConnect
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
import threading
import pyotp,time
from datetime import datetime
import pandas as pd
from dateutil.tz import gettz
import logging
import sys
from logzero import logger
import pytz
import streamlit as st
time_placeholder = st.empty()

API_KEY =    'CjOKjC5g'
USERNAME =  'G93179'
PIN =       '4789'
TOKEN =     'U4EAZJ3L44CNJHNUZ56R22TPKI'
CORRELATION_ID = 'Wdn749NDjMfh23'
LIVE_FEED_JSON={}
output_string=""
FEED_MODE = 1
TIME_ZONE = pytz.timezone('Asia/Kolkata')
TZ_INFO = datetime.now(TIME_ZONE).tzinfo
def login():
  obj=SmartConnect(api_key=API_KEY)
  data = obj.generateSession(USERNAME,PIN,pyotp.TOTP(TOKEN).now())
  AUTH_TOKEN = data['data']['jwtToken']
  refreshToken= data['data']['refreshToken']
  FEED_TOKEN=obj.getfeedToken()
  res = obj.getProfile(refreshToken)
  sws = SmartWebSocketV2(AUTH_TOKEN, API_KEY, USERNAME, FEED_TOKEN ,max_retry_attempt=5)
  return obj, sws

def on_data(wsapp, msg):
  try:
      #print("Ticks: {}".format(msg))
      LIVE_FEED_JSON[msg['token']] = {'token' :msg['token'] , 'ltp':msg['last_traded_price']/100}
      output = []
      for key, value in LIVE_FEED_JSON.items():
        if key == '99926000':output.append(f"NIFTY:{int(value['ltp'])}")
        elif key == '99926009': output.append(f"BANKNIFTY:{int(value['ltp'])}")
        elif key == '99919000': output.append(f"SENSEX:{int(value['ltp'])}")
      output_string = ", ".join(output)
      time_placeholder.text(output_string)
  except Exception as e:
      print(e)

def on_error(wsapp, error):
  logger.error(f"---------Connection Error {error}-----------")
def on_close(wsapp):
  logger.info("---------Connection Close-----------")
def close_connection(sws):
  sws.MAX_RETRY_ATTEMPT = 0
  sws.close_connection()
def subscribeSymbol(token_list,sws):
  logger.info(f'Subscribe -------  {token_list}')
  sws.subscribe(CORRELATION_ID, FEED_MODE, token_list)

def connectFeed(sws,tokeList =None):
  def on_open(wsapp):
      logger.info("on open")
      token_list = [{"exchangeType": 1,"tokens": ["99926000","99926009"]},{"exchangeType": 3,"tokens": ["99919000"]}]
      if tokeList  : token_list.append(tokeList)
      sws.subscribe(CORRELATION_ID, FEED_MODE, token_list)
  sws.on_open = on_open
  sws.on_data = on_data
  sws.on_error = on_error
  sws.on_close = on_close
  sws.connect
  #threading.Thread(target =sws.connect,daemon=True).start()

SMART_API_OBJ , SMART_WEB =  login()
connectFeed(SMART_WEB)
SMART_WEB.connect()
#while True:
#  SMART_WEB.connect()
#  time.sleep(60)
