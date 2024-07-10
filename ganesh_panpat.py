import streamlit as st
import numpy
import requests
import datetime
from dateutil.tz import gettz
import pandas as pd
from SmartApi.smartConnect import SmartConnect
import pyotp
from logzero import logger
import pandas_ta as pdta
import warnings
import yfinance as yf
import time
warnings.filterwarnings('ignore')
NoneType = type(None)
import math
st.set_page_config(page_title="Algo App",layout="wide",initial_sidebar_state="expanded",)
st.markdown("""
  <style>
    .block-container {padding-top: 0.9rem;padding-bottom: 0rem;padding-left: 2rem;padding-right: 5rem;}
  </style>
  """, unsafe_allow_html=True)
st.title("Welcome To Algo Trading")
if 'Logged_in' not in st.session_state:st.session_state['Logged_in']="Guest"
if 'login_time' not in st.session_state:st.session_state['login_time']="login_time"
if 'last_check' not in st.session_state:st.session_state['last_check']="last_check"
if 'bnf_expiry_day' not in st.session_state: st.session_state['bnf_expiry_day']=None
if 'nf_expiry_day' not in st.session_state: st.session_state['nf_expiry_day']=None
if 'fnnf_expiry_day' not in st.session_state: st.session_state['fnnf_expiry_day']=None
if 'sensex_expiry_day' not in st.session_state: st.session_state['sensex_expiry_day']=None
if 'opt_list' not in st.session_state:st.session_state['opt_list']=[]
if 'fut_list' not in st.session_state:st.session_state['fut_list']=[]
if 'options_trade_list' not in st.session_state:st.session_state['options_trade_list']=[]
if 'stop_loss' not in st.session_state:st.session_state['stop_loss']={}
if 'target_list' not in st.session_state:st.session_state['target_list']={}
if 'index_trade_end' not in st.session_state:st.session_state['index_trade_end']={}
if 'todays_trade' not in st.session_state:st.session_state['todays_trade']=[]
if 'orderbook' not in st.session_state:st.session_state['orderbook']=[]
if 'pending_orders' not in st.session_state:st.session_state['pending_orders']=[]
if 'near_opt_df' not in st.session_state:st.session_state['near_opt_df']=[]

def get_token_df():
  url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
  d = requests.get(url).json()
  token_df = pd.DataFrame.from_dict(d)
  token_df['expiry'] = pd.to_datetime(token_df['expiry']).apply(lambda x: x.date())
  token_df = token_df.astype({'strike': float})
  now_dt=datetime.datetime.now(tz=gettz('Asia/Kolkata')).date()-datetime.timedelta(days=0)
  token_df=token_df[token_df['expiry']>=now_dt]
  bnf_expiry_day = (token_df[(token_df['name'] == 'BANKNIFTY') & (token_df['instrumenttype'] == 'OPTIDX')])['expiry'].min()
  nf_expiry_day = (token_df[(token_df['name'] == 'NIFTY') & (token_df['instrumenttype'] == 'OPTIDX')])['expiry'].min()
  fnnf_expiry_day = (token_df[(token_df['name'] == 'FINNIFTY') & (token_df['instrumenttype'] == 'OPTIDX')])['expiry'].min()
  sensex_expiry_day = (token_df[(token_df['name'] == 'SENSEX') & (token_df['instrumenttype'] == 'OPTIDX')])['expiry'].min()
  st.session_state['bnf_expiry_day']=bnf_expiry_day
  st.session_state['nf_expiry_day']=nf_expiry_day
  st.session_state['fnnf_expiry_day']=fnnf_expiry_day
  st.session_state['sensex_expiry_day']=sensex_expiry_day
  opt_list=token_df[((token_df['name'] == 'BANKNIFTY') & (token_df['expiry'] == bnf_expiry_day) |
                   (token_df['name'] == 'NIFTY') & (token_df['expiry'] == nf_expiry_day) |
                   (token_df['name'] == 'FINNIFTY') & (token_df['expiry'] == fnnf_expiry_day) |
                   (token_df['name'] == 'SENSEX') & (token_df['expiry'] == sensex_expiry_day))]
  st.session_state['opt_list']=opt_list
  fut_token=token_df[(token_df['instrumenttype'] == 'FUTIDX') | (token_df['instrumenttype'] == 'FUTCOM')]
  fut_list=['BANKNIFTY','NIFTY','SILVERMIC','SILVER']
  fut_token = fut_token[fut_token['name'].isin(fut_list)]
  fut_token = fut_token.sort_values(by = ['name', 'expiry'], ascending = [True, True], na_position = 'first')
  st.session_state['fut_list']=fut_token
if st.session_state['bnf_expiry_day']==None:get_token_df()
tab0, tab1, tab2, tab3, tab4, tab5, tab6, tab7,tab8, tab9, tab10= st.tabs(["Log","Order Book", "Position","Todays Trade","Open Order", "Settings",
                                                                    "Token List","Future List","GTT Orders",'Back Test','Near Options'])
with tab0:
  login_details=st.empty()
  login_details.text(f"Welcome:{st.session_state['Logged_in']} Login:{st.session_state['login_time']} Last Check:{st.session_state['last_check']}")
  index_ltp_string=st.empty()
  index_ltp_string.text(f"Index Ltp: ")
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
    trade_info=st.empty()
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
  todays_trade_updated=st.empty()
  todays_trade_updated.text(f"Todays Trade : ")
  todays_trade_datatable=st.empty()
  sl_container=st.empty()
  sl_container.text(f"Trail SL : ")
with tab4:
  open_order_updated=st.empty()
  open_order_updated.text(f"Open Order : ")
  open_order=st.empty()
with tab5:
  ind_col1,ind_col2,ind_col3,ind_col4=st.columns([5,1.5,1.5,1.5])
  indicator_list=['ST_7_3 Trade', 'ST_10_2 Trade','ST_10_1 Trade', 'RSI MA Trade','RSI_60 Trade','MACD Trade','PSAR Trade','DI Trade',
                  'MA Trade','EMA Trade','EMA_5_7 Trade','MA 21 Trade','HMA Trade','RSI_60 Trade','EMA_High_Low Trade','Two Candle Theory',
                  'TEMA_EMA_9 Trade','Multi Time ST Trade']
  with ind_col1:
    index_list=st.multiselect('Select Index',['NIFTY','BANKNIFTY','SENSEX'],['NIFTY','BANKNIFTY','SENSEX'])
    time_frame_interval = st.multiselect('Select Time Frame',['IDX:5M', 'IDX:15M','IDX:1M', 'OPT:5M', 'OPT:1M','GTT:5M'],['IDX:5M','OPT:5M','OPT:1M','GTT:5M'])
    five_buy_indicator = st.multiselect('5M Indicator',indicator_list,['ST_7_3 Trade', 'ST_10_2 Trade'])
    five_opt_buy_indicator = st.multiselect('5M OPT Indicator',indicator_list,['ST_7_3 Trade', 'ST_10_2 Trade'])
    gtt_indicator=st.multiselect('GTT Indicator',['5M_ST','5M_ST_10_2','1M_10_1','1M_10_2'],['5M_ST','5M_ST_10_2'])
    one_buy_indicator = st.multiselect('1M Indicator',indicator_list,[])
    one_opt_buy_indicator = st.multiselect('1M OPT Indicator',indicator_list,['ST_7_3 Trade','TEMA_EMA_9 Trade'])
    fifteen_buy_indicator = st.multiselect('15M Indicator',indicator_list,[])
    three_buy_indicator = st.multiselect('3M Indicator',indicator_list,[])
    fut_list=st.multiselect('Select Future',['SILVERMIC','SILVER'],[])
    with ind_col2:
      target_order_type = st.selectbox('Target Order',('Target', 'Stop_Loss', 'NA'),1)
      target_type = st.selectbox('Target Type',('Points', 'Per Cent','Indicator','ATR'),1)
      if target_type=="ATR":
        sl_point=st.number_input(label="SL",min_value=1, max_value=100, value=3, step=None)
        target_point=st.number_input(label="Target",min_value=1, max_value=100, value=3, step=None)
      elif target_type!="Per Cent":
        sl_point=st.number_input(label="SL",min_value=1, max_value=100, value=30, step=None)
        target_point=st.number_input(label="Target",min_value=1, max_value=100, value=50, step=None)
      elif target_type!="Indicator":
        sl_point=st.number_input(label="SL",min_value=1, max_value=100, value=30, step=None)
        target_point=st.number_input(label="Target",min_value=1, max_value=100, value=50, step=None)
    with ind_col3:
      lots_to_trade=st.number_input(label="Lots To Trade",min_value=1, max_value=10, value=1, step=None)
    with ind_col4:
      st.date_input("BNF Exp",st.session_state['bnf_expiry_day'])
      st.date_input("NF Exp",st.session_state['nf_expiry_day'])
      st.date_input("FIN NF Exp",st.session_state['fnnf_expiry_day'])
      st.date_input("SENSEX Exp",st.session_state['sensex_expiry_day'])
with tab6:
    token_df=st.empty()
    token_df=st.dataframe(st.session_state['opt_list'],hide_index=True)
with tab7:
    fut_token_df=st.empty()
    fut_token_df=st.dataframe(st.session_state['fut_list'],hide_index=True)
with tab8:
  gtt_order_updated=st.empty()
  gtt_order_updated.text(f"GTT Open Order : ")
  gtt_order_datatable=st.empty()
with tab9:
  backtest=st.button(label="Back Test")
with tab10:
  near_opt_updated=st.empty()
  near_opt_updated.text(f"Near Option Updated : ")
  near_opt_df=st.empty()
  near_opt_df=st.dataframe(st.session_state['near_opt_df'],hide_index=True)


def telegram_bot_sendtext(bot_message):
  BOT_TOKEN = '5051044776:AAHh6XjxhRT94iXkR4Eofp2PPHY3Omk2KtI'
  BOT_CHAT_ID = '-1001542241163'
  BOT_CHAT_ONE_MINUTE='-882387563'
  if 'TEMA_EMA_9 Trade' in bot_message and "BANKNIFTY" in bot_message:BOT_CHAT_ID=BOT_CHAT_ONE_MINUTE
  try:
    bot_message=st.session_state['Logged_in']+':\n'+bot_message
    send_text = 'https://api.telegram.org/bot' + BOT_TOKEN + '/sendMessage?chat_id=' + BOT_CHAT_ID + \
                  '&parse_mode=HTML&text=' + bot_message
    response = requests.get(send_text)
  except Exception as e: pass

