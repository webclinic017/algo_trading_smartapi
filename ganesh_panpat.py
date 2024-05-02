import streamlit as st
from streamlit.logger import get_logger
import yfinance as yf
import datetime
import time
from dateutil.tz import gettz
import pandas as pd
import pandas_ta as pdta
LOGGER = get_logger(__name__)
st.set_page_config(page_title="Algo App",layout="wide",initial_sidebar_state="expanded",)
st.markdown("""
  <style>
    .block-container {padding-top: 0.5rem;padding-bottom: 0rem;padding-left: 2rem;padding-right: 5rem;}
  </style>
  """, unsafe_allow_html=True)
st.write("# Welcome to My Algo!")
start=st.button("Start")
order_book_updated=st.empty()
order_book_updated.text(f"Orderbook : ")
order_datatable=st.empty()

#Calculate Indicator
#update Buy and Sell trade info
def get_trade_info(df):
  for i in ['ST_7_3 Trade','MACD Trade','PSAR Trade','DI Trade','MA Trade','EMA Trade','BB Trade','Trade','Trade End',
            'Rainbow MA','Rainbow Trade','MA 21 Trade','ST_10_2 Trade','Two Candle Theory','HMA Trade','VWAP Trade',
            'EMA_5_7 Trade','ST_10_4_8 Trade','EMA_High_Low Trade','RSI MA Trade','RSI_60 Trade','ST_10_1 Trade','TEMA_EMA_9 Trade']:df[i]='-'
  if df['Time Frame'][0]=="3m" or df['Time Frame'][0]=="THREE MINUTE" or df['Time Frame'][0]=="3min": df['Time Frame']="3m";time_frame="3m"
  elif df['Time Frame'][0]=="5m" or df['Time Frame'][0]=="FIVE MINUTE" or df['Time Frame'][0]=="5min": df['Time Frame']="5m";time_frame="5m"
  elif df['Time Frame'][0]=="15m" or df['Time Frame'][0]=="FIFTEEN MINUTE" or df['Time Frame'][0]=="15min": df['Time Frame']="15m";time_frame="15m"
  elif df['Time Frame'][0]=="1m" or df['Time Frame'][0]=="ONE MINUTE" or df['Time Frame'][0]=="1min": df['Time Frame']="1m";time_frame="1m"
  time_frame=df['Time Frame'][0]
  if time_frame=="5m":indicator_list=['ST_7_3 Trade','ST_10_2 Trade','RSI_60 Trade']
  elif time_frame=="15m":indicator_list=['ST_7_3 Trade','ST_10_2 Trade','RSI_60 Trade']
  elif time_frame=="1m":indicator_list=['TEMA_EMA_9 Trade']
  elif time_frame=="3m":indicator_list=[]
  else:indicator_list=['ST_7_3 Trade','ST_10_2 Trade','TEMA_EMA_9 Trade','RSI_60 Trade']
  Symbol=df['Symbol'][0]
  for i in range(0,len(df)):
    try:
      #df['Date'][i]=df['Datetime'][i].strftime('%Y.%m.%d')
      if df['Close'][i-1]<=df['Supertrend'][i-1] and df['Close'][i]> df['Supertrend'][i]: df['ST_7_3 Trade'][i]="Buy"
      elif df['Close'][i-1]>=df['Supertrend'][i-1] and df['Close'][i]< df['Supertrend'][i]: df['ST_7_3 Trade'][i]="Sell"

      if df['MACD'][i]>df['MACD signal'][i] and df['MACD'][i-1]< df['MACD signal'][i-1]: df['MACD Trade'][i]="Buy"
      elif df['MACD'][i]<df['MACD signal'][i] and df['MACD'][i-1]> df['MACD signal'][i-1]: df['MACD Trade'][i]="Sell"

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

      if df['Close'][i-1]< df['Supertrend_10_2'][i-1] and df['Close'][i]> df['Supertrend_10_2'][i]: df['ST_10_2 Trade'][i]="Buy"
      elif df['Close'][i-1]> df['Supertrend_10_2'][i-1] and df['Close'][i]< df['Supertrend_10_2'][i]: df['ST_10_2 Trade'][i]="Sell"

      if df['Close'][i-1]< df['Supertrend_10_1'][i-1] and df['Close'][i]> df['Supertrend_10_1'][i]: df['ST_10_1 Trade'][i]="Buy"
      elif df['Close'][i-1]> df['Supertrend_10_1'][i-1] and df['Close'][i]< df['Supertrend_10_1'][i]: df['ST_10_1 Trade'][i]="Sell"

      #if df['HMA_21'][i-1]< df['HMA_55'][i-1] and df['HMA_21'][i]> df['HMA_55'][i]: df['HMA Trade'][i]="Buy"
      #elif df['HMA_21'][i-1]> df['HMA_55'][i-1] and df['HMA_21'][i]< df['HMA_55'][i]: df['HMA Trade'][i]="Sell"

      if df['Tema_9'][i-1]< df['EMA_9'][i-1] and df['Tema_9'][i]> df['EMA_9'][i]: df['TEMA_EMA_9 Trade'][i]="Buy"
      elif df['Tema_9'][i-1]> df['EMA_9'][i-1] and df['Tema_9'][i]< df['EMA_9'][i]: df['TEMA_EMA_9 Trade'][i]="Sell"

      if int(df['RSI'][i])>=60 and int(df['RSI'][i-1]) < 60 : df['RSI_60 Trade'][i]="Buy"

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

      for indicator in indicator_list:
        if df[indicator][i]=="Buy":
          df['Trade'][i]="Buy"
          df['Trade End'][i]="Buy"
          break
        elif df[indicator][i]=="Sell":
          df['Trade'][i]="Sell"
          df['Trade End'][i]="Sell"
          break
        else:
          df['Trade'][i]="-"
          df['Trade End'][i]="-"
    except Exception as e:
      pass
  #df['ADX']=df['ADX'].round(decimals = 2)
  #df['ADX']= df['ADX'].astype(str)
  df['Atr']=df['Atr'].round(decimals = 2)
  df['Atr']= df['Atr'].astype(str)
  df['RSI']=df['RSI'].round(decimals = 2)
  df['RSI']= df['RSI'].astype(str)
  if Symbol=="^NSEBANK" or Symbol=="BANKNIFTY" or Symbol=="^NSEI" or Symbol=="NIFTY" or Symbol=="SENSEX" or Symbol=="^BSESN":
    symbol_type="IDX"
  else: symbol_type= "OPT"
  df['Indicator']=(symbol_type+" "+df['Trade']+" "+df['Time Frame']+":"+" ST_7_3:"+df['ST_7_3 Trade']+
                   " ST_10_2:"+df['ST_10_2 Trade']+ " ST_10_1:"+df['ST_10_1 Trade']+ " MACD:"+df['MACD Trade']+
                   " TEMA_EMA_9:"+df['TEMA_EMA_9 Trade']+ " RSI_60:"+df['RSI_60 Trade'])
  df['RSI']= df['RSI'].astype(float)
  df['Indicator'] = df['Indicator'].str.replace(' ST_7_3:-','')
  #df['Indicator'] = df['Indicator'].str.replace(' EMA:-','')
  #df['Indicator'] = df['Indicator'].str.replace(' MA:-','')
  df['Indicator'] = df['Indicator'].str.replace(' MACD:-','')
  df['Indicator'] = df['Indicator'].str.replace(' ST_10_2:-','')
  df['Indicator'] = df['Indicator'].str.replace(' ST_10_1:-','')
  #df['Indicator'] = df['Indicator'].str.replace(' HMA:-','')
  #df['Indicator'] = df['Indicator'].str.replace(' MA_21:-','')
  #df['Indicator'] = df['Indicator'].str.replace(' EMA_5_7 Trade:-','')
  #df['Indicator'] = df['Indicator'].str.replace(' EMA_5_7:-','')
  #df['Indicator'] = df['Indicator'].str.replace(' VWAP:-','')
  #df['Indicator'] = df['Indicator'].str.replace(' EMA_H_L:-','')
  #df['Indicator'] = df['Indicator'].str.replace(' Two Candle Theory:-','')
  df['Indicator'] = df['Indicator'].str.replace(' RSI_60:-','')
  df['Indicator'] = df['Indicator'].str.replace(' TEMA_EMA_9:-','')
  df['Indicator'] = df['Indicator'].str.replace(':Buy',',')
  df['Indicator'] = df['Indicator'].str.replace(':Sell',',')
  #df['Indicator'] = df['Indicator'].str.replace('3m Two Candle Theory:','2 Candle Theory:')
  df["Indicator"] = df["Indicator"].str[:-1]
  return df
