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
st.write(f"Last Login {st.session_state['login_time']}")
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
placeholder.text(print_ltp())

@st.cache_resource
def get_token_df():
  url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
  d = requests.get(url).json()
  token_df = pd.DataFrame.from_dict(d)
  token_df['expiry'] = pd.to_datetime(token_df['expiry']).apply(lambda x: x.date())
  token_df = token_df.astype({'strike': float})
  st.session_state['token_df']=token_df
  now_dt=datetime.datetime.now(tz=gettz('Asia/Kolkata')).date()-datetime.timedelta(days=0)
  expiry_df=token_df
  expiry_df = token_df[(token_df['name'] == 'BANKNIFTY') & (token_df['instrumenttype'] == 'OPTIDX') & (token_df['expiry']>=now_dt)]
  expiry_day = expiry_df['expiry'].min()
  bnf_expiry_df = token_df[(token_df['name'] == 'BANKNIFTY') & (token_df['instrumenttype'] == 'OPTIDX') & (token_df['expiry']>=now_dt)]
  bnf_expiry_day = bnf_expiry_df['expiry'].min()
  nf_expiry_df = token_df[(token_df['name'] == 'NIFTY') & (token_df['instrumenttype'] == 'OPTIDX') & (token_df['expiry']>=now_dt)]
  nf_expiry_day = nf_expiry_df['expiry'].min()
  monthly_expiry_df = token_df[(token_df['name'] == 'BANKNIFTY') & (token_df['instrumenttype'] == 'FUTIDX')  & (token_df['expiry']>=now_dt)]
  monthly_expiry_day = monthly_expiry_df['expiry'].min()

get_token_df()

def getTokenInfo (symbol, exch_seg ='NSE',instrumenttype='OPTIDX',strike_price = 0,pe_ce = 'CE',expiry_day = None):
  if symbol=="BANKNIFTY" or symbol=="^NSEBANK":
    expiry_day=st.session_state['bnf_expiry_day']
  elif symbol=="NIFTY" or symbol=="^NSEI":
    expiry_day=st.session_state['nf_expiry_day']
  df = st.session_state['token_df']
  strike_price = strike_price*100
  if exch_seg == 'NSE':
      eq_df = df[(df['exch_seg'] == 'NSE') ]
      return eq_df[eq_df['name'] == symbol]
  elif exch_seg == 'NFO' and ((instrumenttype == 'FUTSTK') or (instrumenttype == 'FUTIDX')):
      return df[(df['exch_seg'] == 'NFO') & (df['instrumenttype'] == instrumenttype) & (df['name'] == symbol)].sort_values(by=['expiry'])
  elif exch_seg == 'NFO' and (instrumenttype == 'OPTSTK' or instrumenttype == 'OPTIDX'):
      return (df[(df['exch_seg'] == 'NFO') & (df['expiry']==expiry_day) &  (df['instrumenttype'] == instrumenttype) & (df['name'] == symbol)
      & (df['strike'] == strike_price) & (df['symbol'].str.endswith(pe_ce))].sort_values(by=['expiry']))

def get_ce_pe_data(symbol,indexLtp="-"):
  indexLtp=float(indexLtp) if indexLtp!="-" else get_index_ltp(symbol)
  # ATM
  if symbol=='BANKNIFTY' or symbol=='^NSEBANK':
    symbol='BANKNIFTY'
    ATMStrike = math.floor(indexLtp/100)*100
    expiry_day=bnf_expiry_day
  elif symbol=='NIFTY' or symbol=='^NSEI':
    symbol='NIFTY'
    val2 = math.fmod(indexLtp, 50)
    val3 = 50 if val2 >= 25 else 0
    ATMStrike = indexLtp - val2 + val3
    expiry_day=nf_expiry_day
  #CE,#PE
  ce_strike_symbol = getTokenInfo(symbol,'NFO','OPTIDX',ATMStrike,'CE',expiry_day).iloc[0]
  pe_strike_symbol = getTokenInfo(symbol,'NFO','OPTIDX',ATMStrike,'PE',expiry_day).iloc[0]
  return indexLtp, ce_strike_symbol,pe_strike_symbol

def get_index_ltp(symbol):
  symbol_i="^NSEI"
  if symbol=="BANKNIFTY" or symbol=="^NSEBANK" or symbol[:4]=="BANK": symbol="BANKNIFTY"; symbol_i="^NSEBANK"
  elif symbol=="NIFTY" or symbol=="^NSEI" or symbol[:4]=='NIFT': symbol="NIFTY"; symbol_i="^NSEI"
  try:
    data=yf.Ticker(symbol_i).history(interval='1m',period='1d')
    indexLtp=round(float(data['Close'].iloc[-1]),2)
    #indexLtp=int(yf.Ticker(symbol_i).fast_info['last_price'])
  except Exception as e:
    try:
      data=yf.Ticker(symbol_i).history(interval='1m',period='1d')
      indexLtp=int(data['Close'].iloc[-1])
    except Exception as e:
       try:
          spot_token=getTokenInfo_index(symbol).iloc[0]['token']
          ltpInfo = obj.ltpData('NSE',symbol,spot_token)
          indexLtp = ltpInfo['data']['ltp']
       except Exception as e:
          print('Error get_index_ltp :',e)
  return indexLtp

def getTokenInfo_index(symbol):
  df = token_df
  return df[(df['exch_seg'] == 'NSE') & (df['symbol']== (symbol))]

