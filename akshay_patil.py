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
from streamlit_autorefresh import st_autorefresh
import datetime
from dateutil.tz import gettz
import time
import pandas as pd
import yfinance as yf
import math
import logzero
NoneType = type(None)
pd.set_option('mode.chained_assignment', None)
st.set_page_config(page_title="Algo App",layout="wide",initial_sidebar_state="expanded",)
st.markdown("""
  <style>
    .block-container {padding-top: 0.5rem;padding-bottom: 0rem;padding-left: 2rem;padding-right: 5rem;}  
  </style>
  """, unsafe_allow_html=True)
user="Akshay"
#cnt=st_autorefresh(interval=60*1000,debounce=False,key="Ganesh_refresh")
if 'algo_running' not in st.session_state:st.session_state['algo_running']="Not Running"
if 'algo_last_run' not in st.session_state:st.session_state['algo_last_run']=datetime.datetime.now(tz=gettz('Asia/Kolkata'))
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
    
obj=SmartConnect(api_key=st.session_state['api_key'],access_token=st.session_state['access_token'],
                 refresh_token=st.session_state['refresh_token'],feed_token=st.session_state['feed_token'],userId=st.session_state['userId'])
st.header(f"Welcome {st.session_state['user_name']}")
last_login=st.empty()
placeholder = st.empty()
col1,col2=st.columns([1,9])
with col1:
  nf_ce=st.button(label="NF CE")
  bnf_ce=st.button(label="BNF CE")
  nf_pe=st.button(label="NF PE")
  bnf_pe=st.button(label="BNF PE")
  close_all=st.button("Close All")
  algo_state=st.checkbox("Run Algo")
with col2:
  tab1, tab2, tab3, tab4= st.tabs(["Order_Book", "Position","Algo Trade", "Settings"])
  with tab1:order_datatable=st.empty()
  with tab2:position_datatable=st.empty()
  with tab3:algo_datatable=st.empty()
    if index_symbol=="NIFTY" or index_symbol=="^NSEI": index_ltp=st.session_state['Nifty']
  if index_ltp=="-": index_ltp=get_index_ltp(index_symbol)
  indexLtp, ce_strike_symbol,pe_strike_symbol=get_ce_pe_data(index_symbol,indexLtp=index_ltp)
  if ce_pe=="CE":symbol=ce_strike_symbol
  if ce_pe=="PE":symbol=pe_strike_symbol
  buy_option(symbol,"Manual Buy","5m")

def index_trade(symbol="-",interval="-",candle_type="NORMAL",token="-",exch_seg="-"):
  try:
    fut_data=get_historical_data(symbol,interval=interval,token=token,exch_seg=exch_seg,candle_type=candle_type)
    trade=str(fut_data['Trade'].values[-1])
    trade_end=str(fut_data['Trade End'].values[-1])
    if trade!="-":
      indicator_strategy=fut_data['Indicator'].values[-1]
      indexLtp=fut_data['Close'].values[-1]
      interval_yf=fut_data['Time Frame'].values[-1]
      indexLtp, ce_strike_symbol,pe_strike_symbol=get_ce_pe_data(symbol,indexLtp=indexLtp)
      if trade=="Buy" : buy_option(ce_strike_symbol,indicator_strategy,interval)
      elif trade=="Sell" : buy_option(pe_strike_symbol,indicator_strategy,interval)
    print(symbol + "_" +fut_data['Time Frame'].values[-1]+" " +str(datetime.datetime.now())+
          "\n"+fut_data.tail(2)[['Datetime','Symbol','Close','Trade','Trade End','Supertrend','Supertrend_10_2','RSI','Indicator']].to_string(index=False))
    return fut_data
  except Exception as e:
    print('Error in index trade:',symbol,e)

def get_near_options(bnf_ltp,nf_ltp):
  symbol_list=['BANKNIFTY','NIFTY']
  df = pd.DataFrame()
  for symbol in symbol_list:
    indexLtp=bnf_ltp if symbol=="BANKNIFTY" else nf_ltp
    ltp=indexLtp*100
    expiry_day=bnf_expiry_day if symbol=="BANKNIFTY" else nf_expiry_day
    a = (token_df[(token_df['name'] == symbol) & (token_df['expiry']==expiry_day) & (token_df['strike']>=ltp) &
                    (token_df['symbol'].str.endswith('CE'))].sort_values(by=['strike']).head(2)).sort_values(by=['strike'], ascending=True)
    a.reset_index(inplace=True)
    a['Serial'] = a['index'] + 1
    a.drop(columns=['index'], inplace=True)
    b=(token_df[(token_df['name'] == symbol) & (token_df['expiry']==expiry_day) & (token_df['strike']<=ltp) &
                    (token_df['symbol'].str.endswith('PE'))].sort_values(by=['strike']).tail(2)).sort_values(by=['strike'], ascending=False)
    b.reset_index(inplace=True)
    b['Serial'] = b['index'] + 1
    b.drop(columns=['index'], inplace=True)
    df=pd.concat([df, a,b])
  df.sort_index(inplace=True)
  print(f"Option List:BNF {bnf_ltp} NF {nf_ltp} as on {datetime.datetime.now()}")
  print(df)
  return df

