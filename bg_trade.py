import asyncio
import websockets
import json

connections = set()
connections.add('wss://stream.binance.com:9443/stream?streams=btcusdt@ticker')
connections.add('wss://stream.binance.com:9443/stream?streams=ethusdt@ticker')
connections.add('wss://stream.binance.com:9443/stream?streams=fisusdt@ticker')

async def handle_socket(uri, ):
    counter = 0
    async with websockets.connect(uri) as websocket:
        
        async for message in websocket:
            message = json.loads(message)            
            data = message["data"]
            
            #print(f"\n---Raw Data---\n{data}")
            #print("\n---Parsed Data---\n")
            print(f"流名称: {message['stream']}")
            print(f"时间戳:{data['E']}")
            print(f"最后价格:{data['c']}")
            print(f"最后交易量:{data['q']}")
            print(f"24小时最高价: {data['h']}")
            print("\n------\n")
async def handler():
    await asyncio.gather(*[handle_socket(uri) for uri in connections])
    #await asyncio.wait(handle_socket(connections[0]))
    #await asyncio.wait([handle_socket(uri) for uri in connections])

asyncio.get_event_loop().run_until_complete(handler())