import streamlit as st
st.set_page_config(page_title="Algo App",layout="wide",initial_sidebar_state="expanded", )
if 'user_name' not in st.session_state:
   st.session_state['user_name']="Guest"
   st.session_state['user_name']="Guest"
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
warnings.filterwarnings('ignore')
NoneType = type(None)
def get_user_pwd(user):
  if user=='Ganesh': username = 'G93179'; pwd = '4789'; apikey = 'CjOKjC5g'; token='U4EAZJ3L44CNJHNUZ56R22TPKI'
  elif user=='Kalyani': username = 'K205244'; pwd = '4789'; apikey = 'lzC7yJmt'; token='YDV6CJI6BEU3GWON7GZTZNU3RM'
  elif user=="Akshay": username='A325394'; pwd='1443'; apikey='OeSllszj'; token='G4OKBQKHXPS67EN2WMVP3TZ7X4'
  return username,pwd,apikey,token,user
username,pwd,apikey,token,user=get_user_pwd("Ganesh")
obj=SmartConnect(api_key=apikey)
@st.cache_resource
def angel_login():
   try:
      FEED_TOKEN = None;TOKEN_MAP = None;SMART_API_OBJ = None
      global user_name
      data = obj.generateSession(username,pwd,pyotp.TOTP(token).now())
      refreshToken= data['data']['refreshToken']
      feedToken=obj.getfeedToken()
      userProfile= obj.getProfile(refreshToken)
      aa= userProfile.get('data')
      st.session_state['user_name']=aa.get('name').title()
      st.session_state['login_time']=datetime.datetime.now()
      user=aa.get('name').title().split(' ')[0]
   except Exception as e:
      st.write("Unable to login")
      st.write(e)
angel_login()
@st.cache_resource
def get_token_df():
  global symbolDf,token_df
  url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
  d = requests.get(url).json()
  token_df = pd.DataFrame.from_dict(d)
  token_df['expiry'] = pd.to_datetime(token_df['expiry']).apply(lambda x: x.date())
  token_df = token_df.astype({'strike': float})
  return token_df
token_df=get_token_df()

global lots_to_trade,banknifty_target,banknifty_sl,nifty_target
global nifty_sl,trailing_stop_loss,percent_target,percent_loss,percent_trail
global trade_exit,stop_loss_type,trailing_stop_loss_type,target_order_type
global near_option_trade
global one_m_timeframe,three_m_timeframe,five_m_timeframe,fifteen_m_timeframe
global bank_nifty_trading,nifty_trading,stock_trading,bnf_start_trade,nf_start_trade
global day_end_exit_all
global open_position
global banknifty_sl_one_min,banknifty_target_one_min
global nifty_sl_one_min,nifty_target_one_min,robo_order_one_min
global Candle_trading,index_trail,two_candle_low_target
global pnl, pnl_sl,pnl_tgt
global candle_trade_target
global atr_sl, atr_target
pnl=0
pnl_sl=-10000
pnl_tgt=10000
lots_to_trade=1
trade_exit='supertrend' #@param ['atr','percent', 'points', 'indicator', 'supertrend']
day_end_exit_all='Yes' #@param ['Yes', 'No']
#points exit
banknifty_target=10; banknifty_sl=20
nifty_target=5; nifty_sl=10
trailing_stop_loss=10
banknifty_target_one_min=20; banknifty_sl_one_min=40
nifty_target_one_min=10; nifty_sl_one_min=20
percent_target= 30; percent_loss= 30
atr_sl=2; atr_target=1
near_option_trade="No"
two_candle_low_target=2

target_order_type="Stop_Loss" #@param ['Target','Stop_Loss','NA']
stop_loss_type='points' #@param ['points','three_candle_low','previous_candle_low']
candle_trade_target='points' #@param ['points','three_candle_low','previous_candle_low']
index_trail='three_candle_low' #@param ['three_candle_low','previous_candle_low','NA']
trailing_stop_loss_type='supertrend'#@param ['atr','supertrend','No']

percent_stop_trail=5
#Select Time Frames
one_m_timeframe='No' #@param ['Yes','No']
robo_order_one_min='Yes' #@param ['Yes','No']
five_m_timeframe='Yes' #@param ['Yes','No']
three_m_timeframe='No' #@param ['Yes','No']
fifteen_m_timeframe='Yes' #@param ['Yes','No']
#Select Index
bank_nifty_trading='Yes' #@param ['Yes','No']
nifty_trading='Yes' #@param ['Yes','No']
stock_trading='No' #@param ['Yes','No']
stock_scanner='Yes' #@param ['Yes','No']
Candle_trading='No' #@param ['Yes','No']

global market_open
global intraday_close
global market_close
market_open=datetime.datetime.now(tz=gettz('Asia/Kolkata')).replace(hour=9, minute=16, second=0, microsecond=0)
intraday_close=datetime.datetime.now(tz=gettz('Asia/Kolkata')).replace(hour=15, minute=0, second=0, microsecond=0)
market_close=datetime.datetime.now(tz=gettz('Asia/Kolkata')).replace(hour=15, minute=30, second=0, microsecond=0)

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

global signal_dict,orb_dict,order_history,target_history,orderbook,todays_trade_log,ltp_history
orb_dict = {"NIFTY_5m_high": "-", "NIFTY_5m_low": "-","NIFTY_15m_high":"-","NIFTY_15m_low":"-",
          "BANKNIFTY_5m_high": "-", "BANKNIFTY_5m_low": "-","BANKNIFTY_15m_high":"-","BANKNIFTY_15m_low":"-"}
signal_dict = {"NIFTY_1m": "-", "NIFTY_3m": "-","NIFTY_5m":"-","NIFTY_15m":"-",
      "BANKNIFTY_1m": "-","BANKNIFTY_3m":"-", "BANKNIFTY_5m":"-","BANKNIFTY_15m":"-",
      "NIFTY_1m_indicator": "-", "NIFTY_3m_indicator": "-","NIFTY_5m_indicator":"-","NIFTY_15m_indicator":"-",
      "BANKNIFTY_1m_indicator": "-","BANKNIFTY_3m_indicator":"-", "BANKNIFTY_5m_indicator":"-","BANKNIFTY_15m_indicator":"-"}
order_history=pd.DataFrame(columns = ['OrderID','Symbol','Time', 'LTP','Price','Target','Stop Loss','1000 Target','25% Target'])
target_history=pd.DataFrame(columns = ['OrderID','Symbol','Time', 'LTP','Price','Target'])
ltp_history=pd.DataFrame(columns = ['OrderID','Symbol','Time', 'LTP'])
orderbook=pd.DataFrame(columns=['variety', 'ordertype', 'producttype', 'duration', 'price','triggerprice', 'quantity',
                                'disclosedquantity', 'squareoff','stoploss', 'trailingstoploss', 'tradingsymbol', 'transactiontype',
                                'exchange', 'symboltoken', 'ordertag', 'instrumenttype', 'strikeprice','optiontype', 'expirydate', 'lotsize',
                                'cancelsize', 'averageprice','filledshares', 'unfilledshares', 'orderid', 'text', 'status','orderstatus',
                                'updatetime', 'exchtime', 'exchorderupdatetime','fillid', 'filltime', 'parentorderid'])
todays_trade_log = pd.DataFrame(columns=['variety', 'ordertype', 'producttype', 'duration', 'price',
       'triggerprice', 'quantity', 'disclosedquantity', 'squareoff','stoploss', 'trailingstoploss', 'tradingsymbol', 'transactiontype',
       'exchange', 'symboltoken', 'ordertag', 'instrumenttype', 'strikeprice','optiontype', 'expirydate', 'lotsize', 'cancelsize', 'averageprice',
       'filledshares', 'unfilledshares', 'orderid', 'text', 'status','orderstatus', 'updatetime', 'exchtime', 'exchorderupdatetime',
       'fillid', 'filltime', 'parentorderid', 'Sell', 'Exit Time','Sell Indicator', 'Status', 'LTP', 'Profit', 'Index SL', 'Time Frame',
       'Target', 'Stop Loss', 'Profit %'])

#get near option
def get_near_options(bnf_ltp,nf_ltp):
  symbol_list=['BANKNIFTY','NIFTY']
  df = pd.DataFrame()
  for symbol in symbol_list:
    indexLtp=bnf_ltp if symbol=="BANKNIFTY" else nf_ltp
    ltp=indexLtp*100
    expiry_day=bnf_expiry_day if symbol=="BANKNIFTY" else nf_expiry_day
    a = (token_df[(token_df['name'] == symbol) & (token_df['expiry']==expiry_day) & (token_df['strike']>=ltp) &
                    (token_df['symbol'].str.endswith('CE'))].sort_values(by=['strike']).head(4)).sort_values(by=['strike'], ascending=True)
    a.reset_index(inplace=True)
    a['Serial'] = a['index'] + 1
    a.drop(columns=['index'], inplace=True)
    b=(token_df[(token_df['name'] == symbol) & (token_df['expiry']==expiry_day) & (token_df['strike']<=ltp) &
                    (token_df['symbol'].str.endswith('PE'))].sort_values(by=['strike']).tail(4)).sort_values(by=['strike'], ascending=False)
    b.reset_index(inplace=True)
    b['Serial'] = b['index'] + 1
    b.drop(columns=['index'], inplace=True)
    df=pd.concat([df, a,b])
  df.sort_index(inplace=True)
  return df

def trade_near_options(time_frame):
  time_frame=str(time_frame)+"m"
  bnf_ltp=get_index_ltp("^NSEBANK")
  nf_ltp=get_index_ltp("^NSEI")
  near_option_list=get_near_options(bnf_ltp,nf_ltp)
  b_trade="-";n_trade="-"
  for i in range(0,len(near_option_list)):
    try:
      #print('Near Options :',near_option_list['symbol'].iloc[i])
      if (near_option_list['name'].iloc[i]=="BANKNIFTY" and b_trade=="-") or (near_option_list['name'].iloc[i]=="NIFTY" and n_trade=="-"):
        df=get_historical_data(symbol=near_option_list['symbol'].iloc[i],interval=time_frame,token=near_option_list['token'].iloc[i],exch_seg="NFO")
        if (df['St Trade'].values[-1]=="Buy" or df['ST_10_2 Trade'].values[-1]=="Buy" or
            df['EMA_High_Low Trade'].values[-1]=="Buy" or df["RSI MA Trade"].values[-1]=="Buy"):
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
          strategy=indicator + " (" +str(sl)+":"+str(target)+') '+" RSI:"+str(int(df['RSI'].values[-1]))
          buy_option(symbol=strike_symbol,indicator_strategy=strategy,interval=time_frame)
          if near_option_list['name'].iloc[i]=="BANKNIFTY": b_trade="Buy"
          if near_option_list['name'].iloc[i]=="NIFTY": n_trade="Buy"
          print(df.tail(1)[['Datetime','Symbol','Close','Trade','Trade End','Supertrend','Supertrend_10_2','RSI','Indicator']].to_string(index=False))
        time.sleep(1)
    except Exception as e:
      print(e)

#Get Token Info
def getTokenInfo (symbol, exch_seg ='NSE',instrumenttype='OPTIDX',strike_price = 0,pe_ce = 'CE',expiry_day = None):
  if symbol=="BANKNIFTY" or symbol=="^NSEBANK":
    expiry_day=bnf_expiry_day
  elif symbol=="NIFTY" or symbol=="^NSEI":
    expiry_day=nf_expiry_day
  df = token_df
  strike_price = strike_price*100
  if exch_seg == 'NSE':
      eq_df = df[(df['exch_seg'] == 'NSE') ]
      return eq_df[eq_df['name'] == symbol]
  elif exch_seg == 'NFO' and ((instrumenttype == 'FUTSTK') or (instrumenttype == 'FUTIDX')):
      return df[(df['exch_seg'] == 'NFO') & (df['instrumenttype'] == instrumenttype) & (df['name'] == symbol)].sort_values(by=['expiry'])
  elif exch_seg == 'NFO' and (instrumenttype == 'OPTSTK' or instrumenttype == 'OPTIDX'):
      return (df[(df['exch_seg'] == 'NFO') & (df['expiry']==expiry_day) &  (df['instrumenttype'] == instrumenttype) & (df['name'] == symbol)
      & (df['strike'] == strike_price) & (df['symbol'].str.endswith(pe_ce))].sort_values(by=['expiry']))

# get current bank nifty data
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

#Get Expire Days and future token
def get_expiry_day_fut_token():
  global expiry_day,bnf_expiry_day,nf_expiry_day,monthly_expiry_day,bnf_future_symbol,bnf_future_token,nf_future_symbol,nf_future_token
  global bnf_future,nf_future
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
  bnf_future = getTokenInfo('BANKNIFTY','NFO','FUTIDX','','',monthly_expiry_day).iloc[0]
  bnf_future_symbol=bnf_future['symbol']
  bnf_future_token=bnf_future['token']
  nf_future = getTokenInfo('NIFTY','NFO','FUTIDX','','',monthly_expiry_day).iloc[0]
  nf_future_symbol=nf_future['symbol']
  nf_future_token=nf_future['token']
get_expiry_day_fut_token()

#@title Angel

#variety: NORMAL/STOPLOSS * transactiontype: BUY/SELL * ordertype: MARKET/LIMIT/STOPLOSS_LIMIT * producttype: DELIVERY/CARRYFORWARD
#Duration: DAY/IOC * exchange: BSE/NSE/NFO/MCX
#Place Order
def place_order(token,symbol,qty,buy_sell,ordertype='MARKET',price=0,variety='NORMAL',exch_seg='NFO',producttype='CARRYFORWARD',triggerprice=0,squareoff=0,stoploss=0,ordertag='-'):
   try:
      orderparams = {"variety": variety,"tradingsymbol": symbol,"symboltoken": int(token),"transactiontype": buy_sell,"exchange": exch_seg,
                     "ordertype": ordertype,"producttype": producttype,"duration": "DAY","price": int(float(price)),"squareoff":int(float(squareoff)),
                     "stoploss": int(float(stoploss)),"quantity": int(float(qty)),"triggerprice":int(float(triggerprice)),"ordertag":ordertag,"trailingStopLoss":5}
      st.write(orderparams)
      orderId=obj.placeOrder(orderparams)
      st.write(orderId)
      LTP_Price=round(float(get_ltp_price(symbol=symbol,token=token,exch_seg=exch_seg)),2)
      print(f'{buy_sell} Order Placed: {orderId} Symbol: {symbol} LTP: {LTP_Price} Ordertag: {ordertag}')
      return orderId,LTP_Price
   except Exception as e:
      st.write("Order placement failed")
      st.write(e)
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
                                  "totalsellvalue","cfbuyavgprice","cfsellavgprice","totalbuyavgprice","totalsellavgprice","netprice",'realised', 'unrealised'])
  pnl=float(position['realised'].sum())+float(position['unrealised'].sum())
  open_position = position[(position['netqty'] > '0') & (position['instrumenttype'] == 'OPTIDX')]
  if len(position)!=0:
    print(position[['tradingsymbol','netqty','totalbuyavgprice','totalsellavgprice','realised', 'unrealised', 'ltp']].to_string(index=False))
  return position,open_position

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
          #df['price'].iloc[j]=float(ordertag.split("LTP: ",1)[1])
        if df['price'].iloc[j]==0:df['price'].iloc[j]='-'
      if df['price'].iloc[j]=='-':
        df['price'].iloc[j]=get_ltp_price(symbol=df['tradingsymbol'].iloc[j],token=df['symboltoken'].iloc[j],exch_seg=df['exchange'].iloc[j])
    except Exception as e:
      pass
  return df

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

