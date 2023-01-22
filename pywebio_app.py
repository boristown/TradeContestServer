from pywebio import *
from pywebio.input import *
from pywebio.output import *
from pywebio.pin import *
from klines import *
from binanceAPI import *
import time
from collections import defaultdict
import requests

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
def pywebio_run():
    interval = '1d'
    symbol = 'BTCUSDT'
    current_time = int(time.time() * 1000)
    period = 30 * 24 * 60 * 60 * 1000
    period_min = 60 * 1000
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
    put_text(symbol)
    while True:
        changed = pin_wait_change(['search','selectBase', 'selectInterval', 'selectPeriod'])
        with use_scope('kline', clear=True):
            name=changed['name']
            selinterval = pin.selectInterval
            selperiod = pin.selectPeriod
            #put_text(selinterval+','+selperiod)
            interval=selinterval.replace('分钟','m').replace('小时','h').replace('天','d')
            current_time = int(time.time() * 1000)
            period = selperiod.replace('最近','').replace('小时', 'h').replace('天', 'd').replace('月', 'M').replace('年', 'y')
            mdata = get_market_data(pin.selectBase == "USDT",period)
            period = period.replace('y', ' * 365 * 24 * 60 * 60 * 1000')
            period = period.replace('M', ' * 30 * 24 * 60 * 60 * 1000')
            period = period.replace('d', ' * 24 * 60 * 60 * 1000')
            period = period.replace('h', ' * 60 * 60 * 1000')
            period = period.replace('m', ' * 60 * 1000')
            period = eval(period)
            html = draw_klines(symbol, interval, current_time - period, current_time, [], 1)
            put_html(html)
            put_table(mdata)
            put_table([
                ['Type', 'Content'],
                ['html', put_html('X<sup>2</sup>')],
                ['text', '<hr/>'],
                ['buttons', put_buttons(['A', 'B'], onclick=...)],  
                ['markdown', put_markdown('`Awesome PyWebIO!`')],
                ['file', put_file('hello.text', b'hello world')],
                ['table', put_table([['A', 'B'], ['C', 'D']])]
            ])
    #put_input('input', label='This is a input widget')

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

def get_binance_ticker(self,usdt_on,interval):
    if usdt_on:
        url = local_url + "ticker_u/" + interval
    else:
        url = local_url + "ticker_b/" + interval
    data = requests.get(url).json()
    return data