user='Ganesh'; username = 'G93179'; pwd = '4789'; apikey = 'Rz6IiOsd'; token='U4EAZJ3L44CNJHNUZ56R22TPKI'
obj = SmartConnect(apikey)
totp = pyotp.TOTP(token).now()
correlation_id = "abcde"
data = obj.generateSession(username, pwd, totp)
if data['status'] == False:logger.error(data)
else:
  authToken = data['data']['jwtToken']
  refreshToken = data['data']['refreshToken']
  feedToken = obj.getfeedToken()
  res = obj.getProfile(refreshToken)
  obj.generateToken(refreshToken)
  userProfile= obj.getProfile(refreshToken)
  aa= userProfile.get('data')
  login_name=aa.get('name').title()
  st.session_state['Logged_in']=login_name.split()[0]
  st.session_state['login_time']=datetime.datetime.now(tz=gettz('Asia/Kolkata')).replace(microsecond=0).time()
  st.session_state['last_check']=datetime.datetime.now(tz=gettz('Asia/Kolkata')).replace(microsecond=0).time()

#Order
def place_order(token,symbol,qty,buy_sell,ordertype='MARKET',price=0,variety='NORMAL',exch_seg='NFO',producttype='CARRYFORWARD',
                triggerprice=0,squareoff=0,stoploss=0,ordertag='-'):
  try:
    orderparams = {"variety": variety,"tradingsymbol": symbol,"symboltoken": token,"transactiontype": buy_sell,"exchange": exch_seg,
      "ordertype": ordertype,"producttype": producttype,"duration": "DAY","price": int(float(price)),"squareoff":int(float(squareoff)),
      "stoploss": int(float(stoploss)),"quantity": str(qty),"triggerprice":int(float(triggerprice)),"ordertag":ordertag,"trailingStopLoss":5}
    orderId=obj.placeOrder(orderparams)
    return orderId
  except Exception as e:
    logger.info(f"error in place_order Order placement failed: {e}")
    orderId='Order placement failed'
    telegram_bot_sendtext(f'{buy_sell} Order placement failed : {symbol}')
    return orderId
  
def modify_order(variety,orderid,ordertype,producttype,price,quantity,tradingsymbol,symboltoken,exchange,triggerprice=0,squareoff=0,stoploss=0):
  try:
    modifyparams = {"variety": variety,"orderid": orderid,"ordertype": ordertype,"producttype": producttype,
                    "duration": "DAY","price": price,"quantity": quantity,"tradingsymbol":tradingsymbol,
                    "symboltoken":symboltoken,"exchange":exchange,"squareoff":squareoff,"stoploss": stoploss,"triggerprice":triggerprice}
    obj.modifyOrder(modifyparams)
  except Exception as e:
    logger.info(f"error in modify_order: {e}")

def cancel_order(orderID,variety):
  try:
    obj.cancelOrder(orderID,variety=variety)
  except Exception as e:
    logger.info(f"Error cancel_order: {e}")

def cancel_all_order(symbol):
  try:
    orderbook,pending_orders=get_order_book()
    if isinstance(orderbook,NoneType)!=True:
      orderlist = orderbook[(orderbook['tradingsymbol'] == symbol) &
                            ((orderbook['orderstatus'] != 'complete') & (orderbook['orderstatus'] != 'cancelled') &
                              (orderbook['orderstatus'] != 'rejected') & (orderbook['orderstatus'] != 'AMO CANCELLED'))]
      orderlist_a = orderbook[(orderbook['tradingsymbol'] == symbol) & (orderbook['variety'] == 'ROBO') &
                              (orderbook['transactiontype'] == 'BUY') & (orderbook['orderstatus'] == 'complete')]
      orderlist=pd.concat([orderlist,orderlist_a])
      for i in range(0,len(orderlist)):
        cancel_order(orderlist.iloc[i]['orderid'],orderlist.iloc[i]['variety'])
  except Exception as e:
    logger.info(f"Error cancel_all_order: {e}")

#LTP
def get_yf_ltp(symbol="-",token="-",exch_seg='-'):
  try:
    data=yf.Ticker(symbol).history(interval='1m',period='1d')
    return round(float(data['Close'].iloc[-1]),2)
  except Exception as e:
    logger.info(f"error in get_yf_ltp: {e}")
    return "Unable to get LTP"
  
def get_angel_ltp(symbol="-",token="-",exch_seg='-'):
    try:
      return obj.getMarketData("LTP",{exch_seg:[token]})['data']['fetched'][0]['ltp']
    except Exception as e:
        try:
            return obj.ltpData(exch_seg,symbol,token)['data']['ltp']
        except Exception as e: return "Unable to get LTP"

def get_ltp_price(symbol="-",token="-",exch_seg='-'):
  try:
    symbol_i="-";ltp="Unable to get LTP"
    if symbol=="BANKNIFTY" or symbol=="^NSEBANK": symbol_i="^NSEBANK";token='99926009';exch_seg='NSE'
    elif symbol=="NIFTY" or symbol=="^NSEI": symbol_i="^NSEI";token='99926000';exch_seg='NSE'
    elif symbol=="SENSEX" or symbol=="^BSESN": symbol_i="^BSESN";token='99919000';exch_seg='BSE'
    if symbol_i!="-":ltp=get_yf_ltp(symbol=symbol_i,token=token,exch_seg=exch_seg)
    if ltp=="Unable to get LTP":ltp=get_angel_ltp(symbol=symbol,token=token,exch_seg=exch_seg)
    return ltp
  except Exception as e:
    logger.info(f"error in get_ltp_price: {e}")
    return "Unable to get LTP"
  
def print_ltp():
  try:
    data=pd.DataFrame(obj.getMarketData(mode="OHLC",exchangeTokens={"NSE": ["99926000","99926009"],"BSE": ['99919000']})['data']['fetched'])
    data['change']=data['ltp']-data['close']
    data.sort_values(by=['tradingSymbol'], inplace=True)
    print_sting=datetime.datetime.now(tz=gettz('Asia/Kolkata')).replace(microsecond=0, tzinfo=None).time()
    for i in range(0,len(data)):
      print_sting=f"{print_sting} {data.iloc[i]['tradingSymbol']} {int(data.iloc[i]['ltp'])}({int(data.iloc[i]['change'])})"
    print_sting=print_sting.replace("Nifty 50","Nifty")
    print_sting=print_sting.replace("Nifty Bank","BankNifty")
    return print_sting
  except Exception as e:
    logger.info(f"error in print_ltp: {e}")
    return None

# Tradebook,Get Order Book and Historical Data
def get_open_position():
  try:
    position=obj.position()
    if position['status']==True and position['data'] is not None:
      position=position['data']
      position=pd.DataFrame(position)
      position[['realised', 'unrealised']] = position[['realised', 'unrealised']].astype(float)
      pnl=int(position['realised'].sum())+float(position['unrealised'].sum())
      open_position = position[(position['netqty'] > '0') & (position['instrumenttype'] == 'OPTIDX')]
      if len(open_position)==0:open_position=None
      position_datatable.dataframe(position[['tradingsymbol',"totalbuyavgprice","totalsellavgprice","netqty",'realised', 'unrealised','ltp']],hide_index=True)
      position_updated.text(f"PNL : {datetime.datetime.now(tz=gettz('Asia/Kolkata')).time().replace(microsecond=0)}: {pnl}")
      return position,open_position
    else:
      position_updated.text(f"No Open Position : {datetime.datetime.now(tz=gettz('Asia/Kolkata')).time().replace(microsecond=0)}")
      return None,None
  except Exception as e:
    position_updated.text(f"error in get_open_position : {datetime.datetime.now(tz=gettz('Asia/Kolkata')).time().replace(microsecond=0)}")
    logger.info(f"error in get_open_position: {e}")
    return None,None

def get_order_book():
  try:
    orderbook=obj.orderBook()
    if orderbook['status']==True:
      orderbook=orderbook['data']
      orderbook=pd.DataFrame(orderbook)
      #orderbook[['price','squareoff','stoploss','triggerprice']]=orderbook[['price','squareoff','stoploss','triggerprice']].astype(float)
      #orderbook[['quantity']]=orderbook[['quantity']].astype(int)
      #orderbook['updatetime'] = pd.to_datetime(orderbook['updatetime']).dt.time
      g_orderbook=orderbook[['updatetime','orderid','transactiontype','status','tradingsymbol','price','averageprice','quantity','ordertag']]
      g_orderbook['updatetime'] = pd.to_datetime(g_orderbook['updatetime']).dt.time
      g_orderbook = g_orderbook.sort_values(by=['updatetime'], ascending=[False])
      order_datatable.dataframe(g_orderbook,hide_index=True)
      order_book_updated.text(f"Orderbook : {datetime.datetime.now(tz=gettz('Asia/Kolkata')).time().replace(microsecond=0)}")
      pending_orders = orderbook[((orderbook['orderstatus'] != 'complete') & (orderbook['orderstatus'] != 'cancelled') &
                              (orderbook['orderstatus'] != 'rejected') & (orderbook['orderstatus'] != 'AMO CANCELLED'))]
      pending_orders = pending_orders[(pending_orders['instrumenttype'] == 'OPTIDX')]
      n_pending_orders=pending_orders[['updatetime','orderid','transactiontype','status','tradingsymbol','price','averageprice','quantity','ordertag']]
      n_pending_orders = n_pending_orders.sort_values(by=['updatetime'], ascending=[False])
      open_order.dataframe(n_pending_orders,hide_index=True)
      open_order_updated.text(f"Pending Orderbook : {datetime.datetime.now(tz=gettz('Asia/Kolkata')).time().replace(microsecond=0)}")
      return orderbook,pending_orders
    else:
      order_book_updated.text(f"No Order : {datetime.datetime.now(tz=gettz('Asia/Kolkata')).time().replace(microsecond=0)}")
      open_order_updated.text(f"No Open Order : {datetime.datetime.now(tz=gettz('Asia/Kolkata')).time().replace(microsecond=0)}")
      return None,None
  except Exception as e:
    print(f'Error in getting order book {e}')
    order_book_updated.text(f"Error in getting Orderbook : {datetime.datetime.now(tz=gettz('Asia/Kolkata')).time().replace(microsecond=0)}")
    open_order_updated.text(f"Error in getting Orderbook : {datetime.datetime.now(tz=gettz('Asia/Kolkata')).time().replace(microsecond=0)}")
  return None,None

