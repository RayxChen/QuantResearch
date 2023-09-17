#!/usr/bin/env python3

#import WebSocket client library (and others)
import sys
import json
import signal
import time
import _thread
import websocket

#import numpy as np
import pandas as pd


# Parse command line arguments (symbol and depth)
if len(sys.argv) < 3:
    sys.exit(1)
else:
    api_symbol = sys.argv[1]
    api_depth = int(sys.argv[2])

# Define order book variables
api_book = {'bid':{}, 'ask':{} }

def to_int(x, shift):
    return int(float(x)*shift)

#price_pow = 10, vol_pow = 10**8, timestamp_pow = 10**6
def build_int(price, vol, ts):
    '''price, vol, ts: string,
    timestamp string: '1665671311.165199', rm starting 16'''
    inte, frac = ts.split('.')
    return to_int(price, 10), to_int(vol, 100000000), int(inte[2:]), int(frac)


power = [10, 10**8, 10**6]
def power_shift(x, i):
    return int(float(x)*power[i])

# Define order book update functions
def dicttofloat(data):
    return float(data[0])

def api_book_update(api_book_side, api_book_data):
    for data in api_book_data:
        price_level = data[0]
        volume = data[1]
        timestamp = data[2]
        # add
        if float(volume) > 0.0:
            api_book[api_book_side][price_level] = [volume, timestamp]
        # delete
        else:
            api_book[api_book_side].pop(price_level)
        if api_book_side == 'bid':
            api_book['bid'] = dict(sorted(api_book['bid'].items(), key=dicttofloat, reverse=True)[:api_depth])
        elif api_book_side == 'ask':
            api_book['ask'] = dict(sorted(api_book['ask'].items(), key=dicttofloat)[:api_depth])


# Define WebSocket callback functions
def ws_thread(*args):
    ws = websocket.WebSocketApp('wss://ws.kraken.com/', on_open=ws_open, on_message=ws_message)
    ws.run_forever()

def ws_open(ws):
    ws.send('{"event":"subscribe", "subscription":{"name":"book", "depth":%(api_depth)d}, "pair":["%(api_symbol)s"]}' % {'api_depth':api_depth, 'api_symbol':api_symbol})

def ws_message(ws, ws_data):
    api_data = json.loads(ws_data)
#    print('api_data',api_data)
    if 'event' in api_data:
        return
    else:
        # initial snapshot
        if 'as' in api_data[1]:
            api_book_update('ask', api_data[1]['as'])
            api_book_update('bid', api_data[1]['bs'])
        # update
        else:
            for data in api_data[1:len(api_data)-2]:
                if 'a' in data:
                    api_book_update('ask', data['a'])
                elif 'b' in data:
                    api_book_update('bid', data['b'])

def save_data(bid_ask):
    df = pd.DataFrame(bid_ask, columns=['bid_price', 'bid_vol', 'bid_time_int', 'bid_time_frac', 'ask_price', 'ask_vol', 'ask_time_int', 'ask_time_frac'], dtype='uint32')
    df.to_hdf('new_data.h5',key='kraken_OB_price', mode='a')


if __name__ == "__main__":
    
    # Start new thread for WebSocket interface
    _thread.start_new_thread(ws_thread, ())
    
    # Output order book (once per second) in main thread
    try:
        while True:
            if len(api_book['bid']) < api_depth or len(api_book['ask']) < api_depth:
                time.sleep(1)
            else:
                bid = sorted(api_book['bid'].items(), key=dicttofloat, reverse=True)
                ask = sorted(api_book['ask'].items(), key=dicttofloat)
                bid_ask = [[*build_int(x[0], *x[1]), *build_int(y[0], *y[1])] for x, y in zip(bid, ask)]
                save_data(bid_ask)
                time.sleep(1)
    except KeyboardInterrupt:
        sys.exit(0)