def get_ltp_price(symbol="-",token="-",exch_seg='-'):
  try:
    data=obj.getMarketData("LTP",{exch_seg:[token]})['data']['fetched'][0]['ltp']
    return data
  except:
    try:
      #if symbol=="-" or token=="-" or exch_seg=="-":
      df_b=token_df[((token_df['exch_seg']=="NSE") | (token_df['exch_seg']=="NFO"))]
      df_b=df_b[(df_b['symbol'].str.startswith(symbol))]
      if len(df_b)!=1: df_b=df_b[((df_b['symbol'].str.startswith(symbol)) | (df_b['name'].str.startswith(symbol)))]
      if len(df_b)!=1: df_b=df_b[(df_b['name']==symbol) & (token_df['exch_seg']=="NSE")]
      if len(df_b)!=1: df_b=df_b[df_b['symbol'].str.contains('-EQ')]
      df_a=token_df[(token_df['token']==str(token)) & ((token_df['exch_seg']=="NSE") | (token_df['exch_seg']=="NFO"))]
      df_a=df_a.append(df_b)
      df_a=df_a.drop_duplicates()
      symbol=df_a['symbol'].iloc[0]
      token=df_a['token'].iloc[0]
      name=df_a['name'].iloc[0]
      exch_seg=df_a['exch_seg'].iloc[0]
      try:
        ltpInfo = obj.ltpData(exch_seg,symbol,token)
        ltp_price = ltpInfo['data']['ltp']
      except Exception as e:
          ltp_price=0
          print("Unable to get LTP")
    except Exception as e:
      ltp_price=0
      print("Unable to get LTP")
    return ltp_price
          
def place_order(token,symbol,qty,buy_sell,ordertype='MARKET',price=0,variety='NORMAL',exch_seg='NFO',producttype='CARRYFORWARD',
                triggerprice=0,squareoff=0,stoploss=0,ordertag='-'):
  for i in range(0,3):
    try:
      orderparams = {"variety": variety,"tradingsymbol": symbol,"symboltoken": token,"transactiontype": buy_sell,"exchange": exch_seg,
        "ordertype": ordertype,"producttype": producttype,"duration": "DAY","price": int(float(price)),"squareoff":int(float(squareoff)),
        "stoploss": int(float(stoploss)),"quantity": str(qty),"triggerprice":int(float(triggerprice)),"ordertag":ordertag,"trailingStopLoss":5}
      orderId=obj.placeOrder(orderparams)
      LTP_Price=round(float(get_ltp_price(symbol=symbol,token=token,exch_seg=exch_seg)),2)
      print(f'{buy_sell} Order Placed: {orderId} Symbol: {symbol} LTP: {LTP_Price} Ordertag: {ordertag}')
      return orderId,LTP_Price
      break
    except Exception as e:
      print("Order placement failed: ",e)
      orderId='Order placement failed'
      LTP_Price='Order placement failed'
  return orderId,LTP_Price
                  
def buy_option(symbol,indicator_strategy,interval,index_sl="-"):
  try:
    option_token=symbol['token']
    option_symbol=symbol['symbol']
    lotsize=int(symbol['lotsize'])
    orderId,ltp_price=place_order(token=option_token,symbol=option_symbol,qty=lotsize,buy_sell='BUY',ordertype='MARKET',price=0,
                          variety='NORMAL',exch_seg='NFO',producttype='CARRYFORWARD',ordertag=indicator_strategy)
    buy_msg=(f'Buy: {option_symbol}\nLTP: {ltp_price}\n{indicator_strategy}')
    telegram_bot_sendtext(buy_msg)
  except Exception as e:pass

def manual_buy(index_symbol,ce_pe="CE",index_ltp="-"):
  if index_ltp=="-":indexLtp=get_index_ltp(index_symbol)
  indexLtp, ce_strike_symbol,pe_strike_symbol=get_ce_pe_data(index_symbol,indexLtp=indexLtp)
  if ce_pe=="CE":symbol=ce_strike_symbol
  if ce_pe=="PE":symbol=pe_strike_symbol
  buy_option(symbol,"Manual Buy","5m")

def telegram_bot_sendtext(bot_message):
  BOT_TOKEN = '5051044776:AAHh6XjxhRT94iXkR4Eofp2PPHY3Omk2KtI'
  BOT_CHAT_ID = '-1001542241163'
  BOT_CHAT_ONE_MINUTE = '-1001542241163'
  #BOT_CHAT_ONE_MINUTE='-882387563'
  import requests
  bot_message=st.session_state['user_name']+':\n'+bot_message
  matches = ["Candle"]
  if any(x in bot_message for x in matches): check_msg=True
  else: check_msg=False
  if check_msg==True:
    send_text = 'https://api.telegram.org/bot' + BOT_TOKEN + '/sendMessage?chat_id=' + BOT_CHAT_ONE_MINUTE + \
              '&parse_mode=HTML&text=' + bot_message
  else:
    send_text = 'https://api.telegram.org/bot' + BOT_TOKEN + '/sendMessage?chat_id=' + BOT_CHAT_ID + \
                '&parse_mode=HTML&text=' + bot_message
  response = requests.get(send_text)
        
if nf_ce:manual_buy("NIFTY",ce_pe="CE",index_ltp="-")
if nf_pe:manual_buy("NIFTY",ce_pe="PE",index_ltp="-")
if bnf_ce:manual_buy("BANKNIFTY",ce_pe="CE",index_ltp="-")
if bnf_pe:manual_buy("BANKNIFTY",ce_pe="PE",index_ltp="-")