def get_ltp_token(tokenlist):
  try:
    ltp_df=pd.DataFrame(obj.getMarketData(mode="LTP",exchangeTokens={ "NSE": ["99926000","99926009"], "NFO": list(tokenlist)})['data']['fetched'])
    return ltp_df
  except Exception as e:
    ltp_df=pd.DataFrame(columns = ['exchange','tradingSymbol','symbolToken','ltp'])
    return ltp_df

#Historical Data
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
    if (symbol[0]=="^" or "NS" in symbol) and symbol !="-":
      df=yfna_data(symbol,yf_interval,str(period)+"d")
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
      print("Yahoo Data Not Found")
      return "No data found, symbol may be delisted"
    return df
  except:
    print("Yahoo Data Not Found")
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
    if isinstance(df, str) or (isinstance(df, pd.DataFrame)==True and len(df)==0):
      print("Angel Data Not Found")
      return "No data found, symbol may be delisted"
    return df
  except:
    print("Angel Data Not Found")
    return "No data found, symbol may be delisted"

#Get LTP Price
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

def candlestick_pattern(df):
  df['DOJI']=pdta.cdl_doji(open=df['Open'],high=df['High'],low=df['Low'],close=df['Close'])
  df['CLOSINGMARUBOZU'] = pdta.closingmarubozu(open=df['Open'],high=df['High'],low=df['Low'],close=df['Close'])
  df['ENGULFING'] = pdta.engulfing(open=df['Open'],high=df['High'],low=df['Low'],close=df['Close'])
  df['HAMMER'] = pdta.hammer(open=df['Open'],high=df['High'],low=df['Low'],close=df['Close'])
  df['HANGINGMAN'] = pdta.hangingman(open=df['Open'],high=df['High'],low=df['Low'],close=df['Close'])
  df['INVERTEDHAMMER'] = pdta.invertedhammer(open=df['Open'],high=df['High'],low=df['Low'],close=df['Close'])
  df['MARUBOZU']  = pdta.marubozu(open=df['Open'],high=df['High'],low=df['Low'],close=df['Close'])
  return df

#update Buy and Sell trade info
def get_trade_info(df):
  for i in ['St Trade','MACD Trade','PSAR Trade','DI Trade','MA Trade','EMA Trade','BB Trade','Trade','Trade End',
            'Rainbow MA','Rainbow Trade','MA 21 Trade','ST_10_2 Trade','Two Candle Theory','HMA Trade','VWAP Trade',
            'EMA_5_7 Trade','ST_10_4_8 Trade','EMA_High_Low Trade','RSI MA Trade']:df[i]='-'
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

      #if int(df['RSI'][i])>=50 and df['RSI'][i-1]< df['RSI_MA'][i-1] and df['RSI'][i]> df['RSI_MA'][i]: df['RSI MA Trade'][i]="Buy"

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
        if (ST=="Buy" or EMA=="Buy" or MA=="Buyy" or ST_10_2=="Buy" or HMA_Trade=="Buyy" or MA=='Buyy'):
          df['Trade'][i]="Buy"; df['Trade End'][i]="Buy"
        elif (ST=="Sell" or EMA=="Sell" or MA=="Selll" or ST_10_2=="Sell" or HMA_Trade=="Selll" or MA=='Selll'):
          df['Trade'][i]="Sell"; df['Trade End'][i]="Sell"
        #if EMA_High_Low=="Buy":df['Trade'][i]="Buy";df['Trade End'][i]="Buy"
        #if EMA_High_Low=="Sell":df['Trade'][i]="Sell";df['Trade End'][i]="Sell"

      elif time_frame=="15m" or time_frame=="FIFTEEN_MINUTE" or time_frame=="15min":
        if (ST=="Buy" or MACD=="Buyy" or EMA=="Buy" or MA=="Buyy" or ST_10_2=="Buy"):
          df['Trade'][i]="Buy"; df['Trade End'][i]="Buy"
        elif (ST=="Sell" or MACD=="Selll" or EMA=="Sell" or MA=="Selll" or ST_10_2=="Sell"):
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
                   " ST_10_2:"+df['ST_10_2 Trade']+ " MA_21:"+df['MA 21 Trade']+" Two Candle Theory:"+df['Two Candle Theory'])#+" RSI:"+df['RSI'])
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
    df=get_trade_info(df)
    return df
  except Exception as e:
    print("Error in calculate Indicator",e)
    return df

# Calculate Heikin Ashi
def calculate_heikin_ashi(df):
  for i in range(2,len(df)):
    o=df['Open'][i-0]
    h=df['High'][i-0]
    l=df['Low'][i-0]
    c=df['Close'][i-0]
    df['Open'][i]=(o+c)/2
    df['Close'][i]=(o+h+l+c)/4
  return df

#First Trde
def first_trade_new():
  now = datetime.datetime.now(tz=gettz('Asia/Kolkata'))
  print('First Trade...',datetime.datetime.now(tz=gettz('Asia/Kolkata')).replace(microsecond=0, tzinfo=None))
  marketclose = now.replace(hour=9, minute=20, second=0, microsecond=0)
  marketclose_a = now.replace(hour=9, minute=16, second=0, microsecond=0)
  marketopen = now.replace(hour=0, minute=5, second=0, microsecond=0)
  while now < marketclose_a and now > marketopen:
    time.sleep(60-datetime.datetime.now(tz=gettz('Asia/Kolkata')).second+1)
    now = datetime.datetime.now(tz=gettz('Asia/Kolkata'))
    print_ltp()
  print('Lets Begin...')

def manual_buy(index_symbol,ce_pe="CE",index_ltp="-"):
   if index_ltp=="-":indexLtp=get_index_ltp(index_symbol)
   indexLtp, ce_strike_symbol,pe_strike_symbol=get_ce_pe_data(index_symbol,indexLtp=indexLtp)
   if ce_pe=="CE":symbol=ce_strike_symbol
   if ce_pe=="PE":symbol=pe_strike_symbol
   st.write(f'Manual Buy {index_symbol} {indexLtp} {symbol["symbol"]}')
   buy_option(symbol,"Manual Buy","5m")

#Index Trade Details
def index_trade(symbol="-",interval="-",candle_type="NORMAL",token="-",exch_seg="-"):
  try:
    tm=datetime.datetime.now(tz=gettz('Asia/Kolkata')).time().replace(microsecond=0)
    fut_data=get_historical_data(symbol,interval=interval,token=token,exch_seg=exch_seg,candle_type=candle_type)
    trade=str(fut_data['Trade'].values[-1])
    trade_end=str(fut_data['Trade End'].values[-1])
    if trade!="-" or trade_end!="-":
      indicator_strategy=fut_data['Indicator'].values[-1]
      indexLtp=fut_data['Close'].values[-1]
      interval_yf=fut_data['Time Frame'].values[-1]
      if symbol[:4]=="BANK" or symbol=="BANKNIFTY" or symbol=="^NSEBANK": symbol="BANKNIFTY"
      elif symbol[:4]=="NIFT" or symbol=="NIFTY" or symbol=="^NSEI": symbol="NIFTY"
      if "Candle" in indicator_strategy :
        two_candle_trade=todays_trade_log[(todays_trade_log['Status'] == 'Pending') & (todays_trade_log['ordertag'].str.contains("Candle"))]
        if len(two_candle_trade)!=0: trade='-'
      if trade!="-":
        if interval=="3m" or indexLtp=="-" or 'FUT' in symbol: indexLtp=get_index_ltp(symbol)
        indexLtp, ce_strike_symbol,pe_strike_symbol=get_ce_pe_data(symbol,indexLtp=indexLtp)
        if (bank_nifty_trading=='Yes' and symbol=="BANKNIFTY") or (nifty_trading=='Yes' and symbol=="NIFTY"):
          if trade=="Buy" : buy_option(ce_strike_symbol,indicator_strategy,interval)
          elif trade=="Sell" : buy_option(pe_strike_symbol,indicator_strategy,interval)
    if symbol=="BANKNIFTY" or symbol=="^NSEBANK": symbol="BANKNIFTY"
    elif symbol=="NIFTY" or symbol=="^NSEI": symbol="NIFTY"
    interval_yf=fut_data['Time Frame'].values[-1]
    indicator_strategy=fut_data['Indicator'].values[-1]
    signal_dict[symbol + "_" +interval_yf] = trade_end
    signal_dict[symbol + "_" +interval_yf+"_indicator"] = indicator_strategy
    print(symbol + "_" +interval_yf+"\n"+fut_data.tail(2)[['Datetime','Symbol','Close','Trade','Trade End','Supertrend','Supertrend_10_2','RSI','Indicator']].to_string(index=False))
    return fut_data
  except Exception as e:
    print('Error in index trade:',symbol,e)

#Buy Option and Place Stop Loss Order
def buy_option(symbol,indicator_strategy,interval,index_sl="-"):
   try:
      option_token=symbol['token']
      option_symbol=symbol['symbol']
      lotsize=int(symbol['lotsize'])*lots_to_trade
      st.write(f'{option_token},{option_symbol} {lotsize}')
      orderId,ltp_price=place_order(token=option_token,symbol=option_symbol,qty=lotsize,buy_sell='BUY',ordertype='MARKET',price=0,
                          variety='NORMAL',exch_seg='NFO',producttype='CARRYFORWARD',ordertag=indicator_strategy)
      #LTP_Price=str(round(float(get_ltp_price(symbol=option_symbol,token=option_token,exch_seg='NFO')),2))
      #indicator_strategy=indicator_strategy + " LTP: "+ LTP_Price
      if 'Candle' in indicator_strategy:
        index_symbol="BANKNIFTY" if option_symbol[:4]=='BANK' else 'NIFTY'
        fut_data=get_historical_data(symbol=index_symbol,interval='3m',token="-",exch_seg="-",candle_type="NORMAL")
        fut_data=fut_data.tail(2)
        ce_sl=fut_data['Low'].min()
        pe_sl=fut_data['High'].max()
        index_sl = ce_sl if option_symbol[-2:]=="CE" else pe_sl
        indicator_strategy=indicator_strategy+" Index SL: "+ str(int(float(index_sl)))
      if "(" in indicator_strategy and ")" in indicator_strategy:
        stop_loss=(indicator_strategy.split('('))[1].split(':')[0]
        target_price=(indicator_strategy.split(stop_loss+':'))[1].split(')')[0]
        stop_loss=int(float(stop_loss))
        target_price=int(float(target_price))
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
      tm=datetime.datetime.now(tz=gettz('Asia/Kolkata')).replace(microsecond=0, tzinfo=None)
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

#Exit Position
def exit_position(symboltoken,tradingsymbol,qty,ltp_price,sl,ordertag='',producttype='CARRYFORWARD'):
  position,open_position=get_open_position()
  try:
    if isinstance(open_position,str)==True or len(open_position)==0:
      orderId,ltp_price=place_order(token=symboltoken,symbol=tradingsymbol,qty=qty,buy_sell='SELL',ordertype='MARKET',price=0,
                          variety='NORMAL',exch_seg='NFO',producttype=producttype,ordertag=ordertag)
    else:
      position=open_position[(open_position.tradingsymbol==tradingsymbol) & (open_position.netqty!='0')]
      if len(position)!=0:
        cancel_all_order(tradingsymbol)
        orderId,ltp_price=place_order(token=symboltoken,symbol=tradingsymbol,qty=qty,buy_sell='SELL',ordertype='STOPLOSS_LIMIT',price=sl,
                        variety='STOPLOSS',exch_seg='NFO',producttype=producttype,triggerprice=sl,squareoff=sl, stoploss=sl,ordertag=ordertag)
        print ('Exit Alert In Option: ' , tradingsymbol,'LTP:',ltp_price,'SL:',sl)
      else: print('No Open Position : ',tradingsymbol)
  except Exception as e:
    print('Error in exit_position:',e)

# Close Options Positions on alert in index
def close_options_position(bnf_trade,nf_trade):
  position,open_position=get_open_position()
  if bnf_trade!="-" and nf_trade!="-":
    open_position=get_open_position()
    orderbook=get_order_book()
  else:
    if isinstance(open_position,str)==True : #or open_position=='No Position' or len(open_position)==0)
      print("No Position")
    else:
      for i in open_position.index:
        try:
          tradingsymbol=open_position.loc[i]['tradingsymbol']
          if ((bnf_trade=='Sell' and tradingsymbol[-2:]=='CE' and tradingsymbol.startswith('BANK')) or
            (bnf_trade=='Buy' and tradingsymbol[-2:]=='PE' and tradingsymbol.startswith('BANK')) or
            (nf_trade=='Sell' and tradingsymbol[-2:]=='CE' and tradingsymbol.startswith('NIFTY')) or
            (nf_trade=='Buy' and tradingsymbol[-2:]=='PE' and tradingsymbol.startswith('NIFTY'))) :
            symboltoken=open_position.loc[i]['symboltoken']
            qty=open_position['netqty'][i]
            producttype=open_position['producttype'][i]
            ltp_price=float(open_position['ltp'][i])
            sl=float(ltp_price)
            exit_position(symboltoken,tradingsymbol,qty,ltp_price,ltp_price,ordertag='Indicator Exit LTP: '+str(ltp_price),producttype=producttype)
          time.sleep(1)
        except Exception as e:
          print('Error in Close index trade:',e)

