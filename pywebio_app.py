from pywebio import *
from pywebio.input import *
from pywebio.output import *
from pywebio.pin import *
from klines import *
import time

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
    # html = draw_klines(symbol, interval, current_time - period, current_time, [], 1)
    # put_html(html)
    # put_buttons(
    #     ['市场名', '价格', '成交额'+down_triangle, '涨幅'], 
    #     onclick=None
    #     )
    while True:
        changed = pin_wait_change(['search','selectBase', 'selectInterval', 'selectPeriod'])
        with use_scope('kline', clear=True):
            name=changed['name']
            selinterval = pin.selectInterval
            selperiod = pin.selectPeriod
            put_text(selinterval+','+selperiod)
            interval=selinterval.replace('分钟','m').replace('小时','h').replace('天','d')
            current_time = int(time.time() * 1000)
            period = selperiod.replace('最近','').replace('小时', 'h').replace('天', 'd').replace('月', 'M').replace('年', 'y')
            period = period.replace('y', ' * 365 * 24 * 60 * 60 * 1000')
            period = period.replace('M', ' * 30 * 24 * 60 * 60 * 1000')
            period = period.replace('d', ' * 24 * 60 * 60 * 1000')
            period = period.replace('h', ' * 60 * 60 * 1000')
            period = period.replace('m', ' * 60 * 1000')
            period = eval(period)
            html = draw_klines(symbol, interval, current_time - period, current_time, [], 1)
            put_html(html)
    #put_input('input', label='This is a input widget')