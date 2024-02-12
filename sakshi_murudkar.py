import streamlit as st
st.set_page_config(page_title="Algo App",layout="wide",initial_sidebar_state="expanded",)
st.markdown("""
  <style>
    .block-container {padding-top: 0.5rem;padding-bottom: 0rem;padding-left: 2rem;padding-right: 5rem;}
  </style>
  """, unsafe_allow_html=True)

# Start Main App
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
from logzero import logger
import re
# %load_ext autotime
pd.options.mode.chained_assignment = None
warnings.filterwarnings('ignore')
NoneType = type(None)

global index_trade_indicator,index_trade_end_indicator,option_indicator,option_trade_end_indicator
global lots_to_trade,target_order_type,near_options_trade
global bnf_5m_trade,nf_5m_trade,sensex_5m_trade,nf_5m_trade_end,bnf_5m_trade_end,sensex_5m_trade_end
global five_m_timeframe
index_trade_indicator=['ST_7_3','ST_10_2','ST_10_1']
index_trade_end_indicator=['ST_7_3','ST_10_2','ST_10_1']
option_indicator=['ST_7_3','ST_10_2']
option_trade_end_indicator=['ST_7_3','ST_10_2']
lots_to_trade=1
target_order_type="Stop Loss"
near_options_trade="Yes"
bnf_5m_trade="-"
nf_5m_trade="-"
sensex_5m_trade="-"
nf_5m_trade_end="-"
bnf_5m_trade_end="-"
sensex_5m_trade_end="-"
five_m_timeframe="Yes"

#Telegram Msg
def telegram_bot_sendtext(bot_message):
  BOT_TOKEN = '5051044776:AAHh6XjxhRT94iXkR4Eofp2PPHY3Omk2KtI'
  BOT_CHAT_ID = '-1001542241163'
  BOT_CHAT_ONE_MINUTE = '-1001542241163'
  #BOT_CHAT_ONE_MINUTE='-882387563'
  import requests
  bot_message=user+':\n'+bot_message
  matches = ["Candle"]
  send_text = 'https://api.telegram.org/bot' + BOT_TOKEN + '/sendMessage?chat_id=' + BOT_CHAT_ID + \
                '&parse_mode=HTML&text=' + bot_message
  response = requests.get(send_text)

#Login Details
def get_user_pwd(user):
  global username,pwd,apikey,token
  if user=='Ganesh': username = 'G93179'; pwd = '4789'; apikey = 'CjOKjC5g'; token='U4EAZJ3L44CNJHNUZ56R22TPKI'
  elif user=='Kalyani': username = 'K205244'; pwd = '4789'; apikey = 'lzC7yJmt'; token='YDV6CJI6BEU3GWON7GZTZNU3RM'
  elif user=="Akshay": username='A325394'; pwd='1443'; apikey='OeSllszj'; token='G4OKBQKHXPS67EN2WMVP3TZ7X4'
  elif user=="Kailash": username='K80392'; pwd='5769'; apikey='A7Q0LWtF'; token='GEVK2DBIADONB3YRYKOALABXR4'
  return username,pwd,apikey,token,user

#Angel Login
username,pwd,apikey,token,user=get_user_pwd("Ganesh")

obj=SmartConnect(api_key=apikey)
if 'user_name' not in st.session_state:
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
  logger.info('Login Sucess')
  logger.info('....!!! Jay Shri Ganesh !!!....\n....!!! Jay Mahalaxmi !!!....\n....!!! Have a profitable Day !!!....')
obj=SmartConnect(api_key=st.session_state['api_key'],access_token=st.session_state['access_token'],
                 refresh_token=st.session_state['refresh_token'],feed_token=st.session_state['feed_token'],userId=st.session_state['userId'])

def get_token_df():
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
  opt_list=token_df[((token_df['name'] == 'BANKNIFTY') & (token_df['expiry'] == bnf_expiry_day) |
                   (token_df['name'] == 'NIFTY') & (token_df['expiry'] == nf_expiry_day) |
                   (token_df['name'] == 'FINNIFTY') & (token_df['expiry'] == fnnf_expiry_day) |
                   (token_df['name'] == 'SENSEX') & (token_df['expiry'] == sensex_expiry_day))]
  st.session_state['opt_list']=opt_list

