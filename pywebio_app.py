from pywebio import *
from pywebio.input import *
from pywebio.output import *
from klines import *
import time

#实现初始画面：
#首先显示币种名称
#然后显示k线图
#之后是设置列（交易货币[USDT/BTC]，K线周期，时间窗口）
#底部是可以排序和滑动的市场清单（列：市场名，价格，成交额，涨幅）
#当选择列表中的市场名的时候，切换顶部的市场
#默认排序：按成交额降序排列
def pywebio_run():
    def change_symbol(symbol):
        pass
        #set_scope('klines', clear=True)
        #put_klines(symbol)
    interval = '1d'
    symbol = 'BTCUSDT'
    current_time = int(time.time() * 1000)
    period = 30 * 24 * 60 * 60 * 1000
    html = draw_klines(symbol, interval, current_time - period, current_time, [], 1)
    put_html(html)
    put_buttons(['USDT', 'BTC'], onclick=change_symbol)
    #put_button('BTCUSDT', onclick=lambda: put_html(html))
    #put_button('Clear', onclick=lambda: clear())