#Calculate Pivot Points
def calculate_pivot(symbol):
  symbol_yf='^NSEBANK' if symbol=="BANKNIFTY" else '^NSEI'
  data_ohlc=yf.Ticker(symbol_yf).history(interval='1d')
  data_ohlc = data_ohlc.round(decimals=2)
  data_ohlc.reset_index(level=0, inplace=True)
  date=data_ohlc['Date'].values[-1]
  date = pd.to_datetime(str(date))
  date = date.strftime('%Y.%m.%d')
  today= datetime.datetime.now(tz=gettz('Asia/Kolkata'))
  today = pd.to_datetime(str(today))
  today = today.strftime('%Y.%m.%d')
  if date==today:
    data_ohlc=data_ohlc.iloc[:-1]
  h=data_ohlc['High'].values[-1]
  l=data_ohlc['Low'].values[-1]
  c=data_ohlc['Close'].values[-1]
  P = round((h + l + c)/3,2)
  S1=round(P-(0.383*(h-l)),2)
  S2=round(P-(0.618*(h-l)),2)
  S3=round(P-(1*(h-l)),2)
  R1=round(P+(0.383*(h-l)),2)
  R2=round(P+(0.618*(h-l)),2)
  R3=round(P+(1*(h-l)),2)
  #pivot_trade=pivot_point_cross(f_close,s_close,P,S1,S2,S3,R1,R2,R3,symbol)
  return P,S1,S2,S3,R1,R2,R3

#Close Trade
def closing_trade():
  now = datetime.datetime.now(tz=gettz('Asia/Kolkata'))
  print('...Closing Trade...')
  marketclose = now.replace(hour=15, minute=30, second=0, microsecond=0)
  marketopen = now.replace(hour=0, minute=5, second=0, microsecond=0)
  day_end = now.replace(hour=15, minute=20, second=0, microsecond=0)
  while now < marketclose and  now > marketopen:
    try:
      now_time=datetime.datetime.now(tz=gettz('Asia/Kolkata'))
      time.sleep(1)
      signal_dict = {"NIFTY_1m": "-", "NIFTY_3m": "-","NIFTY_5m":"-","NIFTY_15m":"-",
      "BANKNIFTY_1m": "-","BANKNIFTY_3m":"-", "BANKNIFTY_5m":"-","BANKNIFTY_15m":"-",
      "NIFTY_1m_indicator": "-", "NIFTY_3m_indicator": "-","NIFTY_5m_indicator":"-","NIFTY_15m_indicator":"-",
      "BANKNIFTY_1m_indicator": "-","BANKNIFTY_3m_indicator":"-", "BANKNIFTY_5m_indicator":"-","BANKNIFTY_15m_indicator":"-"}
      for symbol_yf in ['^NSEI','^NSEBANK']:
        for interval_yf in ['5m','15m']:
          symbol="NIFTY" if symbol_yf=='^NSEI' else 'BANKNIFTY'
          fut_data=get_historical_data(symbol=symbol_yf,interval=interval_yf,token="-",exch_seg="-",candle_type="NORMAL")
          trade=str(fut_data['Trade'].values[-1])
          trade_end=str(fut_data['Trade End'].values[-1])
          indicator_strategy=fut_data['Indicator'].values[-1]
          signal_dict[symbol + "_" +interval_yf] = trade_end
          signal_dict[symbol + "_" +interval_yf+"_indicator"] = indicator_strategy
      get_todays_trade()
      closing_index_trade()
      check_target_sl()
      if (now_time.minute==15):
        print('\nOne Hour Trade...')
        send_status()
        day_stock_scaner('60m')
      print_ltp()
      print('___________________________________________')
      if now > day_end: day_end_close()
      now=datetime.datetime.now(tz=gettz('Asia/Kolkata'))
      time.sleep(60-now.second+1)
    except Exception as e:
      print("Error In Closing Trade",e)
  print ('Bye... Market Closed')
  send_active_order()

def print_ltp():
  try:
    data=pd.DataFrame(obj.getMarketData(mode="OHLC",exchangeTokens={ "NSE": [99926000,99926009], "NFO": []})['data']['fetched'])
    data['change']=data['ltp']-data['close']
    print_sting=datetime.datetime.now(tz=gettz('Asia/Kolkata')).replace(microsecond=0, tzinfo=None).time()
    for i in range(0,len(data)):print_sting=f"{print_sting} {data.iloc[i]['tradingSymbol']} {int(data.iloc[i]['ltp'])}({int(data.iloc[i]['change'])})"
    print_sting=print_sting.replace("Nifty 50","Nifty")
    print_sting=print_sting.replace("Nifty Bank","BankNifty")
    st.write(print_sting)
  except Exception as e:
    st.write(e)

def send_active_order():
  active_order="Active Orders:"
  margin=0
  for i in range(0,len(todays_trade_log)):
      if todays_trade_log['Status'].iloc[i]=='Pending':
        symboltoken=todays_trade_log['symboltoken'].iloc[i]
        tradingsymbol=todays_trade_log['tradingsymbol'].iloc[i]
        #ltpInfo = obj.ltpData('NFO',tradingsymbol,symboltoken)
        #ltp=int(ltpInfo['data']['ltp'])
        ltp=get_ltp_price(symbol=tradingsymbol,token=symboltoken,exch_seg="NFO")
        ltp_price = str(ltp)
        buy_price=todays_trade_log['price'].iloc[i]
        trade_info=(todays_trade_log['tradingsymbol'].iloc[i] +' ' + str(todays_trade_log['price'].iloc[i]) + " LTP:"+ ltp_price)
        active_order=active_order+"\n"+trade_info
        margin=margin+(float(todays_trade_log['price'].iloc[i])*float(todays_trade_log['quantity'].iloc[i]))
  if active_order=="Active Orders:": active_order="No Active Order"
  active_order=active_order+'\nMargin Used: '+str(float(margin))
  return "\n"+active_order

# Get Active Order or position
def get_active_order(symbol):
  try:
    orderId,orderPrice='NoOrder','NoOrder'
    orderBook=obj.orderBook()['data']
    if isinstance(orderBook,NoneType)!=True:
      d= pd.DataFrame.from_dict(obj.orderBook()['data'])
      orderBook=d[['orderid','exchange','transactiontype','orderstatus','symboltoken','tradingsymbol','price',
                  'quantity','updatetime','variety','ordertype','producttype']]
      orderBook = orderBook[(orderBook['tradingsymbol'] == symbol) &
                            ((orderBook['orderstatus'] != 'complete') & (orderBook['orderstatus'] != 'cancelled') &
                             (orderBook['orderstatus'] != 'rejected') & (orderBook['orderstatus'] != 'AMO CANCELLED'))]
      if len(orderBook)==0: orderId,orderPrice='NoOrder','NoOrder'
      elif len(orderBook) !=0:
          orderId=orderBook.iloc[0]['orderid']
          orderPrice=int(orderBook.iloc[0]['price'])
    return orderId,orderPrice
  except Exception as e:
    orderId,orderPrice='NoOrder','NoOrder'
    return orderId,orderPrice

def send_status():
  trade=len(todays_trade_log)
  exit_loss=len(todays_trade_log[(todays_trade_log['Status']=='Closed') & (todays_trade_log['Profit'] <0 )])
  exit_win=len(todays_trade_log[(todays_trade_log['Status']=='Closed') & (todays_trade_log['Profit'] >0 )])
  active=len(todays_trade_log[(todays_trade_log['Status'] == 'Pending')])
  pl=int((todays_trade_log['Profit'].sum()))
  active_order=send_active_order()
  telegram_bot_sendtext("Exit Win :"+str(exit_win)+ "\nExit Loss :"+str(exit_loss) +"\nActive :"+str(active)+"\nTrade :"+str(trade)+
                        "\nProfit :"+str(pl)+active_order)

#Get Index Token
def getTokenInfo_index(symbol):
  df = token_df
  return df[(df['exch_seg'] == 'NSE') & (df['symbol']== (symbol))]

#Get Last Buy Price of order
def get_price_of_position(symbol):
  price='-'
  position=obj.position()['data']
  position=pd.DataFrame(position)
  position=position[(position['tradingsymbol']==symbol)]
  price=position.iloc[0]['cfbuyavgprice']
  trade_book=obj.tradeBook()['data']
  if isinstance(trade_book,NoneType)!=True:
    trade_book=pd.DataFrame(trade_book)
    trade_book = trade_book[(trade_book['tradingsymbol'] == symbol) & (trade_book['transactiontype'] == 'BUY')]
    no_of_trades=(len(trade_book))
    if no_of_trades!=0:
      trade_book=trade_book.sort_values(by=['filltime'], ascending=False)
      price=trade_book.iloc[0]['fillprice']
  return price

def get_todays_trade_index(symbol,interval="-",candle_type="-",token="-",exch_seg="-",dat='-'):
  df=get_historical_data(symbol=symbol,interval=interval,candle_type=candle_type,token=token,exch_seg=exch_seg)
  df['Trade Time'] = df.index
  df = df[(df['Date'] == dat) & (df['Trade'] != '-')]
  df=df.reset_index()
  for i in range(0,len(df)):
    if df['Time Frame'].iloc[i]=="Candle Pattern": df['Trade Time'].iloc[i]=df['Trade Time'].iloc[i] + datetime.timedelta(minutes=3)
    elif df['Time Frame'].iloc[i]=="5m": df['Trade Time'].iloc[i]=df['Trade Time'].iloc[i] + datetime.timedelta(minutes=5)
    elif df['Time Frame'].iloc[i]=="15m": df['Trade Time'].iloc[i]=df['Trade Time'].iloc[i] + datetime.timedelta(minutes=15)
  df=df[['Trade Time','Close','Trade','Trade End','Indicator']]
  df['Trade End Time']= datetime.datetime.now(tz=gettz('Asia/Kolkata')).replace(hour=15, minute=29, second=0, microsecond=0, tzinfo=None)
  df['Exit Indicator']='-'
  df['Symbol']="BANKNIFTY" if symbol=="^NSEBANK" else "NIFTY"
  df['Remark']='-'
  return df

def update_order_history():
  global order_history
  for i in range(0,len(order_history)):
    if pd.isna(order_history['Target'].iloc[i])==True:
      order_history['Stop Loss'].iloc[i]=order_history['LTP'].iloc[i]*0.7
      order_history['Target'].iloc[i]=order_history['LTP'].iloc[i]*1.3
      sl=order_history['LTP'].iloc[i]*0.7
      tgt=order_history['LTP'].iloc[i]*1.3
      if trade_exit=="percent":
        sl=order_history['LTP'].iloc[i]*0.7
        tgt=order_history['LTP'].iloc[i]*1.3
      elif trade_exit=="indicator":
        sl=order_history['LTP'].iloc[i]*0.001
        tgt=order_history['LTP'].iloc[i]*10
      elif trade_exit=="points":
        sl=order_history['LTP'].iloc[i]-(banknifty_sl if order_history['Symbol'].iloc[i][:4]=="BANK" else nifty_sl)
        tgt=order_history['LTP'].iloc[i]+(banknifty_target if order_history['Symbol'].iloc[i][:4]=="BANK" else nifty_target)
      if tgt >= order_history['Target'].iloc[i]: order_history['Target'].iloc[i]=tgt
      if sl >= order_history['Stop Loss'].iloc[i]: order_history['Stop Loss'].iloc[i]=sl

def trail_sl_with_atr():
  global order_history
  for i in range(0,len(todays_trade_log)):
    if todays_trade_log['Status'].iloc[i]!='Closed':
      interval="1m" if "1m" in todays_trade_log['ordertag'].iloc[i] else "5m"
      old_opt_data=get_historical_data(symbol=todays_trade_log['tradingsymbol'].iloc[i],interval=interval,token=todays_trade_log['symboltoken'].iloc[i]
                      ,exch_seg=todays_trade_log['exchange'].iloc[i],candle_type="NORMAL")
      LTP_Price=get_ltp_price(symbol=todays_trade_log['tradingsymbol'].iloc[i],token=todays_trade_log['symboltoken'].iloc[i],
                                exch_seg=todays_trade_log['exchange'].iloc[i])
      if trailing_stop_loss_type=="atr":
        sl=round(float(float(LTP_Price)-(float(old_opt_data['Atr'].iloc[-1])*3)),2)
        order_history=order_history.append({'OrderID':todays_trade_log['orderid'].iloc[i],'Symbol':todays_trade_log['tradingsymbol'].iloc[i],
                      'Time':todays_trade_log['updatetime'].iloc[i],'LTP':todays_trade_log['LTP'].iloc[i],'Price':todays_trade_log['price'].iloc[i],
                      'Stop Loss':sl},ignore_index = True)
      if trailing_stop_loss_type=="supertrend":
        if float(old_opt_data['Supertrend'].iloc[-1]) <= float(LTP_Price):
          sl=float(old_opt_data['Supertrend'].iloc[-1])
          order_history=order_history.append({'OrderID':todays_trade_log['orderid'].iloc[i],'Symbol':todays_trade_log['tradingsymbol'].iloc[i],
                      'Time':todays_trade_log['updatetime'].iloc[i],'LTP':todays_trade_log['LTP'].iloc[i],'Price':todays_trade_log['price'].iloc[i],
                      'Stop Loss':sl},ignore_index = True)
        if float(old_opt_data['Supertrend_10_2'].iloc[-1]) <= float(LTP_Price):
          sl=float(old_opt_data['Supertrend'].iloc[-1])
          order_history=order_history.append({'OrderID':todays_trade_log['orderid'].iloc[i],'Symbol':todays_trade_log['tradingsymbol'].iloc[i],
                      'Time':todays_trade_log['updatetime'].iloc[i],'LTP':todays_trade_log['LTP'].iloc[i],'Price':todays_trade_log['price'].iloc[i],
                      'Stop Loss':sl},ignore_index = True)
      dummy_order_history = order_history[(order_history['OrderID'] == todays_trade_log['orderid'].iloc[i])]
      sl=round(dummy_order_history['Stop Loss'].max(),2)
      print(todays_trade_log['tradingsymbol'].iloc[i],"Buy:"+str(todays_trade_log['price'].iloc[i]),' LTP:'+str(LTP_Price)," SL:"+str(sl))
  change_sl()

def change_sl():
  global todays_trade_log, order_history
  for i in range(0,len(todays_trade_log)):
    if todays_trade_log['Status'].iloc[i]!='Closed':
      dummy_order_history = order_history[(order_history['OrderID'] == todays_trade_log['orderid'].iloc[i])]
      if len(dummy_order_history)==0:
        sl=int(todays_trade_log['price'].iloc[i]*0.7)
        order_history=order_history.append({'OrderID':todays_trade_log['orderid'].iloc[i],'Symbol':todays_trade_log['tradingsymbol'].iloc[i],
                                        'Time':todays_trade_log['updatetime'].iloc[i],'LTP':todays_trade_log['LTP'].iloc[i],
                                        'Price':todays_trade_log['price'].iloc[i],
                                        'Stop Loss':sl},ignore_index = True)
      todays_trade_log['Stop Loss'].iloc[i]=dummy_order_history['Stop Loss'].max()