#Historical Data and Calculate Indicator
def yfna_data(symbol,interval,period):
  try:
    df=yf.Ticker(symbol).history(interval=interval,period=str(period)+"d")
    df['Datetime'] = df.index
    df['Datetime']=df['Datetime'].dt.tz_localize(None)
    df.index=df['Datetime']
    df=df[['Datetime','Open','High','Low','Close','Volume']]
    df['Date']=df['Datetime'].dt.strftime('%m/%d/%y')
    df['Datetime'] = pd.to_datetime(df['Datetime']).dt.time
    df=df[['Date','Datetime','Open','High','Low','Close','Volume']]
    df=df.round(2)
    if isinstance(df, str) or (isinstance(df, pd.DataFrame)==True and len(df)==0):
      logger.info(f"Yahoo Data Not Found {symbol}: {e}")
      return "No data found, symbol may be delisted"
    return df
  except Exception as e:
    logger.info(f"error in yfna_data {symbol}: {e}")
    return None
  
def angel_data(token,interval,exch_seg,period=5):
  try:
    to_date= datetime.datetime.now(tz=gettz('Asia/Kolkata'))
    from_date = to_date - datetime.timedelta(days=period)
    fromdate = from_date.strftime("%Y-%m-%d %H:%M")
    todate = to_date.strftime("%Y-%m-%d %H:%M")
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
    logger.info(f"error in angel_data : {e}")
    return None
  
def get_historical_data(symbol="-",interval='5m',token="-",exch_seg="-",candle_type="NORMAL"):
  try:
    symbol_i="-";df=None
    if (symbol=="^NSEI" or symbol=="NIFTY") : symbol_i,token,exch_seg="^NSEI",99926000,"NSE"
    elif (symbol=="^NSEBANK" or symbol=="BANKNIFTY") : symbol_i,token,exch_seg="^NSEBANK",99926009,"NSE"
    elif (symbol=="^BSESN" or symbol=="SENSEX") : symbol_i,token,exch_seg="^BSESN",99919000,"BSE"
    if symbol[3:]=='-EQ': symbol=symbol[:-3]+".NS"
    if (interval=="5m" or interval=='FIVE_MINUTE'): period,delta_time,agl_interval,yf_interval=5,5,"FIVE_MINUTE","5m"
    elif (interval=="1m" or interval=='ONE_MINUTE') : period,delta_time,agl_interval,yf_interval=1,1,"ONE_MINUTE","1m"
    elif (interval=="15m" or interval=='FIFTEEN_MINUTE'): period,delta_time,agl_interval,yf_interval=5,15,"FIFTEEN_MINUTE","15m"
    elif (interval=="60m" or interval=='ONE_HOUR'): period,delta_time,agl_interval,yf_interval=30,60,"ONE_HOUR","60m"
    elif (interval=="1d" or interval=='ONE_DAY') : period,delta_time,agl_interval,yf_interval=100,5,"ONE_DAY","1d"
    else:period,delta_time,agl_interval,yf_interval=5,1,"ONE_MINUTE","1m"
    if (symbol_i[0]=="^"):df=yfna_data(symbol_i,yf_interval,period)
    else:df=angel_data(token,agl_interval,exch_seg,period)
    now=datetime.datetime.now(tz=gettz('Asia/Kolkata')).replace(microsecond=0, tzinfo=None)
    #if now - df.index[-1] > datetime.timedelta(minutes=5):df=angel_data(token,agl_interval,exch_seg,period)
    #else:df=angel_data(token,agl_interval,exch_seg,period)
    # if odd_candle ==True:
    #   df=df.groupby(pd.Grouper(freq=odd_interval+'in')).agg({"Date":"first","Datetime":"first","Open": "first", "High": "max",
    #                                                     "Low": "min", "Close": "last","Volume": "sum"})
    #   df=df[(df['Open']>0)]
    #if df is None:return None
    now=datetime.datetime.now(tz=gettz('Asia/Kolkata')).replace(microsecond=0, tzinfo=None)
    last_candle=now.replace(second=0, microsecond=0)- datetime.timedelta(minutes=delta_time)
    df = df[(df.index <= last_candle)]
    df['Time Frame']=yf_interval
    df['Time']=now.time()
    df.index.names = ['']
    df['VWAP']=pdta.vwap(high=df['High'],low=df['Low'],close=df['Close'],volume=df['Volume'])
    df = df.reset_index(drop=True)
    df=df[['Time','Date','Datetime','Open','High','Low','Close','Volume','VWAP','Time Frame']]
    df['Symbol']=symbol
    df=calculate_indicator(df)
    df=df.round(2)
    return df
  except Exception as e:
    logger.info(f"error in get_historical_data: {e}")
    return None
    
def get_trade_info(df):
  for i in ['ST_7_3 Trade','MACD Trade','PSAR Trade','DI Trade','MA Trade','EMA Trade','BB Trade','Trade','Trade End',
            'Rainbow MA','Rainbow Trade','MA 21 Trade','ST_10_2 Trade','Two Candle Theory','HMA Trade','VWAP Trade',
            'EMA_5_7 Trade','ST_10_4_8 Trade','EMA_High_Low Trade','RSI MA Trade','RSI_60 Trade','ST_10_1 Trade','TEMA_EMA_9 Trade']:df[i]='-'
  time_frame=df['Time Frame'][0]
  Symbol=df['Symbol'][0]
  symbol_type = "IDX" if Symbol in ["^NSEBANK", "BANKNIFTY", "^NSEI", "NIFTY", "SENSEX", "^BSESN"] else "OPT"
  indicator_list=[]
  if symbol_type=="IDX":
    if time_frame=="5m":indicator_list=five_buy_indicator
    elif time_frame=="15m":indicator_list=fifteen_buy_indicator
    else:indicator_list=['ST_7_3 Trade','ST_10_2 Trade','TEMA_EMA_9 Trade','RSI_60 Trade']
  elif symbol_type=="OPT":
    if time_frame=="5m":indicator_list=five_opt_buy_indicator
    elif time_frame=="15m":indicator_list=[]
    elif time_frame=="1m":indicator_list=one_opt_buy_indicator
    else:indicator_list=['ST_7_3 Trade','ST_10_2 Trade','TEMA_EMA_9 Trade','RSI_60 Trade']
  df['Indicator']=symbol_type+" "+df['Time Frame']
  df['Trade']="-"
  df['Trade End']="-"
  for i in range(1, len(df)):
    try:
      if df.iloc[i-1]['Close'] <= df.iloc[i-1]['Supertrend'] and df.iloc[i]['Close'] > df.iloc[i]['Supertrend']:
        df.loc[i, 'ST_7_3 Trade'] = "Buy"
      elif df.iloc[i-1]['Close'] >= df.iloc[i-1]['Supertrend'] and df.iloc[i]['Close'] < df.iloc[i]['Supertrend']:
        df.loc[i, 'ST_7_3 Trade'] = "Sell"

      if df.iloc[i]['MACD'] > df.iloc[i]['MACD signal'] and df.iloc[i-1]['MACD'] < df.iloc[i-1]['MACD signal']:
        df.loc[i, 'MACD Trade'] = "Buy"
      elif df.iloc[i]['MACD'] < df.iloc[i]['MACD signal'] and df.iloc[i-1]['MACD'] > df.iloc[i-1]['MACD signal']:
        df.loc[i, 'MACD Trade'] = "Sell"

      if df.iloc[i-1]['Close'] < df.iloc[i-1]['Supertrend_10_2'] and df.iloc[i]['Close'] > df.iloc[i]['Supertrend_10_2']:
        df.loc[i, 'ST_10_2 Trade'] = "Buy"
      elif df.iloc[i-1]['Close'] > df.iloc[i-1]['Supertrend_10_2'] and df.iloc[i]['Close'] < df.iloc[i]['Supertrend_10_2']:
        df.loc[i, 'ST_10_2 Trade'] = "Sell"

      if df.iloc[i-1]['Close'] < df.iloc[i-1]['Supertrend_10_1'] and df.iloc[i]['Close'] > df.iloc[i]['Supertrend_10_1']:
        df.loc[i, 'ST_10_1 Trade'] = "Buy"
      elif df.iloc[i-1]['Close'] > df.iloc[i-1]['Supertrend_10_1'] and df.iloc[i]['Close'] < df.iloc[i]['Supertrend_10_1']:
        df.loc[i, 'ST_10_1 Trade'] = "Sell"

      if df.iloc[i-1]['Tema_9'] < df.iloc[i-1]['EMA_9'] and df.iloc[i]['Tema_9'] > df.iloc[i]['EMA_9'] and int(df.iloc[i]['RSI']) >= 55:
        df.loc[i, 'TEMA_EMA_9 Trade'] = "Buy"
      elif df.iloc[i-1]['Tema_9'] > df.iloc[i-1]['EMA_9'] and df.iloc[i]['Tema_9'] < df.iloc[i]['EMA_9']:
        df.loc[i, 'TEMA_EMA_9 Trade'] = "Sell"

      if int(df.iloc[i]['RSI']) >= 60 and int(df.iloc[i-1]['RSI']) < 60: df.loc[i, 'RSI_60 Trade'] = "Buy"

      #if df['Close'][i-1]<=df['PSAR'][i-1] and df['Close'][i]> df['PSAR'][i]: df['PSAR Trade'][i]="Buy"
      #elif df['Close'][i-1]>=df['PSAR'][i-1] and df['Close'][i]< df['PSAR'][i]: df['PSAR Trade'][i]="Sell"

      #if df['PLUS_DI'][i-1]<=df['MINUS_DI'][i-1] and df['PLUS_DI'][i]> df['MINUS_DI'][i]: df['DI Trade'][i]="Buy"
      #elif df['PLUS_DI'][i-1]>=df['MINUS_DI'][i-1] and df['PLUS_DI'][i]< df['MINUS_DI'][i]: df['DI Trade'][i]="Sell"

      #if df['MA_50'][i-1]<=df['MA_200'][i-1] and df['MA_50'][i]> df['MA_200'][i]: df['MA Trade'][i]="Buy"
      #elif df['MA_50'][i-1]>=df['MA_200'][i-1] and df['MA_50'][i]< df['MA_200'][i]: df['MA Trade'][i]="Sell"

      #if df['EMA_12'][i-1]<=df['EMA_26'][i-1] and df['EMA_12'][i]> df['EMA_26'][i]: df['EMA Trade'][i]="Buy"
      #elif df['EMA_12'][i-1]>=df['EMA_26'][i-1] and df['EMA_12'][i]< df['EMA_26'][i]: df['EMA Trade'][i]="Sell"

      #if df['EMA_5'][i-1]<=df['EMA_7'][i-1] and df['EMA_5'][i]> df['EMA_7'][i]: df['EMA_5_7 Trade'][i]="Buy"
      #elif df['EMA_5'][i-1]>=df['EMA_7'][i-1] and df['EMA_5'][i]< df['EMA_7'][i]: df['EMA_5_7 Trade'][i]="Sell"

      #if df['Close'][i-1]< df['MA_21'][i-1] and df['Close'][i]> df['MA_21'][i]: df['MA 21 Trade'][i]="Buy"
      #elif df['Close'][i-1]> df['MA_21'][i-1] and df['Close'][i]< df['MA_21'][i]: df['MA 21 Trade'][i]="Sell"

      #if df['HMA_21'][i-1]< df['HMA_55'][i-1] and df['HMA_21'][i]> df['HMA_55'][i]: df['HMA Trade'][i]="Buy"
      #elif df['HMA_21'][i-1]> df['HMA_55'][i-1] and df['HMA_21'][i]< df['HMA_55'][i]: df['HMA Trade'][i]="Sell"

      #if int(df['RSI'][i])>=60 or int(df['RSI'][i])<=40:
      #  if df['Close'][i-1]<df['EMA_High'][i-1] and df['Close'][i] > df['EMA_High'][i]: df['EMA_High_Low Trade'][i]="Buy"
      #  if df['Close'][i-1]>df['EMA_Low'][i-1] and df['Close'][i]<df['EMA_Low'][i]: df['EMA_High_Low Trade'][i]="Sell"

      #if (df['Close'][i-1]<df['Open'][i-1] and df['Close'][i]< df['Open'][i] and
      #  df['Close'][i]< df['Supertrend_10_2'][i] and df['RSI'][i]<=40 and df['VWAP'][i]>df['Close'][i] and
      #  df['Close'][i]<df['WMA_20'][i] and df['Volume'][i]>1000):
      #  df['Two Candle Theory'][i]='Sell'
      #elif (df['Close'][i-1] > df['Open'][i-1] and df['Close'][i] > df['Open'][i] and
      #  df['Close'][i] > df['Supertrend_10_2'][i] and df['RSI'][i] >= 50 and df['VWAP'][i]<df['Close'][i] and
      #  df['Close'][i]>df['WMA_20'][i] and df['Volume'][i]>1000):
      #  df['Two Candle Theory'][i]='Buy'
      for indicator_trade in indicator_list:
        if df[indicator_trade][i]=="Buy":
          df.loc[i,'Trade']="Buy"
          df.loc[i,'Trade End']="Buy"
          df.loc[i,'Indicator']=df['Trade'][i]+" "+df['Indicator'][i]+":"+indicator_trade+' RSI:'+str(int(df['RSI'][i]))
          break
        elif df[indicator_trade][i]=="Sell":
          df.loc[i,'Trade']="Sell"
          df.loc[i,'Trade End']="Sell"
          df.loc[i,'Indicator']=df['Trade'][i]+" "+df['Indicator'][i]+":"+indicator_trade+' RSI:'+str(int(df['RSI'][i]))
          break
    except Exception as e:pass
  return df

