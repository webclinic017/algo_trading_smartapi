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
  with tab4:
    buy_indicator = st.multiselect('Select Buy Indicator',['St Trade', 'ST_10_2 Trade', 'RSI MA Trade', 'RSI_60 Trade'],
                                   ['St Trade', 'ST_10_2 Trade', 'RSI MA Trade', 'RSI_60 Trade'])
    time_frame = st.multiselect('Select Time Frame',['IDX:5M', 'IDX:15M', 'OPT:5M', 'OPT:15M','IDX:1M'],
                                   ['IDX:5M', 'IDX:15M', 'OPT:5M'])
    col1_tab4,col2_tab4,col3_tab4,col4_tab4,col5_tab4=st.columns(5)
    with col1_tab4:
      banknifty_target=st.number_input(label="Bank Nifty Target",min_value=10, max_value=100, value=10, step=None)
      nifty_target=st.number_input(label="Nifty Target",min_value=5, max_value=100, value=5, step=None)
    with col2_tab4:
      banknifty_sl=st.number_input(label="Bank Nifty SL",min_value=10, max_value=100, value=10, step=None)
      nifty_sl=st.number_input(label="Nifty SL",min_value=5, max_value=100, value=5, step=None)
    with col3_tab4:
      target_order_type = st.selectbox('Target Order',('Target', 'Stop_Loss', 'NA'),1)
      lots_to_trade=st.number_input(label="Lots To Trade",min_value=1, max_value=10, value=1, step=None)
    with col4_tab4:
      target_type = st.selectbox('Target Type',('Points', 'Per Cent'),0)

@st.cache_resource
def get_token_df():
  url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
  d = requests.get(url).json()
  token_df = pd.DataFrame.from_dict(d)
  token_df['expiry'] = pd.to_datetime(token_df['expiry']).dt.date
  token_df = token_df.astype({'strike': float})
  st.session_state['token_df']=token_df
  return token_df
token_df=get_token_df()

@st.cache_resource
def get_expiry_day_fut_token():
  now_dt=datetime.datetime.now(tz=gettz('Asia/Kolkata')).date()-datetime.timedelta(days=0)
  token_df=st.session_state['token_df']
  expiry_df=token_df
  expiry_df = token_df[(token_df['name'] == 'BANKNIFTY') & (token_df['instrumenttype'] == 'OPTIDX') & (token_df['expiry']>=now_dt)]
  expiry_day=expiry_df['expiry'].min()
  bnf_expiry_df = token_df[(token_df['name'] == 'BANKNIFTY') & (token_df['instrumenttype'] == 'OPTIDX') & (token_df['expiry']>=now_dt)]
  bnf_expiry_day=bnf_expiry_df['expiry'].min()
  nf_expiry_df = token_df[(token_df['name'] == 'NIFTY') & (token_df['instrumenttype'] == 'OPTIDX') & (token_df['expiry']>=now_dt)]
  nf_expiry_day=nf_expiry_df['expiry'].min()
  st.session_state['nf_expiry_day'] = nf_expiry_day
  st.session_state['expiry_day'] = expiry_day
  st.session_state['bnf_expiry_day'] = bnf_expiry_day
  return expiry_day,nf_expiry_day,bnf_expiry_day
expiry_day,nf_expiry_day,bnf_expiry_day=get_expiry_day_fut_token()

def getTokenInfo (symbol, exch_seg ='NSE',instrumenttype='OPTIDX',strike_price = 0,pe_ce = 'CE',expiry_day = None):
  if symbol=="BANKNIFTY" or symbol=="^NSEBANK":expiry_day=st.session_state['bnf_expiry_day']
  elif symbol=="NIFTY" or symbol=="^NSEI":expiry_day=st.session_state['nf_expiry_day']
  df = st.session_state['token_df']
  strike_price = strike_price*100
  if exch_seg == 'NSE':
      eq_df = df[(df['exch_seg'] == 'NSE') ]
      df=eq_df[eq_df['name'] == symbol]
  elif exch_seg == 'NFO' and ((instrumenttype == 'FUTSTK') or (instrumenttype == 'FUTIDX')):
      df=df[(df['exch_seg'] == 'NFO') & (df['instrumenttype'] == instrumenttype) & (df['name'] == symbol)].sort_values(by=['expiry'])
  elif exch_seg == 'NFO' and (instrumenttype == 'OPTSTK' or instrumenttype == 'OPTIDX'):
      df=(df[(df['exch_seg'] == 'NFO') & (df['expiry']==expiry_day) &  (df['instrumenttype'] == instrumenttype) & (df['name'] == symbol)
      & (df['strike'] == strike_price) & (df['symbol'].str.endswith(pe_ce))].sort_values(by=['expiry']))
  return df
  
def update_order_book():
  try:
    orderbook=obj.orderBook()['data']
    if orderbook==None:order_datatable.write("No Order Placed")
    else:
      orderbook=pd.DataFrame(orderbook)
      orderbook=orderbook.sort_values(by = ['updatetime'], ascending = [False], na_position = 'first')
      orderbook=update_price_orderbook(orderbook)
      orderbook['price']=round(orderbook['price'].astype(int),2)
      orderbook = orderbook.rename(columns={'transactiontype':'trans','quantity':'qty'})
      order_datatable.table(orderbook[['updatetime','orderid','trans','status','tradingsymbol','price','qty','ordertag']])
  except Exception as e:pass

def update_position():
  try:
    position=obj.position()['data']
    if position== None:position_datatable.write("No Position")
    else:
     position=pd.DataFrame(position)
     position_datatable.table(position[['tradingsymbol','netqty','buyavgprice','sellavgprice','realised','unrealised','ltp']])
  except Exception as e:pass

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
          df['price'].iloc[j]=float(abc)
    except Exception as e:
      pass
  return df