if 'bnf_expiry_day' not in st.session_state:get_token_df()

#variety: NORMAL/STOPLOSS * transactiontype: BUY/SELL * ordertype: MARKET/LIMIT/STOPLOSS_LIMIT * producttype: DELIVERY/CARRYFORWARD
#Duration: DAY/IOC * exchange: BSE/NSE/NFO/MCX
#Place Order
def place_order(token,symbol,qty,buy_sell,ordertype='MARKET',price=0,variety='NORMAL',exch_seg='NFO',producttype='CARRYFORWARD',
                triggerprice=0,squareoff=0,stoploss=0,ordertag='-'):
  try:
    orderparams = {"variety": variety,"tradingsymbol": symbol,"symboltoken": token,"transactiontype": buy_sell,"exchange": exch_seg,
      "ordertype": ordertype,"producttype": producttype,"duration": "DAY","price": int(float(price)),"squareoff":int(float(squareoff)),
      "stoploss": int(float(stoploss)),"quantity": str(qty),"triggerprice":int(float(triggerprice)),"ordertag":ordertag,"trailingStopLoss":5}
    orderId=obj.placeOrder(orderparams)
    print(f'{buy_sell} Order Placed: {orderId} Symbol: {symbol} Ordertag: {ordertag} Price: {price}')
    return orderId
  except Exception as e:
    logger.error(f"error in place_order Order placement failed: {e}")
    orderId='Order placement failed'
    return orderId

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
    logger.error(f"Error cancel_all_order {e}")

#gtt rule creation
def place_gtt_order(token,symbol,exch_seg,producttype,buy_sell,price,qty):
  try:
    gttCreateParams={"tradingsymbol" : symbol,"symboltoken" : token, "exchange" : exch_seg,"producttype" : producttype,
                     "transactiontype" : buy_sell,"price" : price, "qty" : qty,"disclosedqty": qty,"triggerprice" : price,"timeperiod" : 365}
    rule_id=obj.gttCreateRule(gttCreateParams)
    print("The GTT rule id is: {}".format(rule_id))
  except Exception as e:
    logger.error(f"GTT Rule creation failed {e}")

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

