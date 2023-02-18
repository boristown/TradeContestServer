import asyncio
import my_websockets
import json
import datetime
import os
from collections import Counter
import binanceAPI
import bisect
import on_event
import collections

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
#   "b": 88,          // Buyer order ID;
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

def update_order_limit_buy(timestamp,symbol,price,orders:collections.deque):
    n = len(orders)
    if n == 0: return
    #1.1 限价买入单，如果价格低于挂单价格，就执行挂单，然后删除该挂单
    #找到第一个大于price的订单
    posr = bisect.bisect_right(orders,price,key=lambda x:x[0])
    #更新posr以及posr之后的订单
    for i in range(posr,n):
        order_id = orders[i][1]
        order_price = orders[i][0]
        user_key = orders[i][2]
        on_event.execute_limit_buy(user_key, order_id, symbol ,order_price, timestamp)
    for i in range(posr,n):
        orders.pop()

def update_order_limit_sell(timestamp,symbol,price,orders:collections.deque):
    n = len(orders)
    if n == 0: return
    #1.2 限价卖出单，如果价格高于挂单价格，就执行挂单，然后删除该挂单
    #找到第一个大于等于price的订单
    posl = bisect.bisect_left(orders,price,key=lambda x:x[0])
    #更新posl之前的订单
    for i in range(posl):
        order_id = orders[i][1]
        order_price = orders[i][0]
        user_key = orders[i][2]
        on_event.execute_limit_sell(user_key, order_id, symbol ,order_price, timestamp)
    for i in range(posl):
        orders.popleft()

def update_order_trend_buy(timestamp,symbol,price,orders:collections.deque):
    n = len(orders)
    if n == 0: return
    #1.3 趋势追踪买入单，如果市场价格高于或等于挂单价格，就执行挂单，然后删除该挂单
    #找到第一个大于price的订单
    posr = bisect.bisect_right(orders,price,key=lambda x:x[0])
    #更新posr之前的订单
    for i in range(posr):
        order_id = orders[i][1]
        order_price = orders[i][0]
        user_key = orders[i][2]
        on_event.execute_trend_buy(user_key, order_id, symbol ,price, timestamp)
    for i in range(posr):
        orders.popleft()

def update_order_trend_sell(timestamp,symbol,price,orders:collections.deque):
    n = len(orders)
    if n == 0: return
    #1.4 趋势追踪卖出单，如果市场价格低于或等于挂单价格，就执行挂单，然后删除该挂单
    #找到第一个大于等于price的订单
    posl = bisect.bisect_left(orders,price,key=lambda x:x[0])
    #更新posl之后的订单
    for i in range(posl,n):
        order_id = orders[i][1]
        order_price = orders[i][0]
        user_key = orders[i][2]
        on_event.execute_trend_sell(user_key, order_id, symbol ,price, timestamp)
    for i in range(posl,n):
        orders.pop()

def update_order_stop_buy(timestamp,symbol,price,orders:dict):
    n = len(orders)
    if n == 0: return
    #1.5 止损买入单，如果市场从最低点上涨超过x%，就执行挂单，然后删除该挂单
    #首先需要用当前市场价格更新最低点价格low_price(如果当前价格低于low_price)
    #然后计算当前价格与low_price的比例，如果大于ratio_pec%，就执行挂单，然后删除该挂单
    #暴力枚举所有订单，逐个更新
    for key in orders.keys():
        order_item = orders[key]
        order_id = order_item[1]
        order_price = order_item[0]
        user_key = order_item[2]
        low_price = order_item[3]
        ratio_pec = order_item[4]
        if price < low_price:
            low_price = price
        order_item[3] = low_price
        current_ratio = (price - low_price) / low_price
        if current_ratio >= ratio_pec:
            on_event.execute_stop_buy(user_key, order_id, symbol ,price, timestamp)
            del orders[key]

def update_order_stop_sell(timestamp,symbol,price,orders):
    n = len(orders)
    if n == 0: return
    #1.6 止损卖出单，如果市场从最高点下跌超过x%，就执行挂单，然后删除该挂单
    #首先需要用当前市场价格更新最高点价格high_price(如果当前价格高于high_price)
    #然后计算high_price与当前价格的比例，如果大于ratio_pec%，就执行挂单，然后删除该挂单
    #暴力枚举所有订单，逐个更新
    for key in orders.keys():
        order_item = orders[key]
        order_id = order_item[1]
        order_price = order_item[0]
        user_key = order_item[2]
        high_price = order_item[3]
        ratio_pec = order_item[4]
        if price > high_price:
            high_price = price
        order_item[3] = high_price
        current_ratio = (high_price - price) / high_price
        if current_ratio >= ratio_pec:
            on_event.execute_stop_sell(user_key, order_id, symbol ,price, timestamp)
            del orders[key]

def update_order(timestamp,symbol,price,global_orders_pair):
    #1 更新限价买入单
    update_order_limit_buy(timestamp,symbol,price,global_orders_pair[0])
    #2 更新限价卖出单
    update_order_limit_sell(timestamp,symbol,price,global_orders_pair[1])
    #3 更新趋势追踪买入单
    update_order_trend_buy(timestamp,symbol,price,global_orders_pair[2])
    #4 更新趋势追踪卖出单
    update_order_trend_sell(timestamp,symbol,price,global_orders_pair[3])
    #5 更新追踪止损买入单
    update_order_stop_buy(timestamp,symbol,price,global_orders_pair[4])
    #6 更新追踪止损卖出单
    update_order_stop_sell(timestamp,symbol,price,global_orders_pair[5])

def solve(data,global_orders_pair):
    timestamp = data['T']
    symbol = data['s']
    price = data['p']
    update_order(timestamp,symbol,price,global_orders_pair)

async def handle_socket(pair, global_orders_pair):
    pair = pair.lower()
    uri = f'wss://stream.binance.com:9443/stream?streams={pair}@trade'
    path = f'db/orders/{pair}.txt'
    while True:
        #print(f'checking: {path}')
        #检测是否有挂单
        #扫描db/orders下的所有文件*.txt，如果有文件，文件名就是交易对的名称（例如，btcusdt.txt）
        # 就表示该交易对下有挂单，就需要订阅该交易对的ticker
        if os.path.exists(path):
            print(f"Connecting to {uri}")
            async with my_websockets.connect(uri) as websocket:
                async for message in websocket:
                    message = json.loads(message)
                    data = message['data']
                    solve(data, global_orders_pair)
        else:
            #如果没有挂单，就不需要订阅该交易对的ticker
            #等待一秒，再检测是否有挂单
            await asyncio.sleep(2)

async def handler(global_orders):
    sym_list = [a for a in binanceAPI.SYM_DICT]
    print(sym_list)
    await asyncio.gather(*[handle_socket(pair,global_orders[pair]) for pair in sym_list])

def start_listening(global_orders):
    asyncio.get_event_loop().run_until_complete(handler(global_orders))