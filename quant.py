import pandas as pd
import yfinance as yf
import numpy as np
import pandas_ta as ta
import streamlit as st
rr = pd.DataFrame()
rsi = pd.DataFrame()
#******************************Add your tickers and strategy here********************************
tickers = ['MOM100.NS','SILVERBEES.NS'] #tickers
def strategy(rr,rsi):
  buySignal=(rr < 0) & (rsi < 40)
  sellSignal=(rr > 0) & (rsi > 70)
  return buySignal,sellSignal
#*********************************************************************

st.set_page_config(page_title="Quant Signals", layout="wide")

@st.cache_data
def load_data(tickers):
    df = yf.download(tickers, period='5y', auto_adjust=False)['Adj Close']
    return df.ffill()

df = load_data(tickers)
def cal():
  for a in tickers:
    rr[a] = df[a].pct_change(periods=63) * 100
    rsi[a] = ta.rsi(df[a],period=30)
#Strategy
  signal_buy,signal_sell=strategy(rr,rsi)

  return signal_buy,signal_sell
signal_buy,signal_sell=cal()

def pair(a,buy,sell,df=df):
    paired = pd.merge_asof(
    buy,
    sell,
    left_on='Buy_Date',
    right_on='Sell_Date',
    direction='forward')
    paired = paired[paired['Buy_Date'] < paired['Sell_Date']]
    overlap = paired['Buy_Date'] <= paired['Sell_Date'].shift(1)
    paired = paired[~overlap]
    paired['Buy_Price'] =(df.loc[paired['Buy_Date'],a].values)
    paired['Sell_Price'] = df.loc[paired['Sell_Date'],a].values

    return paired

def show(a, signal_buy=signal_buy, signal_sell=signal_sell):
    buy = (
        signal_buy[a]
        .loc[signal_buy[a]]
        .reset_index()
        .rename(columns={'Date': 'Buy_Date'})
    )

    sell = (
        signal_sell[a]
        .loc[signal_sell[a]]
        .reset_index()
        .rename(columns={'Date': 'Sell_Date'})
    )

    buy = buy.sort_values('Buy_Date')
    sell = sell.sort_values('Sell_Date')

    p = pair(a, buy, sell)
    p['Return%'] = ((p['Sell_Price'] - p['Buy_Price']) / p['Buy_Price']) * 100

    st.dataframe(p)


#Streamlit
st.sidebar.header("Select Stock")
stock = st.sidebar.selectbox("Choose", tickers)
st.write(df.columns)

st.title("Quant Trading Signals")
st.write(stock)
result = show(stock)
