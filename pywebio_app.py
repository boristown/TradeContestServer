from pywebio import *
from pywebio.input import *
from pywebio.output import *

#实现初始画面：
#首先显示币种名称
#然后显示k线图
#之后是设置列（交易货币[USDT/BTC]，K线周期，时间窗口）
#底部是可以排序和滑动的市场清单（列：市场名，价格，成交额，涨幅）
#当选择列表中的市场名的时候，切换顶部的市场
#默认排序：按成交额降序排列
def pywebio_run():
    path = 'html/BTCUSDT_1h.html'
    put_button('BTCUSDT', onclick=lambda: put_html(open(path, 'r', encoding='utf-8').read()))
    #put_html(open(path, 'r', encoding='utf-8').read())
    #name = input.input("what's your name")
    #output.put_text("hello", name)

