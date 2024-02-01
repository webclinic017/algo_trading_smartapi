"""# Main Code"""

# Commented out IPython magic to ensure Python compatibility.
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
import logzero
import re
import streamlit as st
print('....!!! Jay Shri Ganesh !!!....\n....!!! Jay Mahalaxmi !!!....\n....!!! Have a profitable Day !!!....')

# %load_ext autotime
pd.options.mode.chained_assignment = None
warnings.filterwarnings('ignore')
NoneType = type(None)
st.set_page_config(page_title="Algo App",layout="wide",initial_sidebar_state="expanded",)
st.markdown("""
  <style>
    .block-container {padding-top: 0.5rem;padding-bottom: 0rem;padding-left: 2rem;padding-right: 5rem;}  
  </style>
  """, unsafe_allow_html=True)
global lots_to_trade,target_order_type,five_m_timeframe,fifteen_m_timeframe,three_m_timeframe,one_m_timeframe,near_options_trade
global bnf_5m_trade,nf_5m_trade,sensex_5m_trade
global nf_5m_trade_end,bnf_5m_trade_end,sensex_5m_trade_end
lots_to_trade=1
target_order_type="Target"
five_m_timeframe="Yes"
fifteen_m_timeframe="Yes"
three_m_timeframe="No"
one_m_timeframe="No"
near_options_trade="Yes"
bnf_5m_trade="-"
nf_5m_trade="-"
sensex_5m_trade="-"
nf_5m_trade_end="-"
bnf_5m_trade_end="-"
sensex_5m_trade_end="-"

#Telegram Msg
def telegram_bot_sendtext(bot_message):
  BOT_TOKEN = '5051044776:AAHh6XjxhRT94iXkR4Eofp2PPHY3Omk2KtI'
  BOT_CHAT_ID = '-1001542241163'
  BOT_CHAT_ONE_MINUTE = '-1001542241163'
  #BOT_CHAT_ONE_MINUTE='-882387563'
  import requests
  bot_message=user+':\n'+bot_message
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

#Login Details
def get_user_pwd(user):
  global username,pwd,apikey,token
  if user=='Ganesh': username = 'G93179'; pwd = '4789'; apikey = 'CjOKjC5g'; token='U4EAZJ3L44CNJHNUZ56R22TPKI'
  elif user=='Kalyani': username = 'K205244'; pwd = '4789'; apikey = 'lzC7yJmt'; token='YDV6CJI6BEU3GWON7GZTZNU3RM'
  elif user=="Akshay": username='A325394'; pwd='1443'; apikey='OeSllszj'; token='G4OKBQKHXPS67EN2WMVP3TZ7X4'
  elif user=="Kailash": username='K80392'; pwd='8999'; apikey='A7Q0LWtF'; token='GEVK2DBIADONB3YRYKOALABXR4'
  return username,pwd,apikey,token,user

#Angel Login
username,pwd,apikey,token,user=get_user_pwd("Ganesh")
obj=SmartConnect(api_key=apikey)
if 'user_name' not in st.session_state:
  try:
    FEED_TOKEN = None;TOKEN_MAP = None;SMART_API_OBJ = None
    global user_name
    data = obj.generateSession(username,pwd,pyotp.TOTP(token).now())
    refreshToken= data['data']['refreshToken']
    feedToken=obj.getfeedToken()
    userProfile= obj.getProfile(refreshToken)
    aa= userProfile.get('data')
    st.session_state['user_name']=aa.get('name').title()
    st.session_state['login_time']=datetime.datetime.now(tz=gettz('Asia/Kolkata')).replace(microsecond=0, tzinfo=None).time()
    st.session_state['access_token']=obj.access_token
    st.session_state['refresh_token']=obj.refresh_token
    st.session_state['feed_token']=obj.feed_token
    st.session_state['userId']=obj.userId
    st.session_state['api_key']=apikey
    st.session_state['user_name']=aa.get('name').title().split(' ')[0]
  except Exception as e:
    print("Unable to login error in angel_login",e)

obj=SmartConnect(api_key=st.session_state['api_key'],access_token=st.session_state['access_token'],
                 refresh_token=st.session_state['refresh_token'],feed_token=st.session_state['feed_token'],userId=st.session_state['userId'])

def get_token_df():
  global token_df
  url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
  d = requests.get(url).json()
  token_df = pd.DataFrame.from_dict(d)
  token_df['expiry'] = pd.to_datetime(token_df['expiry']).apply(lambda x: x.date())
  token_df = token_df.astype({'strike': float})

  global bnf_expiry_day,nf_expiry_day,fnnf_expiry_day,sensex_expiry_day
  now_dt=datetime.datetime.now(tz=gettz('Asia/Kolkata')).date()-datetime.timedelta(days=0)
  bnf_expiry_day = (token_df[(token_df['name'] == 'BANKNIFTY') & (token_df['instrumenttype'] == 'OPTIDX') & (token_df['expiry']>=now_dt)])['expiry'].min()
  nf_expiry_day = (token_df[(token_df['name'] == 'NIFTY') & (token_df['instrumenttype'] == 'OPTIDX') & (token_df['expiry']>=now_dt)])['expiry'].min()
  fnnf_expiry_day = (token_df[(token_df['name'] == 'FINNIFTY') & (token_df['instrumenttype'] == 'OPTIDX') & (token_df['expiry']>=now_dt)])['expiry'].min()
  sensex_expiry_day = (token_df[(token_df['name'] == 'SENSEX') & (token_df['instrumenttype'] == 'OPTIDX') & (token_df['expiry']>=now_dt)])['expiry'].min()
  st.session_state['bnf_expiry_day']=bnf_expiry_day
  st.session_state['nf_expiry_day']=nf_expiry_day
  st.session_state['fnnf_expiry_day']=fnnf_expiry_day
  st.session_state['sensex_expiry_day']=sensex_expiry_day
  token_df=token_df[((token_df['name'] == 'BANKNIFTY') & (token_df['expiry'] == bnf_expiry_day) |
                   (token_df['name'] == 'NIFTY') & (token_df['expiry'] == nf_expiry_day) |
                   (token_df['name'] == 'FINNIFTY') & (token_df['expiry'] == fnnf_expiry_day) |
                   (token_df['name'] == 'SENSEX') & (token_df['expiry'] == sensex_expiry_day))]
  st.session_state['opt_list']=token_df

if 'bnf_expiry_day' not in st.session_state:get_token_df()
"""Order"""

#variety: NORMAL/STOPLOSS * transactiontype: BUY/SELL * ordertype: MARKET/LIMIT/STOPLOSS_LIMIT * producttype: DELIVERY/CARRYFORWARD
#Duration: DAY/IOC * exchange: BSE/NSE/NFO/MCX
#Place Order
def place_order(token,symbol,qty,buy_sell,ordertype='MARKET',price=0,variety='NORMAL',exch_seg='NFO',producttype='CARRYFORWARD',
                triggerprice=0,squareoff=0,stoploss=0,ordertag='-'):
  global orderId,LTP_Price
  try:
    orderparams = {"variety": variety,"tradingsymbol": symbol,"symboltoken": token,"transactiontype": buy_sell,"exchange": exch_seg,
      "ordertype": ordertype,"producttype": producttype,"duration": "DAY","price": int(float(price)),"squareoff":int(float(squareoff)),
      "stoploss": int(float(stoploss)),"quantity": str(qty),"triggerprice":int(float(triggerprice)),"ordertag":ordertag,"trailingStopLoss":5}
    orderId=obj.placeOrder(orderparams)
    LTP_Price=round(float(get_ltp_price(symbol=symbol,token=token,exch_seg=exch_seg)),2)
    print(f'{buy_sell} Order Placed: {orderId} Symbol: {symbol} LTP: {LTP_Price} Ordertag: {ordertag}')
    return orderId,LTP_Price
  except Exception as e:
    print("error in place_order Order placement failed: ",e)
    orderId='Order placement failed'
    LTP_Price='Order placement failed'
    return orderId,LTP_Price

