from pywebio import *
from pywebio.input import *
from pywebio.output import *
from pywebio.pin import *
from klines import *
from binanceAPI import *
import time
from collections import defaultdict
import requests
import random

local_url = 'https://aitrad.in/'

up_triangle = '▲'
down_triangle = '▼'

#实现初始画面：
#首先显示币种名称
#然后显示k线图
#之后是设置列（交易货币[USDT/BTC]，K线周期，时间窗口）
#底部是可以排序和滑动的市场清单（列：市场名，价格，成交额，涨幅）
#当选择列表中的市场名的时候，切换顶部的市场
#默认排序：按成交额降序排列
class client:
    def __init__(self, client_id, interval, symbol, current_time, period, period_min):
        self.client_id = client_id
        self.interval = interval
        self.symbol = symbol
        self.current_time = current_time
        self.period = period
        self.period_min = period_min

def ramdom_str(length):
    str = ''
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    for i in range(length):
        str += chars[random.randint(0, len(chars) - 1)]
    return str

def pywebio_run():
    client_id = ramdom_str(32)
    cli = client(client_id, '', '', 0, 0, 0)
    cli.interval = '1d'
    cli.symbol = 'BTCUSDT'
    cli.current_time = int(time.time() * 1000)
    cli.period = 30 * 24 * 60 * 60 * 1000
    cli.period_min = 60 * 1000
    #cli = client(client_id, interval, symbol, current_time, period, period_min)
    put_input('search', placeholder ='输入市场名。')
    put_row([
        put_select('selectBase', options=['USDT', 'BTC']),
        put_select('selectInterval', 
        options=[
            '3分钟','5分钟','15分钟',
            '30分钟','1小时','2小时',
            '6小时','1天','3天',
            '7天','14天'
            ],
        value='1小时'
            ),
        #默认值是最近1天
        put_select('selectPeriod', 
        options=[
            '最近1小时','最近2小时','最近6小时',
            '最近12小时','最近1天','最近3天',
            '最近7天','最近1月','最近3月',
            '最近6月','最近1年'],
            value='最近1天',
            )
    ])
    put_row([
        put_input('symbol', value=cli.symbol, readonly=True),
    ])
    def set_symbol(name):
        #nonlocal symbol
        cli.symbol = name
        pin.symbol = cli.symbol
        #put_text(symbol)
        return cli.symbol

    while True:
        changed = pin_wait_change(['search','symbol','selectBase', 'selectInterval', 'selectPeriod'])
        with use_scope('kline', clear=True):
            name=changed['name']
            selinterval = pin.selectInterval
            selperiod = pin.selectPeriod
            #put_text(selinterval+','+selperiod)
            cli.interval=selinterval.replace('分钟','m').replace('小时','h').replace('天','d')
            cli.current_time = int(time.time() * 1000)
            cli.period = selperiod.replace('最近','').replace('小时', 'h').replace('天', 'd').replace('月', 'M').replace('年', 'y')
            mdata = [['市场名','价格','成交额','涨幅%']]
            mbody = get_market_data(pin.selectBase == "USDT",cli.period)
            for row in mbody:
                sym = row[0]
                row[0]=put_button(row[0],onclick=lambda : set_symbol(sym))
                mdata.append(row)
            cli.period = cli.period.replace('y', ' * 365 * 24 * 60 * 60 * 1000')
            cli.period = cli.period.replace('M', ' * 30 * 24 * 60 * 60 * 1000')
            cli.period = cli.period.replace('d', ' * 24 * 60 * 60 * 1000')
            cli.period = cli.period.replace('h', ' * 60 * 60 * 1000')
            cli.period = cli.period.replace('m', ' * 60 * 1000')
            cli.period = eval(cli.period)
            html = draw_klines(
                cli.symbol, cli.interval, cli.current_time - cli.period, cli.current_time, [], 1)
            put_text(cli.symbol) #显示市场名 居中
            put_html(html)
            put_table(mdata)
            
def get_market_data(usdt_on,period):
    data1d = get_binance_ticker(usdt_on,period)
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

def get_binance_ticker(usdt_on,interval):
    if usdt_on:
        url = local_url + "ticker_u/" + interval
    else:
        url = local_url + "ticker_b/" + interval
    print(url)
    data = requests.get(url).json()
    return data