def calculate_indicator(df):
  try:
    df['RSI']=pdta.rsi(df['Close'],timeperiod=14)
    df['MACD']=pdta.macd(close=df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)['MACD_12_26_9']
    df['MACD signal']=pdta.macd(close=df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)['MACDs_12_26_9']
    df['Macdhist']=pdta.macd(close=df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)['MACDh_12_26_9']
    df['Supertrend']=pdta.supertrend(high=df['High'],low=df['Low'],close=df['Close'],length=7,multiplier=3)['SUPERT_7_3.0']
    df['Supertrend_10_2']=pdta.supertrend(high=df['High'],low=df['Low'],close=df['Close'],length=10,multiplier=2)['SUPERT_10_2.0']
    df['Supertrend_10_1']=pdta.supertrend(high=df['High'],low=df['Low'],close=df['Close'],length=10,multiplier=1)['SUPERT_10_1.0']
    df['Atr']=pdta.atr(high=df['High'], low=df['Low'], close=df['Close'], length=14)
    df['Tema_9']=pdta.tema(df['Close'],9)
    df['EMA_9']=pdta.ema(df['Close'],length=6)
    #df['UBB']=pdta.bbands(df['Close'],length=20, std=2, ddof=0)['BBU_20_2.0']
    #df['MBB']=pdta.bbands(df['Close'],length=20, std=2, ddof=0)['BBM_20_2.0']
    #df['LBB']=pdta.bbands(df['Close'],length=20, std=2, ddof=0)['BBL_20_2.0']
    #df['Supertrend_10_4']=pdta.supertrend(high=df['High'],low=df['Low'],close=df['Close'],length=10,multiplier=4)['SUPERT_10_4.0']
    #df['Supertrend_10_8']=pdta.supertrend(high=df['High'],low=df['Low'],close=df['Close'],length=10,multiplier=8)['SUPERT_10_8.0']
    #df['PSAR']=pdta.psar(high=df['High'],low=df['Low'],acceleration=0.02, maximum=0.2)['PSARl_0.02_0.2']
    #df['ADX']=pdta.adx(df['High'],df['Low'],df['Close'],14)['ADX_14']
    #df['MINUS_DI']=pdta.adx(df['High'],df['Low'],df['Close'],14)['DMN_14']
    #df['PLUS_DI']=pdta.adx(df['High'],df['Low'],df['Close'],14)['DMP_14']
    #df['MA_200']=df['Close'].rolling(200).mean()
    #df['MA_50']=df['Close'].rolling(50).mean()
    #df['EMA_12']=pdta.ema(df['Close'],length=12)
    #df['EMA_26']=pdta.ema(df['Close'],length=26)
    #df['EMA_13']=pdta.ema(df['Close'],length=13)
    #df['EMA_5']=pdta.ema(df['Close'],length=5)
    #df['EMA_7']=pdta.ema(df['Close'],length=7)
    #df['MA_1']=df['Close'].rolling(1).mean()
    #df['MA_2']=df['Close'].rolling(2).mean()
    #df['MA_3']=df['Close'].rolling(3).mean()
    #df['MA_4']=df['Close'].rolling(4).mean()
    #df['MA_5']=df['Close'].rolling(5).mean()
    #df['MA_6']=df['Close'].rolling(6).mean()
    #df['MA_7']=df['Close'].rolling(7).mean()
    #df['MA_8']=df['Close'].rolling(8).mean()
    #df['MA_9']=df['Close'].rolling(9).mean()
    #df['MA_10']=df['Close'].rolling(10).mean()
    #df['MA_21']=pdta.ema(df['Close'],length=21)
    #df['WMA_20']=pdta.wma(df['Close'],length=20)
    #df['HMA_21']=pdta.hma(df['Close'],length=21)
    #df['HMA_55']=pdta.hma(df['Close'],length=55)
    #df['RSI_MA']=df['RSI'].rolling(14).mean()
    #df['EMA_High']=pdta.ema(df['High'],length=21)
    #df['EMA_Low']=pdta.ema(df['Low'],length=21)
    #df = df.round(decimals=2)
    df=get_trade_info(df)
    return df
  except Exception as e:
    logger.info(f"Error in calculate Indicator: {e}")
    return df

# Index Trade
def getTokenInfo(symbol, exch_seg ='NFO',instrumenttype='OPTIDX',strike_price = 0,pe_ce = 'CE',expiry_day = None):
  try:
    token_df=st.session_state['opt_list']
    if exch_seg == 'NSE' or exch_seg == 'BSE': return token_df[(token_df['exch_seg'] == exch_seg) & (token_df['name'] == symbol)]
    elif (instrumenttype == 'FUTSTK') or (instrumenttype == 'FUTIDX'):
        return token_df[(token_df['instrumenttype'] == instrumenttype) & (token_df['name'] == symbol)].sort_values(by=['expiry'], ascending=True)
    elif (instrumenttype == 'OPTSTK' or instrumenttype == 'OPTIDX'):
        return (token_df[(token_df['name'] == symbol) & (token_df['expiry']==expiry_day) &
                (token_df['instrumenttype'] == instrumenttype) & (token_df['strike'] == strike_price*100) &
                (token_df['symbol'].str.endswith(pe_ce))].sort_values(by=['expiry']))
  except Exception as e:return None

# get current CE and PE
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
  return indexLtp, ce_strike_symbol,pe_strike_symbol