def print_ltp():
  try:
    data=pd.DataFrame(obj.getMarketData(mode="OHLC",exchangeTokens={"NSE": ["99926000","99926009"],"BSE": ['99919000'], "NFO": []})['data']['fetched'])
    data['change']=data['ltp']-data['close']
    print_sting=datetime.datetime.now(tz=gettz('Asia/Kolkata')).replace(microsecond=0, tzinfo=None).time()
    for i in range(0,len(data)):print_sting=f"{print_sting} {data.iloc[i]['tradingSymbol']} {int(data.iloc[i]['ltp'])}({int(data.iloc[i]['change'])})"
    print_sting=print_sting.replace("Nifty 50","Nifty")
    print_sting=print_sting.replace("Nifty Bank","BankNifty")
    return print_sting
  except Exception as e:
    logger.error(f"Error in print_ltp {e}")
    return None


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
  pnl=int(position['realised'].sum())+float(position['unrealised'].sum())
  open_position = position[(position['netqty'] > '0') & (position['instrumenttype'] == 'OPTIDX')]
  if len(position)!=0:
    print(f'PNL: {pnl}')
    print(position[['tradingsymbol','buyqty','sellqty','netqty','totalbuyavgprice','totalsellavgprice','realised', 'unrealised', 'ltp']].to_string(index=False))
  st.session_state['position']=position
  st.session_state['open_position']=open_position
  position_table=position[['tradingsymbol','netqty','totalbuyavgprice','totalsellavgprice','realised', 'unrealised', 'ltp']]
  position_datatable.dataframe(position_table,hide_index=True)
  position_updated.text(f"Position : {datetime.datetime.now(tz=gettz('Asia/Kolkata')).time().replace(microsecond=0)}")
  return position,open_position

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
      orderbook['updatetime'] = pd.to_datetime(orderbook['updatetime']).dt.time
      orderbook=orderbook.sort_values(by = ['updatetime'], ascending = [True], na_position = 'first')
      pending_orders = orderbook[((orderbook['orderstatus'] != 'complete') & (orderbook['orderstatus'] != 'cancelled') &
                              (orderbook['orderstatus'] != 'rejected') & (orderbook['orderstatus'] != 'AMO CANCELLED'))]
      pending_orders = pending_orders[(pending_orders['instrumenttype'] == 'OPTIDX')]
      if len(pending_orders)!=0:
        print(pending_orders[['updatetime','tradingsymbol','quantity','price','orderstatus','ordertag','instrumenttype']].to_string(index=False))
    else:
      orderbook= pd.DataFrame(columns = ['variety', 'ordertype', 'producttype', 'duration', 'price','triggerprice', 'quantity', 'disclosedquantity',
          'squareoff','stoploss', 'trailingstoploss', 'tradingsymbol', 'transactiontype','exchange', 'symboltoken', 'ordertag', 'instrumenttype',
          'strikeprice','optiontype', 'expirydate', 'lotsize', 'cancelsize', 'averageprice','filledshares', 'unfilledshares', 'orderid', 'text',
          'status','orderstatus', 'updatetime', 'exchtime', 'exchorderupdatetime','fillid', 'filltime', 'parentorderid', 'uniqueorderid'])
      pending_orders=orderbook
  except Exception as e:
    orderbook= pd.DataFrame(columns = ['variety', 'ordertype', 'producttype', 'duration', 'price','triggerprice', 'quantity', 'disclosedquantity',
          'squareoff','stoploss', 'trailingstoploss', 'tradingsymbol', 'transactiontype','exchange', 'symboltoken', 'ordertag', 'instrumenttype',
          'strikeprice','optiontype', 'expirydate', 'lotsize', 'cancelsize', 'averageprice','filledshares', 'unfilledshares', 'orderid', 'text',
          'status','orderstatus', 'updatetime', 'exchtime', 'exchorderupdatetime','fillid', 'filltime', 'parentorderid', 'uniqueorderid'])
    pending_orders=orderbook
    logger.error(f"Error in get_order_book {e}")
  st.session_state['orderbook']=orderbook
  st.session_state['pendingorder']=pending_orders
  n_orderbook=orderbook[['updatetime','orderid','transactiontype','status','tradingsymbol','price','averageprice','quantity','ordertag']]
  order_datatable.dataframe(n_orderbook,hide_index=True)
  order_book_updated.text(f"Orderbook : {datetime.datetime.now(tz=gettz('Asia/Kolkata')).time().replace(microsecond=0)}")
  n_pending_orders=pending_orders[['updatetime','orderid','transactiontype','status','tradingsymbol','price','averageprice','quantity','ordertag']]
  open_order.dataframe(n_pending_orders,hide_index=True)
  open_order_updated.text(f"Pending Orderbook : {datetime.datetime.now(tz=gettz('Asia/Kolkata')).time().replace(microsecond=0)}")
  return orderbook,pending_orders

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
      logger.error(f"Yahoo Data Not Found {symbol}")
      return "No data found, symbol may be delisted"
    return df
  except:
    logger.error(f"Yahoo Data Not Found {symbol}")
    return "No data found, symbol may be delisted"

#Angel Historical Data
def angel_data(token,interval,exch_seg,fromdate,todate):
  try:
    historicParam={"exchange": exch_seg,"symboltoken": token,"interval": interval,"fromdate": fromdate, "todate": todate}
    res_json=obj.getCandleData(historicParam)
    df = pd.DataFrame(res_json['data'], columns=['timestamp','O','H','L','C','V'])
    df = df.rename(columns={'timestamp':'Datetime','O':'Open','H':'High','L':'Low','C':'Close','V':'Volume'})
    df['Datetime'] = df['Datetime'].apply(lambda x: datetime.datetime.fromisoformat(x))
    df['Datetime'] = pd.to_datetime(df['Datetime'],format = '%Y-%m-%d %H:%M:%S')
    df['Datetime']=df['Datetime'].dt.tz_localize(None)
    df = df.set_index('Datetime')
    df['Datetime']=pd.to_datetime(df.index,format = '%Y-%m-%d %H:%M:%S')
    df['Date']=df['Datetime'].dt.strftime('%m/%d/%y')
    df['Datetime'] = pd.to_datetime(df['Datetime']).dt.time
    df=df[['Date','Datetime','Open','High','Low','Close','Volume']]
    return df
  except Exception as e:
    logger.error(f"Angel Data Not Found {token} error {e}")
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
    logger.error(f"get_historical_data {e}")

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
        if ST_10_1=="Buyy" or ST_10_2=="Buy" or ST=="Buy":
          df['Trade'][i]="Buy"
          df['Trade End'][i]="Buy"
        if ST_10_1=="Selll" or ST_10_2=="Sell" or ST=="Sell":
          df['Trade'][i]="Sell"
          df['Trade End'][i]="Buy"
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
    logger.error(f"Error in calculate Indicator {e}")
    return df