def update_ltp_buy_df(buy_df):
  tokenlist=buy_df['symboltoken'].values.tolist()
  ltp_df=get_ltp_token(numpy.unique(tokenlist))
  for i in range(0,len(buy_df)):
    symboltoken=int(buy_df['symboltoken'].iloc[i])
    n_ltp_df=ltp_df[ltp_df['symbolToken']==symboltoken]
    if len(n_ltp_df)!=0:
      buy_df['LTP'].iloc[i]=n_ltp_df['ltp'].iloc[0]
    else:
      buy_df['LTP'].iloc[i]=get_ltp_price(symbol=buy_df['tradingsymbol'].iloc[i],token=buy_df['symboltoken'].iloc[i],exch_seg=buy_df['exchange'].iloc[i])
  return buy_df

def max_margin():
  margin=0
  for i in range(0,len(orderbook)):
    amt=float(orderbook['quantity'].iloc[i])*float(orderbook['price'].iloc[i])
    if orderbook['transactiontype'].iloc[i]=="BUY":
      margin=margin+amt
    else:
      margin=margin-amt
  return margin

def update_target_sl_new(buy_df):
  for i in range(0,len(buy_df)):
    try:
      if "(" in buy_df['ordertag'].iloc[i] and ")" in buy_df['ordertag'].iloc[i]:
        sl=(buy_df['ordertag'].iloc[i].split('('))[1].split(':')[0]
        tgt=(buy_df['ordertag'].iloc[i].split(sl+':'))[1].split(')')[0]
        buy_df['Stop Loss'].iloc[i]=sl
        buy_df['Target'].iloc[i]=tgt
    except Exception as e:
      print(e)
  return buy_df

def update_target_sl(buy_df):
  global order_history,target_history
  for i in range(0,len(buy_df)):
    try:
      if "(" in buy_df['ordertag'].iloc[i] and ")" in buy_df['ordertag'].iloc[i]:
        sl=(buy_df['ordertag'].iloc[i].split('('))[1].split(':')[0]
        tgt=(buy_df['ordertag'].iloc[i].split(sl+':'))[1].split(')')[0]
        buy_df['Stop Loss'].iloc[i]=sl
        buy_df['Target'].iloc[i]=tgt
      else:
        buy_df['Stop Loss'].iloc[i]=int(float(buy_df['price'].iloc[i]*0.7))
        buy_df['Target'].iloc[i]=int(float(buy_df['price'].iloc[i]*1.5))
    except Exception as e:
      print('Error found in ',e)
  return buy_df

def update_high_low(n_todays_trade_log):
  global ltp_history
  n_todays_trade_log['High']="-";n_todays_trade_log['Low']="-"
  for i in range(0,len(n_todays_trade_log)):
    try:
      dummy_target_history = update_high_low[(update_high_low['OrderID'] == n_todays_trade_log['orderid'].iloc[i])]
      n_todays_trade_log['High'].iloc[i]=dummy_target_history['LTP'].max()
      n_todays_trade_log['Low'].iloc[i]=dummy_target_history['LTP'].min()
    except Exception as e:
      pass
  return n_todays_trade_log

def get_todays_trade():
  try:
    global todays_trade_log,orderbook,pending_trade,n_todays_trade_log,dataframe
    get_order_book()
    #complete_order=orderbook[(orderbook['status']=="complete")]
    #if len(complete_order)>= 1:orderbook=orderbook[(orderbook['status']=="complete")]
    sell_df=orderbook[(orderbook['transactiontype']=="SELL") & ((orderbook['status']=="complete") | (orderbook['status']=="rejected"))]
    sell_df['Remark']='-'
    buy_df=orderbook[(orderbook['transactiontype']=="BUY") & ((orderbook['status']=="complete") | (orderbook['status']=="rejected"))]
    buy_df['Sell']='-'
    buy_df['Exit Time']=datetime.datetime.now(tz=gettz('Asia/Kolkata')).replace(hour=15, minute=30, second=0, microsecond=0,tzinfo=None)
    buy_df['Sell Indicator']='-';buy_df['Status']='Pending'
    for i in ['LTP','Profit','Index SL','Time Frame','Target','Stop Loss','Profit %','High','Low']:buy_df[i]='-'
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
    buy_df['ordertag']=buy_df['ordertag'].str.strip()
    buy_df=update_target_sl(buy_df)
    #for i in range(0,len(buy_df)):
    #  if "Target Hit" in buy_df['Sell Indicator'].iloc[i]: buy_df['Status'].iloc[i]="Target Hit"
    #  elif "Stop Loss Hit" in buy_df['Sell Indicator'].iloc[i]: buy_df['Status'].iloc[i]="Stop Loss Hit"
    buy_df[['Stop Loss', 'Target']] = buy_df[['Stop Loss', 'Target']].astype(int)
    for i in range(0,len(buy_df)):
      try:
        ordertag=buy_df['ordertag'].iloc[i]
        if "Index SL: " in ordertag: buy_df['Index SL'].iloc[i]=float(ordertag.split("Index SL: ",1)[1])
      except Exception as e: pass
    if len(buy_df)!=0: buy_df=update_ltp_buy_df(buy_df)
    for i in range(0,len(buy_df)):
      if buy_df['Status'].iloc[i]!='Closed':
        #buy_df['LTP'].iloc[i]=get_ltp_price(symbol=buy_df['tradingsymbol'].iloc[i],token=buy_df['symboltoken'].iloc[i],exch_seg=buy_df['exchange'].iloc[i])
        buy_df['Profit'].iloc[i]=float((buy_df['LTP'].iloc[i]-buy_df['price'].iloc[i]))*float(buy_df['quantity'].iloc[i])
        buy_df['Profit %'].iloc[i]=((buy_df['LTP'].iloc[i]/buy_df['price'].iloc[i])-1)*100
      else:
        buy_df['Profit'].iloc[i]=float((buy_df['Sell'].iloc[i]-buy_df['price'].iloc[i]))*float(buy_df['quantity'].iloc[i])
        buy_df['Profit %'].iloc[i]=((buy_df['Sell'].iloc[i]/buy_df['price'].iloc[i])-1)*100
    buy_df['Profit %']=buy_df['Profit %'].astype(float).round(2)
    buy_df[['quantity', 'Target','Stop Loss','Profit']] = buy_df[['quantity', 'Target','Stop Loss','Profit']].astype(int)
    buy_df=buy_df.round(2)
    todays_trade_log=buy_df.sort_values(by = ['Status', 'updatetime'], ascending = [False, True], na_position = 'first')
    ganesh_sl_trail()
    n_todays_trade_log=todays_trade_log[(todays_trade_log['Status']=='Pending')]
    #margin=int(n_todays_trade_log['Margin'].sum())
    if len(n_todays_trade_log)!=0:
      print(n_todays_trade_log[['updatetime','tradingsymbol','price','Stop Loss','Target','LTP','Status','Profit','Profit %','ordertag']].to_string(index=False))
    elif len(todays_trade_log)!=0:
      print(todays_trade_log[['updatetime','tradingsymbol','price','Stop Loss','Target','LTP','Status','Sell','Profit','Profit %','ordertag','Sell Indicator']].to_string(index=False))
  except Exception as e:
    print("Error get_todays_trade",e)
    todays_trade_log = pd.DataFrame(columns = ['updatetime','symboltoken','tradingsymbol','exchange','price','ordertag',
        'Sell','Exit Time','quantity','Sell Indicator','Status','LTP','Profit','Index SL','Time Frame','Stop Loss','Target'])

def close_one_minute_todays_trade(bnf_signal='-',nf_signal='-',bnf_indicator='Indicator Exit',nf_indicator='Indicator Exit'):
  for i in range(0,len(todays_trade_log)):
    if todays_trade_log['Status'].iloc[i]=="Pending" and "1m" in todays_trade_log['ordertag'].iloc[i]:
      tradingsymbol=todays_trade_log['tradingsymbol'].iloc[i]
      symboltoken=todays_trade_log['symboltoken'].iloc[i]
      qty=todays_trade_log['quantity'].iloc[i]
      producttype=todays_trade_log['producttype'].iloc[i]
      orderid=todays_trade_log['orderid'].iloc[i]
      ltp_price=get_ltp_price(symbol=tradingsymbol,token=symboltoken,exch_seg="NFO")
      if ((bnf_signal=='Sell' and tradingsymbol[-2:]=='CE' and tradingsymbol[:4]=='BANK') or
        (bnf_signal=='Buy' and tradingsymbol[-2:]=='PE' and tradingsymbol[:4]=='BANK') or
        (nf_signal=='Sell' and tradingsymbol[-2:]=='CE' and tradingsymbol[:5]=='NIFTY') or
        (nf_signal=='Buy' and tradingsymbol[-2:]=='PE' and tradingsymbol[:5]=='NIFTY')):
        ordertag=bnf_indicator if tradingsymbol[:4]=='BANK' else nf_indicator
        ordertag=str(orderid)+" " + ordertag + ' LTP: '+ str(ltp_price)
        place_order(token=symboltoken,symbol=tradingsymbol,qty=qty,buy_sell='SELL',ordertype='STOPLOSS_LIMIT',price=ltp_price,
           variety='STOPLOSS',exch_seg='NFO',producttype=producttype,triggerprice=ltp_price,squareoff=ltp_price, stoploss=ltp_price,
           ordertag=ordertag)
        prt=float(ltp_price)-float(todays_trade_log['price'].iloc[i])
        todays_trade_log['Profit'].iloc[i]=float(prt)*float(todays_trade_log['quantity'].iloc[i])
        trade_info=(todays_trade_log['tradingsymbol'].iloc[i] + '\nBuy: ' + str(todays_trade_log['price'].iloc[i]) +
                    '\nTarget: ' +str(todays_trade_log['Target'].iloc[i])+ ' Stop Loss: ' +str(int(todays_trade_log['Stop Loss'].iloc[i]))+
                    ' LTP:' +str(float(ltp_price))+ '\nBuy Time: '+str(todays_trade_log['updatetime'].iloc[i])+
                    '\nIndicator: ' + str(todays_trade_log['ordertag'].iloc[i])+
                    '\nProfit: ' + str(int(todays_trade_log['Profit'].iloc[i])))
        pl=("Realised:"+str(int(todays_trade_log[(todays_trade_log['Status']=='Closed')]['Profit'].sum())) +
          " Unrealised:"+str(int(todays_trade_log[(todays_trade_log['Status']!='Closed')]['Profit'].sum())))
        todays_trade_log['Status'].iloc[i]="Closed"
        telegram_bot_sendtext("Exit: "+ ordertag +'\n'+ trade_info +'\n'+ pl)
      elif float(ltp_price)>= float(todays_trade_log['price'].iloc[i])*1.25:
        sl=str(int(float((todays_trade_log['price'].iloc[i])*1.05)))
        trail_sl_new(symboltoken,tradingsymbol,qty,ltp_price,sl,ordertag='SL Trail LTP: '+sl,producttype=producttype)

def close_all_todays_trade(bnf_signal='-',nf_signal='-',bnf_indicator='Indicator Exit',nf_indicator='Indicator Exit'):
  for i in range(0,len(todays_trade_log)):
    if todays_trade_log['Status'].iloc[i]=="Pending":
      tradingsymbol=todays_trade_log['tradingsymbol'].iloc[i]
      symboltoken=todays_trade_log['symboltoken'].iloc[i]
      qty=todays_trade_log['quantity'].iloc[i]
      producttype=todays_trade_log['producttype'].iloc[i]
      orderid=todays_trade_log['orderid'].iloc[i]
      ltp_price=get_ltp_price(symbol=tradingsymbol,token=symboltoken,exch_seg="NFO")
      if ((bnf_signal=='Sell' and tradingsymbol[-2:]=='CE' and tradingsymbol[:4]=='BANK') or
        (bnf_signal=='Buy' and tradingsymbol[-2:]=='PE' and tradingsymbol[:4]=='BANK') or
        (nf_signal=='Sell' and tradingsymbol[-2:]=='CE' and tradingsymbol[:5]=='NIFTY') or
        (nf_signal=='Buy' and tradingsymbol[-2:]=='PE' and tradingsymbol[:5]=='NIFTY')):
        ordertag=bnf_indicator if tradingsymbol[:4]=='BANK' else nf_indicator
        ordertag=str(orderid)+" " + ordertag + ' LTP: '+ str(ltp_price)
        orderId,ltp_price=place_order(token=symboltoken,symbol=tradingsymbol,qty=qty,buy_sell='SELL',ordertype='STOPLOSS_LIMIT',price=ltp_price,
           variety='STOPLOSS',exch_seg='NFO',producttype=producttype,triggerprice=ltp_price,squareoff=ltp_price, stoploss=ltp_price,
           ordertag=ordertag)
        if str(orderId)!='Order placement failed':
          prt=float(ltp_price)-float(todays_trade_log['price'].iloc[i])
          todays_trade_log['Profit'].iloc[i]=float(prt)*float(todays_trade_log['quantity'].iloc[i])
          trade_info=(todays_trade_log['tradingsymbol'].iloc[i] + '\nBuy: ' + str(todays_trade_log['price'].iloc[i]) +
                      '\nTarget: ' +str(todays_trade_log['Target'].iloc[i])+ ' Stop Loss: ' +str(int(todays_trade_log['Stop Loss'].iloc[i]))+
                      ' LTP:' +str(float(ltp_price))+ '\nBuy Time: '+str(todays_trade_log['updatetime'].iloc[i])+
                      '\nIndicator: ' + str(todays_trade_log['ordertag'].iloc[i])+
                      '\nProfit: ' + str(int(todays_trade_log['Profit'].iloc[i])))
          pl=("Realised:"+str(int(todays_trade_log[(todays_trade_log['Status']=='Closed')]['Profit'].sum())) +
            " Unrealised:"+str(int(todays_trade_log[(todays_trade_log['Status']!='Closed')]['Profit'].sum())))
          todays_trade_log['Status'].iloc[i]="Closed"
          telegram_bot_sendtext("Exit: "+ ordertag +'\n'+ trade_info +'\n'+ pl)
      elif float(ltp_price)>= float(todays_trade_log['price'].iloc[i])*1.25:
        sl=str(int(float((todays_trade_log['price'].iloc[i])*1.05)))
        trail_sl_new(symboltoken,tradingsymbol,qty,ltp_price,sl,ordertag='SL Trail LTP: '+sl,producttype=producttype)

def cancel_options_all_order(bnf_signal='-',nf_signal='-'):
  get_order_book()
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