#Buy Position
def buy_option(symbol,indicator_strategy="Manual Buy",interval="5m",index_sl="-"):
  try:
    option_token=symbol['token']; option_symbol=symbol['symbol']; exch_seg=symbol['exch_seg']; lotsize=int(symbol['lotsize'])
    orderId=place_order(token=option_token,symbol=option_symbol,qty=lotsize,buy_sell='BUY',ordertype='MARKET',price=int(0),
                          variety='NORMAL',exch_seg=exch_seg,producttype='CARRYFORWARD',ordertag=indicator_strategy)
    if str(orderId)=='Order placement failed':
      telegram_bot_sendtext(f'Order Failed Buy: {option_symbol} Indicator {indicator_strategy}')
      return
    try:
      ltp_price=round(float(get_ltp_price(symbol=option_symbol,token=option_token,exch_seg=exch_seg)),2)
      target_price=int(float(ltp_price*((100+30)/100)))
      stop_loss=int(float(ltp_price*((100-50)/100)))
      if target_type=="Per Cent":
        target_price=int(float(ltp_price*((100+target_point)/100)))
        stop_loss=int(float(ltp_price*((100-sl_point)/100)))
      elif target_type=="Points":
        target_price=int(ltp_price+target_point)
        stop_loss=int(ltp_price-sl_point)
      elif 'TEMA_EMA_9 Trade' in indicator_strategy:
        target_price=int(ltp_price+10)
        stop_loss=int(ltp_price-10)
      else:
        target_price=int(ltp_price*2)
        stop_loss=int(ltp_price*0.5)
        #old_data=get_historical_data(symbol=option_symbol,interval='5m',token=option_token,exch_seg=exch_seg,candle_type="NORMAL")
        #target_price=int(float(ltp_price+(float(old_data['Atr'].iloc[-1])*2)))
        #stop_loss=int(float(ltp_price-(float(old_data['Atr'].iloc[-1])*2)))
      indicator_strategy=indicator_strategy+ " LTP:"+str(int(ltp_price))+"("+str(int(stop_loss))+":"+str(int(target_price))+")"
      buy_msg=(f'Buy: {option_symbol}\nPrice: {trade_price} LTP: {ltp_price}\n{indicator_strategy}\nTarget: {target_price} Stop Loss: {stop_loss}')
      telegram_bot_sendtext(buy_msg)
    except:
      ltp_price=0
    orderbook=obj.orderBook()['data']
    orderbook=pd.DataFrame(orderbook)
    orders= orderbook[(orderbook['orderid'] == orderId)]
    orders_status=orders.iloc[0]['orderstatus']
    trade_price=orders.iloc[0]['averageprice']
    if orders_status== 'complete':
      if st.session_state['target_order_type']=="Target":
        place_order(token=option_token,symbol=option_symbol,qty=lotsize,buy_sell='SELL',ordertype='LIMIT',price=target_price,
                    variety='NORMAL',exch_seg=exch_seg,producttype='CARRYFORWARD',ordertag=str(orderId)+" Target order Placed")
      elif st.session_state['target_order_type']=='Stop_Loss':
        place_order(token=option_token,symbol=option_symbol,qty=lotsize,buy_sell='SELL',ordertype='STOPLOSS_LIMIT',price=stop_loss,
                    variety='STOPLOSS',exch_seg=exch_seg,producttype='CARRYFORWARD',triggerprice=stop_loss,squareoff=stop_loss,
                    stoploss=stop_loss, ordertag=str(orderId)+" Stop Loss order Placed")
  except Exception as e:
    logger.info(f"Error in buy_option: {e}")
#Exit Position
def exit_position(symboltoken,tradingsymbol,exch_seg,qty,ltp_price,sl,ordertag='',producttype='CARRYFORWARD'):
  try:
    cancel_all_order(tradingsymbol)
    orderId=place_order(token=symboltoken,symbol=tradingsymbol,qty=qty,buy_sell='SELL',ordertype='STOPLOSS_LIMIT',price=sl,
                        variety='STOPLOSS',exch_seg=exch_seg,producttype=producttype,triggerprice=sl,squareoff=sl, stoploss=sl,ordertag=ordertag)
    logger.info(f"Exit Alert In Option: {tradingsymbol} LTP:{ltp_price} SL:{sl} Ordertag {ordertag}")
    #telegram_bot_sendtext(sell_msg)
  except Exception as e:
    logger.info(f"Error in exit_position: {e}")

def cancel_index_order(nf_5m_trade_end="-",bnf_5m_trade_end="-",sensex_5m_trade_end="-"):
  if nf_5m_trade_end!="-" or bnf_5m_trade_end!="-" or sensex_5m_trade_end!="-":
    orderbook,pending_orders=get_order_book()
    for i in range(0,len(pending_orders)):
      try:
        tradingsymbol=pending_orders.loc[i]['tradingsymbol']
        if ((tradingsymbol[-2:]=='CE' and tradingsymbol.startswith("NIFTY") and nf_5m_trade_end=="Sell") or
            (tradingsymbol[-2:]=='CE' and tradingsymbol.startswith("BANKNIFTY") and bnf_5m_trade_end=="Sell") or
            (tradingsymbol[-2:]=='CE' and tradingsymbol.startswith("SENSEX") and sensex_5m_trade_end=="Sell") or
            (tradingsymbol[-2:]=='PE' and tradingsymbol.startswith("NIFTY") and nf_5m_trade_end=="Buy") or
            (tradingsymbol[-2:]=='PE' and tradingsymbol.startswith("BANKNIFTY") and bnf_5m_trade_end=="Buy") or
            (tradingsymbol[-2:]=='PE' and tradingsymbol.startswith("SENSEX") and sensex_5m_trade_end=="Buy")):
            orderID=pending_orders.loc[i]['orderid']
            variety=pending_orders.loc[i]['variety']
            cancel_order(orderID,variety)
      except Exception as e:
        logger.info(f"error in cancel_index_order: {e}")
        pass
      
def close_options_position(position,nf_5m_trade_end="-",bnf_5m_trade_end="-",sensex_5m_trade_end="-"):
  cancel_index_order(nf_5m_trade_end,bnf_5m_trade_end,sensex_5m_trade_end)
  position,open_position=get_open_position()
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
    except Exception as e:
      logger.info(f"Error in Close index trade: {e}")

def index_trade(symbol,interval):
  try:
    fut_data=get_historical_data(symbol=symbol,interval=interval,token="-",exch_seg="-",candle_type="NORMAL")
    if fut_data is None: return None
    trade=str(fut_data['Trade'].values[-1])
    if trade!="-":
      indicator_strategy=f"{fut_data['Indicator'].values[-1]} ATR: {fut_data['Atr'].values[-1]}"
      indexLtp=fut_data['Close'].values[-1]
      indexLtp, ce_strike_symbol,pe_strike_symbol=get_ce_pe_data(symbol,indexLtp=indexLtp)
      if trade=="Buy" : buy_option(ce_strike_symbol,indicator_strategy,interval)
      elif trade=="Sell" : buy_option(pe_strike_symbol,indicator_strategy,interval)
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
    st.session_state['index_trade_end'][symbol+"_"+interval] = trade
  except Exception as e:
    logger.info(f"error in index_trade: {e}")

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

def all_near_options():
  df=pd.DataFrame()
  for symbol in index_list:
    try:
      index_ltp=get_ltp_price(symbol)
      if symbol=="NIFTY":symbol_expiry=st.session_state['nf_expiry_day']
      elif symbol=="BANKNIFTY":symbol_expiry=st.session_state['bnf_expiry_day']
      elif symbol=="SENSEX":symbol_expiry=st.session_state['sensex_expiry_day']
      else:symbol_expiry="-"
      option_list=get_near_options(symbol,index_ltp,symbol_expiry)
      df=pd.concat([df,option_list])
    except Exception as e:print(e)
  st.session_state['near_opt_df']=df
  near_opt_df.dataframe(df,hide_index=True)
  near_opt_updated.text(f"Near Option Updated : {datetime.datetime.now(tz=gettz('Asia/Kolkata')).time().replace(microsecond=0)}")

def trade_near_options(time_frame):
  try:
    option_list=st.session_state['near_opt_df']
    for symbol in index_list:
      for i in range(0,len(option_list)):
        symbol_name=option_list['symbol'].iloc[i]
        if symbol_name.startswith(symbol):
          token_symbol=option_list['token'].iloc[i]
          exch_seg=option_list['exch_seg'].iloc[i]
          opt_data=get_historical_data(symbol=symbol_name,interval=time_frame,token=token_symbol,exch_seg=exch_seg)
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
          if opt_data['Trade'].values[-1]=="Buy":
            indicator=f"{opt_data['Indicator'].values[-1]} ATR: {opt_data['Atr'].values[-1]}"
            strike_symbol=option_list.iloc[i]
            buy_option(symbol=strike_symbol,indicator_strategy=indicator,interval=time_frame,index_sl="-")
            break
  except Exception as e:logger.info(f"Trade Near Option Error {e}")

def closing_trade():
  try:
    orderbook,pending_orders=get_order_book()
    st.session_state['NIFTY_5m_Trade']="Buy"
    st.session_state['BANKNIFTY_5m_Trade']="Buy"
    st.session_state['SENSEX_5m_Trade']="Buy"
    todays_trade=get_todays_trade(orderbook)
    st.session_state['NIFTY_5m_Trade']="Sell"
    st.session_state['BANKNIFTY_5m_Trade']="Sell"
    st.session_state['SENSEX_5m_Trade']="Sell"
    todays_trade=get_todays_trade(orderbook)
  except:pass

def trail_sl():
  orderbook,pending_orders=get_order_book()
  if pending_orders is not None:
    for i in range(0,len(pending_orders)):
      try:
        if pending_orders['status'].iloc[i] not in ['rejected','complete','cancelled']:
          if pending_orders['transactiontype'].iloc[i]=="SELL":
            order_price=pending_orders['price'].iloc[i]
            new_sl=order_price
            symbol=pending_orders['tradingsymbol'].iloc[i]
            token=pending_orders['symboltoken'].iloc[i]
            exch_seg=pending_orders['exchange'].iloc[i]
            ltp_price=get_ltp_price(symbol=symbol,token=token,exch_seg=exch_seg)
            if ltp_price>order_price:
              old_data=get_historical_data(symbol=symbol,interval="5m",token=token,exch_seg=exch_seg,candle_type="NORMAL")
              atr=ltp_price-(float(old_data['Atr'].iloc[-1])*2)
              st_10_2=float(old_data['Supertrend_10_2'].iloc[-1])
              st_7_3=float(old_data['Supertrend'].iloc[-1])
              st_10_1=float(old_data['Supertrend_10_1'].iloc[-1])
              if st_7_3 > new_sl and st_7_3 < ltp_price: new_sl=int(st_7_3)
              if st_10_2 > new_sl and st_10_2 < ltp_price: new_sl=int(st_10_2)
              if atr > new_sl and atr < ltp_price : new_sl=int(atr)
              transactiontype=pending_orders['transactiontype'].iloc[i]
              variety=pending_orders['variety'].iloc[i]
              orderid=pending_orders['orderid'].iloc[i]
              ordertype=pending_orders['ordertype'].iloc[i]
              producttype=pending_orders['producttype'].iloc[i]
              quantity=pending_orders['quantity'].iloc[i]
              modify_order(variety,orderid,ordertype,producttype,new_sl,quantity,symbol,token,exch_seg,new_sl,new_sl,new_sl)
      except Exception as e:
        logger.info(f"error in trail_sl: {e}")
        pass