def get_ltp_token(tokenlist):
  try:
    ltp_df=pd.DataFrame(obj.getMarketData(mode="LTP",exchangeTokens={ "NSE": ["99926000","99926009"], "NFO": list(tokenlist)})['data']['fetched'])
    return ltp_df
  except Exception as e:
    ltp_df=pd.DataFrame(columns = ['exchange','tradingSymbol','symbolToken','ltp'])
    return ltp_df

def ganesh_sl_trail(todays_trade_log):
  for i in range(0,len(todays_trade_log)):
    if todays_trade_log['Status'].iloc[i]=="Pending":
      try:
        ordertag=todays_trade_log['ordertag'].iloc[i]
        symbol=todays_trade_log['tradingsymbol'].iloc[i]
        token=todays_trade_log['symboltoken'].iloc[i]
        exchange=todays_trade_log['exchange'].iloc[i]
        price=float(todays_trade_log['price'].iloc[i])
        old_data=get_historical_data(symbol=symbol,interval="5m",token=token,exch_seg=exchange,candle_type="NORMAL")
        st_10_2=float(old_data['Supertrend_10_2'].iloc[-1])
        st_7_3=float(old_data['Supertrend'].iloc[-1])
        close_price=float(old_data['Close'].iloc[-1])
        if st_7_3 < close_price: todays_trade_log['Stop Loss'].iloc[i]=st_7_3
        elif st_10_2 < close_price: todays_trade_log['Stop Loss'].iloc[i]=st_10_2
        todays_trade_log['Stop Loss'].iloc[i]=int(todays_trade_log['Stop Loss'].iloc[i])
      except Exception as e:
        print(e)
  return(todays_trade_log)

def print_ltp():
  try:
    data=pd.DataFrame(obj.getMarketData(mode="OHLC",exchangeTokens={ "NSE": ["99926000","99926009"], "NFO": []})['data']['fetched'])
    data['change']=data['ltp']-data['close']
    print_sting=datetime.datetime.now(tz=gettz('Asia/Kolkata')).replace(microsecond=0, tzinfo=None).time()
    for i in range(0,len(data)):
      if data.iloc[i]['tradingSymbol']=="Nifty 50" and int(data.iloc[i]['ltp'])>1:st.session_state['Nifty']=int(data.iloc[i]['ltp'])
      if data.iloc[i]['tradingSymbol']=="Nifty Bank" and int(data.iloc[i]['ltp'])>1:st.session_state['BankNifty']=int(data.iloc[i]['ltp'])
      print_sting=f"{print_sting} {data.iloc[i]['tradingSymbol']} {int(data.iloc[i]['ltp'])}({int(data.iloc[i]['change'])})"
      print_sting=print_sting.replace("Nifty 50","Nifty")
      print_sting=print_sting.replace("Nifty Bank","BankNifty")
      placeholder.text(print_sting)
  except Exception as e: pass

if 'Nifty' not in st.session_state:print_ltp()
#main algo code
def telegram_bot_sendtext(bot_message):
  BOT_TOKEN = '5051044776:AAHh6XjxhRT94iXkR4Eofp2PPHY3Omk2KtI'
  BOT_CHAT_ID = '-1001542241163'
  bot_message=st.session_state['user_name']+':\n'+bot_message
  send_text = 'https://api.telegram.org/bot' + BOT_TOKEN + '/sendMessage?chat_id=' + BOT_CHAT_ID + \
                '&parse_mode=HTML&text=' + bot_message
  response = requests.get(send_text)


def get_token_info(symbol='-',token='-',exch_seg='-'):
  if symbol=='-' and token=='-': symbol,token,exch_seg='-','-','-'
  if token=='-':
    df=token_df[token_df['symbol'].str.contains(symbol)]
    if len(df)!=1 : df=df[df['symbol'].str.contains("-EQ") & (df['exch_seg'] == 'NSE') & (df['name']==symbol)]
    if df.empty==False : symbol,token,exch_seg=df.iloc[0]['symbol'],df.iloc[0]['token'],df.iloc[0]['exch_seg']
  elif symbol=='-':
    df=token_df[(token_df['token']==str(token)) & ((token_df['exch_seg']=='NSE') | (token_df['exch_seg']=='NFO'))]
    if df.empty==False : symbol,token,exch_seg=df.iloc[0]['symbol'],df.iloc[0]['token'],df.iloc[0]['exch_seg']
  return symbol,token,exch_seg

def getTokenInfo_index(symbol):
  df = token_df
  return df[(df['exch_seg'] == 'NSE') & (df['symbol']== (symbol))]

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
  print(f"{symbol} LTP:{indexLtp} {ce_strike_symbol['symbol']} & {pe_strike_symbol['symbol']}")
  #print(symbol+' LTP:',indexLtp,ce_strike_symbol['symbol'],'&',pe_strike_symbol['symbol'])
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

def get_ltp_price(symbol="-",token="-",exch_seg='-'):
  try:
    return obj.getMarketData("LTP",{exch_seg:[token]})['data']['fetched'][0]['ltp']
  except:
    try:
      ltpInfo = obj.ltpData(exch_seg,symbol,token)
      return ltpInfo['data']['ltp']
    except Exception as e:
      return "Unable to get LTP"
    
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
    except Exception as e:
      print("Order placement failed: ",e)
      orderId='Order placement failed'
      LTP_Price='Order placement failed'
  return orderId,LTP_Price

def modify_order(variety,orderid,ordertype,producttype,price,quantity,tradingsymbol,symboltoken,exchange,triggerprice=0,squareoff=0,stoploss=0):
  modifyparams = {"variety": variety,"orderid": orderid,"ordertype": ordertype,"producttype": producttype,
                  "duration": "DAY","price": price,"quantity": quantity,"tradingsymbol":tradingsymbol,
                  "symboltoken":symboltoken,"exchange":exchange,"squareoff":squareoff,"stoploss": stoploss,"triggerprice":triggerprice}
  obj.modifyOrder(modifyparams)
  print('Order modify')