def close_all_position(bnf_signal='-',nf_signal='-',bnf_indicator='Indicator Exit',nf_indicator='Indicator Exit'):
  #cancel_options_all_order(bnf_signal='-',nf_signal='-')
  if isinstance(open_position,str)==True : #or open_position=='No Position' or len(open_position)==0)
    pass
  else:
    for i in open_position.index:
      try:
        tradingsymbol=open_position.loc[i]['tradingsymbol']
        symboltoken=open_position.loc[i]['symboltoken']
        qty=open_position['netqty'][i]
        producttype=open_position['producttype'][i]
        ltp_price=float(open_position['ltp'][i])
        sl=int(float(ltp_price))
        position_cnt=0
        ordertag=bnf_indicator if tradingsymbol[:4]=='BANK' else nf_indicator
        ordertag=ordertag + ' LTP: '+ str(ltp_price)
        if ((bnf_signal=='Sell' and tradingsymbol[-2:]=='CE' and tradingsymbol[:4]=='BANK') or
          (bnf_signal=='Buy' and tradingsymbol[-2:]=='PE' and tradingsymbol[:4]=='BANK') or
          (nf_signal=='Sell' and tradingsymbol[-2:]=='CE' and tradingsymbol[:5]=='NIFTY') or
          (nf_signal=='Buy' and tradingsymbol[-2:]=='PE' and tradingsymbol[:5]=='NIFTY')):
          orderId,ltp_price=place_order(token=symboltoken,symbol=tradingsymbol,qty=qty,buy_sell='SELL',ordertype='STOPLOSS_LIMIT',price=sl,
                    variety='STOPLOSS',exch_seg='NFO',producttype=producttype,triggerprice=sl,squareoff=sl, stoploss=sl,ordertag=ordertag)
          if str(orderId)!='Order placement failed':
            telegram_bot_sendtext("Exit: "+tradingsymbol +"\n"+ ordertag)
      except Exception as e:
        print("Error in close_all_position:", e)

#get Stock Token
def getTokenInfo_stk (symbol):
    df=token_df
    df=df[token_df['symbol'].str.contains(symbol)]
    eq_df = df[(df['exch_seg'] == 'NSE')]
    return df[(df['exch_seg'] == 'NSE') & (df['name']== (symbol)) & (df['symbol'].str.endswith('-EQ'))]

#place stop loss and target order
def sl_target_order(orderId,symbol,token,price,LTP_Price):
  target= banknifty_target if symbol[:4]=='BANK' else nifty_target
  stop_loss= banknifty_sl if symbol[:4]=='BANK' else nifty_sl
  if trade_exit=='percent' or trade_exit=='indicator':
    target_price=(LTP_Price*(100+percent_target))/100; stop_loss_price=(LTP_Price*(100-percent_loss))/100
  elif trade_exit=='points':
    target_price=LTP_Price+target; stop_loss_price=LTP_Price-stop_loss
  elif trade_exit=='atr':
    old_data=get_historical_data(symbol=symbol,interval='5m',token=token,exch_seg="NFO",candle_type="NORMAL")
    atr=int(float(old_data['Atr'].values[-1]))
    target_price=int(LTP_Price+(atr*atr_target)); stop_loss_price=int(LTP_Price-(atr*atr_sl))
  else: target_price=LTP_Price+target; stop_loss_price=LTP_Price-stop_loss
  return target_price, stop_loss_price

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

#VWAP Index Trade Details
def vwap_index_trade(symbol="-",interval="-",candle_type="NORMAL",token="-",exch_seg="-"):
  try:
    fut_data=get_historical_data(symbol,interval=interval,token=token,exch_seg=exch_seg,candle_type=candle_type)
    trade=str(fut_data['VWAP Trade'].values[-1])
    trade_end=str(fut_data['VWAP Trade'].values[-1])
    if trade!="-" or trade_end!="-":
      indicator_strategy=fut_data['Indicator'].values[-1]
      if symbol[:4]=="BANK" or symbol=="BANKNIFTY" or symbol=="^NSEBANK": symbol="BANKNIFTY"
      elif symbol[:4]=="NIFT" or symbol=="NIFTY" or symbol=="^NSEI": symbol="NIFTY"
      indexLtp=get_index_ltp(symbol)
      interval_yf=fut_data['Time Frame'].values[-1]
      if trade!="-":
        indexLtp, ce_strike_symbol,pe_strike_symbol=get_ce_pe_data(symbol,indexLtp=indexLtp)
        if (bank_nifty_trading=='Yes' and symbol=="BANKNIFTY") or (nifty_trading=='Yes' and symbol=="NIFTY"):
          if trade=="Buy" : buy_option(ce_strike_symbol,indicator_strategy,interval)
          elif trade=="Sell" : buy_option(pe_strike_symbol,indicator_strategy,interval)
    print(fut_data.tail(2)[['Datetime','Close','Trade','Trade End','Supertrend','Supertrend_10_2','RSI','VWAP','WMA_20','Indicator']].to_string(index=False))
    if trade_end!="-":
      if symbol=='NIFTY': nf_signal=trade
      else: nf_signal='-'
      if symbol=='BANKNIFTY': bnf_signal=trade
      else: bnf_signal="-"
      close_vwap_index_trade('VWAP Trade Exit',bnf_signal,nf_signal)
  except Exception as e:
    print('Error in index trade:',symbol,e)

#exit vwap index trade
def close_vwap_index_trade(indicator,bnf_signal="-",nf_signal='-'):
  for i in range(0,len(todays_trade_log)):
    if todays_trade_log['Status'].iloc[i]=="Pending":
      tradingsymbol=todays_trade_log['tradingsymbol'].iloc[i]
      symboltoken=todays_trade_log['symboltoken'].iloc[i]
      qty=todays_trade_log['quantity'].iloc[i]
      producttype=todays_trade_log['producttype'].iloc[i]
      orderid=todays_trade_log['orderid'].iloc[i]
      ltp_price=get_ltp_price(symbol=tradingsymbol,token=symboltoken,exch_seg="NFO")
      if ((bnf_signal=='Sell' and tradingsymbol[-2:]=='CE' and tradingsymbol[:4]=='BANK') or
        (bnf_signal=='Buy' and tradingsymbol[-2:]=='PE' and tradingsymbol[:4]=='BANK') or
        (nf_signal=='Sell' and tradingsymbol[-2:]=='CE' and tradingsymbol[:5]=='NIFTY') or
        (nf_signal=='Buy' and tradingsymbol[-2:]=='PE' and tradingsymbol[:5]=='NIFTY')):
        ordertag=indicator
        ordertag=str(orderid)+" " + ordertag + ' LTP: '+ str(ltp_price)
        place_order(token=symboltoken,symbol=tradingsymbol,qty=qty,buy_sell='SELL',ordertype='STOPLOSS_LIMIT',price=ltp_price,
           variety='STOPLOSS',exch_seg='NFO',producttype=producttype,triggerprice=ltp_price,squareoff=ltp_price, stoploss=ltp_price,
           ordertag=ordertag)
        prt=float(ltp_price)-float(todays_trade_log['price'].iloc[i])
        todays_trade_log['Profit'].iloc[i]=float(prt)*float(todays_trade_log['quantity'].iloc[i])
        trade_info=(todays_trade_log['tradingsymbol'].iloc[i] + '\nBuy: ' + str(todays_trade_log['price'].iloc[i]) +
                    '\nTarget: ' +str(todays_trade_log['Target'].iloc[i])+ ' Stop Loss: ' +str(todays_trade_log['Stop Loss'].iloc[i])+
                    ' LTP:' +str(float(ltp_price))+ '\nBuy Time: '+str(todays_trade_log['updatetime'].iloc[i])+
                    '\nIndicator: ' + str(todays_trade_log['ordertag'].iloc[i])+
                    '\nProfit: ' + str(int(todays_trade_log['Profit'].iloc[i])))
        pl=("Realised:"+str(int(todays_trade_log[(todays_trade_log['Status']=='Closed')]['Profit'].sum())) +
          " Unrealised:"+str(int(todays_trade_log[(todays_trade_log['Status']!='Closed')]['Profit'].sum())))
        todays_trade_log['Status'].iloc[i]="Closed"
        telegram_bot_sendtext("Exit: "+ ordertag +'\n'+ trade_info +'\n'+ pl)

#recheck position exit or not
def recheck_exit_position(tradingsymbol):
  try:
    position=pd.DataFrame(obj.position()['data'])
    position = position[['symboltoken','tradingsymbol','netqty','totalbuyavgprice','totalsellavgprice','ltp']]
    position=position[(position.tradingsymbol==tradingsymbol) & (position.netqty!='0')]
    position_cnt=len(position)
    if position_cnt!=0:
      print("***Cant Exit position of ", tradingsymbol,'Please manually exit.')
    return position_cnt
  except Exception as e:
    print('Error in Recheck exit_position:',e)

#One Hour Index Trend
def index_trend_60min():
  symbol_list=['^NSEBANK','^NSEI']
  msg='One Hour Trend Change '
  for symbol in symbol_list:
    onehour=get_historical_data(symbol=symbol,interval='60m',token="-",exch_seg="-",candle_type="NORMAL")
    #onehour=historical_data_yfna(symbol,'60m')
    recent_candle=onehour.iloc[-1]
    St_Trade=recent_candle['St Trade']
    if St_Trade!="-":
      msg= msg + " " +symbol +" One hour trend change to: " +St_Trade
    time.sleep(2)
  if msg !="One Hour Trend Change ":
    telegram_bot_sendtext(msg)

#Scan Index
def day_index_scanner(interval,remark):
  dat=(datetime.datetime.now(tz=gettz('Asia/Kolkata'))- datetime.timedelta(days=0)).strftime("%m/%d/%y")
  print(dat)
  buy_list,sell_list=[],[]
  remark=''
  interval='60m'
  global buy_list_msg, sell_list_msg
  buy_list_msg=str(remark)+' Buy List- '
  sell_list_msg=str(remark)+' Sell List- '
  symbol_list=['^NSEBANK','^NSEI']
  for i in symbol_list:
    try:
        symbol=i
        stock_name=i
        old_data=get_historical_data(symbol=symbol,interval=interval,token="-",exch_seg="-",candle_type="NORMAL")
        #old_data= historical_data_yfna(i,interval)
        if old_data['St Trade'].iloc[-1]!="-" :
          LTP=int(old_data.loc[-1]['Close'])
          if old_data.loc[-1]['St Trade']=='Buy':
            print("*" + old_data.loc[-1]['St Trade']+ ' '+ stock_name + ' '+ str(LTP))
            buy_list.append(stock_name)
            Supertrend=old_data.loc[-1]['Supertrend']
            buy_list_msg= buy_list_msg + "\n" + "*" + stock_name + " : " + str(LTP) + ' ST:'+ str(Supertrend)
          elif old_data.loc[-1]['St Trade']=='Sell':
            print("*" + old_data.loc[-1]['St Trade']+ ' '+ stock_name + ' '+ str(LTP))
            sell_list.append(stock_name)
            Supertrend=old_data.loc[-1]['Supertrend']
            sell_list_msg= sell_list_msg + "\n" + "*" + stock_name + " : " + str(LTP)+ ' ST:'+ str(Supertrend)
        else:
          old_data=old_data[(old_data['Date']==dat)]
          ll=len(old_data[(old_data['St Trade']=='Buy') | (old_data['St Trade'] =='Sell')])
          if ll!=0:
            for j in old_data.index:
              LTP=int(old_data.loc[j]['Close'])
              if old_data.loc[j]['St Trade']=='Buy':
                print(old_data.loc[j]['St Trade']+ ' '+ stock_name + ' '+ str(LTP))
                buy_list.append(stock_name)
                Supertrend=old_data.loc[j]['Supertrend']
                buy_list_msg= buy_list_msg + "\n" + stock_name + " : " + str(LTP) + ' ST:'+ str(Supertrend)
              elif old_data.loc[j]['St Trade']=='Sell':
                print(old_data.loc[j]['St Trade']+ ' '+ stock_name + ' '+ str(LTP))
                sell_list.append(stock_name)
                Supertrend=old_data.loc[j]['Supertrend']
                sell_list_msg= sell_list_msg + "\n" + stock_name + " : " + str(LTP)+ ' ST:'+ str(Supertrend)
    except Exception as e:
        print('Error in Scan for:',symbol,e)
  if buy_list_msg!=str(remark)+' Buy List- ':
    telegram_bot_sendtext(buy_list_msg)
  if sell_list_msg!=str(remark)+' Sell List- ':
    telegram_bot_sendtext(sell_list_msg)
  print('\nBuy List:',buy_list,'Sell List:',sell_list)

def day_stock_scaner(interval):
  global trade_list
  trade_list=pd.DataFrame()
  ticker_list = symbolDf['YF_Name'].tolist()
  #ticker_list=['TCS.NS','SBIN.NS']
  dat=datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime("%m/%d/%y")
  data=yf.download(tickers=ticker_list,interval=interval,period ='100d',group_by='ticker')
  for i in ticker_list:
    try:
      df=data[i]
      df['Datetime'] = df.index
      df['Datetime']=df['Datetime'].dt.tz_localize(None)
      df['Date']=df['Datetime'].dt.strftime('%m/%d/%y')
      df.index=df['Datetime']
      df['Supertrend']=pdta.supertrend(high=df['High'],low=df['Low'],close=df['Close'],length=7,multiplier=3)['SUPERT_7_3.0']
      df['St Trade']='-'
      for k in range(0,len(df)):
        if df['Close'][k-1]<=df['Supertrend'][k-1] and df['Close'][k]> df['Supertrend'][k]:
          df['St Trade'][k]="Buy"
        elif df['Close'][k-1]>=df['Supertrend'][k-1] and df['Close'][k]< df['Supertrend'][k]:
          df['St Trade'][k]="Sell"
      df=df[(df['Date']==dat)]
      ll=len(df[(df['St Trade']=='Buy') | (df['St Trade'] =='Sell')])
      if ll!=0:
        for j in df.index:
          if df.loc[j]['St Trade']!="-":
            trade_list=trade_list.append({'Stock Name':i.replace('.NS',''),'Time':df.loc[j]['Datetime'],
                'Trade': df.loc[j]['St Trade'],'Close':int(df.loc[j]['Close']),
                'Supertrend':df.loc[j]['Supertrend'],'Interval':interval},ignore_index = True)
    except Exception as e:
      pass
  trade_list=trade_list.round(1)
  trade_list['Stock Name'] = trade_list['Stock Name'].str.replace('&',' And ')
  for trade in ['Buy','Sell']:
    for interval in ['60m','120m']:
      try:
        ndf = trade_list[(trade_list['Interval'] == interval) & (trade_list['Trade'] == trade)]
        if len(ndf)!=0:
          scan_list=dat+" Scan List : " +trade +" "+interval
          for i in ndf.index:
            scan_list=scan_list+"\n"+ndf['Stock Name'].loc[i]+':'+str(ndf['Close'].loc[i])+'/St '+str(ndf['Supertrend'].loc[i])
          print(scan_list)
          telegram_bot_sendtext(scan_list)
      except Exception as e:
        print('Error in Scan for:',e)