def calculate_indicator(df):
  try:
    df['RSI']=pdta.rsi(df['Close'],timeperiod=14)
    #df['UBB']=pdta.bbands(df['Close'],length=20, std=2, ddof=0)['BBU_20_2.0']
    #df['MBB']=pdta.bbands(df['Close'],length=20, std=2, ddof=0)['BBM_20_2.0']
    #df['LBB']=pdta.bbands(df['Close'],length=20, std=2, ddof=0)['BBL_20_2.0']
    df['MACD']=pdta.macd(close=df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)['MACD_12_26_9']
    df['MACD signal']=pdta.macd(close=df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)['MACDs_12_26_9']
    df['Macdhist']=pdta.macd(close=df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)['MACDh_12_26_9']
    df['Supertrend']=pdta.supertrend(high=df['High'],low=df['Low'],close=df['Close'],length=7,multiplier=3)['SUPERT_7_3.0']
    df['Supertrend_10_2']=pdta.supertrend(high=df['High'],low=df['Low'],close=df['Close'],length=10,multiplier=2)['SUPERT_10_2.0']
    df['Supertrend_10_1']=pdta.supertrend(high=df['High'],low=df['Low'],close=df['Close'],length=10,multiplier=1)['SUPERT_10_1.0']
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
    df['Atr']=pdta.atr(high=df['High'], low=df['Low'], close=df['Close'], length=14)
    #df['HMA_21']=pdta.hma(df['Close'],length=21)
    #df['HMA_55']=pdta.hma(df['Close'],length=55)
    #df['RSI_MA']=df['RSI'].rolling(14).mean()
    #df['EMA_High']=pdta.ema(df['High'],length=21)
    #df['EMA_Low']=pdta.ema(df['Low'],length=21)
    df['Tema_9']=pdta.tema(df['Close'],9)
    df['EMA_9']=pdta.ema(df['Close'],length=6)
    #df = df.round(decimals=2)
    df=get_trade_info(df)
    return df
  except Exception as e:
    print("Error in calculate Indicator",e)
    return df
    