def cancel_order(orderID,variety):
  obj.cancelOrder(orderID,variety=variety)
  print('order cancelled',orderID)

def buy_option(symbol,indicator_strategy,interval,index_sl="-"):
  try:
    option_token=symbol['token']
    option_symbol=symbol['symbol']
    lotsize=int(symbol['lotsize'])*lots_to_trade
    orderId,ltp_price=place_order(token=option_token,symbol=option_symbol,qty=lotsize,buy_sell='BUY',ordertype='MARKET',price=0,
                          variety='NORMAL',exch_seg='NFO',producttype='CARRYFORWARD',ordertag=indicator_strategy)
    if "(" in indicator_strategy and ")" in indicator_strategy:
      stop_loss=(indicator_strategy.split('('))[1].split(':')[0]
      target_price=(indicator_strategy.split(stop_loss+':'))[1].split(')')[0]
      stop_loss=int(float(stop_loss))
      target_price=int(float(target_price))
    elif "Manual" in indicator_strategy:
      sl=banknifty_sl if "BANK" in option_symbol else nifty_sl
      tgt=banknifty_target if "BANK" in option_symbol else nifty_target
      if target_type == 'Points':
        stop_loss=ltp_price-sl
        target_price=ltp_price+tgt
      else:
        stop_loss=ltp_price*(100-sl)/100
        target_price=ltp_price*(100+tgt)/100
    else:
      old_data=get_historical_data(symbol=option_symbol,interval='5m',token=option_token,exch_seg="NFO",candle_type="NORMAL")
      ltp_price=float(old_data['Close'].iloc[-1])
      st_price=float(old_data['Supertrend'].iloc[-1]) if float(old_data['Supertrend'].iloc[-1])<ltp_price else 0
      st_10_price=float(old_data['Supertrend_10_2'].iloc[-1]) if float(old_data['Supertrend_10_2'].iloc[-1])<ltp_price else 0
      stop_loss=int(max(st_price,st_10_price,ltp_price*0.7))
      target_price=int(float(ltp_price)+(float(ltp_price)-float(stop_loss))*2)
      indicator_strategy=indicator_strategy+ " (" +str(stop_loss)+":"+str(target_price)+') '
    if str(orderId)=='Order placement failed': return
    orderbook=obj.orderBook()['data']
    orderbook=pd.DataFrame(orderbook)
    orders= orderbook[(orderbook['orderid'] == orderId)]
    orders_status=orders.iloc[0]['orderstatus']; trade_price=orders.iloc[0]['averageprice']
    if orders_status != 'complete': trade_price='-'
    order_price=ltp_price if trade_price=='-' else trade_price
    if trade_price!='-':
      if target_order_type=="Target":
        place_order(token=option_token,symbol=option_symbol,qty=lotsize,buy_sell='SELL',ordertype='LIMIT',price=target_price,
                    variety='NORMAL',exch_seg='NFO',producttype='CARRYFORWARD',ordertag=str(orderId)+" Target order Placed")
      else:
        place_order(token=option_token,symbol=option_symbol,qty=lotsize,buy_sell='SELL',ordertype='STOPLOSS_LIMIT',price=stop_loss,
                    variety='STOPLOSS',exch_seg='NFO',producttype='CARRYFORWARD',triggerprice=stop_loss,squareoff=stop_loss,
                    stoploss=stop_loss, ordertag=str(orderId)+" Stop Loss order Placed")
    buy_msg=(f'Buy: {option_symbol}\nPrice: {trade_price} LTP: {ltp_price}\n{indicator_strategy}\nTarget: {target_price} Stop Loss: {stop_loss}')
    print(buy_msg)
    telegram_bot_sendtext(buy_msg)
  except Exception as e:
    print('Error in buy_option:',e)

def cancel_options_all_order(bnf_signal='-',nf_signal='-'):
  orderbook,pending_orders=get_order_book()
  orderlist = orderbook[((orderbook['orderstatus'] != 'complete') & (orderbook['orderstatus'] != 'cancelled') &
                      (orderbook['orderstatus'] != 'rejected') & (orderbook['orderstatus'] != 'AMO CANCELLED'))]
  orderlist_a = orderbook[(orderbook['variety'] == 'ROBO') & (orderbook['transactiontype'] == 'BUY') & (orderbook['orderstatus'] == 'complete')]
  orderlist=orderlist.append(orderlist_a)
  orderlist=orderlist[['orderid','updatetime','symboltoken','tradingsymbol','exchange','price','variety','quantity','status']]
  for i in range(0,len(orderlist)):
    try:
      tradingsymbol=orderlist['tradingsymbol'].iloc[i]
      if ((bnf_signal=='Sell' and tradingsymbol[-2:]=='CE' and tradingsymbol[:4]=='BANK') or
        (bnf_signal=='Buy' and tradingsymbol[-2:]=='PE' and tradingsymbol[:4]=='BANK') or
        (nf_signal=='Sell' and tradingsymbol[-2:]=='CE' and tradingsymbol[:5]=='NIFTY') or
        (nf_signal=='Buy' and tradingsymbol[-2:]=='PE' and tradingsymbol[:5]=='NIFTY')):
        cancel_order(orderlist['orderid'].iloc[i],orderlist['variety'].iloc[i])
    except Exception as e:
      print("Error in cancel_options_all_order", e)

