import asyncio
import websockets
import json
import datetime

connections = set()
connections.add('wss://stream.binance.com:9443/stream?streams=btcusdt@ticker')
connections.add('wss://stream.binance.com:9443/stream?streams=ethusdt@ticker')
connections.add('wss://stream.binance.com:9443/stream?streams=fisusdt@ticker')

def timestamp2yyyymmddhhmmss(timestamp):
    return datetime.datetime.fromtimestamp(timestamp/1000).strftime('%Y-%m-%d %H:%M:%S')

async def handle_socket(uri, ):
    counter = 0
    async with websockets.connect(uri) as websocket:
        
        async for message in websocket:
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
    await asyncio.gather(*[handle_socket(uri) for uri in connections])
    #await asyncio.wait(handle_socket(connections[0]))
    #await asyncio.wait([handle_socket(uri) for uri in connections])

asyncio.get_event_loop().run_until_complete(handler())