def orb_strategy():
  buy_list,sell_list=[],[]
  global buy_list_msg
  global sell_list_msg
  buy_list_msg='Open = Low List-'
  sell_list_msg='Open = High List-'
  for i in symbolDf.index:
      try:
          symbol=symbolDf.loc[i]['symbol']
          token=symbolDf.loc[i]['token']
          stock_name=symbolDf.loc[i]['Revised_Name']
          ltpInfo = obj.ltpData('NSE',symbol,token)
          L=ltpInfo['data']['low']
          H=ltpInfo['data']['high']
          O=ltpInfo['data']['open']
          if O==L:
            buy_list.append(stock_name)
            buy_list_msg= buy_list_msg + stock_name +': ' + str(O) +'\n'
          elif O==H:
            sell_list.append(stock_name)
            sell_list_msg=sell_list_msg+stock_name +': ' + str(O) +'\n'
      except Exception as e:
          print('Error in Scan for:',symbol,e)
  telegram_bot_sendtext(buy_list_msg)
  telegram_bot_sendtext(sell_list_msg)
  print('Buy List:',buy_list,'Sell List:',sell_list)

def get_pivot_level():
  global bnf_P,bnf_S1,bnf_S2,bnf_S3,bnf_R1,bnf_R2,bnf_R3
  global nf_P,nf_S1,nf_S2,nf_S3,nf_R1,nf_R2,nf_R3
  bnf_P,bnf_S1,bnf_S2,bnf_S3,bnf_R1,bnf_R2,bnf_R3=calculate_pivot('BANKNIFTY')
  nf_P,nf_S1,nf_S2,nf_S3,nf_R1,nf_R2,nf_R3=calculate_pivot('NIFTY')
  bnf_P,bnf_S1,bnf_S2,bnf_S3,bnf_R1,bnf_R2,bnf_R3,nf_P,nf_S1,nf_S2,nf_S3,nf_R1,nf_R2,nf_R3

#tril Sl new
def trail_sl_new(symboltoken,tradingsymbol,qty,ltp_price,sl,ordertag='',producttype='CARRYFORWARD'):
  try:
    if isinstance(open_position,str)==True:
      print('No Open Position:',tradingsymbol)
    else:
      position=open_position[(open_position.tradingsymbol==tradingsymbol) & (open_position.netqty!='0')]
      if len(position)!=0:
        cancel_all_order(tradingsymbol)
        place_order(token=symboltoken,symbol=tradingsymbol,qty=qty,buy_sell='SELL',ordertype='STOPLOSS_LIMIT',price=sl,
                        variety='STOPLOSS',exch_seg='NFO',producttype=producttype,triggerprice=sl,squareoff=sl, stoploss=sl,ordertag=ordertag)
        print ('Exit Alert In Option: ' , tradingsymbol,'LTP:',ltp_price,'SL:',sl)
        position_cnt=recheck_exit_position(tradingsymbol)
      else: print('No Open Position : ',tradingsymbol)
  except Exception as e:
    print('Error in trail_sl_new:',e)

def close_trade_alert_send(i,ltp,remark,status):
  tm=datetime.datetime.now(tz=gettz('Asia/Kolkata')).replace(microsecond=0, tzinfo=None)
  todays_trade_log['Sell'][i]=ltp
  todays_trade_log['LTP'][i]=ltp
  todays_trade_log['Status'][i]=str(status)
  prt=int(float(todays_trade_log['Sell'][i]))-int(float(todays_trade_log['price'][i]))
  todays_trade_log['Profit'][i]=prt*int(float(todays_trade_log['quantity'][i]))
  trade_info=(todays_trade_log['tradingsymbol'][i]+
              '\nBuy: ' + str(todays_trade_log['price'][i]) + '\nTarget: ' +str(todays_trade_log['Target'][i])+
              ' Stop Loss: ' +str(todays_trade_log['Stop Loss'][i])+ ' LTP:' +str(todays_trade_log['LTP'][i]) +
              '\nBuy Time: '+str(todays_trade_log['updatetime'][i])+ '\nIndicator: ' + str(todays_trade_log['ordertag'][i])+
              '\nProfit: ' + str(todays_trade_log['Profit'][i]))
  pl=(todays_trade_log['Profit'].sum())
  telegram_bot_sendtext(remark +'\n'+ trade_info+'\nRealised:'+str(pl))
  print(remark +'\n'+ trade_info)

#Trail Stop loss
def trail_sl(symboltoken,tradingsymbol,trade_info,i, ltp,three_candle,f_low):
  if trailing_stop_loss_type=='points':
    sl=ltp-trailing_stop_loss
  else:
    if trailing_stop_loss_type=='three_candle_low':
      sl= three_candle
    elif trailing_stop_loss_type=='previous_candle_low':
      sl=f_low
  if int(sl) < int(ltp) and int(sl) > int(todays_trade_log['Stop Loss'][i]):
    #telegram_bot_sendtext("SL Trail to :"+ str(sl) +"\n" + trade_info)
    print("SL Trail to :"+ str(sl) +"\n" + trade_info)
    todays_trade_log['Stop Loss'][i]=sl

def close_holding():
  dat=(datetime.datetime.now(tz=gettz('Asia/Kolkata'))- datetime.timedelta(days=0)).strftime("%m/%d/%y")
  holdings=obj.holding()['data']
  holdings=pd.DataFrame(holdings)
  for i in holdings.index:
    try:
        time.sleep(1)
        tradingsymbol=holdings.loc[i]['tradingsymbol']
        symboltoken=holdings.loc[i]['symboltoken']
        exch_seg=holdings.loc[i]['exchange']
        #tradingsymbol=tradingsymbol.replace('-EQ','')
        old_data=get_historical_data(symbol=tradingsymbol,interval='60m',token=symboltoken,exch_seg=exch_seg,candle_type="NORMAL")
        #old_data= historical_data_yfna(tradingsymbol+'.NS','60m')
        old_data=old_data[(old_data['Date']==dat)]
        for j in old_data.index:
          if old_data.loc[j]['St Trade']=='Buy':
            telegram_bot_sendtext("Add " + tradingsymbol)
          elif old_data.loc[j]['St Trade']=='Sell':
            telegram_bot_sendtext("Exit " + tradingsymbol)
    except Exception as e:
      print('Error in close_holding for:',tradingsymbol,e)

def one_min_target_check(open_position,bnf_signal,nf_signal):
  close_options_position(open_position,bnf_signal,nf_signal)
  if len(todays_trade_log)!=0 or isinstance(open_position,str)==False :
    if isinstance(open_position,str)!=True :
      for i in open_position.index:
        try:
          symboltoken=open_position.loc[i]['symboltoken']
          tradingsymbol=open_position.loc[i]['tradingsymbol']
          buyprice=open_position.loc[i]['Buy Rate']
          qty=open_position.loc[i]['netqty']
          producttype=open_position.loc[i]['producttype']
          #ltpInfo = obj.ltpData('NFO',tradingsymbol,symboltoken)
          #ltp_price = ltpInfo['data']['ltp']
          ltp_price=get_ltp_price(symbol=tradingsymbol,token=symboltoken,exch_seg="NFO")
          print(tradingsymbol +' ' +str(buyprice) +':' +str(ltp_price)+"*")
          if ((tradingsymbol[-2:]=='CE' and tradingsymbol[:4]=='BANK' and bnf_signal=="Sell") or
              (tradingsymbol[-2:]=='PE' and tradingsymbol[:4]=='BANK' and bnf_signal=="Buy") or
              (tradingsymbol[-2:]=='CE' and tradingsymbol[:4]=='NIFT' and bnf_signal=="Sell") or
              (tradingsymbol[-2:]=='PE' and tradingsymbol[:4]=='NIFT' and bnf_signal=="Buy")):
              exit_position(symboltoken,tradingsymbol,qty,ltp_price,ltp_price,ordertag="Indicator Exit",producttype=producttype)
        except Exception as e:
          print('Error in one_min_target_check:',tradingsymbol,e)
        time.sleep(5)

def supertrend_trail_order(open_position):
  if isinstance(open_position,str)==False and trade_exit=="indicator":
    for i in open_position.index:
      try:
        symboltoken=open_position.loc[i]['symboltoken']
        tradingsymbol=open_position.loc[i]['tradingsymbol']
        buyprice=open_position.loc[i]['Buy Rate']
        qty=open_position.loc[i]['netqty']
        producttype=open_position.loc[i]['producttype']
        option_old_data=get_historical_data(symbol=tradingsymbol,interval="FIVE_MINUTE")
        st=int(option_old_data.iloc[-1]['Supertrend'])-10
        #ltpInfo = int(obj.ltpData('NFO',tradingsymbol,symboltoken)['data']['ltp'])
        ltpInfo=int(get_ltp_price(symbol=tradingsymbol,token=symboltoken,exch_seg="NFO"))
        orderId,orderPrice=get_active_order(tradingsymbol)
        if orderPrice=='NoOrder': orderPrice=1
        if ltpInfo >= st and st > orderPrice :
          exit_position(symboltoken,tradingsymbol,qty,ltpInfo,st,"ST trail",producttype=producttype)
      except Exception as e:
          print('Error in supertrend_trail_order:',e)

def check_target_sl():
  global reload_todays_task
  global order_history,ltp_history
  reload_todays_task=False
  for i in range(0,len(todays_trade_log)):
    reload_todays_task=False
    if todays_trade_log['Status'].iloc[i]=='Pending':
      try:
        time.sleep(1)
        symboltoken=todays_trade_log['symboltoken'].iloc[i]
        tradingsymbol=todays_trade_log['tradingsymbol'].iloc[i]
        producttype=todays_trade_log['producttype'].iloc[i]
        orderid=todays_trade_log['orderid'].iloc[i]
        ltp_price=get_ltp_price(symbol=tradingsymbol,token=symboltoken,exch_seg="NFO")
        ltp=int(ltp_price)
        prt=ltp-int(float(todays_trade_log['price'].iloc[i]))
        todays_trade_log['Profit'].iloc[i]=int(prt*int(float(todays_trade_log['quantity'].iloc[i])))
        todays_trade_log['LTP'].iloc[i]=ltp
        #print(tradingsymbol,ltp,"(",todays_trade_log['Stop Loss'].iloc[i],"/",todays_trade_log['Target'].iloc[i],")")
        if (int(float(ltp_price)) <= int(float(todays_trade_log['Stop Loss'].iloc[i])) or
          int(float(ltp_price)) >= int(float(todays_trade_log['Target'].iloc[i]))):
          reload_todays_task=True
          updatetime=todays_trade_log['updatetime'].iloc[i]
          qty=todays_trade_log['quantity'].iloc[i]
          todays_trade_log['LTP'].iloc[i]=ltp
          indicator=str(todays_trade_log['ordertag'].iloc[i])
          trade_info=(todays_trade_log['tradingsymbol'].iloc[i]+ '\nBuy: ' + str(todays_trade_log['price'].iloc[i])+
                      '\nTarget: ' +str(int(todays_trade_log['Target'].iloc[i]))+ ' Stop Loss: ' +str(int(todays_trade_log['Stop Loss'].iloc[i]))+
                      ' LTP:' +str(todays_trade_log['LTP'].iloc[i]) + '\nBuy Time: '+str(todays_trade_log['updatetime'].iloc[i]) +
                      '\n' + str(todays_trade_log['ordertag'].iloc[i])+'\nProfit:'+str(int(todays_trade_log['Profit'].iloc[i])))
          pl=("Realised:"+str(int(todays_trade_log[(todays_trade_log['Status']=='Closed')]['Profit'].sum())) +
            " Unrealised:"+str(int(todays_trade_log[(todays_trade_log['Status']!='Closed')]['Profit'].sum())))
          if int(ltp_price) <= int(todays_trade_log['Stop Loss'].iloc[i]):
            todays_trade_log['Status'].iloc[i]="Stop Loss Hit"
            orderId,ltp_price=exit_position(symboltoken,tradingsymbol,qty,ltp_price,ltp_price,ordertag=str(orderid)+" Stop Loss Hit LTP: "+str(float(ltp_price)),producttype=producttype)
            if str(orderId)!='Order placement failed': telegram_bot_sendtext("Stop Loss Hit LTP: "+str(float(ltp_price))+ '\n' + trade_info+'\n'+ pl)
          elif int(ltp_price) >= int(todays_trade_log['Target'].iloc[i]):
            todays_trade_log['Status'].iloc[i]="Target Hit"
            orderId,ltp_price=exit_position(symboltoken,tradingsymbol,qty,ltp_price,ltp_price,ordertag=str(orderid)+" Target Hit LTP: "+str(float(ltp_price)),producttype=producttype)
            if str(orderId)!='Order placement failed': telegram_bot_sendtext("Target Hit LTP: "+str(float(ltp_price))+ '\n' + trade_info+'\n'+ pl)
      except Exception as e:
        print('Error in check_target_sl:',e)
  if reload_todays_task==True: get_todays_trade()
  exit_candle_pattern_trade()