def cancel_all_order(symbol):
  orderbook,pending_orders=get_order_book()
  try:
    if isinstance(orderbook,NoneType)!=True:
      orderlist = orderbook[(orderbook['tradingsymbol'] == symbol) &
                            ((orderbook['orderstatus'] != 'complete') & (orderbook['orderstatus'] != 'cancelled') &
                              (orderbook['orderstatus'] != 'rejected') & (orderbook['orderstatus'] != 'AMO CANCELLED'))]
      orderlist_a = orderbook[(orderbook['tradingsymbol'] == symbol) & (orderbook['variety'] == 'ROBO') &
                              (orderbook['transactiontype'] == 'BUY') & (orderbook['orderstatus'] == 'complete')]
      orderlist=orderlist.append(orderlist_a)
      for i in range(0,len(orderlist)):
        cancel_order(orderlist.iloc[i]['orderid'],orderlist.iloc[i]['variety'])
  except Exception as e:
    print("Error cancel_all_order",e)

def get_order_book():
  try:
    for attempt in range(3):
      try:
        orderbook=obj.orderBook()['data']
        if orderbook!=None: break
      except: pass
    if orderbook!=None: #or isinstance(orderbook,NoneType)!=True
      orderbook= pd.DataFrame.from_dict(orderbook)
      orderbook['updatetime'] = pd.to_datetime(orderbook['updatetime'])
      orderbook=orderbook.sort_values(by = ['updatetime'], ascending = [True], na_position = 'first')
      #orderbook['price']="-"
      for i in range(0,len(orderbook)):
        if orderbook['ordertag'].iloc[i]=="": orderbook['ordertag'].iloc[i]="-"
        if orderbook['status'].iloc[i]=="complete":
          orderbook['ordertag'].iloc[i]="*" + orderbook['ordertag'].iloc[i]
          orderbook['price'].iloc[i]=orderbook['averageprice'].iloc[i]
  except Exception as e:
    print("Error in getting orderbook")
    orderbook= pd.DataFrame(columns = ['variety', 'ordertype', 'producttype', 'duration', 'price','triggerprice', 'quantity', 'disclosedquantity',
                'squareoff','stoploss', 'trailingstoploss', 'tradingsymbol', 'transactiontype','exchange', 'symboltoken', 'ordertag', 'instrumenttype',
                'strikeprice','optiontype', 'expirydate', 'lotsize', 'cancelsize', 'averageprice','filledshares', 'unfilledshares', 'orderid', 'text',
                'status','orderstatus', 'updatetime', 'exchtime', 'exchorderupdatetime','fillid', 'filltime', 'parentorderid'])
    pending_orders=orderbook
    print("Error in get_order_book",e)
  pending_orders = orderbook[((orderbook['orderstatus'] != 'complete') & (orderbook['orderstatus'] != 'cancelled') &
                              (orderbook['orderstatus'] != 'rejected') & (orderbook['orderstatus'] != 'AMO CANCELLED'))]
  return orderbook,pending_orders

def get_open_position():
  try:
    position=obj.position()['data']
    if position!=None:
      position=pd.DataFrame(position)
      position[['realised', 'unrealised']] = position[['realised', 'unrealised']].astype(float)
    else:
      position= pd.DataFrame(columns = ["exchange","symboltoken","producttype","tradingsymbol","symbolname","instrumenttype","priceden",
                                  "pricenum","genden","gennum","precision","multiplier","boardlotsize","buyqty","sellqty","buyamount",
                                  "sellamount","symbolgroup","strikeprice","optiontype","expirydate","lotsize","cfbuyqty","cfsellqty",
                                  "cfbuyamount","cfsellamount","buyavgprice","sellavgprice","avgnetprice","netvalue","netqty","totalbuyvalue",
                                  "totalsellvalue","cfbuyavgprice","cfsellavgprice","totalbuyavgprice","totalsellavgprice","netprice",'realised', 'unrealised'])
  except Exception as e:
    position= pd.DataFrame(columns = ["exchange","symboltoken","producttype","tradingsymbol","symbolname","instrumenttype","priceden",
                                  "pricenum","genden","gennum","precision","multiplier","boardlotsize","buyqty","sellqty","buyamount",
                                  "sellamount","symbolgroup","strikeprice","optiontype","expirydate","lotsize","cfbuyqty","cfsellqty",
                                  "cfbuyamount","cfsellamount","buyavgprice","sellavgprice","avgnetprice","netvalue","netqty","totalbuyvalue",
                                  "totalsellvalue","cfbuyavgprice","cfsellavgprice","totalbuyavgprice","totalsellavgprice","netprice",'realised', 'unrealised'])
  open_position = position[(position['netqty'] > '0') & (position['instrumenttype'] == 'OPTIDX')]
  if len(position)!=0:
    print(position[['tradingsymbol','netqty','totalbuyavgprice','totalsellavgprice','realised', 'unrealised', 'ltp']].to_string(index=False))
  return position,open_position

def sl_trail():
  position,open_position=get_open_position()
  for i in range(0,len(open_position)):
    try:
        symbol=open_position['tradingsymbol'].iloc[i]
        token=open_position['symboltoken'].iloc[i]
        exchange=open_position['exchange'].iloc[i]
        qty=open_position['netqty'].iloc[i]
        price=float(open_position['totalbuyavgprice'].iloc[i])
        old_data=get_historical_data(symbol=symbol,interval="5m",token=token,exch_seg=exchange,candle_type="NORMAL")
        st_10_2=float(old_data['Supertrend_10_2'].iloc[-1])
        st_7_3=float(old_data['Supertrend'].iloc[-1])
        ema_low=float(old_data['EMA_Low'].iloc[-1])
        close_price=float(old_data['Close'].iloc[-1])
        if st_7_3 < close_price: sl=st_7_3
        elif st_10_2 < close_price: sl=st_10_2
        else: sl=float(max(close_price)*0.7)
        cancel_all_order(symbol)
        orderId,ltp_price=place_order(token=token,symbol=symbol,qty=qty,buy_sell='SELL',ordertype='STOPLOSS_LIMIT',price=sl,
                variety='STOPLOSS',exch_seg='NFO',producttype='CARRYFORWARD',triggerprice=sl,squareoff=sl, stoploss=sl,ordertag="SL Order")
    except Exception as e:
        print(e)
    
