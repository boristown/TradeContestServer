import asyncio
import websockets
import json

connections = set()
connections.add('wss://stream.binance.com:9443/stream?streams=btcusdt@ticker')
connections.add('wss://stream.binance.com:9443/stream?streams=ethusdt@ticker')

async def handle_socket(uri, ):
    counter = 0
    async with websockets.connect(uri) as websocket:
        
        async for message in websocket:
            message = json.loads(message)            
            data = message["data"]
            
            print(f"\n---Raw Data---\n{data}")
            print("\n---Parsed Data---\n")
            print(f"STREAM NAME: {message['stream']}")
            print(f"TIMESTAMP:{data['E']}")
            print(f"LAST PRICE:{data['c']}")
            print(f"LAST QUANTITY:{data['q']}")
            print(f"24h HIGH: {data['h']}")
            print("\n------\n")
async def handler():
    await asyncio.wait([handle_socket(uri) for uri in connections])

asyncio.get_event_loop().run_until_complete(handler())