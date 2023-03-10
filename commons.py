import random
import requests
import time
import functools
from collections import *
import copy
import binanceAPI
import client
import json
import db
from pyecharts.charts import Pie
from pyecharts import options as opts
from pyecharts.globals import ThemeType
import pywebio.pin

up_triangle = '▲'
down_triangle = '▼'

cookie_key = 'aitrad.in.key'

local_url = 'https://aitrad.in/'

#最大杠杆倍数
max_leverage_ratio = 200.0

#交易手续费
fees_ratio = 0.001

#获取时间戳（十秒）
def get_ts10():
    return int(time.time() / 10)

tabs = ['交易', '我的', '排行', '市场']
tab_pos = {v: i+1 for i, v in enumerate(tabs)}

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

def get_account_percent(user_account):
    #获取账户各币种的百分比
    attr = []
    val = []
    tot_amount = 0
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
        abs_delta = abs(delta)
        tot_amount += abs_delta
        if delta > 0:
            sign = '+'
        else:
            sign = '-'
        attr.append(sign + symbol)
        val.append(abs_delta)
    return attr, val

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
    ts10 = get_ts10()
    btc_price = get_base_price('BTC',ts10) if not usdt_on else 1
    for symbol in symbolinfo:
        info = symbolinfo[symbol]
        data.append([symbol,float(info["price"]),float(info["Volume1d"]) * btc_price,float(info["Change1d"])])
    data = [[d[0],d[1],d[2],d[3]] for d in data]
    return data

def get_binance_ticker(cli,usdt_on,interval):
    key=(usdt_on,interval)
    if key in cli.ticker_cache:
        return cli.ticker_cache[key]
    if 'M' in interval or 'y' in interval:
        interval = '7d'
    if usdt_on:
        ticker = db.ticker('u',interval)
        # path = '/db/ticker_u/' + interval + '.json'
    else:
        ticker = db.ticker('b',interval)
        # path = '/db/ticker_b/' + interval + '.json'
    data = ticker.read()
    cli.ticker_cache[key] = copy.deepcopy(data)
    return data

def make_market_html( mdata):
    #载入模板/template/market_template.html
    with open('template/market_template.html', 'r', encoding='utf-8') as f:
        html = f.read()
    table_html = '<table cellpadding="0" id="table" style="text-align: center;">'
    table_html += '<tr class="top" style="background-color: #CCCCCC; cursor: pointer;">'
    table_html += '<td>市场</td>'
    table_html += '<td>价格</td>'
    table_html += '<td>涨幅1d</td>'
    table_html += '<td>成交1d</td>'
    table_html += '<td>涨幅7d</td>'
    table_html += '<td>成交7d</td>'
    table_html += '</tr>'
    for d in mdata:
        sym = d[0]
        sym2 = binanceAPI.SYM_DICT[sym][0]
        #search_upper = symbol.upper()
        #if search_upper and search_upper not in sym and search_upper not in sym2: continue
        table_html += '<tr>'
        table_html += '<td>' + sym2 + '</td>'
        table_html += '<td>' + str(d[1]) + '</td>'
        table_html += '<td>' + str(d[3]) + '</td>'
        table_html += '<td>' + str('%.4g' % d[2]) + '</td>'
        table_html += '<td>' + str(d[5]) + '</td>'
        table_html += '<td>' + str('%.4g' % d[4]) + '</td>'
        table_html += '</tr>'
    table_html += '</table>'
    html = html.replace('<!--my table-->', table_html)
    return html

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
def get_rank_list(cli):
    print("get_rank_list")
    #读取users.json
    users = db.users().read()
    cur_tsms = get_tsms()
    user_list = []
    for user in users:
        u = users[user]
        user_account = u['account']
        #计算每个人的账户价值（USDT单位）
        total_balance = get_total_balance(user_account)
        #保留两位小数
        total_balance = round(total_balance, 2)
        #注册时间(ms)
        register_time = u['reg_time']
        #天数
        days = (cur_tsms - register_time) / 1000 / 60 / 60 / 24
        #保留两位小数
        days = round(days, 2)
        #交易次数
        trade_cnt = int(u['trade_cnt'])
        print(user, total_balance, days, trade_cnt)
        #用户名
        username = u['name']
        if username == "":
            continue
        #用户清单
        user_list.append([username, total_balance, trade_cnt, days, 0])
    #添加特殊用户：基准账户
    user_list.append(['基准账户', 1000000.0, 0, "∞", 0])
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
            if user_list[i][0] == cli.user_name:
                my_rank = user_list[i][4]
                my_days = user_list[i][3]
                break
    return user_list, my_rank, my_days

def get_pie_chart_html(user_account):
    #参考：https://blog.csdn.net/vv_eve/article/details/107991704
    print("def get_pie_chart_html")
    attr,val = get_account_percent(user_account)
    print(attr,val)
    height = "350px"
    chart = Pie(init_opts=opts.InitOpts(width="350px", height=height, theme=ThemeType.LIGHT))
    pair = [(k,v) for k,v in zip(attr,val) if v != 0]
    print(chart)
    chart.add(
        "", 
        data_pair=pair,
    rosetype='radius',
    radius=["40%", "55%"],
    center=["35%", "50%"],# 位置设置
    )
    print("chart",chart)
    chart.set_global_opts(
        title_opts=opts.TitleOpts(title="账户资产比例"),
        legend_opts=opts.LegendOpts(pos_left="65%", orient="vertical"),
        )
    return chart.render_notebook()

def get_orders_table(orders):
    ans = []
    ans.append(["类型", "交易对", "方向", "价格", "数量", "时间", "状态"])
    for od in orders:
        ans.append([
            od["type"],
            od["symbol"],
            od["side"],
            od["price"],
            od["amount"],
            od["ts"],
            od["status"]
            ])
    return ans