def get_trade_info(df):
  for i in ['St Trade','MACD Trade','PSAR Trade','DI Trade','MA Trade','EMA Trade','BB Trade','Trade','Trade End',
            'Rainbow MA','Rainbow Trade','MA 21 Trade','ST_10_2 Trade','Two Candle Theory','HMA Trade','VWAP Trade',
            'EMA_5_7 Trade','ST_10_4_8 Trade','EMA_High_Low Trade','RSI MA Trade','RSI_60 Trade']:df[i]='-'
  if df['Time Frame'][0]=="3m" or df['Time Frame'][0]=="THREE MINUTE" or df['Time Frame'][0]=="3min": df['Time Frame']="3m";time_frame="3m"
  elif df['Time Frame'][0]=="5m" or df['Time Frame'][0]=="FIVE MINUTE" or df['Time Frame'][0]=="5min": df['Time Frame']="5m";time_frame="5m"
  elif df['Time Frame'][0]=="15m" or df['Time Frame'][0]=="FIFTEEN MINUTE" or df['Time Frame'][0]=="15min": df['Time Frame']="15m";time_frame="15m"
  elif df['Time Frame'][0]=="1m" or df['Time Frame'][0]=="ONE MINUTE" or df['Time Frame'][0]=="1min": df['Time Frame']="1m";time_frame="1m"
  time_frame=df['Time Frame'][0]
  Symbol=df['Symbol'][0]
  df['Brahmastra']=''
  for i in range(0,len(df)):
    try:
      #df['Date'][i]=df['Datetime'][i].strftime('%Y.%m.%d')
      if df['Close'][i-1]<=df['Supertrend'][i-1] and df['Close'][i]> df['Supertrend'][i]: df['St Trade'][i]="Buy"
      elif df['Close'][i-1]>=df['Supertrend'][i-1] and df['Close'][i]< df['Supertrend'][i]: df['St Trade'][i]="Sell"

      if df['MACD'][i]>df['MACD signal'][i] and df['MACD'][i-1]< df['MACD signal'][i-1]: df['MACD Trade'][i]="Buy"
      elif df['MACD'][i]<df['MACD signal'][i] and df['MACD'][i-1]> df['MACD signal'][i-1]: df['MACD Trade'][i]="Sell"

      if df['Close'][i-1]<=df['PSAR'][i-1] and df['Close'][i]> df['PSAR'][i]: df['PSAR Trade'][i]="Buy"
      elif df['Close'][i-1]>=df['PSAR'][i-1] and df['Close'][i]< df['PSAR'][i]: df['PSAR Trade'][i]="Sell"

      if df['PLUS_DI'][i-1]<=df['MINUS_DI'][i-1] and df['PLUS_DI'][i]> df['MINUS_DI'][i]: df['DI Trade'][i]="Buy"
      elif df['PLUS_DI'][i-1]>=df['MINUS_DI'][i-1] and df['PLUS_DI'][i]< df['MINUS_DI'][i]: df['DI Trade'][i]="Sell"

      if df['MA_50'][i-1]<=df['MA_200'][i-1] and df['MA_50'][i]> df['MA_200'][i]: df['MA Trade'][i]="Buy"
      elif df['MA_50'][i-1]>=df['MA_200'][i-1] and df['MA_50'][i]< df['MA_200'][i]: df['MA Trade'][i]="Sell"

      if df['EMA_12'][i-1]<=df['EMA_26'][i-1] and df['EMA_12'][i]> df['EMA_26'][i]: df['EMA Trade'][i]="Buy"
      elif df['EMA_12'][i-1]>=df['EMA_26'][i-1] and df['EMA_12'][i]< df['EMA_26'][i]: df['EMA Trade'][i]="Sell"

      if df['EMA_5'][i-1]<=df['EMA_7'][i-1] and df['EMA_5'][i]> df['EMA_7'][i]: df['EMA_5_7 Trade'][i]="Buy"
      elif df['EMA_5'][i-1]>=df['EMA_7'][i-1] and df['EMA_5'][i]< df['EMA_7'][i]: df['EMA_5_7 Trade'][i]="Sell"

      if df['Close'][i-1]< df['MA_21'][i-1] and df['Close'][i]> df['MA_21'][i]: df['MA 21 Trade'][i]="Buy"
      elif df['Close'][i-1]> df['MA_21'][i-1] and df['Close'][i]< df['MA_21'][i]: df['MA 21 Trade'][i]="Sell"

      if df['Close'][i-1]< df['Supertrend_10_2'][i-1] and df['Close'][i]> df['Supertrend_10_2'][i]: df['ST_10_2 Trade'][i]="Buy"
      elif df['Close'][i-1]> df['Supertrend_10_2'][i-1] and df['Close'][i]< df['Supertrend_10_2'][i]: df['ST_10_2 Trade'][i]="Sell"

      if df['HMA_21'][i-1]< df['HMA_55'][i-1] and df['HMA_21'][i]> df['HMA_55'][i]: df['HMA Trade'][i]="Buy"
      elif df['HMA_21'][i-1]> df['HMA_55'][i-1] and df['HMA_21'][i]< df['HMA_55'][i]: df['HMA Trade'][i]="Sell"

      if int(df['RSI'][i])>=60 and int(df['RSI'][i-1]) < 60 : df['RSI_60 Trade'][i]="Buy"

      if int(df['RSI'][i])>=60 or int(df['RSI'][i])<=40:
        if df['Close'][i-1]<df['EMA_High'][i-1] and df['Close'][i] > df['EMA_High'][i]: df['EMA_High_Low Trade'][i]="Buy"
        if df['Close'][i-1]>df['EMA_Low'][i-1] and df['Close'][i]<df['EMA_Low'][i]: df['EMA_High_Low Trade'][i]="Sell"

      if (df['Close'][i-1]<df['Open'][i-1] and df['Close'][i]< df['Open'][i] and
        df['Close'][i]< df['Supertrend_10_2'][i] and df['RSI'][i]<=40 and df['VWAP'][i]>df['Close'][i] and
        df['Close'][i]<df['WMA_20'][i] and df['Volume'][i]>1000):
        df['Two Candle Theory'][i]='Sell'
      elif (df['Close'][i-1] > df['Open'][i-1] and df['Close'][i] > df['Open'][i] and
        df['Close'][i] > df['Supertrend_10_2'][i] and df['RSI'][i] >= 50 and df['VWAP'][i]<df['Close'][i] and
        df['Close'][i]>df['WMA_20'][i] and df['Volume'][i]>1000):
        df['Two Candle Theory'][i]='Buy'

      RSI=df['RSI'][i];          ST=df['St Trade'][i]
      MACD=df['MACD Trade'][i];  EMA=df['EMA Trade'][i]
      MA=df['MA 21 Trade'][i];   ST_10_2=df['ST_10_2 Trade'][i]
      RSI_60=df['RSI_60 Trade'][i]
      Two_Candle_Theory=df['Two Candle Theory'][i]; HMA_Trade=df['HMA Trade'][i]
      EMA_5_7_Trade=df['EMA_5_7 Trade'][i];EMA_High_Low=df['EMA_High_Low Trade'][i]

      df['Brahmastra'][i]=' Brahmastra' if (ST==MACD or ST_10_2==MACD) and MACD!="-" else ''
      if time_frame=="1m" or time_frame=="ONE_MINUTE" or time_frame=="1min":
        if (ST=="Buy" or MACD=="Buyy" or EMA=="Buyy" or MA=="Buyy" or ST_10_2=="Buyy" or EMA_High_Low=="Buy") and (int(RSI)<=40 or int(RSI)>=60) :
          df['Trade'][i]="Buy"; df['Trade End'][i]="Buyy"
        elif (ST=="Sell" or MACD=="Selll" or EMA=="Selll" or MA=="Selll" or ST_10_2=="Selll" or EMA_High_Low=="Sell") and (int(RSI)<=40 or int(RSI)>=60):
          df['Trade'][i]="Sell"; df['Trade End'][i]="Selll"

      elif time_frame=="3m" or time_frame=="THREE_MINUTE" or time_frame=="3min" or time_frame=="Candle Pattern":
        if Two_Candle_Theory=="Buy" :
          df['Trade'][i]="Buy"; df['Trade End'][i]="Buy"
        elif Two_Candle_Theory=="Sell":
          df['Trade'][i]="Sell"; df['Trade End'][i]="Sell"

      elif time_frame=="5m" or time_frame=="FIVE_MINUTE" or time_frame=="5min":
        if (ST=="Buy" or EMA=="Buyy" or MA=="Buyy" or ST_10_2=="Buy" or HMA_Trade=="Buyy" or MA=='Buyy' or RSI_60=="Buyy"):
          df['Trade'][i]="Buy"; df['Trade End'][i]="Buy"
        elif (ST=="Sell" or EMA=="Selll" or MA=="Selll" or ST_10_2=="Sell" or HMA_Trade=="Selll" or MA=='Selll'):
          df['Trade'][i]="Sell"; df['Trade End'][i]="Sell"
        #if EMA_High_Low=="Buy":df['Trade'][i]="Buy";df['Trade End'][i]="Buy"
        #if EMA_High_Low=="Sell":df['Trade'][i]="Sell";df['Trade End'][i]="Sell"

      elif time_frame=="15m" or time_frame=="FIFTEEN_MINUTE" or time_frame=="15min":
        if (ST=="Buy" or MACD=="Buyy" or EMA=="Buyy" or MA=="Buyy" or ST_10_2=="Buy" or RSI_60=="Buyy"):
          df['Trade'][i]="Buy"; df['Trade End'][i]="Buy"
        elif (ST=="Sell" or MACD=="Selll" or EMA=="Selll" or MA=="Selll" or ST_10_2=="Sell"):
          df['Trade'][i]="Sell"; df['Trade End'][i]="Sell"

      if 'FUT' in Symbol:
        if df['Close'][i-1]< df['VWAP'][i-1] and df['Close'][i]> df['VWAP'][i]: df['VWAP Trade'][i]="Buy"
        elif df['Close'][i-1]> df['VWAP'][i-1] and df['Close'][i]< df['VWAP'][i]: df['VWAP Trade'][i]="Sell"

    except Exception as e:
      pass
  df['ADX']=df['ADX'].round(decimals = 2)
  df['ADX']= df['ADX'].astype(str)
  df['Atr']=df['Atr'].round(decimals = 2)
  df['Atr']= df['Atr'].astype(str)
  df['RSI']=df['RSI'].round(decimals = 2)
  df['RSI']= df['RSI'].astype(str)
  symbol_type="IDX" if Symbol=="^NSEBANK" or Symbol=="BANKNIFTY" or Symbol=="^NSEI" or Symbol=="NIFTY" else "OPT"
  df['Indicator']=(symbol_type+" "+df['Trade']+" "+df['Time Frame']+":"+" ST:"+df['St Trade']+" EMA:"+df['EMA Trade']+" MACD:"+df['MACD Trade']+
                   " ST_10_2:"+df['ST_10_2 Trade']+ " MA_21:"+df['MA 21 Trade']+" Two Candle Theory:"+df['Two Candle Theory']+" RSI_60:"+df['RSI_60 Trade'])
  df['RSI']= df['RSI'].astype(float)
  df['Indicator'] = df['Indicator'].str.replace(' ST:-','')
  df['Indicator'] = df['Indicator'].str.replace(' EMA:-','')
  df['Indicator'] = df['Indicator'].str.replace(' MA:-','')
  df['Indicator'] = df['Indicator'].str.replace(' MACD:-','')
  df['Indicator'] = df['Indicator'].str.replace(' ST_10_2:-','')
  df['Indicator'] = df['Indicator'].str.replace(' HMA:-','')
  df['Indicator'] = df['Indicator'].str.replace(' MA_21:-','')
  df['Indicator'] = df['Indicator'].str.replace(' EMA_5_7 Trade:-','')
  df['Indicator'] = df['Indicator'].str.replace(' EMA_5_7:-','')
  df['Indicator'] = df['Indicator'].str.replace(' VWAP:-','')
  df['Indicator'] = df['Indicator'].str.replace(' EMA_H_L:-','')
  df['Indicator'] = df['Indicator'].str.replace(' Two Candle Theory:-','')
  df['Indicator'] = df['Indicator'].str.replace(' RSI_60:-','')
  df['Indicator'] = df['Indicator'].str.replace(':Buy',',')
  df['Indicator'] = df['Indicator'].str.replace(':Sell',',')
  df['Indicator'] = df['Indicator'].str.replace('3m Two Candle Theory:','2 Candle Theory:')
  df["Indicator"] = df["Indicator"].str[:-1]
  return df