def close_todays_trade_log():
  tm=datetime.datetime.now(tz=gettz('Asia/Kolkata')).replace(microsecond=0, tzinfo=None)
  bnf_signal="-"; nf_signal='-'
  global signal_dict
  if signal_dict['BANKNIFTY_15m']=="Sell" or signal_dict['BANKNIFTY_5m']=="Sell": bnf_signal="Sell"
  elif signal_dict['BANKNIFTY_15m']=="Buy" or signal_dict['BANKNIFTY_5m']=="Buy": bnf_signal="Buy"
  if signal_dict['NIFTY_15m']=="Sell" or signal_dict['NIFTY_5m']=="Sell": nf_signal="Sell"
  elif signal_dict['NIFTY_15m']=="Buy" or signal_dict['NIFTY_5m']=="Buy": nf_signal="Buy"
  bnf_indicator=(signal_dict["BANKNIFTY_5m_indicator"]+signal_dict["BANKNIFTY_15m_indicator"]).replace("-",'')
  nf_indicator=(signal_dict["NIFTY_5m_indicator"]+signal_dict["NIFTY_15m_indicator"]).replace("-",'')
  for i in range(0,len(todays_trade_log)):
    if todays_trade_log['Status'].iloc[i]=='Pending':
      try:
        time.sleep(1)
        symboltoken=todays_trade_log['symboltoken'].iloc[i]
        tradingsymbol=todays_trade_log['tradingsymbol'].iloc[i]
        updatetime=todays_trade_log['updatetime'].iloc[i]
        producttype=todays_trade_log['producttype'].iloc[i]
        #ltpInfo = obj.ltpData('NFO',tradingsymbol,symboltoken)
        #ltp_price = ltpInfo['data']['ltp']
        ltp_price=get_ltp_price(symbol=tradingsymbol,token=symboltoken,exch_seg="NFO")
        todays_trade_log['LTP'].iloc[i]=float(ltp_price)
        ltp=float(ltp_price)
        qty=todays_trade_log['quantity'].iloc[i]
        prt=ltp-float(todays_trade_log['price'].iloc[i])
        indicator=str(todays_trade_log['ordertag'].iloc[i])
        todays_trade_log['Profit'].iloc[i]=int(float(prt*float(todays_trade_log['quantity'].iloc[i])))
        trade_info=(todays_trade_log['tradingsymbol'].iloc[i] +'\nBuy: ' + str(todays_trade_log['price'].iloc[i]) +
                      '\nTarget: ' +str(todays_trade_log['Target'].iloc[i])+ ' Stop Loss: ' +str(todays_trade_log['Stop Loss'].iloc[i])+
                      ' LTP:' +str(todays_trade_log['LTP'].iloc[i]) + '\nBuy Time: '+str(todays_trade_log['updatetime'].iloc[i]) +
                      '\n' + str(todays_trade_log['ordertag'].iloc[i])+'\nProfit:'+str(todays_trade_log['Profit'].iloc[i]))
        pl="\nTodays Realised" + str((todays_trade_log['Profit'].sum()))
        if ltp <= int(todays_trade_log['Stop Loss'].iloc[i]):
          todays_trade_log['Status'].iloc[i]="Stop Loss Hit"
          close_trade_alert_send(i,ltp,'Stop Loss Hit',"Exit")
          exit_position(symboltoken,tradingsymbol,qty,ltp_price,ltp_price,ordertag="Stop Loss Hit LTP: " + str(float(ltp_price)),producttype=producttype)
        elif ltp >= int(todays_trade_log['Target'].iloc[i]):
          todays_trade_log['Status'].iloc[i]="Target Hit"
          close_trade_alert_send(i,ltp,'Target Hit',"Exit")
          exit_position(symboltoken,tradingsymbol,qty,ltp_price,ltp_price,ordertag="Target Hit LTP: " + str(float(ltp_price)),producttype=producttype)
        if ((tradingsymbol[-2:]=='CE' and tradingsymbol[:4]=='BANK' and bnf_signal=="Sell") or
            (tradingsymbol[-2:]=='PE' and tradingsymbol[:4]=='BANK' and bnf_signal=="Buy") or
            (tradingsymbol[-2:]=='CE' and tradingsymbol[:4]=='NIFT' and nf_signal=="Sell") or
            (tradingsymbol[-2:]=='PE' and tradingsymbol[:4]=='NIFT' and nf_signal=="Buy")):
          todays_trade_log['Status'].iloc[i]="Indicator Exit"
          exit_position(symboltoken,tradingsymbol,qty,ltp_price,ltp_price,ordertag="Indicator Exit LTP: " + str(float(ltp_price)),producttype=producttype)
          if tradingsymbol[:4]=='BANK': close_trade_alert_send(i,ltp,'Indicator Exit '+bnf_indicator,"Exit")
          elif tradingsymbol[:4]=='NIFT': close_trade_alert_send(i,ltp,'Indicator Exit '+nf_indicator,"Exit")
        elif trailing_stop_loss_type!='No':
          option_old_data=get_historical_data(symbol="-",interval='5m',token=symboltoken,exch_seg="NFO",candle_type="NORMAL")
          #option_old_data=fetch_historical_data(symboltoken,"NFO","FIVE_MINUTE")
          f_low=int(option_old_data['Low'].values[-1])
          s_low=int(option_old_data['Low'].values[-2])
          t_low=int(option_old_data['Low'].values[-3])
          fr_low=int(option_old_data['Low'].values[-4])
          Supertrend=int(option_old_data['Supertrend'].values[-1])
          three_candle=max(min(f_low,s_low,t_low,fr_low),todays_trade_log['Stop Loss'].iloc[i],todays_trade_log['price'].iloc[i])
          if todays_trade_log['Profit'].iloc[i]>=1000 :
            st_price=max(int(option_old_data['Supertrend'].values[-1]),int(option_old_data['Supertrend_10_2'].values[-1]))
            trail_sl(symboltoken,tradingsymbol,trade_info,i, ltp,st_price,st_price)
      except Exception as e:
        print('Error in close_todays_trade_log:',e)

def exit_candle_pattern_trade():
  bnf_ltp=int(get_index_ltp("BANKNIFTY"))
  nf_ltp=int(get_index_ltp("NIFTY"))
  tm=datetime.datetime.now(tz=gettz('Asia/Kolkata')).replace(microsecond=0, tzinfo=None).time()
  #print(tm,"BANKNIFTY:",bnf_ltp,"NIFTY:",nf_ltp)
  for i in range(0,len(todays_trade_log)):
    try:
      if todays_trade_log['Index SL'].iloc[i]!="-" and todays_trade_log['Status'].iloc[i]=='Pending':
        symboltoken=todays_trade_log['symboltoken'].iloc[i]
        tradingsymbol=todays_trade_log['tradingsymbol'].iloc[i]
        qty=todays_trade_log['quantity'].iloc[i]
        orderid=todays_trade_log['orderid'].iloc[i]
        producttype=todays_trade_log['producttype'].iloc[i]
        index_sl=int(todays_trade_log['Index SL'].iloc[i])
        index_ltp=bnf_ltp if tradingsymbol[:4]=='BANK' else nf_ltp
        if ((tradingsymbol[-2:]=='CE' and tradingsymbol[:4]=='BANK' and bnf_ltp < index_sl) or
          (tradingsymbol[-2:]=='PE' and tradingsymbol[:4]=='BANK' and bnf_ltp > index_sl) or
          (tradingsymbol[-2:]=='CE' and tradingsymbol[:4]=='NIFT' and nf_ltp < index_sl) or
          (tradingsymbol[-2:]=='PE' and tradingsymbol[:4]=='NIFT' and nf_ltp > index_sl) or
          (tradingsymbol[-2:]=='CE' and tradingsymbol[:4]=='BANK' and signal_dict['BANKNIFTY_3m']=="Sell") or
          (tradingsymbol[-2:]=='PE' and tradingsymbol[:4]=='BANK' and signal_dict['BANKNIFTY_3m']=="Buy") or
          (tradingsymbol[-2:]=='CE' and tradingsymbol[:4]=='NIFT' and signal_dict['NIFTY_3m']=="Sell") or
          (tradingsymbol[-2:]=='PE' and tradingsymbol[:4]=='NIFT' and signal_dict['NIFTY_3m']=="Buy")):
          ltp_price=get_ltp_price(symbol=tradingsymbol,token=symboltoken,exch_seg="NFO")
          ltp=int(ltp_price)
          todays_trade_log['LTP'].iloc[i]=ltp
          ordertag=str(orderid)+' Index SL Exit ' + str(index_ltp)+' LTP: '+ str(ltp_price)
          cancel_all_order(tradingsymbol)
          place_order(token=symboltoken,symbol=tradingsymbol,qty=qty,buy_sell='SELL',ordertype='STOPLOSS_LIMIT',price=ltp_price,
              variety='STOPLOSS',exch_seg='NFO',producttype=producttype,triggerprice=ltp_price,squareoff=ltp_price, stoploss=ltp_price,
              ordertag=ordertag)
          prt=float(ltp_price)-float(todays_trade_log['price'].iloc[i])
          todays_trade_log['Status'].iloc[i]='Closed'
          todays_trade_log['Profit'].iloc[i]=float(prt)*float(todays_trade_log['quantity'].iloc[i])
          trade_info=(todays_trade_log['tradingsymbol'].iloc[i] + '\nBuy: ' + str(todays_trade_log['price'].iloc[i]) +
                      '\nTarget: ' +str(todays_trade_log['Target'].iloc[i])+ ' Stop Loss: ' +str(todays_trade_log['Stop Loss'].iloc[i])+
                      ' LTP:' +str(float(ltp_price))+ '\nBuy Time: '+str(todays_trade_log['updatetime'].iloc[i])+
                      '\nIndicator: ' + str(todays_trade_log['ordertag'].iloc[i])+ '\nProfit: ' + str(int(todays_trade_log['Profit'].iloc[i])))
          pl=("Realised:"+str(int(todays_trade_log[(todays_trade_log['Status']=='Closed')]['Profit'].sum())) +
              " Unrealised:"+str(int(todays_trade_log[(todays_trade_log['Status']!='Closed')]['Profit'].sum())))
          telegram_bot_sendtext("Exit: "+ ordertag +'\n'+ trade_info +'\n'+ pl)
    except Exception as e:
          print('exit_two_candle_low:',e)

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

def closing_index_trade():
  #global todays_trade_log,bnf_signal,nf_signal
  bnf_signal,nf_signal="-",'-'
  if signal_dict['BANKNIFTY_15m']=="Sell" or signal_dict['BANKNIFTY_5m']=="Sell": bnf_signal="Sell"
  elif signal_dict['BANKNIFTY_15m']=="Buy" or signal_dict['BANKNIFTY_5m']=="Buy": bnf_signal="Buy"
  if signal_dict['NIFTY_15m']=="Sell" or signal_dict['NIFTY_5m']=="Sell": nf_signal="Sell"
  elif signal_dict['NIFTY_15m']=="Buy" or signal_dict['NIFTY_5m']=="Buy": nf_signal="Buy"
  bnf_indicator=(signal_dict["BANKNIFTY_5m_indicator"]+' '+signal_dict["BANKNIFTY_15m_indicator"]).replace("-",'')
  nf_indicator=(signal_dict["NIFTY_5m_indicator"]+' '+signal_dict["NIFTY_15m_indicator"]).replace("-",'')
  if bnf_signal=="Buy" or bnf_signal=="Sell" or nf_signal=="Buy" or nf_signal=="Sell":
    cancel_options_all_order(bnf_signal=bnf_signal,nf_signal=nf_signal)
    close_all_todays_trade(bnf_signal=bnf_signal,nf_signal=nf_signal,bnf_indicator=bnf_indicator,nf_indicator=nf_indicator)
    close_all_position(bnf_signal=bnf_signal,nf_signal=nf_signal,bnf_indicator=bnf_indicator,nf_indicator=nf_indicator)
  if signal_dict['BANKNIFTY_1m']=="Sell" or signal_dict['BANKNIFTY_1m']=="Buy" or signal_dict['NIFTY_1m']=="Sell" or signal_dict['NIFTY_1m']=="Buy" :
    close_one_minute_todays_trade(bnf_signal=signal_dict['BANKNIFTY_1m'],nf_signal=signal_dict['NIFTY_1m'],
                                  bnf_indicator='Indicator Exit',nf_indicator='Indicator Exit')
  exit_candle_pattern_trade()

def day_end_close():
  bnf_indicator="Day End"
  nf_indicator="Day End"
  bnf_signal="Buy"
  nf_signal="Buy"
  cancel_options_all_order(bnf_signal=bnf_signal,nf_signal=nf_signal)
  close_all_todays_trade(bnf_signal=bnf_signal,nf_signal=nf_signal,bnf_indicator=bnf_indicator,nf_indicator=nf_indicator)
  close_all_position(bnf_signal=bnf_signal,nf_signal=nf_signal,bnf_indicator=bnf_indicator,nf_indicator=nf_indicator)

  bnf_signal="Sell"
  nf_signal="Sell"
  cancel_options_all_order(bnf_signal=bnf_signal,nf_signal=nf_signal)
  close_all_todays_trade(bnf_signal=bnf_signal,nf_signal=nf_signal,bnf_indicator=bnf_indicator,nf_indicator=nf_indicator)
  close_all_position(bnf_signal=bnf_signal,nf_signal=nf_signal,bnf_indicator=bnf_indicator,nf_indicator=nf_indicator)

def mark_sl_candle_pattern(Strategy,indexLtp):
  for i in range(0,len(todays_trade_log)):
    if todays_trade_log['Status'][i]=='Pending':
      try:
        if todays_trade_log['ordertag'][i]==Strategy:#"Two Candle Low Strategy":
          todays_trade_log['Index SL'][i]=indexLtp
      except Exception as e:
        print('mark_sl_two_candle_low:',e)

def trail_candle_trade_sl():
  nf_trade=get_historical_data(symbol="^NSEI",interval='5m',token="-",exch_seg="-",candle_type="NORMAL")
  bnf_trade=get_historical_data(symbol="^NSEBANK",interval='5m',token="-",exch_seg="-",candle_type="NORMAL")
  #nf_trade=historical_data_yfna("^NSEI","5m")
  #bnf_trade=historical_data_yfna("^NSEBANK","5m")
  bnf_dump=bnf_trade.tail(4)
  nf_dump=nf_trade.tail(4)
  if index_trail=='three_candle_low':
    bnf_ce_sl=bnf_dump['Low'].min()
    bnf_pe_sl=bnf_dump['High'].max()
    nf_ce_sl=nf_dump['Low'].min()
    nf_pe_sl=nf_dump['High'].max()
  else:
    bnf_ce_sl=bnf_dump['Low'].values[-1]
    bnf_pe_sl=bnf_dump['High'].values[-1]
    nf_ce_sl=nf_dump['Low'].values[-1]
    nf_pe_sl=nf_dump['High'].values[-1]
  for i in range(0,len(todays_trade_log)):
    if todays_trade_log['Status'][i]=='Pending' and todays_trade_log['Time Frame'][i]=="Candle Pattern":
      try:
        tradingsymbol=todays_trade_log['tradingsymbol'][i]
        index_sl=todays_trade_log['Index SL'][i]
        if tradingsymbol[-2:]=='CE' and tradingsymbol[:4]=='BANK' and index_sl < bnf_ce_sl:
          todays_trade_log['Index SL'][i]=bnf_ce_sl
        elif tradingsymbol[-2:]=='PE' and tradingsymbol[:4]=='BANK' and index_sl > bnf_ce_sl:
          todays_trade_log['Index SL'][i]=bnf_pe_sl
        elif tradingsymbol[-2:]=='CE' and tradingsymbol[:4]=='NIFT' and index_sl < nf_ce_sl:
          todays_trade_log['Index SL'][i]=nf_ce_sl
        elif tradingsymbol[-2:]=='PE' and tradingsymbol[:4]=='NIFT' and index_sl > nf_pe_sl:
          todays_trade_log['Index SL'][i]=nf_pe_sl
      except Exception as e:
        print('trail_candle_trade_sl:',e)