def check_indicator_exit(buy_df,minute):
  for i in range(0,len(buy_df)):
      try:
        if buy_df['Status'].iloc[i]=="Pending" and buy_df['price'].iloc[i]!="-":
          symboltoken=buy_df['symboltoken'].iloc[i]
          tradingsymbol=buy_df['tradingsymbol'].iloc[i]
          exch_seg=buy_df['exchange'].iloc[i]
          qty=buy_df['quantity'].iloc[i]
          price=buy_df['price'].iloc[i]
          ltp_price=buy_df['LTP'].iloc[i]
          orderid=buy_df['orderid'].iloc[i]
          indicator=buy_df['ordertag'].iloc[i]
          sl=buy_df['LTP'].iloc[i]
          trade_info = (
          f"{buy_df['tradingsymbol'].iloc[i]}\n"
          f"LTP:{buy_df['LTP'].iloc[i]} Target:{buy_df['Target'].iloc[i]} "
          f"SL:{buy_df['SL'].iloc[i]}\n"
          f"Price:{buy_df['price'].iloc[i]}\n"
          f"Time:{buy_df['updatetime'].iloc[i]}\n"
          f"Indicator: {buy_df['ordertag'].iloc[i]}\n"
          f"Profit: {int(buy_df['Profit'].iloc[i])}")
          ordertag=f"{ltp_price} : {orderid}"
          if minute%15==0 and "15m" in indicator:
            opt_data=get_historical_data(symbol=tradingsymbol,interval="15m",token=symboltoken,exch_seg=exch_seg,candle_type="NORMAL")
          elif (minute%5==0 and "5m" in indicator) or "GTT" in indicator:
            opt_data=get_historical_data(symbol=tradingsymbol,interval="5m",token=symboltoken,exch_seg=exch_seg,candle_type="NORMAL")
          elif "1m" in indicator or indicator=="Buy:Multi Time Frame ST":
            opt_data=get_historical_data(symbol=tradingsymbol,interval="1m",token=symboltoken,exch_seg=exch_seg,candle_type="NORMAL")
          else:
            opt_data=get_historical_data(symbol=tradingsymbol,interval="5m",token=symboltoken,exch_seg=exch_seg,candle_type="NORMAL")
          #check for exit
          if opt_data['ST_7_3 Trade'].values[-1]=="Sell":
            exit_position(symboltoken,tradingsymbol,exch_seg,qty,ltp_price,sl,ordertag='ST_7_3 Exit:'+ordertag,producttype='CARRYFORWARD')
            multiline_string = "Indicator Exit: "+trade_info
            telegram_bot_sendtext(multiline_string)
            buy_df['Status'].iloc[i]="Indicator Exit"
      except Exception as e:
        print(e)
def check_login():
  pass


#Loop Code
def sub_loop_code(now_minute):
  try:
    st.session_state['options_trade_list']=[]
    if (now_minute%5==0 and 'IDX:5M' in time_frame_interval):
      for symbol in index_list: index_trade(symbol,"5m")
      log_holder.dataframe(st.session_state['options_trade_list'],hide_index=True)
      if 'OPT:5M' in time_frame_interval:trade_near_options('5m')
      log_holder.dataframe(st.session_state['options_trade_list'],hide_index=True)
    if (now_minute%15==0 and 'IDX:15M' in time_frame_interval): 
      for symbol in index_list:index_trade(symbol,"15m")
    if 'IDX:1M' in time_frame_interval:
      for symbol in index_list: index_trade(symbol,"1m")
    if 'OPT:1M' in time_frame_interval: trade_near_options('1m')
    if "Multi Time ST Trade" in five_buy_indicator: multi_time_frame()
    log_holder.dataframe(st.session_state['options_trade_list'],hide_index=True)
  except Exception as e:
    logger.info(f"error in sub_loop_code: {e}")

def loop_code():
  now = datetime.datetime.now(tz=gettz('Asia/Kolkata'))
  marketopen = now.replace(hour=9, minute=20, second=0, microsecond=0)
  marketclose = now.replace(hour=18, minute=50, second=0, microsecond=0)
  day_end = now.replace(hour=18, minute=30, second=0, microsecond=0)
  if algo_state==False:return
  all_near_options()
  if now > marketclose: close_day_end_trade()
  while now < marketclose:
    now=datetime.datetime.now(tz=gettz('Asia/Kolkata'))
    next_loop=now.replace(second=0, microsecond=0)+ datetime.timedelta(minutes=1)
    st.session_state['last_check']=now.time()
    login_details.text(f"Welcome:{st.session_state['Logged_in']} Login:{st.session_state['login_time']} Last Check:{st.session_state['last_check']}")
    try:
      if now > marketopen and now < marketclose: sub_loop_code(now.minute)
      elif now > marketclose: close_day_end_trade()
      orderbook,pending_orders=get_order_book()
      position,open_position=get_open_position()
      get_todays_trade(orderbook)
      if now.minute%5==0: trail_sl_todays_trade()
      all_near_options()
      index_ltp_string.text(f"Index Ltp: {print_ltp()}")
      if datetime.datetime.now(tz=gettz('Asia/Kolkata')) < next_loop:
        time.sleep((next_loop-datetime.datetime.now(tz=gettz('Asia/Kolkata'))).seconds)
        time.sleep(1)
    except Exception as e:
      logger.info(f"error in loop_code: {e}")
      now=datetime.datetime.now(tz=gettz('Asia/Kolkata'))
      time.sleep(60-now.second+1)

def get_ltp_token(nfo_list,bfo_list):
  try:
    ltp_df=pd.DataFrame(obj.getMarketData(mode="LTP",exchangeTokens={ "BFO": list(bfo_list), "NFO": list(nfo_list),})['data']['fetched'])
    return ltp_df
  except Exception as e:
    ltp_df=pd.DataFrame(columns = ['exchange','tradingSymbol','symbolToken','ltp'])
    return ltp_df
  
def update_price_orderbook(df):
  for j in range(0,len(df)):
    try:
      if df['ordertag'].iloc[j]=="": df['ordertag'].iloc[j]="GTT Buy OPT 5m:Supertrend Trade"
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
      #if df['price'].iloc[j]=='-':
      #  df['price'].iloc[j]=get_ltp_price(symbol=df['tradingsymbol'].iloc[j],token=df['symboltoken'].iloc[j],exch_seg=df['exchange'].iloc[j])
    except Exception as e:
      pass
  return df

def update_target_sl(buy_df):
  for i in range(0,len(buy_df)):
    try:
      if "(" in buy_df['ordertag'].iloc[i] and ")" in buy_df['ordertag'].iloc[i]:
        sl=(buy_df['ordertag'].iloc[i].split('('))[1].split(':')[0]
        tgt=(buy_df['ordertag'].iloc[i].split(sl+':'))[1].split(')')[0]
        buy_df['SL'].iloc[i]=sl
        buy_df['Target'].iloc[i]=tgt
      elif 'TEMA_EMA_9 Trade' in buy_df['ordertag'].iloc[i] :
        buy_df['Target'].iloc[i]=int(buy_df['price'].iloc[i])+10
        buy_df['SL'].iloc[i]=int(buy_df['price'].iloc[i])-10
      elif 'ATR' in buy_df['ordertag'].iloc[i]:
        indicator_text=buy_df['ordertag'].iloc[i]
        res=int(indicator_text[indicator_text.find('ATR:')+len(indicator_text):])
        buy_df['Target'].iloc[i]=int(buy_df['price'].iloc[i]+(res*target_point))
        buy_df['SL'].iloc[i]=int(buy_df['price'].iloc[i]-(res*sl_point))
      else:
        if buy_df['price'].iloc[i]!="-":
          if target_type=="Per Cent":
            buy_df['Target'].iloc[i]=int(float(buy_df['price'].iloc[i]*((100+target_point)/100)))
            buy_df['SL'].iloc[i]=int(float(buy_df['price'].iloc[i]*((100-sl_point)/100)))
          elif target_type=="Points":
            buy_df['Target'].iloc[i]=int(float(buy_df['price'].iloc[i])+target_point)
            buy_df['SL'].iloc[i]=int(float(buy_df['price'].iloc[i])-sl_point)
          else:
            buy_df['Target'].iloc[i]=int(buy_df['price'].iloc[i]*2)
            buy_df['SL'].iloc[i]=int(buy_df['price'].iloc[i]*0.5)
      trail_sl=st.session_state['stop_loss'].get(buy_df['tradingsymbol'].iloc[i])
      if trail_sl is not None and int(trail_sl) > int(buy_df['SL'].iloc[i]): buy_df['SL'].iloc[i]=int(trail_sl)
    except Exception as e:
      logger.info(f"error in update_target_sl: {e}")
  return buy_df

def update_ltp_buy_df(buy_df):
  nfo_list=numpy.unique(buy_df[buy_df['exchange']=="NFO"]['symboltoken'].values.tolist())
  bfo_list=numpy.unique(buy_df[buy_df['exchange']=="BFO"]['symboltoken'].values.tolist())
  ltp_df=get_ltp_token(nfo_list,bfo_list)
  for i in range(0,len(buy_df)):
    try:
      symboltoken=str(buy_df['symboltoken'].iloc[i])
      n_ltp_df=ltp_df[ltp_df['symbolToken']==symboltoken]
      if len(n_ltp_df)!=0:buy_df['LTP'].iloc[i]=n_ltp_df['ltp'].iloc[0]
      #else:
      #  buy_df['LTP'].iloc[i]=get_ltp_price(symbol=buy_df['tradingsymbol'].iloc[i],token=buy_df['symboltoken'].iloc[i],exch_seg=buy_df['exchange'].iloc[i])
      if buy_df['Status'].iloc[i]!='Closed' and buy_df['price'].iloc[i]!="-":
          #buy_df['LTP'].iloc[i]=get_ltp_price(symbol=buy_df['tradingsymbol'].iloc[i],token=buy_df['symboltoken'].iloc[i],exch_seg=buy_df['exchange'].iloc[i])
          buy_df['Profit'].iloc[i]=(float(buy_df['LTP'].iloc[i])-float(buy_df['price'].iloc[i]))*float(buy_df['quantity'].iloc[i])
          buy_df['Profit %'].iloc[i]=((buy_df['LTP'].iloc[i]/buy_df['price'].iloc[i])-1)*100
      else:
          if buy_df['price'].iloc[i]!="-":
            buy_df['Profit'].iloc[i]=float((buy_df['Sell'].iloc[i]-buy_df['price'].iloc[i]))*float(buy_df['quantity'].iloc[i])
            buy_df['Profit %'].iloc[i]=((buy_df['Sell'].iloc[i]/buy_df['price'].iloc[i])-1)*100
          else:
            buy_df['Profit'].iloc[i]=0
            buy_df['Profit %'].iloc[i]=0
    except Exception as e: logger.info(f"Error in update_ltp_buy_df: {e}")
  return buy_df