def calculate_indicator(df):
  try:
    df['RSI']=pdta.rsi(df['Close'],timeperiod=14)
    df['UBB']=pdta.bbands(df['Close'],length=20, std=2, ddof=0)['BBU_20_2.0']
    df['MBB']=pdta.bbands(df['Close'],length=20, std=2, ddof=0)['BBM_20_2.0']
    df['LBB']=pdta.bbands(df['Close'],length=20, std=2, ddof=0)['BBL_20_2.0']
    df['MACD']=pdta.macd(close=df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)['MACD_12_26_9']
    df['MACD signal']=pdta.macd(close=df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)['MACDs_12_26_9']
    df['Macdhist']=pdta.macd(close=df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)['MACDh_12_26_9']
    df['Supertrend']=pdta.supertrend(high=df['High'],low=df['Low'],close=df['Close'],length=7,multiplier=3)['SUPERT_7_3.0']
    df['Supertrend_10_2']=pdta.supertrend(high=df['High'],low=df['Low'],close=df['Close'],length=10,multiplier=2)['SUPERT_10_2.0']
    df['PSAR']=pdta.psar(high=df['High'],low=df['Low'],acceleration=0.02, maximum=0.2)['PSARl_0.02_0.2']
    df['ADX']=pdta.adx(df['High'],df['Low'],df['Close'],14)['ADX_14']
    df['MINUS_DI']=pdta.adx(df['High'],df['Low'],df['Close'],14)['DMN_14']
    df['PLUS_DI']=pdta.adx(df['High'],df['Low'],df['Close'],14)['DMP_14']
    df['MA_200']=df['Close'].rolling(200).mean()
    df['MA_50']=df['Close'].rolling(50).mean()
    df['EMA_12']=pdta.ema(df['Close'],length=12)
    df['EMA_26']=pdta.ema(df['Close'],length=26)
    df['EMA_13']=pdta.ema(df['Close'],length=13)
    df['EMA_5']=pdta.ema(df['Close'],length=5)
    df['EMA_7']=pdta.ema(df['Close'],length=7)
    df['MA_1']=df['Close'].rolling(1).mean()
    df['MA_2']=df['Close'].rolling(2).mean()
    df['MA_3']=df['Close'].rolling(3).mean()
    df['MA_4']=df['Close'].rolling(4).mean()
    df['MA_5']=df['Close'].rolling(5).mean()
    df['MA_6']=df['Close'].rolling(6).mean()
    df['MA_7']=df['Close'].rolling(7).mean()
    df['MA_8']=df['Close'].rolling(8).mean()
    df['MA_9']=df['Close'].rolling(9).mean()
    df['MA_10']=df['Close'].rolling(10).mean()
    df['MA_21']=pdta.ema(df['Close'],length=21)
    df['WMA_20']=pdta.wma(df['Close'],length=20)
    df['Atr']=pdta.atr(high=df['High'], low=df['Low'], close=df['Close'], length=14)
    df['HMA_21']=pdta.hma(df['Close'],length=21)
    df['HMA_55']=pdta.hma(df['Close'],length=55)
    df['RSI_MA']=df['RSI'].rolling(14).mean()
    df['Supertrend_10_4']=pdta.supertrend(high=df['High'],low=df['Low'],close=df['Close'],length=10,multiplier=4)['SUPERT_10_4.0']
    df['Supertrend_10_8']=pdta.supertrend(high=df['High'],low=df['Low'],close=df['Close'],length=10,multiplier=8)['SUPERT_10_8.0']
    df['EMA_High']=pdta.ema(df['High'],length=21)
    df['EMA_Low']=pdta.ema(df['Low'],length=21)
    #df = df.round(decimals=2)
    df=df.tail(5)
    df=get_trade_info(df)
    return df
  except Exception as e:
    print("Error in calculate Indicator",e)
    return df