def trade_near_options(time_frame):
  near_trade_df = pd.DataFrame()
  time_frame=str(time_frame)+"m"
  bnf_ltp=st.session_state['BankNifty']
  nf_ltp=st.session_state['Nifty']
  #bnf_ltp=get_index_ltp("^NSEBANK")
  #nf_ltp=get_index_ltp("^NSEI")
  near_option_list=get_near_options(bnf_ltp,nf_ltp)
  b_trade="-";n_trade="-"
  for i in range(0,len(near_option_list)):
    try:
      print(f"Options : {near_option_list['symbol'].iloc[i]} {datetime.datetime.now()}")
      if (near_option_list['name'].iloc[i]=="BANKNIFTY" and b_trade=="-") or (near_option_list['name'].iloc[i]=="NIFTY" and n_trade=="-"):
        df=get_historical_data(symbol=near_option_list['symbol'].iloc[i],interval=time_frame,token=near_option_list['token'].iloc[i],exch_seg="NFO")
        if (df['St Trade'].values[-1]=="Buy" or df['ST_10_2 Trade'].values[-1]=="Buy" or
            df['EMA_High_Low Trade'].values[-1]=="Buy" or df["RSI MA Trade"].values[-1]=="Buy" or df["RSI_60 Trade"].values[-1]=="Buy"):
          strike_symbol=near_option_list.iloc[i]
          if df['St Trade'].values[-1]=="Buy": sl= int(df['Supertrend'].values[-1])
          elif df['ST_10_2 Trade'].values[-1]=="Buy": sl= int(df['Supertrend_10_2'].values[-1])
          else: sl=int(df['Close'].values[-1]*0.8)
          target=int(int(df['Close'].values[-1])+((int(df['Close'].values[-1])-sl)*2))
          indicator ="OPT "+str(time_frame)+":"
          if df['St Trade'].values[-1]=="Buy": indicator=indicator + " ST"
          elif df['ST_10_2 Trade'].values[-1]=="Buy": indicator=indicator +" ST_10_2"
          elif df['EMA_High_Low Trade'].values[-1]=="Buy": indicator=indicator +" EMA_High_Low"
          elif df['RSI MA Trade'].values[-1]=="Buy": indicator=indicator +" RSI_MA_14"
          elif df['RSI_60 Trade'].values[-1]=="Buy": indicator=indicator +" RSI_60"
          strategy=indicator + " LTP: "+str(int(df['St Trade'].values[-1]))+" (" +str(sl)+":"+str(target)+') '+" RSI:"+str(int(df['RSI'].values[-1]))
          buy_option(symbol=strike_symbol,indicator_strategy=strategy,interval=time_frame)
          if near_option_list['name'].iloc[i]=="BANKNIFTY": b_trade="Buy"
          if near_option_list['name'].iloc[i]=="NIFTY": n_trade="Buy"
    except Exception as e:
      print(e)


#end main algo code
if algo_state==False:
  st.session_state['algo_running']="Not Running"
  last_login.text(f"Last Login {st.session_state['login_time']} Algo : {st.session_state['algo_running']}")
if nf_ce:manual_buy("NIFTY",ce_pe="CE",index_ltp=st.session_state['Nifty']);st.write(f"Buy Nifty CE {st.session_state['Nifty']}")
if nf_pe:manual_buy("NIFTY",ce_pe="PE",index_ltp=st.session_state['Nifty']);st.write(f"Buy Nifty PE {st.session_state['Nifty']}")
if bnf_ce:manual_buy("BANKNIFTY",ce_pe="CE",index_ltp=st.session_state['BankNifty']);st.write(f"Buy BankNifty CE {st.session_state['BankNifty']}")
if bnf_pe:manual_buy("BANKNIFTY",ce_pe="PE",index_ltp=st.session_state['BankNifty']);st.write(f"Buy BankNifty PE {st.session_state['BankNifty']}")

update_order_book()
update_position()
print_ltp()
sl_trail()

if algo_state:
  while True:
    now_time=datetime.datetime.now(tz=gettz('Asia/Kolkata'))
    print(f"{now_time.replace(microsecond=0,tzinfo=None)}")
    marketclose = now_time.replace(hour=14, minute=50, second=0, microsecond=0)
    marketopen = now_time.replace(hour=9, minute=19, second=0, microsecond=0)
    if now_time>marketopen and now_time < marketclose:
      five_m_timeframe="Yes"
      three_m_timeframe="No"
      fifteen_m_timeframe="Yes"
      one_m_timeframe="No"
      if (now_time.minute%5==0 and five_m_timeframe=='Yes'):
        bnf_trade=index_trade('BANKNIFTY','5m')
        nf_trade=index_trade('NIFTY','5m')
        trade_near_options(5)
      if (now_time.minute%15==0 and fifteen_m_timeframe=='Yes'):
        bnf_trade_15_min=index_trade('BANKNIFTY','15m')
        nf_trade_15_min=index_trade('NIFTY','15m')
      if one_m_timeframe=="Yes":
        bnf_trade_1_min=index_trade('BANKNIFTY','1m')
        nf_trade_1_min=index_trade('NIFTY','1m')
    else:
      st.session_state['algo_running']="Market Closed"
    st.session_state['algo_running']="Running"
    st.session_state['algo_last_run']=datetime.datetime.now(tz=gettz('Asia/Kolkata')).replace(microsecond=0,tzinfo=None)
    last_login.text(f"Login: {st.session_state['login_time']} Algo: {st.session_state['algo_running']} Last run : {st.session_state['algo_last_run']}")
    update_order_book()
    update_position()
    print_ltp()
    sl_trail()
    time.sleep(60-datetime.datetime.now().second)
