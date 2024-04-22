import streamlit as st
import datetime
st.set_page_config(page_title="Algo App",layout="wide",initial_sidebar_state="expanded",)
st.markdown("""
  <style>
    .block-container {padding-top: 0.5rem;padding-bottom: 0rem;padding-left: 2rem;padding-right: 5rem;}
  </style>
  """, unsafe_allow_html=True)
header_text =st.header(f"Welcome To Algo Trading")
last_login=st.empty()
last_login.text(f"Login:")
index_ltp_string=st.empty()
index_ltp_string.text(f"Index Ltp:")
tab0, tab1, tab2, tab3,tab4, tab5,tab6,tab7,tab8= st.tabs(["Log","Order Book", "Position","Todays Trade","Open Order", "Settings",
                                                           "Token List","Future List","Back Test"])
with tab0:
  col1,col2=st.columns([1,9])
  with col1:
    nf_ce=st.button(label="NF CE")
    bnf_ce=st.button(label="BNF CE")
    nf_pe=st.button(label="NF PE")
    bnf_pe=st.button(label="BNF PE")
    close_all=st.button("Close All")
    restart=st.button("Restart")
    algo_state=st.checkbox("Run Algo")
  with col2:
    log_holder=st.empty()
with tab1:
  order_book_updated=st.empty()
  order_book_updated.text(f"Orderbook : ")
  order_datatable=st.empty()
with tab2:
  position_updated=st.empty()
  position_updated.text(f"Position : ")
  position_datatable=st.empty()
with tab3:
  todays_trade_updated=st.empty()
  todays_trade_updated.text(f"Todays Trade : ")
  todays_trade_datatable=st.empty()
with tab4:
  open_order_updated=st.empty()
  open_order_updated.text(f"Open Order : ")
  open_order=st.empty()
with tab5:
  ind_col1,ind_col2,ind_col3,ind_col4=st.columns([5,1.5,1.5,1.5])
  indicator_list=['St Trade', 'ST_10_2 Trade','ST_10_1 Trade', 'RSI MA Trade','RSI_60 Trade','MACD Trade','PSAR Trade','DI Trade',
                  'MA Trade','EMA Trade','EMA_5_7 Trade','MA 21 Trade','HMA Trade','RSI_60 Trade','EMA_High_Low Trade','Two Candle Theory','TEMA_EMA_9 Trade']
  with ind_col1:
    index_list=st.multiselect('Select Index',['NIFTY','BANKNIFTY','SENSEX'],['NIFTY','BANKNIFTY','SENSEX'])
    fut_list=st.multiselect('Select Future',['SILVERMIC','SILVER'],[])
    time_frame_interval = st.multiselect('Select Time Frame',['IDX:5M', 'IDX:15M', 'OPT:5M', 'OPT:15M','IDX:1M'],['IDX:5M','OPT:5M'])
    five_buy_indicator = st.multiselect('Index Indicator',indicator_list,['St Trade', 'ST_10_2 Trade','RSI_60 Trade'])
    option_buy_indicator = st.multiselect('Option Indicator',indicator_list,['St Trade', 'ST_10_2 Trade','RSI_60 Trade'])
    #three_buy_indicator = st.multiselect('Three Minute Indicator',indicator_list,[])
    #one_buy_indicator = st.multiselect('One Minute Indicator',indicator_list,[])
  with ind_col2:
    target_order_type = st.selectbox('Target Order',('Target', 'Stop_Loss', 'NA'),1)
    target_type = st.selectbox('Target Type',('Points', 'Per Cent','Indicator'),1)
    if target_type!="Indicator":
        sl_point=st.number_input(label="SL",min_value=10, max_value=100, value=30, step=None)
        target_point=st.number_input(label="Target",min_value=5, max_value=100, value=50, step=None)
  with ind_col3:
    lots_to_trade=st.number_input(label="Lots To Trade",min_value=1, max_value=10, value=1, step=None)
  with ind_col4:
    st.date_input("BNF Exp",datetime.datetime.now().date())
    st.date_input("NF Exp",datetime.datetime.now().date())
    st.date_input("FIN NF Exp",datetime.datetime.now().date())
    st.date_input("SENSEX Exp",datetime.datetime.now().date())
with tab6:
  token_df=st.empty()
with tab7:
  fut_token_df=st.empty()
with tab8:
  hourly_scan=st.button("Hourly ST Scan")
  daily_backtest=st.button("Todays Trade")
  download_data=st.button("Download Historical Data")

#Main App
from SmartApi.smartConnect import SmartConnect
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
from py5paisa import FivePaisaClient
import re
pd.options.mode.chained_assignment = None
warnings.filterwarnings('ignore')
NoneType = type(None)
CORRELATION_ID = 'Wdn749NDjMfh23'
FEED_MODE = 1

username = 'G93179'; pwd = '4789'; apikey = 'Rz6IiOsd'; token='U4EAZJ3L44CNJHNUZ56R22TPKI'
LIVE_FEED_JSON= {}
SMART_WEB = None
CORRELATION_ID = 'Wdn749NDjMfh23'  # ANY random string
FEED_MODE = 1
if "User_Name" not in st.session_state:
  try:
    obj=SmartConnect(api_key=apikey)
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
    st.session_state['User_Name']=user
  except Exception as e:
    st.write(f"Unable to login error in angel_login {e}")

header_text.header(f"Welcome {st.session_state['User_Name']}")

#Telegram Msg
def telegram_bot_sendtext(bot_message):
  BOT_TOKEN = '5051044776:AAHh6XjxhRT94iXkR4Eofp2PPHY3Omk2KtI'
  BOT_CHAT_ID = '-1001542241163'
  import requests
  bot_message=st.session_state['User_Name']+':\n'+bot_message
  send_text = 'https://api.telegram.org/bot' + BOT_TOKEN + '/sendMessage?chat_id=' + BOT_CHAT_ID + \
                '&parse_mode=HTML&text=' + bot_message
  response = requests.get(send_text)