def recheck_pnl():
  buy_df=st.session_state['todays_trade']
  if len(buy_df)!=0:
    buy_df['Profit %']=buy_df['Profit %'].astype(float).round(2)
    buy_df=buy_df.sort_values(by = ['Status', 'updatetime'], ascending = [False, True], na_position = 'first')
    try:
      pending_trade = buy_df[buy_df['Status'] == 'Pending'].copy()
      pending_trade['price']=pending_trade['price'].astype(float).round(2)
      pending_trade['quantity']=pending_trade['quantity'].astype(float).round(2)
      pending_trade['Margin'] = pending_trade['price'] * pending_trade['quantity']
      total_margin = pending_trade['Margin'].sum()
      active_trades_count = len(pending_trade)
      margin = f"{int(total_margin)}, Active Trades: {active_trades_count}"
    except:margin=0
    buy_df= buy_df[['updatetime','tradingsymbol','price','quantity','ordertag','Exit Time','Status',
                                      'Sell', 'LTP', 'Profit','Target','SL', 'Profit %', 'Sell Indicator']]
    todays_trade_datatable.dataframe(buy_df,hide_index=True)
    now_time=datetime.datetime.now(tz=gettz('Asia/Kolkata')).time().replace(microsecond=0)
    todays_trade_updated.text(f"Todays Trade : {now_time} Profit: {int(buy_df['Profit'].sum())} Margin:{margin}")

def trail_sl_todays_trade():
  buy_df=st.session_state['todays_trade']
  unique_values = buy_df[['tradingsymbol', 'symboltoken','exchange']].drop_duplicates()
  for index, row in unique_values.iterrows():
    try:
      symbol=row['tradingsymbol']
      token=row['symboltoken']
      exch_seg=row['exchange']
      fno_data=get_historical_data(symbol=symbol,interval="5m",token=token,exch_seg=exch_seg,candle_type="NORMAL")
      if fno_data['Supertrend'].iloc[-1] < fno_data['Close'].iloc[-1]:
        new_sl=fno_data['Supertrend'].iloc[-1]
      elif fno_data['Supertrend_10_2'].iloc[-1] < fno_data['Close'].iloc[-1]:
        new_sl=fno_data['Supertrend_10_2'].iloc[-1]
      else:
        new_sl=int(fno_data['Close'].iloc[-1]-(3*fno_data['Atr'].iloc[-1]))
      st.session_state['stop_loss'][symbol]=int(new_sl)
    except:pass

def check_pnl_todays_trade(buy_df):
  for i in range(0,len(buy_df)):
      try:
        if buy_df['Status'].iloc[i]=="Pending" and buy_df['price'].iloc[i]!="-":
          symboltoken=buy_df['symboltoken'].iloc[i]
          tradingsymbol=buy_df['tradingsymbol'].iloc[i]
          exch_seg=buy_df['exchange'].iloc[i]
          qty=buy_df['quantity'].iloc[i]
          price=buy_df['price'].iloc[i]
          ltp_price=buy_df['LTP'].iloc[i]
          orderid=buy_df['orderid'].iloc[i]
          indicator=buy_df['ordertag'].iloc[i]
          sl=buy_df['LTP'].iloc[i]
          trade_info = (
          f"{buy_df['tradingsymbol'].iloc[i]}\n"
          f"LTP:{buy_df['LTP'].iloc[i]} Target:{buy_df['Target'].iloc[i]} "
          f"SL:{buy_df['SL'].iloc[i]}\n"
          f"Price:{buy_df['price'].iloc[i]}\n"
          f"Time:{buy_df['updatetime'].iloc[i]}\n"
          f"Indicator: {buy_df['ordertag'].iloc[i]}\n"
          f"Profit: {int(buy_df['Profit'].iloc[i])}")
          if int(sl)==0:ltp_price=1;sl=1
          ordertag=f"{ltp_price} : {orderid}"
          if int(buy_df['LTP'].iloc[i])< int(buy_df['SL'].iloc[i]):
            exit_position(symboltoken,tradingsymbol,exch_seg,qty,ltp_price,sl,ordertag='SL Hit:'+ordertag,producttype='CARRYFORWARD')
            multiline_string = "SL Hit: "+trade_info
            telegram_bot_sendtext(multiline_string)
            buy_df.loc[i,'Status']="SL Hit"
          elif int(buy_df['LTP'].iloc[i])> int(buy_df['Target'].iloc[i]):
            exit_position(symboltoken,tradingsymbol,exch_seg,qty,ltp_price,sl,ordertag='Target Hit:'+ordertag,producttype='CARRYFORWARD')
            multiline_string = "Target Hit: "+trade_info
            telegram_bot_sendtext(multiline_string)
            buy_df.loc[i,'Status']="Target Hit"
          else:
            exit_trade="No"
            #if tradingsymbol.startswith("NIFTY"):
            #  if " 5m" in indicator and tradingsymbol.endswith("PE") and st.session_state['NIFTY_5m_Trade']=="Buy":exit_trade="Yes"
            #  if " 5m" in indicator and tradingsymbol.endswith("CE") and st.session_state['NIFTY_5m_Trade']=="Sell":exit_trade="Yes"
            #  if " 1m" in indicator and tradingsymbol.endswith("PE") and st.session_state['NIFTY_1m_Trade']=="Buy":exit_trade="Yes"
            #  if " 1m" in indicator and tradingsymbol.endswith("CE") and st.session_state['NIFTY_1m_Trade']=="Sell":exit_trade="Yes"
            #elif tradingsymbol.startswith("BANKNIFTY"):
            #  if " 5m" in indicator and tradingsymbol.endswith("PE") and st.session_state['BANKNIFTY_5m_Trade']=="Buy":exit_trade="Yes"
            #  if " 5m" in indicator and tradingsymbol.endswith("CE") and st.session_state['BANKNIFTY_5m_Trade']=="Sell":exit_trade="Yes"
            #  if " 1m" in indicator and tradingsymbol.endswith("PE") and st.session_state['BANKNIFTY_1m_Trade']=="Buy":exit_trade="Yes"
            #  if " 1m" in indicator and tradingsymbol.endswith("CE") and st.session_state['BANKNIFTY_1m_Trade']=="Sell":exit_trade="Yes"
            #elif tradingsymbol.startswith("SENSEX"):
            #  if " 5m" in indicator and tradingsymbol.endswith("PE") and st.session_state['SENSEX_5m_Trade']=="Buy":exit_trade="Yes"
            #  if " 5m" in indicator and tradingsymbol.endswith("CE") and st.session_state['SENSEX_5m_Trade']=="Sell":exit_trade="Yes"
            #  if " 1m" in indicator and tradingsymbol.endswith("PE") and st.session_state['SENSEX_1m_Trade']=="Buy":exit_trade="Yes"
            #  if " 1m" in indicator and tradingsymbol.endswith("CE") and st.session_state['SENSEX_1m_Trade']=="Sell":exit_trade="Yes"
            if exit_trade=="Yes":
              exit_position(symboltoken,tradingsymbol,exch_seg,qty,ltp_price,sl,ordertag='Indicaor Exit:'+ordertag,producttype='CARRYFORWARD')
              multiline_string = "Indicaor Exit: "+trade_info
              telegram_bot_sendtext(multiline_string)
              buy_df.loc[i,'Status']="Indicaor Exit"
      except Exception as e: logger.info(f"error in check_pnl_todays_trade: {e}")
  return buy_df

def get_todays_trade(orderbook):
  try:
    orderbook=update_price_orderbook(orderbook)
    orderbook['updatetime'] = pd.to_datetime(orderbook['updatetime']).dt.time
    sell_df=orderbook[(orderbook['transactiontype']=="SELL") & ((orderbook['status']=="complete") | (orderbook['status']=="rejected"))]
    sell_df['Remark']='-'
    buy_df=orderbook[(orderbook['transactiontype']=="BUY") & ((orderbook['status']=="complete") | (orderbook['status']=="rejected"))]
    buy_df['Exit Time']=datetime.datetime.now(tz=gettz('Asia/Kolkata')).replace(hour=15, minute=30, second=0, microsecond=0,tzinfo=None).time()
    buy_df['Status']="Pending"
    for i in ['Sell','LTP','Profit','Index SL','Time Frame','Target','SL','Profit %','Sell Indicator']:buy_df[i]='-'
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
    buy_df=update_target_sl(buy_df)
    buy_df=update_ltp_buy_df(buy_df)
    buy_df=check_pnl_todays_trade(buy_df)
    st.session_state['todays_trade']=buy_df
    if len(buy_df)!=0:recheck_pnl()
    sl_container.text("Trail Sl:"+str(st.session_state['stop_loss']))
    buy_df = buy_df.sort_values(by=['Status', 'updatetime'], ascending=[False, True])
    todays_trade_datatable.dataframe(buy_df[['updatetime','tradingsymbol','price','quantity','ordertag','Exit Time','Status',
                                    'Sell', 'LTP', 'Profit','Target','SL', 'Profit %', 'Sell Indicator']],hide_index=True)
    return buy_df
  except Exception as e:
    logger.error(f"Error in get_todays_trade: {e}")
    buy_df= pd.DataFrame(columns = ['updatetime','tradingsymbol','price','quantity','ordertag','Exit Time','Status',
                                    'Sell', 'LTP', 'Profit','Target','SL', 'Profit %', 'Sell Indicator'])
    return buy_df

