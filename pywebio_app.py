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
from copy import deepcopy
from threading import Thread
import json
from functools import cache,lru_cache
from client import client
import redraw
import commons
import on_event
import pywebio_battery

#实现初始画面：
#首先显示币种名称
#然后显示k线图
#之后是设置列（交易货币[USDT/BTC]，K线周期，时间窗口）
#底部是可以排序和滑动的市场清单（列：市场名，价格，成交额，涨幅）
#当选择列表中的市场名的时候，切换顶部的市场
#默认排序：按成交额降序排列

def pywebio_run():
    client_id = commons.ramdom_str(32)
    cli = client(client_id, '', '', 0, 0, 0)
    switch_redraw()
    cli.user_key = pywebio_battery.get_cookie('cli.user_key')
    if cli.user_key:
        on_event.login(cli,'登陆',True)
    global_redraw(cli)

def switch_redraw():
    #市场 / 模拟交易 / 比赛排行
    val_pos=pywebio_battery.get_cookie('pin.switch_tab')
    if not val_pos:
        val_pos=1
    print('val_pos', val_pos)
    print('commons.tabs', commons.tabs)
    val_pos=int(val_pos)
    put_radio(
        'switch_tab', 
        options=commons.tabs,
        inline=True,
        value=commons.tabs[val_pos-1],
    )
    # cookie_switch_tab = pywebio_battery.get_cookie('pin.switch_tab')
    # print('cookie_switch_tab', cookie_switch_tab)
    # if cookie_switch_tab:
    #     pin.switch_tab = commons.tabs[cookie_switch_tab]

#全局重绘
def global_redraw(cli):
    while True:
        redraw.redraw_content(cli)
