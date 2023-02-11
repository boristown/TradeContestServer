import asyncio
import websockets
import json
import datetime
import os
from collections import Counter

# connections = set()
# connections.add('wss://stream.binance.com:9443/stream?streams=btcusdt@ticker')
# connections.add('wss://stream.binance.com:9443/stream?streams=ethusdt@ticker')
# connections.add('wss://stream.binance.com:9443/stream?streams=fisusdt@ticker')

def timestamp2yyyymmddhhmmss(timestamp):
    return datetime.datetime.fromtimestamp(timestamp/1000).strftime('%Y-%m-%d %H:%M:%S')

counter = Counter()
counter2 = Counter()
counter3 = Counter()

async def handle_socket(uri, ):
    #global counter
    #global counter2
    #global counter3
    #counter[uri] += 1
    #print(f"[1]Connecting to {uri} ({counter[uri]})")
    async with websockets.connect(uri) as websocket:

        #counter2[uri] += 1
        #print(f"[2]Connecting to {uri} ({counter2[uri]})")

        async for message in websocket:

            #counter3[uri] += 1
            #print(f"[3]Connecting to {uri} ({counter3[uri]})")

            message = json.loads(message)
            data = message["data"]
    
            #订单处理
            for d in data:
                print(f"{timestamp2yyyymmddhhmmss(d['E'])} {d['s']} {d['c']} USDT")


async def handler():
    #扫描db/orders下的所有文件*.txt，如果有文件，文件名就是交易对的名称（例如，btcusdt.txt）
    # 就表示该交易对下有挂单，就需要订阅该交易对的ticker
    uri_prefix = '!miniTicker@arr'
    uri = 'wss://stream.binance.com:9443/ws/stream?streams=' + uri_prefix
    while True:
        #异步执行handle_socket(uri)
        await handle_socket(uri)
        # connections = set()
        # for filename in os.listdir('db/orders'):
        #     if filename.endswith('.txt'):
        #         pair = filename[:-4].lower()
        #         connections.add(f'wss://stream.binance.com:9443/stream?streams={pair}@miniTicker')
        # await asyncio.gather(*[handle_socket(uri) for uri in connections])
        print("Restarting Websockets...")

asyncio.get_event_loop().run_until_complete(handler())