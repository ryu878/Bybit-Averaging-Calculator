# (C) 2022 Ryan Hayabusa 2022 
# Github: https://github.com/ryu878 
# Discord: ryuryu#4087
# Mail: ev4AR2xihu3xXcdbYy5djGpfe01@gmail.com
#######################################################################################################
import ta
import ccxt
import time
import pandas as pd
from config import *
from inspect import currentframe
from pybit import usdt_perpetual
from binance.client import Client
from colorama import init, Fore, Back, Style



title = 'Ryuryu\'s Bybit Averaging Calculator '
ver = 'v0.1'


terminal_title = title + ver
print(f'\33]0;{terminal_title}\a', end='', flush=True)


exchange = ccxt.bybit({'apiKey':api_key,'secret':api_secret})
binance_client = Client(binance_api_key, binance_api_secret)
client = usdt_perpetual.HTTP(endpoint=endpoint,api_key=api_key,api_secret=api_secret)


symbol = input(' What Asset To check? ')
symbol = (symbol+'USDT').upper()
# symbol = 'DOGEUSDT'


def get_linenumber():
    cf = currentframe()
    global line_number
    line_number = cf.f_back.f_lineno


def get_orderbook():

    orderbook = exchange.fetchOrderBook(symbol=symbol, limit=10)
    global ask
    global bid
    bid = orderbook['bids'][0][0] if len (orderbook['bids']) > 0 else None
    ask = orderbook['asks'][0][0] if len (orderbook['asks']) > 0 else None


def get_decimals():

    symbol_decimals  = client.query_symbol()
    for decimal in symbol_decimals['result']:
        if decimal['name'] == symbol:
            global decimals
            global leverage
            global tick_size
            global min_trading_qty
            global qty_step
            decimals = decimal['price_scale']
            leverage = decimal['leverage_filter']['max_leverage']
            tick_size = decimal['price_filter']['tick_size']
            min_trading_qty = decimal['lot_size_filter']['min_trading_qty']
            qty_step = decimal['lot_size_filter']['qty_step']


def get_position():
    positions = client.my_position(symbol=symbol)
    for position in positions['result']:
        if position['side'] == 'Sell':
            global sell_position_size
            global sell_position_prce
            sell_position_size = position['size']
            sell_position_prce = position['entry_price']
        if position['side'] == 'Buy':
            global buy_position_size
            global buy_position_prce
            buy_position_size = position['size']
            buy_position_prce = position['entry_price']


def get_ema_3_1_low_bybit():

    bars_to_check = 3
    bars = exchange.fetchOHLCV(symbol=symbol, timeframe='1m', limit=bars_to_check*3)
    df = pd.DataFrame(bars,columns=['Time','Open','High','Low','Close','Vol'])
    df['EMA 3-1 Low'] = ta.trend.EMAIndicator(df['Low'], window=bars_to_check).ema_indicator()
    global ema_3_1_low_bybit
    ema_3_1_low_bybit = round((df['EMA 3-1 Low'][(bars_to_check*3)-1]).astype(float),decimals)


def get_ema_6_1_low_bybit():
    
    bars_to_check = 6
    bars = exchange.fetchOHLCV(symbol=symbol, timeframe='1m', limit=bars_to_check*3)
    df = pd.DataFrame(bars,columns=['Time','Open','High','Low','Close','Vol'])
    df['EMA 6-1 Low'] = ta.trend.EMAIndicator(df['Low'], window=bars_to_check).ema_indicator()
    global ema_6_1_low_bybit
    ema_6_1_low_bybit = round((df['EMA 6-1 Low'][(bars_to_check*3)-1]).astype(float),decimals)


def get_ema_27_1_binance():

    bars_to_check = 27
    bars = binance_client.futures_klines(symbol=symbol, interval='1m', limit=bars_to_check*3)
    df = pd.DataFrame(bars, columns=['Time','Open','High','Low','Close','Vol','1','2','3','4','5','6'])
    df['EMA 27-1 Close'] = ta.trend.EMAIndicator(df['Close'], window=bars_to_check).ema_indicator()
    global ema_27_1_binance
    ema_27_1_binance = round((df['EMA 27-1 Close'][(bars_to_check*3)-1]).astype(float),decimals)


while True:

    get_decimals()
    time.sleep(0.1)
    get_position()
    time.sleep(0.1)

    print(' ───────────────────────────────')
    print('  Position size:',sell_position_size)
    print(' Position price:',sell_position_prce)
    print(' ───────────────────────────────')

    get_ema_3_1_low_bybit()
    time.sleep(0.1)
    get_ema_6_1_low_bybit()
    time.sleep(0.1)
    get_ema_27_1_binance()

    print('      EMA 3 low:',ema_3_1_low_bybit)
    print('         EMA 27:',ema_27_1_binance)
    get_orderbook()
    print('  Current price:',ask)
    print(' ───────────────────────────────')

    n1 = sell_position_size
    p1 = sell_position_prce
    p2 = ask
    p31 = ema_3_1_low_bybit
    p61 = ema_6_1_low_bybit
    n31 = n1*(p31-p1)/(p2-p31)
    n61 = n1*(p61-p1)/(p2-p61)

    if ema_6_1_low_bybit > sell_position_prce and ema_3_1_low_bybit > sell_position_prce:
        print(' Orders to add to set price on EMA 3 low:',round(n31,decimals))
        print(' Orders to add to set price on EMA 6 low:',round(n61,decimals))
        print('')
    else:
        print(' Nothing to calculate')
        print('')

    time.sleep(33)