#Modify Order
def modify_order(variety,orderid,ordertype,producttype,price,quantity,tradingsymbol,symboltoken,exchange,triggerprice=0,squareoff=0,stoploss=0):
  modifyparams = {"variety": variety,"orderid": orderid,"ordertype": ordertype,"producttype": producttype,
                  "duration": "DAY","price": price,"quantity": quantity,"tradingsymbol":tradingsymbol,
                  "symboltoken":symboltoken,"exchange":exchange,"squareoff":squareoff,"stoploss": stoploss,"triggerprice":triggerprice}
  obj.modifyOrder(modifyparams)
  print('Order modify')

#Cancel Order
def cancel_order(orderID,variety):
  obj.cancelOrder(orderID,variety=variety)
  print('order cancelled',orderID)

#Cancel all order of symbol
def cancel_all_order(symbol):
  #orderbook,pending_orders=get_order_book()
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

#gtt rule creation
def place_gtt_order(token,symbol,exch_seg,producttype,buy_sell,price,qty):
  try:
    gttCreateParams={"tradingsymbol" : symbol,"symboltoken" : token, "exchange" : exch_seg,"producttype" : producttype,
                     "transactiontype" : buy_sell,"price" : price, "qty" : qty,"disclosedqty": qty,"triggerprice" : price,"timeperiod" : 365}
    rule_id=obj.gttCreateRule(gttCreateParams)
    print("The GTT rule id is: {}".format(rule_id))
  except Exception as e:
    print("GTT Rule creation failed",e)

def get_open_position():
  global pnl,position,open_position
  position=obj.position()['data']
  if position!=None:
    position=pd.DataFrame(position)
    position[['realised', 'unrealised']] = position[['realised', 'unrealised']].astype(float)
  else:
    position= pd.DataFrame(columns = ["exchange","symboltoken","producttype","tradingsymbol","symbolname","instrumenttype","priceden",
                                  "pricenum","genden","gennum","precision","multiplier","boardlotsize","buyqty","sellqty","buyamount",
                                  "sellamount","symbolgroup","strikeprice","optiontype","expirydate","lotsize","cfbuyqty","cfsellqty",
                                  "cfbuyamount","cfsellamount","buyavgprice","sellavgprice","avgnetprice","netvalue","netqty","totalbuyvalue",
                                  "totalsellvalue","cfbuyavgprice","cfsellavgprice","totalbuyavgprice","totalsellavgprice","netprice",'realised', 'unrealised','ltp'])
  pnl=float(position['realised'].sum())+float(position['unrealised'].sum())
  open_position = position[(position['netqty'] > '0') & (position['instrumenttype'] == 'OPTIDX')]
  position=position[['tradingsymbol','netqty','totalbuyavgprice','totalsellavgprice','realised', 'unrealised', 'ltp']]
  now_time=datetime.datetime.now(tz=gettz('Asia/Kolkata')).replace(microsecond=0, tzinfo=None).time()
  position_updated.text(f"Position : {now_time}")
  position_datatable.dataframe(position,hide_index=True)
  if len(position)!=0:
    print(datetime.datetime.now(tz=gettz('Asia/Kolkata')).time().replace(microsecond=0))
    print(position[['tradingsymbol','netqty','totalbuyavgprice','totalsellavgprice','realised', 'unrealised', 'ltp']].to_string(index=False))
  return position,open_position

def update_price_orderbook_old(df):
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
          #df['price'].iloc[j]=float(ordertag.split("LTP: ",1)[1])
        if df['price'].iloc[j]==0:df['price'].iloc[j]='-'
      if df['price'].iloc[j]=='-':
        df['price'].iloc[j]=get_ltp_price(symbol=df['tradingsymbol'].iloc[j],token=df['symboltoken'].iloc[j],exch_seg=df['exchange'].iloc[j])
    except Exception as e:
      print("Error in update_price_orderbook_old",e)
  return df

def update_price_orderbook(orderbook):
  #pattern = r"Available funds - Rs\. ([-\d.]+) .+ You require Rs\. ([\d.]+) funds"
  pattern = r"Rs\. ([-\d.]+) .+ You require Rs\. ([\d.]+) funds"
  for j in range(0,len(orderbook)):
    try:
      if orderbook['averageprice'].iloc[j]!=0:
        orderbook['price'].iloc[j]=orderbook['averageprice'].iloc[j]
      else:
        text=orderbook['text'].iloc[j]
        match = re.search(pattern, text)
        if match:
          available_funds = match.group(1)
          required_funds = match.group(2)
          if int(float(required_funds)) <= 50000: orderbook['price'].iloc[j]=(round(float(required_funds)/float(orderbook['quantity'].iloc[j]),2))
    except Exception as e:
      print("Error in update_price_orderbook_old",e)
  return orderbook

#Get Order Book
def get_order_book():
  global orderbook,pending_orders
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
      orderbook=update_price_orderbook(orderbook)
      ltp_df=get_ltp_token(orderbook['symboltoken'])
      orderbook=pd.merge(orderbook, ltp_df, left_on='symboltoken', right_on='symbolToken')
      orderbook = orderbook.rename(columns={'exchange_x': 'exchange'})
      pending_orders = orderbook[((orderbook['orderstatus'] != 'complete') & (orderbook['orderstatus'] != 'cancelled') &
                              (orderbook['orderstatus'] != 'rejected') & (orderbook['orderstatus'] != 'AMO CANCELLED'))]
    else:
      orderbook= pd.DataFrame(columns = ['variety', 'ordertype', 'producttype', 'duration', 'price','triggerprice', 'quantity', 'disclosedquantity',
                'squareoff','stoploss', 'trailingstoploss', 'tradingsymbol', 'transactiontype','exchange', 'symboltoken', 'ordertag', 'instrumenttype',
                'strikeprice','optiontype', 'expirydate', 'lotsize', 'cancelsize', 'averageprice','filledshares', 'unfilledshares', 'orderid', 'text',
                'status','orderstatus', 'updatetime', 'exchtime', 'exchorderupdatetime','fillid', 'filltime', 'parentorderid','ltp'])
      pending_orders=orderbook
  except Exception as e:
    print("Error in getting orderbook")
    orderbook= pd.DataFrame(columns = ['variety', 'ordertype', 'producttype', 'duration', 'price','triggerprice', 'quantity', 'disclosedquantity',
                'squareoff','stoploss', 'trailingstoploss', 'tradingsymbol', 'transactiontype','exchange', 'symboltoken', 'ordertag', 'instrumenttype',
                'strikeprice','optiontype', 'expirydate', 'lotsize', 'cancelsize', 'averageprice','filledshares', 'unfilledshares', 'orderid', 'text',
                'status','orderstatus', 'updatetime', 'exchtime', 'exchorderupdatetime','fillid', 'filltime', 'parentorderid','ltp'])
    pending_orders=orderbook
    print("Error in get_order_book",e)
  new_orderbook=orderbook[['updatetime','orderid','transactiontype','status','tradingsymbol','price','quantity','ordertag']]
  now_time=datetime.datetime.now(tz=gettz('Asia/Kolkata')).replace(microsecond=0, tzinfo=None).time()
  order_book_updated.text(f"Orderbook : {now_time}")
  order_datatable.dataframe(new_orderbook,hide_index=True)
  return orderbook,pending_orders