def getTokenInfo(symbol, exch_seg ='NFO',instrumenttype='OPTIDX',strike_price = 0,pe_ce = 'CE',expiry_day = None):
  token_df=st.session_state['opt_list']
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
    expiry_day=st.session_state['bnf_expiry_day']
    exch_seg="NFO"
  elif symbol=='NIFTY' or symbol=='^NSEI':
    symbol='NIFTY'
    val2 = math.fmod(indexLtp, 50)
    val3 = 50 if val2 >= 25 else 0
    ATMStrike = indexLtp - val2 + val3
    expiry_day=st.session_state['nf_expiry_day']
    exch_seg="NFO"
  elif symbol=="SENSEX" or symbol=="^BSESN":
    symbol='SENSEX'
    ATMStrike = math.floor(indexLtp/100)*100
    expiry_day=st.session_state['sensex_expiry_day']
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

def buy_option(symbol,indicator_strategy="Manual Buy",interval="5m",index_sl="-"):
  try:
    option_token=symbol['token']
    option_symbol=symbol['symbol']
    exch_seg=symbol['exch_seg']
    lotsize=int(symbol['lotsize'])*lots_to_trade
    orderId=place_order(token=option_token,symbol=option_symbol,qty=lotsize,buy_sell='BUY',ordertype='MARKET',price=0,
                          variety='NORMAL',exch_seg=exch_seg,producttype='CARRYFORWARD',ordertag=indicator_strategy)
    if str(orderId)=='Order placement failed': return
    ltp_price=round(float(get_ltp_price(symbol=option_symbol,token=option_token,exch_seg=exch_seg)),2)
    stop_loss=int(float(ltp_price*0.7))
    target_price=int(float(ltp_price*1.5))
    sl_type='30%'
    try:
      if "(" in indicator_strategy and ")" in indicator_strategy:
        stop_loss=(indicator_strategy.split('('))[1].split(':')[0]
        target_price=(indicator_strategy.split(stop_loss+':'))[1].split(')')[0]
        stop_loss=int(float(stop_loss))
        target_price=int(float(target_price))
        sl_type='OPT Indicator'
      else:
        old_data=get_historical_data(symbol=option_symbol,interval='5m',token=option_token,exch_seg=exch_seg,candle_type="NORMAL")
        close_price=float(old_data['Close'].iloc[-1])
        if float(old_data['Supertrend'].iloc[-1])<close_price*0.8:
          stop_loss=int(float(old_data['Supertrend'].iloc[-1]))
          sl_type='ST'
        elif float(old_data['Supertrend_10_2'].iloc[-1])<close_price*0.8:
          stop_loss=int(float(old_data['Supertrend_10_2'].iloc[-1]))
          sl_type='ST_10_2'
        else:
          stop_loss=int(float(close_price-(float(old_data['Atr'].iloc[-1])*3)))
        indicator_strategy=indicator_strategy+ " (" +str(stop_loss)+":"+str(target_price)+')'
    except Exception as e: pass
    orderbook=obj.orderBook()['data']
    orderbook=pd.DataFrame(orderbook)
    orders= orderbook[(orderbook['orderid'] == orderId)]
    orders_status=orders.iloc[0]['orderstatus']
    trade_price=orders.iloc[0]['averageprice']
    if orders_status== 'complete':
      if target_order_type=="Target":
        place_order(token=option_token,symbol=option_symbol,qty=lotsize,buy_sell='SELL',ordertype='LIMIT',price=target_price,
                    variety='NORMAL',exch_seg=exch_seg,producttype='CARRYFORWARD',ordertag=str(orderId)+" Target order Placed")
      elif target_order_type=="Stop Loss":
        place_order(token=option_token,symbol=option_symbol,qty=lotsize,buy_sell='SELL',ordertype='STOPLOSS_LIMIT',price=stop_loss,
                    variety='STOPLOSS',exch_seg=exch_seg,producttype='CARRYFORWARD',triggerprice=stop_loss,squareoff=stop_loss,
                    stoploss=stop_loss, ordertag=str(orderId)+" Stop Loss order Placed")
    buy_msg=(f'Buy: {option_symbol}\nPrice: {trade_price} LTP: {ltp_price}\n{indicator_strategy}\nTarget: {target_price} Stop Loss: {stop_loss} SL Type:{sl_type}')
    print(buy_msg)
    telegram_bot_sendtext(buy_msg)
  except Exception as e:
    logger.error(f"Error in buy_option: {e}")

