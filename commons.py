import random
import requests
import time
import functools
from collections import *
import copy
import binanceAPI
import client
import json

up_triangle = '▲'
down_triangle = '▼'

local_url = 'https://aitrad.in/'

#最大杠杆倍数
max_leverage_ratio = 20

#交易手续费
fees_ratio = 0.001

#获取时间戳（十秒）
def get_ts10():
    return int(time.time() / 10)

def get_total_balance(user_account):
    #总资产
    #本金 = USDT余额 + BTC数量*当前价格
    ts10 = get_ts10()
    price_btc = get_price_btc(ts10)
    price_eth = get_price_eth(ts10)
    #price_symbol = get_price_symbol(curr_usdt)
    balance = 0
    for symbol in user_account:
        if symbol == 'USDT':
            delta = user_account[symbol]
        elif symbol == 'BTC':
            delta = user_account[symbol] * price_btc
        elif symbol == 'ETH':
            delta = user_account[symbol] * price_eth
        else:
            curr_usdt = symbol + 'USDT'
            price_symbol = get_price_symbol(curr_usdt, ts10)
            delta = user_account[symbol] * price_symbol
        balance += delta
    return balance

def get_leverage_amount(user_account):
    #杠杆金额
    #本金 = USDT余额 + BTC数量*当前价格
    # 当USDT余额为负数时，杠杆金额为:abs(USDT余额)
    # 当BTC数量为负数时，杠杆金额为:abs(BTC数量)*当前价格
    ts10 = get_ts10()
    price_btc = get_price_btc(ts10)
    price_eth = get_price_eth(ts10)
    #price_symbol = get_price_symbol(curr_usdt)
    leverage = 0
    for symbol in user_account:
        if symbol == 'USDT':
            delta = user_account[symbol]
        elif symbol == 'BTC':
            delta = user_account[symbol] * price_btc
        elif symbol == 'ETH':
            delta = user_account[symbol] * price_eth
        else:
            curr_usdt = symbol + 'USDT'
            price_symbol = get_price_symbol(curr_usdt, ts10)
            delta = user_account[symbol] * price_symbol
        if delta < 0:
            leverage -= delta
    return leverage

def get_leverage(user_account):
    #杠杆率
    #杠杆率 = 杠杆金额 / 总资产
    leverage = get_leverage_amount(user_account) / get_total_balance(user_account)
    return leverage

@functools.lru_cache
def get_price_btc(ts10):
    # 获取当前BTCUSDT价格
    url = 'https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT'
    r = requests.get(url)
    price = float(r.json()['price'])
    return price

@functools.lru_cache
def get_price_eth(ts10):
    # 获取当前ETHUSDT价格
    url = 'https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT'
    r = requests.get(url)
    price = float(r.json()['price'])
    return price

@functools.lru_cache
def get_price_symbol(symbol, ts10):
    # 获取当前symbol价格
    url = 'https://api.binance.com/api/v3/ticker/price?symbol=' + symbol
    r = requests.get(url)
    price = float(r.json()['price'])
    return price

def get_tsms():
    return int(time.time() * 1000)
    
#获取随机字符串
def ramdom_str(length):
    str = ''
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    for i in range(length):
        str += chars[random.randint(0, len(chars) - 1)]
    return str

def get_market_data(cli,usdt_on,period):
    data1d = get_binance_ticker(cli,usdt_on,period)
    symbolinfo = defaultdict(dict)
    for d1d in data1d:
        symbol = d1d["symbol"]
        symbolinfo[symbol]["price"] = d1d["lastPrice"]
        symbolinfo[symbol]["Change1d"] = d1d["priceChangePercent"]
        symbolinfo[symbol]["Volume1d"] = d1d["quoteVolume"]
    data = []
    for symbol in symbolinfo:
        info = symbolinfo[symbol]
        data.append([symbol,float(info["price"]),float(info["Volume1d"]),float(info["Change1d"])])
    data = [[d[0],d[1],d[2],d[3]] for d in data]
    return data

def get_binance_ticker(cli,usdt_on,interval):
    key=(usdt_on,interval)
    if key in cli.ticker_cache:
        return cli.ticker_cache[key]
    if 'M' in interval or 'y' in interval:
        interval = '7d'
    if usdt_on:
        url = local_url + "ticker_u/" + interval
    else:
        url = local_url + "ticker_b/" + interval
    print(url)
    data = requests.get(url).json()
    cli.ticker_cache[key] = copy.deepcopy(data)
    return data

#获取币种报价
@functools.lru_cache
def get_quote_price(quote, ts10):
    return get_base_price(quote, ts10)

#获取基准价格
@functools.lru_cache
def get_base_price(base, ts10):
    if base == 'USDT' or base == 'BUSD':
        return 1
    elif base == 'BTC':
        return get_price_btc(ts10)
    elif base == 'ETH':
        return get_price_eth(ts10)
    else:
        curr_usdt = base + 'USDT'
        return get_price_symbol(curr_usdt, ts10)

#分离交易对
# BTCUSDT -> BTC, USDT
# ETHBTC -> ETH, BTC
# EOSETH -> EOS, ETH
# BTCBUSD -> BTC, BUSD
@functools.lru_cache
def split_quote_base(symbol):
    return binanceAPI.SYM_DICT[symbol][1:]

#读取users.json,计算每个人的账户价值（USDT单位），注册时间，交易次数，排序，计算出排行榜
def get_rank_list(cli: client.client):
    #读取users.json
    with open('users.json', 'r') as f:
        users = json.load(f)
    cur_tsms = get_tsms()
    user_list = []
    for user in users:
        u = users[user]
        user_account = u['account']
        #计算每个人的账户价值（USDT单位）
        total_balance = get_total_balance(user_account)
        #注册时间(ms)
        register_time = u['reg_time']
        #天数
        days = (cur_tsms - register_time) / 1000 / 60 / 60 / 24
        #保留两位小数
        days = round(days, 2)
        #交易次数
        trade_count = int(u['trade_count'])
        #用户名
        username = u['name']
        #用户清单
        user_list.append([username, total_balance, trade_count, days, 0])
    #添加特殊用户：基准账户
    user_list.append(['基准账户', 1000000, 0, 0, 0])
    #将用户按账户价值倒序排序
    user_list.sort(key=lambda x: x[1], reverse=True)
    #计算排名:user_list[i][4]
    #相同余额，排名相同
    rank = 1
    for i in range(len(user_list)):
        if i > 0 and user_list[i][1] < user_list[i - 1][1]:
            rank = i + 1
        user_list[i][4] = rank
    my_rank, my_days = 0, 0
    if cli.user_key:
        for i in range(len(user_list)):
            if user_list[i][0] == cli.user_key:
                my_rank = user_list[i][4]
                my_days = user_list[i][3]
                break
    return user_list, my_rank, my_days