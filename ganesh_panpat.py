import streamlit as st
import datetime
from dateutil.tz import gettz
import time
import pandas as pd
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
user="Ganesh"
def get_user_pwd(user):
  if user=='Ganesh': username = 'G93179'; pwd = '4789'; apikey = 'CjOKjC5g'; token='U4EAZJ3L44CNJHNUZ56R22TPKI'
  elif user=='Kalyani': username = 'K205244'; pwd = '4789'; apikey = 'lzC7yJmt'; token='YDV6CJI6BEU3GWON7GZTZNU3RM'
  elif user=="Akshay": username='A325394'; pwd='1443'; apikey='OeSllszj'; token='G4OKBQKHXPS67EN2WMVP3TZ7X4'
  return username,pwd,apikey,token
username,pwd,apikey,token=get_user_pwd(user)
from SmartApi import SmartConnect
import pyotp
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
st.write(f"Last Login {st.session_state['login_time']}")
placeholder = st.empty()
obj=SmartConnect(api_key=st.session_state['api_key'],
                  access_token=st.session_state['access_token'],
                  refresh_token=st.session_state['refresh_token'],
                  feed_token=st.session_state['feed_token'],
                  userId=st.session_state['userId'])
get_orderbook=st.button("Get Order Book")
if get_orderbook:
   orderbook=obj.orderBook()['data']
   orderbook=pd.DataFrame(orderbook)
   orderbook=orderbook.sort_values(by = ['updatetime'], ascending = [True], na_position = 'first')
   orderbook=orderbook[['updatetime','orderid','exchange','transactiontype','orderstatus','symboltoken','tradingsymbol',
                        'price','quantity','variety','ordertype','producttype']]
   st.table(orderbook)
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
with st.sidebar:
  col1,col2=st.columns(2)
  with col1:
    nf_ce=st.button("NF CE")
    bnf_ce=st.button("BNF CE")
  with col2:
    nf_pe=st.button("NF PE")
    bnf_pe=st.button("BNF PE")
placeholder.text(print_ltp())
