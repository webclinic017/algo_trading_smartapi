import streamlit as st
st.set_page_config(page_title="Algo App",layout="wide",initial_sidebar_state="expanded",)
st.markdown("""
  <style>
    .block-container {padding-top: 0.5rem;padding-bottom: 0rem;padding-left: 2rem;padding-right: 5rem;}
  </style>
  """, unsafe_allow_html=True)

from SmartApi import SmartConnect
from SmartApi import SmartWebSocket
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
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
import requests
pd.options.mode.chained_assignment = None
warnings.filterwarnings('ignore')
NoneType = type(None)

username=st.secrets["username"]
pwd=st.secrets["pwd"]
apikey=st.secrets["apikey"]
token=st.secrets["token"]
user=st.secrets["user"]

#Telegram Msg
def telegram_bot_sendtext(bot_message):
  BOT_TOKEN = '5051044776:AAHh6XjxhRT94iXkR4Eofp2PPHY3Omk2KtI'
  BOT_CHAT_ID = '-1001542241163'
  bot_message=st.secrets["user"]+':\n'+bot_message
  send_text = 'https://api.telegram.org/bot' + BOT_TOKEN + '/sendMessage?chat_id=' + BOT_CHAT_ID + '&parse_mode=HTML&text=' + bot_message
  response = requests.get(send_text)

telegram_bot_sendtext("HI")