def get_historical_data(symbol="-",interval='5m',token="-",exch_seg="-",candle_type="NORMAL"):
  try:
    if (symbol=="^NSEI" or symbol=="NIFTY") : symbol,token,exch_seg="^NSEI",99926000,"NSE"
    elif (symbol=="^NSEBANK" or symbol=="BANKNIFTY") : symbol,token,exch_seg="^NSEBANK",99926009,"NSE"
    if symbol[3:]=='-EQ': symbol=symbol[:-3]+".NS"
    odd_candle,odd_interval,df=False,'','No Data Found'
    if (interval=="5m" or interval=='FIVE_MINUTE'): period,delta_time,agl_interval,yf_interval,odd_interval=7,5,"FIVE_MINUTE","5m",'5m'
    elif (interval=="15m" or interval=='FIFTEEN_MINUTE'): period,delta_time,agl_interval,yf_interval,odd_interval=10,15,"FIFTEEN_MINUTE","15m",'15m'
    elif (interval=="60m" or interval=='ONE_HOUR'): period,delta_time,agl_interval,yf_interval,odd_interval=30,60,"ONE_HOUR","60m",'60m'
    elif (interval=="1m" or interval=='ONE_MINUTE') : period,delta_time,agl_interval,yf_interval,odd_interval=7,1,"ONE_MINUTE","1m",'1m'
    elif (interval=="1d" or interval=='ONE_DAY') : period,delta_time,agl_interval,yf_interval,odd_interval=100,5,"ONE_DAY","1d",'1d'
    else:
      period,delta_time,agl_interval,yf_interval,odd_candle=7,1,"ONE_MINUTE","1m",True
      for i in interval:
        if(i.isdigit()): odd_interval+=i
      delta_time=int(odd_interval)
      odd_interval+='m'
    #if (symbol[0]=="^" or "NS" in symbol) and symbol !="-":
    #  df=yfna_data(symbol,yf_interval,str(period)+"d")
    if isinstance(df, str):
      to_date= datetime.datetime.now(tz=gettz('Asia/Kolkata'))
      from_date = to_date - datetime.timedelta(days=period)
      fromdate = from_date.strftime("%Y-%m-%d %H:%M")
      todate = to_date.strftime("%Y-%m-%d %H:%M")
      symbol,token,exch_seg=get_token_info(symbol=symbol,token=token,exch_seg=exch_seg)
      df=angel_data(token,agl_interval,exch_seg,fromdate,todate)
    if odd_candle ==True:
      df=df.groupby(pd.Grouper(freq=odd_interval+'in')).agg({"Date":"first","Datetime":"first","Open": "first", "High": "max",
                                                        "Low": "min", "Close": "last","Volume": "sum"})
      df=df[(df['Open']>0)]
    now=datetime.datetime.now(tz=gettz('Asia/Kolkata')).replace(microsecond=0, tzinfo=None)
    last_candle=now.replace(second=0, microsecond=0)- datetime.timedelta(minutes=delta_time)
    df = df[(df.index <= last_candle)]
    df['Time Frame']=odd_interval
    df.index.names = ['']
    if candle_type=="HEIKIN_ASHI": df=calculate_heikin_ashi(df)
    df['VWAP']=pdta.vwap(high=df['High'],low=df['Low'],close=df['Close'],volume=df['Volume'])
    df=df[['Date','Datetime','Open','High','Low','Close','Volume','VWAP','Time Frame']]
    df['Symbol']=symbol
    df=calculate_indicator(df)
    df=df.round(2)
    return df
  except Exception as e:
    print("get_historical_data",e)

