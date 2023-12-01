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
import datetime
from dateutil.tz import gettz
import time
import pandas as pd
import yfinance as yf
import math
NoneType = type(None)
st.set_page_config(page_title="Algo App",layout="wide",initial_sidebar_state="expanded",)
st.markdown("""
  <style>
    .block-container {padding-top: 0.5rem;padding-bottom: 0rem;padding-left: 2rem;padding-right: 5rem;}  
  </style>
  """, unsafe_allow_html=True)
user="Ganesh"
if 'algo_state' not in st.session_state:st.session_state['algo_state']="Not Running"
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
st.header(f"Welcome {st.session_state['user_name']}")
last_login=st.empty()
last_login.text(f"Last Login {st.session_state['login_time']} Algo : {st.session_state['algo_state']}")
placeholder = st.empty()
placeholder.text('LTP')
obj=SmartConnect(api_key=st.session_state['api_key'],
                  access_token=st.session_state['access_token'],
                  refresh_token=st.session_state['refresh_token'],
                  feed_token=st.session_state['feed_token'],
                  userId=st.session_state['userId'])
col1,col2=st.columns([1,9])
with col1:
  st.write("Manu:")
  nf_ce=st.button("NF CE")
  bnf_ce=st.button("BNF CE")
  nf_pe=st.button("NF PE")
  bnf_pe=st.button("BNF PE")
  close_all=st.button("Close All")
  algo_state=st.button("Run Algo")
  algo_state_stop=st.button("Stop Algo")
with col2:
  tab1, tab2, tab3, tab4= st.tabs(["Order_Book", "Position","Algo Trade", "Settings"])
  with tab1:
    get_orderbook=st.button("OrderBook")
    order_datatable=st.empty()
  with tab2:
    get_position=st.button("Position")
    position_datatable=st.empty()
  with tab3:
    algo_trade=st.button("Algo Trade")
  with tab4:
    lot_size=st.number_input(label="Lots To Trade",min_value=1, max_value=10, value=1, step=None)
    #datatable=st.empty()
def update_price_orderbook(df):
  for j in range(0,len(df)):
    try:
      if df['averageprice'].iloc[j]!=0:df['price'].iloc[j]=df['averageprice'].iloc[j]
      elif df['price'].iloc[j]==0:
        text=df['text'].iloc[j]
        ordertag=df['ordertag'].iloc[j]+" "
        if 'You require Rs. ' in text and ' funds to execute this order.' in text and type(text)==str :
          abc='-'
          abc=(text.split('You require Rs. '))[1].split(' funds to execute this order.')[0]
          if abc!='-' and int(float(abc)) <= 50000:
            df['price'].iloc[j]=(round(float(abc)/float(df['quantity'].iloc[j]),2))
        if df['price'].iloc[j]==0 and "LTP: " in ordertag:
          abc='-'
          abc=(ordertag.split('LTP: '))[1].split(' ')[0]
          df['price'].iloc[j]=round(float(abc),2)
          #df['price'].iloc[j]=float(ordertag.split("LTP: ",1)[1])
        if df['price'].iloc[j]==0:df['price'].iloc[j]='-'
    except Exception as e:
      pass
  return df
if get_orderbook:
   orderbook=obj.orderBook()['data']
   if orderbook==None:
     order_datatable.write("No Order Placed")
   else:
     orderbook=pd.DataFrame(orderbook)
     orderbook=orderbook.sort_values(by = ['updatetime'], ascending = [False], na_position = 'first')
     orderbook=update_price_orderbook(orderbook)
     orderbook['price']=round(orderbook['price'].astype(int),2)
     orderbook = orderbook.rename(columns={'transactiontype':'trans','quantity':'qty'})
     order_datatable.table(orderbook[['updatetime','orderid','trans','status','tradingsymbol','price','qty','ordertag']])
if get_position:
   position=obj.position()['data']
   if position== None:
     position_datatable.write("No Position")
   else:
     position=pd.DataFrame(position)
     position_datatable.table(position[['tradingsymbol','netqty','buyavgprice','sellavgprice','realised','unrealised','ltp']])
def print_ltp():
  try:
    data=pd.DataFrame(obj.getMarketData(mode="OHLC",exchangeTokens={ "NSE": ["99926000","99926009"], "NFO": []})['data']['fetched'])
    data['change']=data['ltp']-data['close']
    print_sting=datetime.datetime.now(tz=gettz('Asia/Kolkata')).replace(microsecond=0, tzinfo=None).time()
    for i in range(0,len(data)):print_sting=f"{print_sting} {data.iloc[i]['tradingSymbol']} {int(data.iloc[i]['ltp'])}({int(data.iloc[i]['change'])})"
    print_sting=print_sting.replace("Nifty 50","Nifty")
    print_sting=print_sting.replace("Nifty Bank","BankNifty")
    return print_sting
  except Exception as e:
    return "Unable to get LTP"
if nf_ce:manual_buy("NIFTY",ce_pe="CE",index_ltp="-")
if nf_pe:manual_buy("NIFTY",ce_pe="PE",index_ltp="-")
if bnf_ce:manual_buy("BANKNIFTY",ce_pe="CE",index_ltp="-")
if bnf_pe:manual_buy("BANKNIFTY",ce_pe="PE",index_ltp="-")
if algo_state:st.session_state['algo_state']='Running'
if algo_state_stop:
  st.session_state['algo_state']='Not Running'
  last_login.text(f"Last Login {st.session_state['login_time']} Algo : {st.session_state['algo_state']}")
  st.rerun()
if st.session_state['algo_state']=='Running':
  last_login.text(f"Last Login {st.session_state['login_time']} Algo : {st.session_state['algo_state']}")
  while True:
    placeholder.text(print_ltp())
    time.sleep(1)
    