#Exit Position
def exit_position(symboltoken,tradingsymbol,exch_seg,qty,ltp_price,sl,ordertag='',producttype='CARRYFORWARD'):
  try:
    #cancel_all_order(tradingsymbol)
    #orderId=place_order(token=symboltoken,symbol=tradingsymbol,qty=qty,buy_sell='SELL',ordertype='STOPLOSS_LIMIT',price=sl,
    #                    variety='STOPLOSS',exch_seg=exch_seg,producttype=producttype,triggerprice=sl,squareoff=sl, stoploss=sl,ordertag=ordertag)
    sell_msg=f"Exit Alert In Option: {tradingsymbol} LTP:{ltp_price} SL:{sl} Ordertag {ordertag}"
    telegram_bot_sendtext(sell_msg)
  except Exception as e:
    logger.error(f"Error in exit_position: {e}")

def close_options_position(position,nf_5m_trade_end="-",bnf_5m_trade_end="-",sensex_5m_trade_end="-"):
  for i in range(0,len(position)):
    try:
      tradingsymbol=position.loc[i]['tradingsymbol']
      if ((tradingsymbol[-2:]=='CE' and tradingsymbol.startswith("NIFTY") and nf_5m_trade_end=="Sell") or
          (tradingsymbol[-2:]=='CE' and tradingsymbol.startswith("BANKNIFTY") and bnf_5m_trade_end=="Sell") or
          (tradingsymbol[-2:]=='CE' and tradingsymbol.startswith("SENSEX") and sensex_5m_trade_end=="Sell") or
          (tradingsymbol[-2:]=='PE' and tradingsymbol.startswith("NIFTY") and nf_5m_trade_end=="Buy") or
          (tradingsymbol[-2:]=='PE' and tradingsymbol.startswith("BANKNIFTY") and bnf_5m_trade_end=="Buy") or
          (tradingsymbol[-2:]=='PE' and tradingsymbol.startswith("SENSEX") and sensex_5m_trade_end=="Buy")):
          qty=position['netqty'][i]
          if int(qty)!=0:
            symboltoken=position.loc[i]['symboltoken']
            producttype=position['producttype'][i]
            exch_seg=position['exchange'][i]
            ltp_price=position['ltp'][i]
            exit_position(symboltoken,tradingsymbol,exch_seg,qty,ltp_price,ltp_price,ordertag='Indicator Exit LTP: '+str(ltp_price),producttype='CARRYFORWARD')
            time.sleep(1)
          else:
            print(f"No Open Position for : {tradingsymbol}")
    except Exception as e:
      logger.error(f"Error in Close index trade: {e}")

def get_near_options(symbol,index_ltp,symbol_expiry):
  token_df=st.session_state['opt_list']
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