def get_ltp_price(symbol="-",token="-",exch_seg='-'):
  symbol_i="-"
  if symbol=="BANKNIFTY" or symbol=="^NSEBANK": symbol_i="^NSEBANK"
  elif symbol=="NIFTY" or symbol=="^NSEI": symbol_i="^NSEI"
  elif symbol=="SENSEX" or symbol=="^BSESN": symbol_i="^BSESN"
  if symbol_i!="-":
    try:
      data=yf.Ticker(symbol_i).history(interval='1m',period='1d')
      return round(float(data['Close'].iloc[-1]),2)
    except:
      indexLtp="Unable to get LTP"
  try:
    return obj.getMarketData("LTP",{exch_seg:[token]})['data']['fetched'][0]['ltp']
    try:
      return obj.ltpData(exch_seg,symbol,token)['data']['ltp']
    except Exception as e: return "Unable to get LTP"
  except Exception as e: return "Unable to get LTP"

def get_ltp_token(tokenlist):
  try:
    ltp_df=pd.DataFrame(obj.getMarketData(mode="LTP",exchangeTokens={"BSE": ['99919000'],"NSE": ["99926000","99926009"],
                                                                     "NFO": list(tokenlist),"BFO": list(tokenlist)})['data']['fetched'])
    return ltp_df
  except Exception as e:
    ltp_df=pd.DataFrame(columns = ['exchange','tradingSymbol','symbolToken','ltp'])
    return ltp_df

def get_near_options(symbol,index_ltp,symbol_expiry):
  ltp=index_ltp*100
  a=token_df[(token_df['name'] == symbol) & (token_df['expiry']==symbol_expiry) & (token_df['strike']<=ltp) &
            (token_df['symbol'].str.endswith('PE'))].sort_values(by=['strike'], ascending=False).head(2)
  a.reset_index(inplace=True)
  b=token_df[(token_df['name'] == symbol) & (token_df['expiry']==symbol_expiry) & (token_df['strike']>=ltp) &
            (token_df['symbol'].str.endswith('CE'))].sort_values(by=['strike'], ascending=True).head(2)
  b.reset_index(inplace=True)
  df=pd.concat([a,b])
  df.sort_index(inplace=True)
  return df

def get_all_near_option(nf_ltp,bnf_ltp,sensex_ltp):
  nf_df=get_near_options("NIFTY",nf_ltp,nf_expiry_day)
  bnf_df=get_near_options("BANKNIFTY",bnf_ltp,bnf_expiry_day)
  sensex_df=get_near_options("SENSEX",sensex_ltp,sensex_expiry_day)
  df = pd.DataFrame()
  df = pd.concat([nf_df,bnf_df,sensex_df])
  return df

def trade_near_options(time_frame):
  df = pd.DataFrame()
  time_frame=str(time_frame)+"m"
  for symbol in ['NIFTY','BANKNIFTY','SENSEX']:
    if (symbol=="NIFTY" and nf_5m_trade=="-") or (symbol=="BANKNIFTY" and bnf_5m_trade=="-") or (symbol=="SENSEX" and sensex_5m_trade=="-"):
      print(f'Near Option {symbol}')
      index_ltp=get_ltp_price(symbol)
      if symbol=="NIFTY":symbol_expiry=nf_expiry_day
      elif symbol=="BANKNIFTY":symbol_expiry=bnf_expiry_day
      elif symbol=="SENSEX":symbol_expiry=sensex_expiry_day
      else:symbol_expiry="-"
      option_list=get_near_options(symbol,index_ltp,symbol_expiry)
      for i in range(0,len(option_list)):
        symbol_name=option_list['symbol'].iloc[i]
        token_symbol=option_list['token'].iloc[i]
        exch_seg=option_list['exch_seg'].iloc[i]
        opt_data=get_historical_data(symbol=symbol_name,interval=time_frame,token=token_symbol,exch_seg=exch_seg)
        df = pd.concat([df,opt_data.tail(1)])
        if (opt_data['ST_7_3 Trade'].values[-1]=="Buy" or opt_data['ST_10_2 Trade'].values[-1]=="Buy"):
          strike_symbol=option_list.iloc[i]
          if opt_data['ST_7_3 Trade'].values[-1]=="Buy": sl= int(opt_data['Supertrend'].values[-1])
          elif opt_data['ST_10_2 Trade'].values[-1]=="Buy": sl= int(opt_data['Supertrend_10_2'].values[-1])
          else: sl=int(opt_data['Close'].values[-1]*0.7)
          target=int(int(opt_data['Close'].values[-1])+((int(opt_data['Close'].values[-1])-sl)*2))
          indicator ="OPT "+str(time_frame)+":"
          if opt_data['ST_7_3 Trade'].values[-1]=="Buy": indicator=indicator + " ST_7_3"
          elif opt_data['ST_10_2 Trade'].values[-1]=="Buy": indicator=indicator +" ST_10_2"
          strategy=indicator + " (" +str(sl)+":"+str(target)+')'
          buy_option(symbol=strike_symbol,indicator_strategy=strategy,interval="5m",index_sl="-")
          break
        print(df[['Datetime','Symbol','Close','Trade','Trade End','Supertrend','Supertrend_10_2','Supertrend_10_1','RSI','Indicator']].to_string(index=False))

def getTokenInfo(symbol, exch_seg ='NFO',instrumenttype='OPTIDX',strike_price = 0,pe_ce = 'CE',expiry_day = None):
  if exch_seg == 'NSE' or exch_seg == 'BSE': return token_df[(token_df['exch_seg'] == exch_seg) & (token_df['name'] == symbol)]
  elif (instrumenttype == 'FUTSTK') or (instrumenttype == 'FUTIDX'):
    return token_df[(token_df['instrumenttype'] == instrumenttype) & (token_df['name'] == symbol)].sort_values(by=['expiry'], ascending=True)
  elif (instrumenttype == 'OPTSTK' or instrumenttype == 'OPTIDX'):
    return (token_df[(token_df['name'] == symbol) & (token_df['expiry']==expiry_day) &
            (token_df['instrumenttype'] == instrumenttype) & (token_df['strike'] == strike_price*100) &
            (token_df['symbol'].str.endswith(pe_ce))].sort_values(by=['expiry']))

# get current bank nifty data
def get_ce_pe_data(symbol,indexLtp="-"):
  indexLtp=float(indexLtp) if indexLtp!="-" else get_ltp_price(symbol)
  # ATM
  if symbol=='BANKNIFTY' or symbol=='^NSEBANK':
    symbol='BANKNIFTY'
    ATMStrike = math.floor(indexLtp/100)*100
    expiry_day=bnf_expiry_day
    exch_seg="NFO"
  elif symbol=='NIFTY' or symbol=='^NSEI':
    symbol='NIFTY'
    val2 = math.fmod(indexLtp, 50)
    val3 = 50 if val2 >= 25 else 0
    ATMStrike = indexLtp - val2 + val3
    expiry_day=nf_expiry_day
    exch_seg="NFO"
  elif symbol=="SENSEX" or symbol=="^BSESN":
    symbol='SENSEX'
    ATMStrike = math.floor(indexLtp/100)*100
    expiry_day=sensex_expiry_day
    exch_seg="BFO"
  else:
    symbol="Cant Find"
    ATMStrike=0
    expiry_day="-"
    exch_seg="-"
  #CE,#PE
  ce_strike_symbol = getTokenInfo(symbol,exch_seg,'OPTIDX',ATMStrike,'CE',expiry_day).iloc[0]
  pe_strike_symbol = getTokenInfo(symbol,exch_seg,'OPTIDX',ATMStrike,'PE',expiry_day).iloc[0]
  print(f"{symbol} LTP:{indexLtp} {ce_strike_symbol['symbol']} & {pe_strike_symbol['symbol']}")
  #print(symbol+' LTP:',indexLtp,ce_strike_symbol['symbol'],'&',pe_strike_symbol['symbol'])
  return indexLtp, ce_strike_symbol,pe_strike_symbol

