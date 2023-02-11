import asyncio
import websockets
import json
import datetime
from collections import Counter

connections = set()
connections.add('wss://stream.binance.com:9443/stream?streams=btcusdt@ticker')
connections.add('wss://stream.binance.com:9443/stream?streams=ethusdt@ticker')
connections.add('wss://stream.binance.com:9443/stream?streams=fisusdt@ticker')

def timestamp2yyyymmddhhmmss(timestamp):
    return datetime.datetime.fromtimestamp(timestamp/1000).strftime('%Y-%m-%d %H:%M:%S')

counter = Counter()
counter2 = Counter()
counter3 = Counter()

async def handle_socket(uri, ):
    global counter
    global counter2
    global counter3
    counter[uri] += 1
    print(f"Connecting to {uri} ({counter[uri]})")
    async with websockets.connect(uri) as websocket:

        counter2[uri] += 1
        print(f"Connecting to {uri} ({counter2[uri]})")

        async for message in websocket:

            counter3[uri] += 1
            print(f"Connecting to {uri} ({counter3[uri]})")

            message = json.loads(message)
            data = message["data"]

            #输出：yyyymmddhhmmss 流名称 最新价格 USDT
            print(f"{timestamp2yyyymmddhhmmss(data['E'])} {message['stream']} {data['c']} USDT")
            
            #print(f"\n---Raw Data---\n{data}")
            #print("\n---Parsed Data---\n")
            # print(f"流名称: {message['stream']}")
            # print(f"时间戳:{data['E']}")
            # print(f"最后价格:{data['c']}")
            # print(f"最后交易量:{data['q']}")
            # print(f"24小时最高价: {data['h']}")
            # print("\n------\n")

async def handler():
    while True:
        await asyncio.gather(*[handle_socket(uri) for uri in connections])
        print("Restarting...")
        #await asyncio.sleep(43200)
    # await asyncio.gather(*[handle_socket(uri) for uri in connections])

asyncio.get_event_loop().run_until_complete(handler())