def trade_near_options(time_frame):
  df = pd.DataFrame()
  for symbol in ['NIFTY','BANKNIFTY','SENSEX']:
    index_ltp=get_ltp_price(symbol)
    if symbol=="NIFTY":symbol_expiry=st.session_state['nf_expiry_day']
    elif symbol=="BANKNIFTY":symbol_expiry=st.session_state['bnf_expiry_day']
    elif symbol=="SENSEX":symbol_expiry=st.session_state['sensex_expiry_day']
    else:symbol_expiry="-"
    option_list=get_near_options(symbol,index_ltp,symbol_expiry)
    for i in range(0,len(option_list)):
      symbol_name=option_list['symbol'].iloc[i]
      token_symbol=option_list['token'].iloc[i]
      exch_seg=option_list['exch_seg'].iloc[i]
      opt_data=get_historical_data(symbol=symbol_name,interval=time_frame,token=token_symbol,exch_seg=exch_seg)
      df = pd.concat([df,opt_data.tail(1)])
      information={'Time':str(datetime.datetime.now(tz=gettz('Asia/Kolkata')).time().replace(microsecond=0)),
                'Symbol':symbol_name,
                'Datetime':str(opt_data['Datetime'].values[-1]),'Close':opt_data['Close'].values[-1],
                'Indicator':opt_data['Indicator'].values[-1],
                'Trade':opt_data['Trade'].values[-1],
                'Trade End':opt_data['Trade End'].values[-1],
                'Supertrend':opt_data['Supertrend'].values[-1],
                'Supertrend_10_2':opt_data['Supertrend_10_2'].values[-1],
                'RSI':opt_data['RSI'].values[-1]}
      st.session_state['options_trade_list'].append(information)
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


def index_trade(symbol,interval):
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
  information={'Time':str(datetime.datetime.now(tz=gettz('Asia/Kolkata')).time().replace(microsecond=0)),
                'Symbol':symbol,
                'Datetime':str(fut_data['Datetime'].values[-1]),'Close':fut_data['Close'].values[-1],
                'Indicator':fut_data['Indicator'].values[-1],
                'Trade':fut_data['Trade'].values[-1],
                'Trade End':fut_data['Trade End'].values[-1],
                'Supertrend':fut_data['Supertrend'].values[-1],
                'Supertrend_10_2':fut_data['Supertrend_10_2'].values[-1],
                'RSI':fut_data['RSI'].values[-1]}
  st.session_state['options_trade_list'].append(information)
  return fut_data.tail(1),trade,trade_end

def closing_trade():
  position,open_position=get_open_position()
  orderbook,pending_orders=get_order_book()
  nf_5m_trade_end="Buy"
  bnf_5m_trade_end="Buy"
  sensex_5m_trade_end="Buy"
  close_options_position(position,nf_5m_trade_end=nf_5m_trade_end,bnf_5m_trade_end=bnf_5m_trade_end,sensex_5m_trade_end=sensex_5m_trade_end)
  nf_5m_trade_end="Sell"
  bnf_5m_trade_end="Sell"
  sensex_5m_trade_end="Sell"
  close_options_position(position,nf_5m_trade_end=nf_5m_trade_end,bnf_5m_trade_end=bnf_5m_trade_end,sensex_5m_trade_end=sensex_5m_trade_end)

def trail_sl():
  if isinstance(open_position,str)==True or len(open_position)==0: pass
  else:
    for i in range(0,len(open_position)):
      try:
        tradingsymbol=open_position.loc[i]['tradingsymbol']
        symboltoken=open_position.loc[i]['symboltoken']
        qty=open_position['buyqty'][i]
        exch_seg=open_position['exchange'][i]
        ltp_price=float(open_position['ltp'][i])
        producttype=open_position['producttype'][i]
        old_data=get_historical_data(symbol=tradingsymbol,interval="5m",token=symboltoken,exch_seg=exch_seg,candle_type="NORMAL")
        st_10_2=float(old_data['Supertrend_10_2'].iloc[-1])
        st_7_3=float(old_data['Supertrend'].iloc[-1])
        st_10_1=float(old_data['Supertrend_10_1'].iloc[-1])
        sl=int(float(ltp_price)*0.8)
        sl_type="20"
        if st_7_3 < ltp_price:
          sl_type="ST_7_3"
          sl=st_7_3
        if st_10_2 < ltp_price:
          sl_type="ST_10_2"
          sl=st_10_2
        ordertag='Trail SL to ' + sl_type +":"+str(int(sl))
        exit_position(symboltoken,tradingsymbol,exch_seg,qty,sl,sl,ordertag=ordertag,producttype='CARRYFORWARD')
      except Exception as e:
        logger.error(f'Error in trail_sl')

