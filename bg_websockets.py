import asyncio
import websockets
import json
import datetime
import os
from collections import Counter
import binanceAPI

# connections = set()
# connections.add('wss://stream.binance.com:9443/stream?streams=btcusdt@ticker')
# connections.add('wss://stream.binance.com:9443/stream?streams=ethusdt@ticker')
# connections.add('wss://stream.binance.com:9443/stream?streams=fisusdt@ticker')

# Payload:
# {
#   "e": "trade",     // Event type
#   "E": 123456789,   // Event time
#   "s": "BNBBTC",    // Symbol
#   "t": 12345,       // Trade ID
#   "p": "0.001",     // Price
#   "q": "100",       // Quantity
#   "b": 88,          // Buyer order ID
#   "a": 50,          // Seller order ID
#   "T": 123456785,   // Trade time
#   "m": true,        // Is the buyer the market maker?
#   "M": true         // Ignore
# }

def timestamp2yyyymmddhhmmss(timestamp):
    return datetime.datetime.fromtimestamp(timestamp/1000).strftime('%Y-%m-%d %H:%M:%S')

# counter = Counter()
# counter2 = Counter()
# counter3 = Counter()

def solve(data):
    #time symbol price quantity
    print(f"{timestamp2yyyymmddhhmmss(data['T'])} {data['s']} {data['p']} {data['q']}")

async def handle_socket(pair, ):
    uri = f'wss://stream.binance.com:9443/stream?streams={pair}@trade'
    path = f'db/orders/{pair}.txt'
    while True:
        print(f'checking: {path}')
        #检测是否有挂单
        #扫描db/orders下的所有文件*.txt，如果有文件，文件名就是交易对的名称（例如，btcusdt.txt）
        # 就表示该交易对下有挂单，就需要订阅该交易对的ticker
        if os.path.exists(path):
            print("Connecting to", uri)
            async with websockets.connect(uri) as websocket:
                async for message in websocket:
                    message = json.loads(message)
                    data = message['data']
                    solve(data)
        else:
            #如果没有挂单，就不需要订阅该交易对的ticker
            #等待一秒，再检测是否有挂单
            await asyncio.sleep(1)

async def handler():
    sym_list = [a for a in binanceAPI.SYM_DICT]
    print(sym_list)
    await asyncio.gather(*[handle_socket(pair) for pair in sym_list])

asyncio.get_event_loop().run_until_complete(handler())