def calculate_heikin_ashi(df):
  for i in range(2,len(df)):
    o=df['Open'][i-0]
    h=df['High'][i-0]
    l=df['Low'][i-0]
    c=df['Close'][i-0]
    df['Open'][i]=(o+c)/2
    df['Close'][i]=(o+h+l+c)/4
  return df

def yfna_data(symbol,interval,period):
  try:
    df=yf.Ticker(symbol).history(interval=interval,period=period)
    df['Datetime'] = df.index
    df['Datetime']=df['Datetime'].dt.tz_localize(None)
    df.index=df['Datetime']
    df=df[['Datetime','Open','High','Low','Close','Volume']]
    df['Date']=df['Datetime'].dt.strftime('%m/%d/%y')
    df['Datetime'] = pd.to_datetime(df['Datetime']).dt.time
    df=df[['Date','Datetime','Open','High','Low','Close','Volume']]
    if isinstance(df, str) or (isinstance(df, pd.DataFrame)==True and len(df)==0):
      print("Yahoo Data Not Found")
      return "No data found, symbol may be delisted"
    return df
  except:
    print("Yahoo Data Not Found")
    return "No data found, symbol may be delisted"

def angel_data(token,interval,exch_seg,fromdate,todate):
  try:
    historicParam={"exchange": exch_seg,"symboltoken": token,"interval": interval,"fromdate": fromdate, "todate": todate}
    res_json=obj.getCandleData(historicParam)
    df = pd.DataFrame(res_json['data'], columns=['timestamp','O','H','L','C','V'])
    df = df.rename(columns={'timestamp':'Datetime','O':'Open','H':'High','L':'Low','C':'Close','V':'Volume'})
    df['Datetime'] = pd.to_datetime(df['Datetime'],format = '%Y-%m-%d %H:%M:%S')
    df['Datetime']=df['Datetime'].dt.tz_localize(None)
    df = df.set_index('Datetime')
    df['Datetime']=pd.to_datetime(df.index,format = '%Y-%m-%d %H:%M:%S')
    df['Date']=df['Datetime'].dt.strftime('%m/%d/%y')
    df['Datetime'] = pd.to_datetime(df['Datetime']).dt.time
    df=df[['Date','Datetime','Open','High','Low','Close','Volume']]
    if isinstance(df, str) or (isinstance(df, pd.DataFrame)==True and len(df)==0):
      print("Angel Data Not Found")
      return "No data found, symbol may be delisted"
    return df
  except:
    print("Angel Data Not Found")
    return "No data found, symbol may be delisted"
   
def manual_buy(index_symbol,ce_pe="CE",index_ltp="-"):
  if index_ltp=="-":
    if index_symbol=="BANKNIFTY" or index_symbol=="^NSEBANK": index_ltp=st.session_state['Bank Nifty']
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