#Yfna Historical Data
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
      print("Yahoo Data Not Found "+symbol)
      return "No data found, symbol may be delisted"
    return df
  except:
    print("Yahoo Data Not Found " +symbol)
    return "No data found, symbol may be delisted"

#Angel Historical Data
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
    return df
  except Exception as e:
    print(f"Angel Data Not Found {token} error {e}")
    return "Angel Data Not Found, symbol may be delisted"

#Historical Data
def get_historical_data(symbol="-",interval='5m',token="-",exch_seg="-",candle_type="NORMAL"):
  try:
    symbol_i="-"
    if (symbol=="^NSEI" or symbol=="NIFTY") : symbol_i,token,exch_seg="^NSEI",99926000,"NSE"
    elif (symbol=="^NSEBANK" or symbol=="BANKNIFTY") : symbol_i,token,exch_seg="^NSEBANK",99926009,"NSE"
    elif (symbol=="^BSESN" or symbol=="SENSEX") : symbol_i,token,exch_seg="^BSESN",99919000,"BSE"
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
    if (symbol_i[0]=="^"):
      df=yfna_data(symbol_i,yf_interval,str(period)+"d")
    if isinstance(df, str):
      to_date= datetime.datetime.now(tz=gettz('Asia/Kolkata'))
      from_date = to_date - datetime.timedelta(days=period)
      fromdate = from_date.strftime("%Y-%m-%d %H:%M")
      todate = to_date.strftime("%Y-%m-%d %H:%M")
      df=angel_data(token,agl_interval,exch_seg,fromdate,todate)
    if odd_candle ==True:
      df=df.groupby(pd.Grouper(freq=odd_interval+'in')).agg({"Date":"first","Datetime":"first","Open": "first", "High": "max",
                                                        "Low": "min", "Close": "last","Volume": "sum"})
      df=df[(df['Open']>0)]
    if isinstance(df, str):
      df=pd.DataFrame(columns=['Date', 'Datetime', 'Open', 'High', 'Low', 'Close', 'Volume', 'VWAP','Time Frame', 'Symbol', 'RSI', 'UBB',
          'MBB', 'LBB', 'MACD','MACD signal', 'Macdhist', 'Supertrend', 'Supertrend_10_2','Supertrend_10_1', 'Supertrend_10_4',
          'Supertrend_10_8', 'PSAR', 'ADX','MINUS_DI', 'PLUS_DI', 'MA_200', 'MA_50', 'EMA_12', 'EMA_26', 'EMA_13','EMA_5', 'EMA_7',
          'MA_1', 'MA_2', 'MA_3', 'MA_4', 'MA_5', 'MA_6','MA_7', 'MA_8', 'MA_9', 'MA_10', 'MA_21', 'WMA_20', 'Atr', 'HMA_21',
          'HMA_55', 'RSI_MA', 'EMA_High', 'EMA_Low', 'St Trade', 'MACD Trade','PSAR Trade', 'DI Trade', 'MA Trade', 'EMA Trade',
          'BB Trade', 'Trade','Trade End', 'Rainbow MA', 'Rainbow Trade', 'MA 21 Trade','ST_10_2 Trade', 'Two Candle Theory',
          'HMA Trade', 'VWAP Trade','EMA_5_7 Trade', 'ST_10_4_8 Trade', 'EMA_High_Low Trade','RSI MA Trade', 'RSI_60 Trade', 'ST_10_1 Trade', 'Indicator'])
      return df
    now=datetime.datetime.now(tz=gettz('Asia/Kolkata')).replace(microsecond=0, tzinfo=None)
    last_candle=now.replace(second=0, microsecond=0)- datetime.timedelta(minutes=delta_time)
    df = df[(df.index <= last_candle)]
    df['Time Frame']=odd_interval
    df.index.names = ['']
    df['VWAP']=pdta.vwap(high=df['High'],low=df['Low'],close=df['Close'],volume=df['Volume'])
    df=df[['Date','Datetime','Open','High','Low','Close','Volume','VWAP','Time Frame']]
    df['Symbol']=symbol
    df=calculate_indicator(df)
    df=df.round(2)
    return df
  except Exception as e:
    print("get_historical_data",e)

#update Buy and Sell trade info
def get_trade_info(df):
  for i in ['ST_7_3 Trade','MACD Trade','PSAR Trade','DI Trade','MA Trade','EMA Trade','BB Trade','Trade','Trade End',
            'Rainbow MA','Rainbow Trade','MA 21 Trade','ST_10_2 Trade','Two Candle Theory','HMA Trade','VWAP Trade',
            'EMA_5_7 Trade','ST_10_4_8 Trade','EMA_High_Low Trade','RSI MA Trade','RSI_60 Trade','ST_10_1 Trade']:df[i]='-'
  if df['Time Frame'][0]=="3m" or df['Time Frame'][0]=="THREE MINUTE" or df['Time Frame'][0]=="3min": df['Time Frame']="3m";time_frame="3m"
  elif df['Time Frame'][0]=="5m" or df['Time Frame'][0]=="FIVE MINUTE" or df['Time Frame'][0]=="5min": df['Time Frame']="5m";time_frame="5m"
  elif df['Time Frame'][0]=="15m" or df['Time Frame'][0]=="FIFTEEN MINUTE" or df['Time Frame'][0]=="15min": df['Time Frame']="15m";time_frame="15m"
  elif df['Time Frame'][0]=="1m" or df['Time Frame'][0]=="ONE MINUTE" or df['Time Frame'][0]=="1min": df['Time Frame']="1m";time_frame="1m"
  time_frame=df['Time Frame'][0]
  Symbol=df['Symbol'][0]
  for i in range(0,len(df)):
    try:
      #df['Date'][i]=df['Datetime'][i].strftime('%Y.%m.%d')
      if df['Close'][i-1]<=df['Supertrend'][i-1] and df['Close'][i]> df['Supertrend'][i]: df['ST_7_3 Trade'][i]="Buy"
      elif df['Close'][i-1]>=df['Supertrend'][i-1] and df['Close'][i]< df['Supertrend'][i]: df['ST_7_3 Trade'][i]="Sell"

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

      if df['Close'][i-1]< df['Supertrend_10_1'][i-1] and df['Close'][i]> df['Supertrend_10_1'][i]: df['ST_10_1 Trade'][i]="Buy"
      elif df['Close'][i-1]> df['Supertrend_10_1'][i-1] and df['Close'][i]< df['Supertrend_10_1'][i]: df['ST_10_1 Trade'][i]="Sell"

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

      RSI=df['RSI'][i];          ST=df['ST_7_3 Trade'][i]
      MACD=df['MACD Trade'][i];  EMA=df['EMA Trade'][i]
      MA=df['MA 21 Trade'][i];   ST_10_2=df['ST_10_2 Trade'][i]
      RSI_60=df['RSI_60 Trade'][i]; ST_10_1=df['ST_10_1 Trade'][i]
      Two_Candle_Theory=df['Two Candle Theory'][i]; HMA_Trade=df['HMA Trade'][i]
      EMA_5_7_Trade=df['EMA_5_7 Trade'][i];EMA_High_Low=df['EMA_High_Low Trade'][i]

      if time_frame=="5m" or time_frame=="FIVE_MINUTE" or time_frame=="5min":
        if ST_10_1=="Buy" or ST_10_2=="Buy" or ST=="Buy":
          df['Trade'][i]="Buy"
        if ST_10_1=="Sell" or ST_10_2=="Sell" or ST=="Sell":
          df['Trade'][i]="Sell"
    except Exception as e:
      pass
  df['ADX']=df['ADX'].round(decimals = 2)
  df['ADX']= df['ADX'].astype(str)
  df['Atr']=df['Atr'].round(decimals = 2)
  df['Atr']= df['Atr'].astype(str)
  df['RSI']=df['RSI'].round(decimals = 2)
  df['RSI']= df['RSI'].astype(str)
  if Symbol=="^NSEBANK" or Symbol=="BANKNIFTY" or Symbol=="^NSEI" or Symbol=="NIFTY" or Symbol=="SENSEX" or Symbol=="^BSESN":
    symbol_type="IDX"
  else: symbol_type= "OPT"
  df['Indicator']=(symbol_type+" "+df['Trade']+" "+df['Time Frame']+":"+" ST_7_3:"+df['ST_7_3 Trade']+
                   " ST_10_2:"+df['ST_10_2 Trade']+ " ST_10_1:"+df['ST_10_1 Trade'])
  df['RSI']= df['RSI'].astype(float)
  df['Indicator'] = df['Indicator'].str.replace(' ST_7_3:-','')
  df['Indicator'] = df['Indicator'].str.replace(' EMA:-','')
  df['Indicator'] = df['Indicator'].str.replace(' MA:-','')
  df['Indicator'] = df['Indicator'].str.replace(' MACD:-','')
  df['Indicator'] = df['Indicator'].str.replace(' ST_10_2:-','')
  df['Indicator'] = df['Indicator'].str.replace(' ST_10_1:-','')
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

