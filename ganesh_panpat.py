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
obj=SmartConnect(api_key=st.session_state['api_key'],
                  access_token=st.session_state['access_token'],
                  refresh_token=st.session_state['refresh_token'],
                  feed_token=st.session_state['feed_token'],
                  userId=st.session_state['userId'])
col1,col2=st.columns([2,8])
with col1:
   get_orderbook=st.button("Get Order Book")
with col2:
   tbl=st.table()
if get_orderbook:
   orderbook=obj.orderBook()['data']
   orderbook=pd.DataFrame(orderbook)
   orderbook=orderbook[['updatetime','tradingsymbol','ordertag','price','ordertag']]
   st.table(orderbook)