def close_day_end_trade():
  orderbook,pending_orders=get_order_book()
  buy_df=get_todays_trade(orderbook)
  for i in range(0,len(buy_df)):
    try:
      if buy_df['Status'].iloc[i]=="Pending":
        symboltoken=buy_df['symboltoken'].iloc[i]
        tradingsymbol=buy_df['tradingsymbol'].iloc[i]
        exch_seg=buy_df['exchange'].iloc[i]
        qty=buy_df['quantity'].iloc[i]
        price=buy_df['price'].iloc[i]
        ltp_price=buy_df['LTP'].iloc[i]
        orderid=buy_df['orderid'].iloc[i]
        indicator=buy_df['ordertag'].iloc[i]
        sl=buy_df['LTP'].iloc[i]
        trade_info = (
        f"{buy_df['tradingsymbol'].iloc[i]}\n"
        f"LTP:{buy_df['LTP'].iloc[i]} Target:{buy_df['Target'].iloc[i]} "
        f"SL:{buy_df['SL'].iloc[i]}\n"
        f"Price:{buy_df['price'].iloc[i]}\n"
        f"Time:{buy_df['updatetime'].iloc[i]}\n"
        f"Indicator: {buy_df['ordertag'].iloc[i]}\n"
        f"Profit: {int(buy_df['Profit'].iloc[i])}")
        ordertag=f"{ltp_price} : {orderid}"
        exit_position(symboltoken,tradingsymbol,exch_seg,qty,ltp_price,sl,ordertag='Day End:'+ordertag,producttype='CARRYFORWARD')
        multiline_string = "Day End: "+trade_info
        telegram_bot_sendtext(multiline_string)
        buy_df.loc[i,'Status']="Day End"
    except: pass
     
def multi_time_frame():
  st.session_state['options_trade_list']=[]
  try:
    for symbol in index_list:
      fut_data=get_historical_data(symbol=symbol,interval="5m",token="-",exch_seg="-",candle_type="NORMAL")
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
      index_ltp=fut_data['Close'].values[-1]
      st_7_3=fut_data['Supertrend'].values[-1]
      if symbol=="NIFTY":symbol_expiry=st.session_state['nf_expiry_day']
      elif symbol=="BANKNIFTY":symbol_expiry=st.session_state['bnf_expiry_day']
      elif symbol=="SENSEX":symbol_expiry=st.session_state['sensex_expiry_day']
      else:symbol_expiry="-"
      option_list=get_near_options(symbol,index_ltp,symbol_expiry)
      for i in range(0,len(option_list)):
        symbol_name=option_list['symbol'].iloc[i]
        token_symbol=option_list['token'].iloc[i]
        exch_seg=option_list['exch_seg'].iloc[i]
        qty=option_list['lotsize'].iloc[i]
        if ((index_ltp>st_7_3 and symbol_name[-2:]=='CE') or
            (index_ltp<st_7_3 and symbol_name[-2:]=='PE')):
          opt_data=get_historical_data(symbol=symbol_name,interval="1m",token=token_symbol,exch_seg=exch_seg)
          if opt_data['ST_7_3 Trade'].values[-1]=="Buy":
            strike_symbol=option_list.iloc[i]
            ltp=int(opt_data['Close'].values[-1])
            Supertrend=int(opt_data['Supertrend'].values[-1])
            tgt=int(2*(ltp-Supertrend))
            ordertag=f"Buy:Multi Time Frame ST LTP:{ltp}({Supertrend}:{tgt})"
            buy_option(symbol=strike_symbol,indicator_strategy=ordertag,interval="1m",index_sl="-")
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
  except Exception as e:pass

def pull_options_data(token_df_new):
  df = pd.DataFrame()
  dat=datetime.datetime.now(tz=gettz('Asia/Kolkata')).date()
  index_name=token_df_new['name'].values[0]
  fl_name=f"{index_name} Options {dat.strftime('%Y_%m_%d')}.csv"
  for i in range(len(token_df_new)):
    try:
      token=token_df_new['token'].values[i]
      symbol=token_df_new['symbol'].values[i]
      exch_seg=token_df_new['exch_seg'].values[i]
      expiry_day=token_df_new['expiry'].values[i]
      old_data=angel_data(token,'ONE_MINUTE',exch_seg,period=7)
      old_data=get_historical_data(symbol=symbol,interval='1m',token=token,exch_seg=exch_seg,candle_type="NORMAL")
      old_data['Symbol']=symbol
      old_data['Expiry']=expiry_day.strftime('%m/%d/%y')
      old_data=old_data[['Symbol','Expiry','Date','Datetime','Open','High','Low','Close']]
      df=pd.concat([df, old_data])
    except Exception as e:
      print('Error in Scan for:',symbol,e)
  st.download_button(label=fl_name,
                         data=df,
                         file_name=fl_name,
                         mime='text/csv',)

def index_back_data():
  dat=datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime("%Y-%m-%d")
  dat=datetime.datetime.now(tz=gettz('Asia/Kolkata')).date()
  symbol_list=['NIFTY','BANKNIFTY','SENSEX']
  for symbol in symbol_list:
    if ((symbol=='NIFTY' and dat==st.session_state['nf_expiry_day']) or 
        (symbol=='BANKNIFTY' and dat==st.session_state['bnf_expiry_day']) or
        (symbol=='SENSEX' and dat==st.session_state['sensex_expiry_day'])) :
      df=get_historical_data(symbol=symbol,interval='1m',token="-",exch_seg="-")
      df = df.round(decimals=2)
      df['Expiry']=dat.strftime('%m/%d/%y')
      df['Symbol']=symbol
      df=df[['Symbol','Expiry','Date','Datetime','Open','High','Low','Close']]
      high=(df['High'].max()+300)*100
      low=(df['Low'].min()-300)*100
      df=df.to_csv(index=False).encode('utf-8')
      fl_name=symbol +"_"+dat.strftime('%Y_%m_%d')+ ".csv"
      st.download_button(label=f"Download {symbol} as CSV",
                         data=df,
                         file_name=fl_name,
                         mime='text/csv',)
      token_df=st.session_state['opt_list']
      token_df_new = token_df[(token_df['name'] == symbol) & (token_df['instrumenttype'] == 'OPTIDX') & (token_df['expiry'] == dat)]
      token_df_new = token_df_new[(token_df_new['strike'] >= low) & (token_df_new['strike'] <= high) ]
      token_df_new.sort_values(by=['strike'], ascending = True, inplace=True)
      pull_options_data(token_df_new)
def index_backtest_old():
  todays_data = pd.DataFrame()
  dat=datetime.datetime.now(tz=gettz('Asia/Kolkata')).strftime("%Y-%m-%d")
  dat=datetime.datetime.now(tz=gettz('Asia/Kolkata')).date()
  symbol_list=['NIFTY','BANKNIFTY','SENSEX']
  for timeframe in ['1m','5m','15m']:
    for symbol in symbol_list:
      df=get_historical_data(symbol=symbol,interval=timeframe,token="-",exch_seg="-")
      df = df.round(decimals=2)
      df['Expiry']=dat.strftime('%m/%d/%y')
      df['Symbol']=symbol
      todays_data=pd.concat([df, todays_data])
  df=todays_data.to_csv(index=False).encode('utf-8')
  fl_name="Todays_Trade_"+dat.strftime('%Y_%m_%d')+ ".csv"
  st.download_button(label=f"Download as CSV",
                         data=df,
                         file_name=fl_name,
                         mime='text/csv',)

def index_backtest():
  todays_data = pd.DataFrame()
  dat=datetime.datetime.now(tz=gettz('Asia/Kolkata')).date()
  symbol_list=['^NSEI','^NSEBANK','^BSESN']
  for timeframe in ['1m','5m','15m']:
    for symbol in symbol_list:
      print(f'{symbol} {timeframe}')
      df=yfna_data(symbol,timeframe,'5')
      print(f'Data fetched {symbol} {timeframe}')
      df['Time Frame']=timeframe
      df.index.names = ['']
      df['VWAP']=pdta.vwap(high=df['High'],low=df['Low'],close=df['Close'],volume=df['Volume'])
      df=df[['Date','Datetime','Open','High','Low','Close','Volume','VWAP','Time Frame']]
      df['Symbol']=symbol
      df=calculate_indicator(df)
      print(f'Indicator calculated {symbol} {timeframe}')
      df['Option']="-"
      df['Option Token']="-"
      df['Option Exch']="-"
      df = df[(df['Date'] == dat)]
      for i in range(0,len(df)):
        if df['Trade'][i-1]!="-":
          symbol=df['Symbol'][i-1]
          indexLtp=df['Close'][i-1]
          indexLtp, ce_strike_symbol,pe_strike_symbol=get_ce_pe_data(symbol,indexLtp=indexLtp)
          if df['Trade'][i]=="Buy":
            df['Option'][i]=ce_strike_symbol['symbol']
            df['Option Token'][i]=ce_strike_symbol['token']
            df['Option Exch'][i]=ce_strike_symbol['exch_seg']
          else:
            df['Option'][i]=pe_strike_symbol['token']
            df['Option Token'][i]=pe_strike_symbol['symbol']
            df['Option Exch'][i]=pe_strike_symbol['exch_seg']
      todays_data=pd.concat([df, todays_data])
  df=todays_data.to_csv(index=False).encode('utf-8')
  fl_name="Todays_Trade_"+dat.strftime('%Y_%m_%d')+ ".csv"
  st.download_button(label=f"Download as CSV",data=df,file_name=fl_name,mime='text/csv',)

if algo_state:
  loop_code()
if nf_ce:
  indexLtp, ce_strike_symbol,pe_strike_symbol=get_ce_pe_data('NIFTY',indexLtp="-")
  buy_option(ce_strike_symbol,'Manual Buy','5m')
if nf_pe:
  indexLtp, ce_strike_symbol,pe_strike_symbol=get_ce_pe_data('NIFTY',indexLtp="-")
  buy_option(pe_strike_symbol,'Manual Buy','5m')
if bnf_ce:
  indexLtp, ce_strike_symbol,pe_strike_symbol=get_ce_pe_data('BANKNIFTY',indexLtp="-")
  buy_option(ce_strike_symbol,'Manual Buy','5m')
if bnf_pe:
  indexLtp, ce_strike_symbol,pe_strike_symbol=get_ce_pe_data('BANKNIFTY',indexLtp="-")
  buy_option(pe_strike_symbol,'Manual Buy','5m')
if restart:
  pass
login_details.text(f"Welcome:{st.session_state['Logged_in']} Login:{st.session_state['login_time']} Last Check:{st.session_state['last_check']}")
index_ltp_string.text(f"Index Ltp: {print_ltp()}")
if backtest: index_backtest()
if __name__ == "__main__":
  try:loop_code()
  except Exception as e:
    st.error(f"An error occurred: {e}")
    st.experimental_rerun()