#Calculate Indicator
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
    df['Supertrend_10_1']=pdta.supertrend(high=df['High'],low=df['Low'],close=df['Close'],length=10,multiplier=1)['SUPERT_10_1.0']
    df['Supertrend_10_4']=pdta.supertrend(high=df['High'],low=df['Low'],close=df['Close'],length=10,multiplier=4)['SUPERT_10_4.0']
    df['Supertrend_10_8']=pdta.supertrend(high=df['High'],low=df['Low'],close=df['Close'],length=10,multiplier=8)['SUPERT_10_8.0']
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
    df['EMA_High']=pdta.ema(df['High'],length=21)
    df['EMA_Low']=pdta.ema(df['Low'],length=21)
    #df = df.round(decimals=2)
    df=get_trade_info(df)
    return df
  except Exception as e:
    print("Error in calculate Indicator",e)
    return df

def buy_option(symbol,indicator_strategy="Manual Buy",interval="5m",index_sl="-"):
  try:
    option_token=symbol['token']
    option_symbol=symbol['symbol']
    exch_seg=symbol['exch_seg']
    lotsize=int(symbol['lotsize'])*lots_to_trade
    try:
      if "(" in indicator_strategy and ")" in indicator_strategy:
        stop_loss=(indicator_strategy.split('('))[1].split(':')[0]
        target_price=(indicator_strategy.split(stop_loss+':'))[1].split(')')[0]
        stop_loss=int(float(stop_loss))
        target_price=int(float(target_price))
      else:
        old_data=get_historical_data(symbol=option_symbol,interval='5m',token=option_token,exch_seg=exch_seg,candle_type="NORMAL")
        ltp_price=float(old_data['Close'].iloc[-1])
        stop_loss=ltp_price*0.7
        if float(old_data['Supertrend'].iloc[-1])<ltp_price: stop_loss=float(old_data['Supertrend'].iloc[-1])
        elif float(old_data['Supertrend_10_2'].iloc[-1])<ltp_price: stop_loss=float(old_data['Supertrend_10_2'].iloc[-1])
        target_price=int(float(ltp_price)+(float(ltp_price)-float(stop_loss))*2)
        indicator_strategy=indicator_strategy+ " (" +str(stop_loss)+":"+str(target_price)+')'
    except Exception as e: pass
    orderId,ltp_price=place_order(token=option_token,symbol=option_symbol,qty=lotsize,buy_sell='BUY',ordertype='MARKET',price=0,
                          variety='NORMAL',exch_seg=exch_seg,producttype='CARRYFORWARD',ordertag=indicator_strategy)
    if str(orderId)=='Order placement failed': return
    orderbook=obj.orderBook()['data']
    orderbook=pd.DataFrame(orderbook)
    orders= orderbook[(orderbook['orderid'] == orderId)]
    orders_status=orders.iloc[0]['orderstatus']; trade_price=orders.iloc[0]['averageprice']
    if orders_status != 'complete': trade_price='-'
    tm=datetime.datetime.now(tz=gettz('Asia/Kolkata')).replace(microsecond=0, tzinfo=None)
    order_price=ltp_price if trade_price=='-' else trade_price
    if trade_price!='-':
      if target_order_type=="Target":
        place_order(token=option_token,symbol=option_symbol,qty=lotsize,buy_sell='SELL',ordertype='LIMIT',price=target_price,
                    variety='NORMAL',exch_seg=exch_seg,producttype='CARRYFORWARD',ordertag=str(orderId)+" Target order Placed")
      else:
        place_order(token=option_token,symbol=option_symbol,qty=lotsize,buy_sell='SELL',ordertype='STOPLOSS_LIMIT',price=stop_loss,
                    variety='STOPLOSS',exch_seg=exch_seg,producttype='CARRYFORWARD',triggerprice=stop_loss,squareoff=stop_loss,
                    stoploss=stop_loss, ordertag=str(orderId)+" Stop Loss order Placed")
    buy_msg=(f'Buy: {option_symbol}\nPrice: {trade_price} LTP: {ltp_price}\n{indicator_strategy}\nTarget: {target_price} Stop Loss: {stop_loss}')
    telegram_bot_sendtext(buy_msg)
  except Exception as e:
    print('Error in buy_option:',e)

#Exit Position
def exit_position(symboltoken,tradingsymbol,exch_seg,qty,ltp_price,sl,ordertag='',producttype='CARRYFORWARD'):
  #position,open_position=get_open_position()
  try:
    if isinstance(open_position,str)==True or len(open_position)==0:
      orderId,ltp_price=place_order(token=symboltoken,symbol=tradingsymbol,qty=qty,buy_sell='SELL',ordertype='MARKET',price=sl,
                          variety='NORMAL',exch_seg=exch_seg,producttype=producttype,ordertag=ordertag)
    else:
      position=open_position[(open_position.tradingsymbol==tradingsymbol) & (open_position.netqty!='0')]
      if len(position)!=0:
        cancel_all_order(tradingsymbol)
        orderId,ltp_price=place_order(token=symboltoken,symbol=tradingsymbol,qty=qty,buy_sell='SELL',ordertype='STOPLOSS_LIMIT',price=sl,
                        variety='STOPLOSS',exch_seg=exch_seg,producttype=producttype,triggerprice=sl,squareoff=sl, stoploss=sl,ordertag=ordertag)
        print ('Exit Alert In Option: ' , tradingsymbol,'LTP:',ltp_price,'SL:',sl)
      else: print('No Open Position : ',tradingsymbol)
  except Exception as e:
    print('Error in exit_position:',e)

# Close Options Positions on alert in index
def close_options_position():
  position,open_position=get_open_position()
  if isinstance(open_position,str)==True or len(open_position)==0: print("No Position")
  else:
    orderbook=get_order_book()
    for index_symbol in ['NIFTY','BANKNIFTY','SENSEX']:
      trade_end="-"
      if index_symbol=="NIFTY": trade_end=nf_5m_trade_end
      elif index_symbol=="BANKNIFTY": trade_end=bnf_5m_trade_end
      elif index_symbol=="SENSEX": trade_end=sensex_5m_trade_end
      for i in open_position.index:
        try:
          tradingsymbol=open_position.loc[i]['tradingsymbol']
          if ((trade_end=='Sell' and tradingsymbol[-2:]=='CE' and tradingsymbol.startswith(index_symbol)) or
            (trade_end=='Buy' and tradingsymbol[-2:]=='PE' and tradingsymbol.startswith(index_symbol))) :
            symboltoken=open_position.loc[i]['symboltoken']
            qty=open_position['netqty'][i]
            producttype=open_position['producttype'][i]
            exch_seg=open_position['exchange'][i]
            ltp_price=get_ltp_price(symbol=tradingsymbol,token=symboltoken,exch_seg=exch_seg)
            sl=float(ltp_price)
            exit_position(symboltoken,tradingsymbol,exch_seg,qty,ltp_price,sl,ordertag='Indicator Exit LTP: '+str(ltp_price),producttype='CARRYFORWARD')
          time.sleep(1)
        except Exception as e:
          print('Error in Close index trade:',e)