def sub_loop_code(now_time):
  if (now_time.minute%5==0 and five_m_timeframe=='Yes'):
    st.session_state['options_trade_list']=[]
    nf_data,nf_5m_trade,nf_5m_trade_end=index_trade("NIFTY","5m")
    bnf_data,bnf_5m_trade,bnf_5m_trade_end=index_trade("BANKNIFTY","5m")
    sensex_data,sensex_5m_trade,sensex_5m_trade_end=index_trade("SENSEX","5m")
    log_holder.dataframe(st.session_state['options_trade_list'],hide_index=True)
    if near_options_trade=="Yes":trade_near_options('5m')
    log_holder.dataframe(st.session_state['options_trade_list'],hide_index=True)
    return nf_5m_trade_end,bnf_5m_trade_end,sensex_5m_trade_end
  else:
    return "-","-","-"
  log_holder.dataframe(st.session_state['options_trade_list'],hide_index=True)

def loop_code():
  global nf_5m_trade_end,bnf_5m_trade_end,sensex_5m_trade_end
  now = datetime.datetime.now(tz=gettz('Asia/Kolkata'))
  marketopen = now.replace(hour=9, minute=20, second=0, microsecond=0)
  marketclose = now.replace(hour=22, minute=50, second=0, microsecond=0)
  day_end = now.replace(hour=22, minute=30, second=0, microsecond=0)
  while now < day_end:
    now = datetime.datetime.now(tz=gettz('Asia/Kolkata'))
    try:
      last_login.text(f"Login: {st.session_state['login_time']} Last Run : {datetime.datetime.now(tz=gettz('Asia/Kolkata')).time().replace(microsecond=0)}")
      if now > marketopen and now < marketclose:
        nf_5m_trade_end,bnf_5m_trade_end,sensex_5m_trade_end=sub_loop_code(now)
        position,open_position=get_open_position()
        orderbook,pending_orders=get_order_book()
        close_options_position(position,nf_5m_trade_end=nf_5m_trade_end,bnf_5m_trade_end=bnf_5m_trade_end,sensex_5m_trade_end=sensex_5m_trade_end)
        #if now.minute%5==0: trail_sl()
      elif now > marketclose:closing_trade()
      index_ltp_string.text(f"Index Ltp: {print_ltp()}")
      now=datetime.datetime.now(tz=gettz('Asia/Kolkata'))
      time.sleep(60-now.second+1)
    except Exception as e:
      logger.error(f"error {e}")
      now=datetime.datetime.now(tz=gettz('Asia/Kolkata'))
      time.sleep(60-now.second+1)



#loop_code()

#close of Main App
st.header(f"Welcome {st.session_state['user_name']}")
last_login=st.empty()
last_login.text(f"Login: {st.session_state['login_time']}")
index_ltp_string=st.empty()
index_ltp_string.text(f"Index Ltp: {print_ltp()}")
tab0, tab1, tab2, tab3, tab4,tab5= st.tabs(["Log","Order Book", "Position","Open Order", "Settings","Token List"])
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
  open_order_updated=st.empty()
  open_order_updated.text(f"Open Order : ")
  open_order=st.empty()
with tab4:
  ind_col1,ind_col2,ind_col3,ind_col4=st.columns([5,1.5,1.5,1.5])
  indicator_list=['St Trade', 'ST_10_2 Trade','ST_10_1 Trade', 'RSI MA Trade','RSI_60 Trade','MACD Trade','PSAR Trade','DI Trade',
                  'MA Trade','EMA Trade','EMA_5_7 Trade','MA 21 Trade','HMA Trade','RSI_60 Trade','EMA_High_Low Trade','Two Candle Theory']
  with ind_col1:
    index_list=st.multiselect('Select Index',['NIFTY','BANKNIFTY','SENSEX'],['NIFTY','BANKNIFTY','SENSEX'])
    time_frame_interval = st.multiselect('Select Time Frame',['IDX:5M', 'IDX:15M', 'OPT:5M', 'OPT:15M','IDX:1M'],['IDX:5M', 'OPT:5M'])
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
position,open_position=get_open_position()
orderbook,pending_orders=get_order_book()
index_ltp_string.text(f"Index Ltp: {print_ltp()}")
last_login.text(f"Login: {st.session_state['login_time']} Last Run : {datetime.datetime.now(tz=gettz('Asia/Kolkata')).time().replace(microsecond=0)}")