def get_yf_data(symbol,interval):
  df=yf.Ticker(symbol).history(interval=interval,period=str(2)+"d")
  df['Datetime'] = df.index
  df['Datetime']=df['Datetime'].dt.tz_localize(None)
  df.index=df['Datetime']
  df=df[['Datetime','Open','High','Low','Close','Volume']]
  df['Date']=df['Datetime'].dt.strftime('%m/%d/%y')
  df['Datetime'] = pd.to_datetime(df['Datetime']).dt.time
  df['Symbol']=symbol
  df['Time Frame']=interval
  df['Time']=datetime.datetime.now(tz=gettz('Asia/Kolkata')).time()
  df=df[['Symbol','Time','Date','Datetime','Open','High','Low','Close','Volume']]
  df=calculate_indicator(df)
  df=df.round(2)
  return df.tail(1)
  
def sub_loop(interval=5):
  df=pd.DataFrame()
  for symbol in ['^NSEI','^NSEBANK','^BSESN']:
    yf_data=get_yf_data(symbol,str(interval)+"m")
    df=pd.concat([df,yf_data])
  return df
def run():
  for i in range(100):
    df=sub_loop(5)
    order_datatable.dataframe(df,hide_index=True)
    order_book_updated.text(f"Orderbook : {datetime.datetime.now(tz=gettz('Asia/Kolkata')).time().replace(microsecond=0)}")
    now=datetime.datetime.now(tz=gettz('Asia/Kolkata'))
    time.sleep(60-now.second+1)
if start==True:
  run()