def index_trade(interval):
  global bnf_5m_trade,nf_5m_trade,sensex_5m_trade
  global nf_5m_trade_end,bnf_5m_trade_end,sensex_5m_trade_end
  df = pd.DataFrame()
  for symbol in ['NIFTY',"BANKNIFTY","SENSEX"]:
    fut_data=get_historical_data(symbol=symbol,interval=interval,token="-",exch_seg="-",candle_type="NORMAL")
    trade=str(fut_data['Trade'].values[-1])
    if trade!="-":
      indicator_strategy=fut_data['Indicator'].values[-1]
      indexLtp=fut_data['Close'].values[-1]
      interval_yf=fut_data['Time Frame'].values[-1]
      indexLtp, ce_strike_symbol,pe_strike_symbol=get_ce_pe_data(symbol,indexLtp=indexLtp)
      if trade=="Buy" : buy_option(ce_strike_symbol,indicator_strategy,interval)
      elif trade=="Sell" : buy_option(pe_strike_symbol,indicator_strategy,interval)
    trade_end=str(fut_data['Trade End'].values[-1])
    if interval=="5m":
      if symbol=="NIFTY":
        nf_5m_trade=trade
        nf_5m_trade_end=trade_end
      elif symbol=="BANKNIFTY":
        bnf_5m_trade=trade
        bnf_5m_trade_end=trade_end
      elif symbol=="SENSEX":
        sensex_5m_trade=trade
        sensex_5m_trade_end=trade_end
    df = pd.concat([df,fut_data.tail(1)])
  print(df[['Datetime','Symbol','Close','Trade','Trade End','Supertrend','Supertrend_10_2','Supertrend_10_1','RSI','Indicator']].to_string(index=False))

def print_ltp():
  try:
    data=pd.DataFrame(obj.getMarketData(mode="OHLC",exchangeTokens={"NSE": ["99926000","99926009"],"BSE": ['99919000'], "NFO": []})['data']['fetched'])
    data['change']=data['ltp']-data['close']
    print_sting=datetime.datetime.now(tz=gettz('Asia/Kolkata')).replace(microsecond=0, tzinfo=None).time()
    for i in range(0,len(data)):print_sting=f"{print_sting} {data.iloc[i]['tradingSymbol']} {int(data.iloc[i]['ltp'])}({int(data.iloc[i]['change'])})"
    print_sting=print_sting.replace("Nifty 50","Nifty")
    print_sting=print_sting.replace("Nifty Bank","BankNifty")
    index_ltp_string.text(f"Index Ltp: {print_sting}")
  except Exception as e:
    pass

def update_target_sl(buy_df):
  pattern = r'\((-?\d+):(-?\d+)\)'
  for i in range(0,len(buy_df)):
    try:
      match = re.search(pattern, buy_df['ordertag'].iloc[i])
      if match:
        buy_df['Stop Loss'].iloc[i]=int(match.group(1))
        buy_df['Target'].iloc[i]=int(match.group(2))
      else:
        buy_df['Stop Loss'].iloc[i]=int(float(buy_df['price'].iloc[i]*0.7))
        buy_df['Target'].iloc[i]=int(float(buy_df['price'].iloc[i]*1.5))
    except Exception as e:
      print('Error found in ',e)
  return buy_df

def update_ltp_buy_df(buy_df):
  tokenlist=buy_df['symboltoken'].values.tolist()
  ltp_df=get_ltp_token(numpy.unique(tokenlist))
  for i in range(0,len(buy_df)):
    try:
      symboltoken=int(buy_df['symboltoken'].iloc[i])
      n_ltp_df=ltp_df[ltp_df['symbolToken']==symboltoken]
      if len(n_ltp_df)!=0:
        buy_df['ltp'].iloc[i]=n_ltp_df['ltp'].iloc[0]
      else:
        buy_df['ltp'].iloc[i]=get_ltp_price(symbol=buy_df['tradingsymbol'].iloc[i],token=buy_df['symboltoken'].iloc[i],exch_seg=buy_df['exchange'].iloc[i])
    except Exception as e:
      pass
  return buy_df

def ganesh_sl_trail(todays_trade_log):
  for i in range(0,len(todays_trade_log)):
    if todays_trade_log['Status'].iloc[i]=="Pending":
      try:
        ordertag=todays_trade_log['ordertag'].iloc[i]
        tradingsymbol=todays_trade_log['tradingsymbol'].iloc[i]
        symboltoken=todays_trade_log['symboltoken'].iloc[i]
        exch_seg=todays_trade_log['exchange'].iloc[i]
        price=float(todays_trade_log['price'].iloc[i])
        old_data=get_historical_data(symbol=tradingsymbol,interval="5m",token=symboltoken,exch_seg=exch_seg,candle_type="NORMAL")
        st_10_2=float(old_data['Supertrend_10_2'].iloc[-1])
        st_7_3=float(old_data['Supertrend'].iloc[-1])
        ema_low=float(old_data['EMA_Low'].iloc[-1])
        close_price=float(old_data['Close'].iloc[-1])
        sl=todays_trade_log['Stop Loss'].iloc[i]
        indicator=old_data["Indicator"].iloc[-1]
        qty=todays_trade_log['quantity'].iloc[i]
        ltp_price=todays_trade_log['ltp'].iloc[i]
        print(f"{tradingsymbol} LTP:{ltp_price} {ordertag} ST_7_3: {old_data['Supertrend'].iloc[-1]} ST_10_2: {old_data['Supertrend_10_2'].iloc[-1]}")
        if old_data['ST_7_3 Trade'].iloc[-1]=="Sell" or old_data['ST_10_2 Trade'].iloc[-1]=="Sell":
          ltp_price=round(float(get_ltp_price(symbol=tradingsymbol,token=symboltoken,exch_seg=exch_seg)),2)
          trade_info=(tradingsymbol+ '\nBuy: ' + str(todays_trade_log['price'].iloc[i])+
                      '\nTarget: ' +str(int(todays_trade_log['Target'].iloc[i]))+ ' Stop Loss: ' +str(int(todays_trade_log['Stop Loss'].iloc[i]))+
                      ' LTP:' +str(todays_trade_log['ltp'].iloc[i]) + '\nBuy Time: '+str(todays_trade_log['updatetime'].iloc[i]) +
                      '\n' + str(todays_trade_log['ordertag'].iloc[i])+'\nProfit:'+str(int(todays_trade_log['Profit'].iloc[i])))
          ordertag=indicator + ' Exit LTP '+ str(todays_trade_log['ltp'].iloc[i])+ ' orderid: ' +str(todays_trade_log['orderid'].iloc[i])
          exit_position(symboltoken,tradingsymbol,exch_seg,qty,ltp_price,ltp_price,ordertag=ordertag,producttype='CARRYFORWARD')
          telegram_bot_sendtext(indicator +" Exit LTP: "+str(float(ltp_price))+ '\n' + trade_info)
          time.sleep(1)
      except Exception as e:
        print(f'error in ganesh_sl_trail {e}')
  return todays_trade_log