def one_candle_low(symbol,fut_data):
  close=float(fut_data['Close'].values[-1])
  open=float(fut_data['Open'].values[-1])
  low=float(fut_data['Low'].values[-1])
  high=max(float(fut_data['High'].values[-1]),float(fut_data['High'].values[-2]))
  active_trade_count=len(todays_trade_log[(todays_trade_log['Status'] == 'Pending') & (todays_trade_log['ordertag'] == 'One Candle Low Strategy')])
  if open > close and active_trade_count==0:
    #trade=historical_data_yfna(symbol,"1m")
    #indexLtp=trade_one_min.iloc[-1]['Open']
    indexLtp=get_index_ltp(symbol)
    if indexLtp < low:
      indexLtp, ce_strike_symbol,pe_strike_symbol=get_ce_pe_data(symbol,indexLtp=indexLtp)
      buy_option(pe_strike_symbol,"One Candle Low Strategy","Candle Pattern",index_sl=high)
      mark_sl_candle_pattern(Strategy="One Candle Low Strategy",indexLtp=high)

def orb_trade(fut_data,interval,symbol,one_min_data):
  try:
    if orb_dict['BANKNIFTY_15m_high']!="-":
      ORBO_count=len(todays_trade_log[(todays_trade_log['Strategy'] == 'ORBO '+symbol+' '+interval)])
      ORBD_count=len(todays_trade_log[(todays_trade_log['Strategy'] == 'ORBD '+symbol+' '+interval)])
      high=float(orb_dict[symbol+"_"+interval+'_high'])
      low=float(orb_dict[symbol+"_"+interval+'_low'])
      target=banknifty_target if symbol=="BANKNIFTY" else nifty_target
      sl=banknifty_sl if symbol=="BANKNIFTY" else nifty_sl
      if one_min_data['Close'].values[-2]>=low and one_min_data['Close'].values[-1]<low and ORBD_count==0:
      #if fut_data['Close'].values[-2]>=low and indexLtp<low and ORBD_count==0:
        indexLtp, ce_strike_symbol,pe_strike_symbol=get_ce_pe_data(symbol,indexLtp=one_min_data['Close'].values[-1])
        buy_option(pe_strike_symbol,'ORBD '+symbol+' '+interval,"Candle Pattern",index_sl=high)
        mark_sl_candle_pattern(Strategy='ORBD '+symbol+' '+interval,indexLtp=high)
      elif one_min_data['Close'].values[-2]<=high and one_min_data['Close'].values[-1]>high and ORBO_count==0:
      #elif fut_data['Close'].values[-2]<=high and indexLtp>high and ORBO_count==0:
        indexLtp, ce_strike_symbol,pe_strike_symbol=get_ce_pe_data(symbol,indexLtp=one_min_data['Close'].values[-1])
        buy_option(ce_strike_symbol,'ORBO '+symbol+' '+interval,"Candle Pattern",index_sl=low)
        mark_sl_candle_pattern(Strategy='ORBO '+symbol+' '+interval,indexLtp=low)
  except Exception as e:
      print('Error in ORBD Trade:',e)

def mark_orb():
  try:
    global orb_dict
    dt=datetime.datetime.now().date().strftime('%m/%d/%y')
    orb_dict = {"NIFTY_5m_high": "-", "NIFTY_5m_low": "-","NIFTY_15m_high":"-","NIFTY_15m_low":"-",
              "BANKNIFTY_5m_high": "-", "BANKNIFTY_5m_low": "-","BANKNIFTY_15m_high":"-","BANKNIFTY_15m_low":"-"}
    for symbol in ['^NSEBANK','^NSEI']:
      n_symbol="NIFTY" if symbol=="^NSEI" else "BANKNIFTY"
      trade=get_historical_data(symbol=symbol,interval='5m',token="-",exch_seg="-",candle_type="NORMAL")
      #trade=historical_data_yfna(symbol,"5m")
      trade=trade[(trade['Date']==dt)].head(3)
      orb_dict[n_symbol + "_5m_low"] = trade.iloc[0]['Low']
      orb_dict[n_symbol + "_5m_high"] = trade.iloc[0]['High']
      orb_dict[n_symbol + "_15m_low"] = trade['Low'].min()
      orb_dict[n_symbol + "_15m_high"] = trade['High'].max()
    print(orb_dict)
  except Exception as e:
    orb_dict = {"NIFTY_5m_high": "-", "NIFTY_5m_low": "-","NIFTY_15m_high":"-","NIFTY_15m_low":"-",
              "BANKNIFTY_5m_high": "-", "BANKNIFTY_5m_low": "-","BANKNIFTY_15m_high":"-","BANKNIFTY_15m_low":"-"}
    print('Error in mark_orb:',e)

def pnl_check():
  try:
    print('Profit Till Now: ',pnl)
    if pnl <=pnl_sl: telegram_bot_sendtext("Account Stop Loss Limit Crossed, Please close all position. its Bad day")
    elif pnl > pnl_tgt: telegram_bot_sendtext("Account Day Target Hit, Please close all position. its Good day")
  except Exception as e:
      print('Error in PNL Check:',e)

def two_candle_strategy(future_token,interval='3m'):
  df=get_historical_data(interval=interval,token=future_token['token'],exch_seg=future_token['exch_seg'],candle_type="NORMAL")
  df['Volume']=df['Volume']*int(future_token['lotsize'])
  return df

def close_position_indicator(interval,indicator,signal):
  for i in range(0,len(todays_trade_log)):
    ordertag=todays_trade_log['ordertag'][i]
    if interval in ordertag and indicator in ordertag and todays_trade_log['Status'][i]=="Pending" and signal not in ordertag:
      print(todays_trade_log.iloc[i])

def ganesh_sl_trail():
  global todays_trade_log
  for i in range(0,len(todays_trade_log)):
    if todays_trade_log['Status'].iloc[i]=="Pending":
      try:
        ordertag=todays_trade_log['ordertag'].iloc[i]
        symbol=todays_trade_log['tradingsymbol'].iloc[i]
        token=todays_trade_log['symboltoken'].iloc[i]
        exchange=todays_trade_log['exchange'].iloc[i]
        price=float(todays_trade_log['price'].iloc[i])
        if "1m" in todays_trade_log['ordertag'].iloc[i]: interval="1m"
        elif "5m" in todays_trade_log['ordertag'].iloc[i]: interval="5m"
        else: interval="15m"
        old_data=get_historical_data(symbol=symbol,interval=interval,token=token,exch_seg=exchange,candle_type="NORMAL")
        st_10_2=float(old_data['Supertrend_10_2'].iloc[-1])
        st_7_3=float(old_data['Supertrend'].iloc[-1])
        ema_low=float(old_data['EMA_Low'].iloc[-1])
        close_price=float(old_data['Close'].iloc[-1])
        old_sl=todays_trade_log['Stop Loss'].iloc[i]
        if st_7_3 < close_price: todays_trade_log['Stop Loss'].iloc[i]=st_7_3
        elif st_10_2 < close_price: todays_trade_log['Stop Loss'].iloc[i]=st_10_2
        else: todays_trade_log['Stop Loss'].iloc[i]=float(max(price,close_price)*0.7)
      except Exception as e:
        print(e)

def trail_sl_treading():
  now_time=datetime.datetime.now(tz=gettz('Asia/Kolkata'))
  while now_time<=market_close:
    time.sleep(10)
    ganesh_sl_trail()
    now_time=datetime.datetime.now(tz=gettz('Asia/Kolkata'))
    time.sleep(60-now_time.second+1)
  print("Trail SL Completed")

def my_loop_threading(symbol,time_frame):
  now_time=datetime.datetime.now(tz=gettz('Asia/Kolkata'))
  while now_time<=intraday_close:
    now_time=datetime.datetime.now(tz=gettz('Asia/Kolkata'))
    if now_time.minute%time_frame==0 and now_time>=market_open:
      trade=index_trade(symbol,str(time_frame)+'m')
      now_time=datetime.datetime.now(tz=gettz('Asia/Kolkata'))
    time.sleep(60-now_time.second+1)
  print(symbol,time_frame,"Completed")

def my_near_option_threading(time_frame):
  now_time=datetime.datetime.now(tz=gettz('Asia/Kolkata'))
  while now_time<=intraday_close:
    now_time=datetime.datetime.now(tz=gettz('Asia/Kolkata'))
    if now_time.minute%time_frame==0 and now_time>=market_open:
      print(now_time.time().replace(microsecond=0, tzinfo=None),"Near Option",time_frame)
      trade_near_options(time_frame)
      now_time=datetime.datetime.now(tz=gettz('Asia/Kolkata'))
    time.sleep(60-now_time.second+1)
  print('Near Options',time_frame,"Completed")

def my_thread_function():
  now_time=datetime.datetime.now(tz=gettz('Asia/Kolkata'))
  while now_time<=market_close:
    check_target_sl()
    now_time=datetime.datetime.now(tz=gettz('Asia/Kolkata'))
    time.sleep(5)
  print("Check SL Target Completed")

def main_threading_function():
  now_time=datetime.datetime.now(tz=gettz('Asia/Kolkata'))
  print("Main Threading started")
  while now_time<=market_close:
    time.sleep(5)
    get_open_position()
    get_todays_trade()
    #closing_index_trade()
    now_time=datetime.datetime.now(tz=gettz('Asia/Kolkata'))
    #trail_sl_with_atr()
    if now_time.minute==22: send_status(); pnl_check()
    print_ltp()
    time.sleep((60-now_time.second+1)-2)
  print("Main Threading Completed")

def threading_loop():
  thread1 = threading.Thread(target=my_loop_threading, name="NIFTY_5M",args=("^NSEI",5,))
  thread2 = threading.Thread(target=my_loop_threading, name="BANKNIFTY_5M",args=("^NSEBANK",5,))
  thread3 = threading.Thread(target=my_loop_threading, name="NIFTY_15M",args=("^NSEI",15,))
  thread4 = threading.Thread(target=my_loop_threading, name="BANKNIFTY_15M",args=("^NSEBANK",15,))
  thread5 = threading.Thread(target=my_near_option_threading, name="NEAR_OPTION_1M",args=(1,))
  thread6 = threading.Thread(target=my_near_option_threading, name="NEAR_OPTION_5M",args=(5,))
  thread7 = threading.Thread(target=main_threading_function,name="MAIN_FUNCTION")
  t = threading.Thread(target=my_thread_function,name="CHECK_SL_TGT")

  thread1.start()
  thread2.start()
  thread3.start()
  thread4.start()
  #thread5.start()
  thread6.start()
  thread7.start()
  t.start()

  thread1.join()
  thread2.join()
  thread3.join()
  thread4.join()
  #thread5.join()
  thread6.join()
  thread7.join()
  t.join()
  print ("Completed")

def sub_loop_code(now_time):
  global signal_dict,orb_dict,orderbook,open_position
  if (now_time.minute%5==0 and five_m_timeframe=='Yes'):
    signal_dict = {"NIFTY_1m": "-", "NIFTY_3m": "-","NIFTY_5m":"-","NIFTY_15m":"-","BANKNIFTY_1m": "-","BANKNIFTY_3m":"-", "BANKNIFTY_5m":"-",
                      "BANKNIFTY_15m":"-","NIFTY_1m_indicator": "-", "NIFTY_3m_indicator": "-","NIFTY_5m_indicator":"-","NIFTY_15m_indicator":"-",
                      "BANKNIFTY_1m_indicator": "-","BANKNIFTY_3m_indicator":"-", "BANKNIFTY_5m_indicator":"-","BANKNIFTY_15m_indicator":"-"}
    bnf_trade=index_trade('BANKNIFTY','5m')
    nf_trade=index_trade('NIFTY','5m')
    trade_near_options(5)
  if (now_time.minute%3==0 and three_m_timeframe=='Yes'):
    nf_trade_3_min=index_trade(symbol=nf_future['symbol'],interval="3m",candle_type="NORMAL",token=nf_future['token'],exch_seg=nf_future['exch_seg'])
    bnf_trade_3_min=index_trade(symbol=bnf_future['symbol'],interval="3m",candle_type="NORMAL",token=bnf_future['token'],exch_seg=bnf_future['exch_seg'])
  if (now_time.minute%15==0 and fifteen_m_timeframe=='Yes'):
    bnf_trade_15_min=index_trade('BANKNIFTY','15m')
    nf_trade_15_min=index_trade('NIFTY','15m')
  if one_m_timeframe=="Yes":
    bnf_trade_1_min=index_trade('BANKNIFTY','1m')
    nf_trade_1_min=index_trade('NIFTY','1m')
  get_open_position()
  get_todays_trade()
  #closing_index_trade()
  #ganesh_sl_trail()
  if now_time.minute==22: send_status(); pnl_check()
  print_ltp()
  #while datetime.now(tz=gettz('Asia/Kolkata')).second <=40 and len(todays_trade_log[todays_trade_log['Status'] == 'Pending'])>0:
  #  check_target_sl()
  #print('----------------------------------------')

#Loop code
def loop_code():
  now = datetime.datetime.now(tz=gettz('Asia/Kolkata'))
  marketclose = now.replace(hour=14, minute=55, second=0, microsecond=0)
  marketopen = now.replace(hour=0, minute=5, second=0, microsecond=0)
  get_todays_trade()
  first_trade_new()
  tm=datetime.datetime.now(tz=gettz('Asia/Kolkata')).replace(microsecond=0, tzinfo=None)
  t = threading.Thread(target=my_thread_function,name="CHECK_SL_TGT")
  t.start()
  while now < marketclose and  now  > marketopen:
    try:
      now_time=datetime.datetime.now(tz=gettz('Asia/Kolkata'))
      print('\n',now_time.time().replace(microsecond=0, tzinfo=None))
      sub_loop_code(now_time)
      now=datetime.datetime.now(tz=gettz('Asia/Kolkata'))
      time.sleep(60-now.second+2)
    except Exception as e:
      print('Error in Loop:',e)
      now=datetime.datetime.now(tz=gettz('Asia/Kolkata'))
      time.sleep(60-now.second+1)
  print ('Bye... Intraday Market Closed')
  closing_trade()

st.header(f"Welcome {st.session_state['user_name']}!!!")
st.write(st.session_state['login_time'])
current_time=st.empty()
c1,c2=st.columns([2,8])
with c1:
   col1, col2 = st.columns(2)
   with col1:
      nf_ce=st.button(label="NF CE")
      bnf_ce=st.button(label="BNF CE")
   with col2:
      nf_pe=st.button(label="NF PE")
      bnf_pe=st.button(label="BNF PE")
with c2:
   st.table(pd.DataFrame(numpy.random.randn(10, 20), columns=("col %d" % i for i in range(20))))
if nf_ce:manual_buy("NIFTY",ce_pe="CE",index_ltp="-")
if nf_pe:manual_buy("NIFTY",ce_pe="PE",index_ltp="-")
if bnf_ce:manual_buy("BANKNIFTY",ce_pe="CE",index_ltp="-")
if bnf_pe:manual_buy("BANKNIFTY",ce_pe="PE",index_ltp="-")
get_ltp=st.button("Get LTP")
if get_ltp:
   print_ltp()