def get_buy_df(orderbook):
  orderbook=orderbook[(orderbook['instrumenttype']=="OPTIDX")]
  buy_df=orderbook[(orderbook['transactiontype']=="BUY") & ((orderbook['status']=="complete")| (orderbook['status']=="rejected"))]
  sell_df=orderbook[(orderbook['transactiontype']=="SELL") & ((orderbook['status']=="complete")| (orderbook['status']=="rejected")) ]
  sell_df['Remark']='-'
  buy_df['Exit Time']=datetime.datetime.now(tz=gettz('Asia/Kolkata')).replace(hour=15, minute=30, second=0, microsecond=0,tzinfo=None)
  buy_df['Sell Indicator']='-';buy_df['Status']='Pending'
  for i in ['Sell','Sell Indicator','Profit','Index SL','Time Frame','Target','Stop Loss','Profit %','High','Low']:buy_df[i]='-'
  for i in range(0,len(buy_df)):
    symbol=buy_df['tradingsymbol'].iloc[i];  updatetime=buy_df['updatetime'].iloc[i];  orderid=buy_df['orderid'].iloc[i]
    if buy_df['Status'].iloc[i]=='Pending':
      for k in range(0,len(sell_df)):
        if (sell_df['tradingsymbol'].iloc[k]==symbol and sell_df['updatetime'].iloc[k] >= updatetime and sell_df['Remark'].iloc[k] =='-' and
            buy_df['status'].iloc[i]==sell_df['status'].iloc[k] and str(orderid) in sell_df['ordertag'].iloc[k]):
          buy_df['Sell'].iloc[i]=sell_df['price'].iloc[k]
          buy_df['Exit Time'].iloc[i]=sell_df['updatetime'].iloc[k]
          buy_df['Sell Indicator'].iloc[i]=sell_df['ordertag'].iloc[k]
          buy_df['Status'].iloc[i]='Closed'; sell_df['Remark'].iloc[k]='Taken'
          break
  for i in range(0,len(buy_df)):
    symbol=buy_df['tradingsymbol'].iloc[i]
    updatetime=buy_df['updatetime'].iloc[i]
    orderid=buy_df['orderid'].iloc[i]
    if buy_df['Status'].iloc[i]=='Pending':
      for j in range(0,len(sell_df)):
        if (sell_df['tradingsymbol'].iloc[j]==symbol and sell_df['updatetime'].iloc[j] >= updatetime and sell_df['Remark'].iloc[j] =='-' and
            buy_df['status'].iloc[i]==sell_df['status'].iloc[j]):
          buy_df['Sell'].iloc[i]=sell_df['price'].iloc[j]
          buy_df['Exit Time'].iloc[i]=sell_df['updatetime'].iloc[j]
          buy_df['Sell Indicator'].iloc[i]=sell_df['ordertag'].iloc[j]
          buy_df['Status'].iloc[i]='Closed'; sell_df['Remark'].iloc[j]='Taken'
          break
  buy_df['updatetime'] = pd.to_datetime(buy_df['updatetime']).dt.time
  buy_df['Exit Time'] = pd.to_datetime(buy_df['Exit Time']).dt.time
  buy_df=buy_df[['orderid','updatetime','symboltoken','tradingsymbol','exchange','quantity','price','Stop Loss','Target','ltp','Status','Sell','Exit Time',
                 'Profit','Profit %','ordertag','Sell Indicator']]
  return buy_df

def get_todays_trade():
  try:
    global todays_trade_log,n_todays_trade_log,dataframe
    orderbook,pending_orders=get_order_book()
    buy_df=get_buy_df(orderbook)
    buy_df=update_target_sl(buy_df)
    for i in range(0,len(buy_df)):
      try:
        if buy_df['Status'].iloc[i]!='Closed':
          #buy_df['ltp'].iloc[i]=get_ltp_price(symbol=buy_df['tradingsymbol'].iloc[i],token=buy_df['symboltoken'].iloc[i],exch_seg=buy_df['exchange'].iloc[i])
          buy_df['Profit'].iloc[i]=float((buy_df['ltp'].iloc[i]-buy_df['price'].iloc[i]))*float(buy_df['quantity'].iloc[i])
          buy_df['Profit %'].iloc[i]=((buy_df['ltp'].iloc[i]/buy_df['price'].iloc[i])-1)*100
        else:
          buy_df['Profit'].iloc[i]=float((buy_df['Sell'].iloc[i]-buy_df['price'].iloc[i]))*float(buy_df['quantity'].iloc[i])
          buy_df['Profit %'].iloc[i]=((buy_df['Sell'].iloc[i]/buy_df['price'].iloc[i])-1)*100
      except Exception as e: pass
    buy_df['Profit %']=buy_df['Profit %'].astype(float).round(2)
    todays_trade_log=buy_df.sort_values(by = ['Status', 'updatetime'], ascending = [False, True], na_position = 'first')
    #todays_trade_log=ganesh_sl_trail(todays_trade_log)
    n_todays_trade_log=todays_trade_log[(todays_trade_log['Status']=='Pending')]
    close_todays_trade(todays_trade_log)
    pnl=int(todays_trade_log['Profit'].sum())
    algo_trade_updated.text(f"Algo Trade :{datetime.datetime.now(tz=gettz('Asia/Kolkata')).time().replace(microsecond=0)} Profit {pnl}")
    todays_trade_log=todays_trade_log[['updatetime','tradingsymbol','price','Stop Loss','Target','ltp','Status','Sell','Profit','Profit %','ordertag','Sell Indicator']]
    algo_datatable.dataframe(todays_trade_log,hide_index=True)
    return todays_trade_log
  except Exception as e:
    print("Error get_todays_trade",e)
    todays_trade_log = pd.DataFrame(columns = ['updatetime','tradingsymbol','price','Stop Loss','Target','ltp','Status','Sell','Profit',
                                               'Profit %','ordertag','Sell Indicator'])
    return todays_trade_log

def closing_trade():
  pass

def close_todays_trade_signal(todays_trade_log,index_symbol,trade_end,indicator="Indicator"):
  for i in range(0,len(todays_trade_log)):
    try:
      if todays_trade_log['Status'].iloc[i]!='Closed':
        tradingsymbol=todays_trade_log['tradingsymbol'].iloc[i]
        if ((trade_end=='Sell' and tradingsymbol[-2:]=='CE' and tradingsymbol.startswith(index_symbol)) or
          (trade_end=='Buy' and tradingsymbol[-2:]=='PE' and tradingsymbol.startswith(index_symbol))) :
          symboltoken=todays_trade_log['symboltoken'].iloc[i]
          tradingsymbol=todays_trade_log['tradingsymbol'].iloc[i]
          exch_seg=todays_trade_log['exchange'].iloc[i]
          qty=todays_trade_log['quantity'].iloc[i]
          ltp_price=todays_trade_log['ltp'].iloc[i]
          sl=todays_trade_log['ltp'].iloc[i]
          trade_info=(tradingsymbol+ '\nBuy: ' + str(todays_trade_log['price'].iloc[i])+
                      '\nTarget: ' +str(int(todays_trade_log['Target'].iloc[i]))+ ' Stop Loss: ' +str(int(todays_trade_log['Stop Loss'].iloc[i]))+
                      ' LTP:' +str(todays_trade_log['ltp'].iloc[i]) + '\nBuy Time: '+str(todays_trade_log['updatetime'].iloc[i]) +
                      '\n' + str(todays_trade_log['ordertag'].iloc[i])+'\nProfit:'+str(int(todays_trade_log['Profit'].iloc[i])))
          ordertag=indicator + ' Exit LTP '+ str(todays_trade_log['ltp'].iloc[i])+ ' orderid: ' +str(todays_trade_log['orderid'].iloc[i])
          exit_position(symboltoken,tradingsymbol,exch_seg,qty,ltp_price,sl,ordertag=ordertag,producttype='CARRYFORWARD')
          telegram_bot_sendtext(indicator +" Exit LTP: "+str(float(ltp_price))+ '\n' + trade_info)
          time.sleep(1)
    except Exception as e:
      print('Error in Close index trade:',e)

def close_todays_trade(todays_trade_log):
  for i in range(0,len(todays_trade_log)):
    try:
      if todays_trade_log['Status'].iloc[i]!='Closed':
        symboltoken=todays_trade_log['symboltoken'].iloc[i]
        tradingsymbol=todays_trade_log['tradingsymbol'].iloc[i]
        exch_seg=todays_trade_log['exchange'].iloc[i]
        qty=todays_trade_log['quantity'].iloc[i]
        ltp_price=todays_trade_log['ltp'].iloc[i]
        sl=todays_trade_log['ltp'].iloc[i]
        trade_info=(tradingsymbol+ '\nBuy: ' + str(todays_trade_log['price'].iloc[i])+
                      '\nTarget: ' +str(int(todays_trade_log['Target'].iloc[i]))+ ' Stop Loss: ' +str(int(todays_trade_log['Stop Loss'].iloc[i]))+
                      ' LTP:' +str(todays_trade_log['ltp'].iloc[i]) + '\nBuy Time: '+str(todays_trade_log['updatetime'].iloc[i]) +
                      '\n' + str(todays_trade_log['ordertag'].iloc[i])+'\nProfit:'+str(int(todays_trade_log['Profit'].iloc[i])))
        if int(todays_trade_log['ltp'].iloc[i])<int(todays_trade_log['Stop Loss'].iloc[i]):
          ordertag='Stop Loss Hit LTP '+ str(todays_trade_log['ltp'].iloc[i])+ ' orderid: ' +str(todays_trade_log['orderid'].iloc[i])
          exit_position(symboltoken,tradingsymbol,exch_seg,qty,ltp_price,sl,ordertag=ordertag,producttype='CARRYFORWARD')
          telegram_bot_sendtext("Stop Loss Hit LTP: "+str(float(ltp_price))+ '\n' + trade_info)
          time.sleep(1)
        #elif int(todays_trade_log['ltp'].iloc[i])>int(todays_trade_log['Target'].iloc[i]):
        #  ordertag='Target Hit LTP '+ str(todays_trade_log['ltp'].iloc[i])+ ' orderid: ' +str(todays_trade_log['orderid'].iloc[i])
        #  exit_position(symboltoken,tradingsymbol,exch_seg,qty,ltp_price,sl,ordertag=ordertag,producttype='CARRYFORWARD')
        #  telegram_bot_sendtext("Target Hit LTP: "+str(float(ltp_price))+ '\n' + trade_info)
        #  time.sleep(1)
    except Exception as e:
      print(f"error {e}")

def day_end_trade(todays_trade_log):
  close_todays_trade_signal(todays_trade_log,"BANKNIFTY","Buy","Day End")
  close_todays_trade_signal(todays_trade_log,"BANKNIFTY","Sell","Day End")
  close_todays_trade_signal(todays_trade_log,"NIFTY","Buy","Day End")
  close_todays_trade_signal(todays_trade_log,"NIFTY","Sell","Day End")
  close_todays_trade_signal(todays_trade_log,"SENSEX","Buy","Day End")
  close_todays_trade_signal(todays_trade_log,"SENSEX","Sell","Day End")

def sub_loop_code(now_time):
  if (now_time.minute%5==0 and five_m_timeframe=='Yes'):
    index_trade("5m")
    if near_options_trade=="Yes":trade_near_options(5)
    close_options_position()
  if (now_time.minute%15==0 and fifteen_m_timeframe=='Yes'): index_trade("15m")
  if (now_time.minute%3==0 and three_m_timeframe=='Yes'): index_trade("3m")
  if (now_time.minute%1==0 and one_m_timeframe=='Yes'): index_trade("1m")

def loop_code():
  now = datetime.datetime.now(tz=gettz('Asia/Kolkata'))
  marketopen = now.replace(hour=9, minute=20, second=0, microsecond=0)
  marketclose = now.replace(hour=20, minute=50, second=0, microsecond=0)
  day_end = now.replace(hour=20, minute=30, second=0, microsecond=0)
  while now < day_end:
    now = datetime.datetime.now(tz=gettz('Asia/Kolkata'))
    try:
      if now > marketopen and now < marketclose:
        sub_loop_code(now)
      print_ltp()
      get_open_position()
      todays_trade_log=get_todays_trade()
      if now.minute%5==0:ganesh_sl_trail(todays_trade_log)
      if now > marketclose:
        closing_trade()
        day_end_trade(todays_trade_log)
      now=datetime.datetime.now(tz=gettz('Asia/Kolkata'))
      time.sleep(60-now.second+1)
    except Exception as e:
      print(f"error {e}")
      now=datetime.datetime.now(tz=gettz('Asia/Kolkata'))
      time.sleep(60-now.second+1)

st.header(f"Welcome {st.session_state['user_name']}")
last_login=st.empty()
last_login.text(f"Login: {st.session_state['login_time']} Algo: Not Running")
index_ltp_string=st.empty()
index_ltp_string.text(f"Index Ltp:")
tab0, tab1, tab2, tab3, tab4,tab5= st.tabs(["Log","Order Book", "Position","Algo Trade", "Settings","Token List"])
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
  algo_trade_updated=st.empty()
  algo_trade_updated.text(f"Algo Trade : ")
  algo_datatable=st.empty()
with tab4:
  ind_col1,ind_col2,ind_col3,ind_col4=st.columns([5,1.5,1.5,1.5])
  indicator_list=['St Trade', 'ST_10_2 Trade','ST_10_1 Trade', 'RSI MA Trade','RSI_60 Trade','MACD Trade','PSAR Trade','DI Trade',
                  'MA Trade','EMA Trade','EMA_5_7 Trade','MA 21 Trade','HMA Trade','RSI_60 Trade','EMA_High_Low Trade','Two Candle Theory']
  with ind_col1:
    index_list=st.multiselect('Select Index',['NIFTY','BANKNIFTY','SENSEX'],['NIFTY','BANKNIFTY','SENSEX'])
    time_frame = st.multiselect('Select Time Frame',['IDX:5M', 'IDX:15M', 'OPT:5M', 'OPT:15M','IDX:1M'],['IDX:5M', 'OPT:5M'])
    five_buy_indicator = st.multiselect('Five Minute Indicator',indicator_list,['St Trade', 'ST_10_2 Trade', 'ST_10_1 Trade'])
    option_buy_indicator = st.multiselect('Option Indicator',indicator_list,['St Trade', 'ST_10_2 Trade'])
    #three_buy_indicator = st.multiselect('Three Minute Indicator',indicator_list,[])
    #one_buy_indicator = st.multiselect('One Minute Indicator',indicator_list,[])
  with ind_col2:
    target_order_type = st.selectbox('Target Order',('Target', 'Stop_Loss', 'NA'),2)
    target_type = st.selectbox('Target Type',('Points', 'Per Cent','Indicator'),2)
    if target_type=="Indicator":
        sl_point=st.number_input(label="SL",min_value=10, max_value=100, value=10, step=None)
        target_point=st.number_input(label="Target",min_value=5, max_value=100, value=100, step=None)
  with ind_col3:
    lots_to_trade=st.number_input(label="Lots To Trade",min_value=1, max_value=10, value=1, step=None)
  with ind_col4:
    st.date_input("BNF Exp",st.session_state['bnf_expiry_day'])
    st.date_input("NF Exp",st.session_state['nf_expiry_day'])
    st.date_input("FIN NF Exp",st.session_state['fnnf_expiry_day'])
    st.date_input("SENSEX Exp",st.session_state['sensex_expiry_day'])
with tab5:
  token_df=st.empty()
  token_df=st.dataframe(st.session_state['opt_list'],hide_index=True)

if algo_state:
  loop_code()
print_ltp()
get_open_position()
get_order_book()
get_todays_trade()
