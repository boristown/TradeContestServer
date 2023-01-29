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
    cli.interval = '1d'
    cli.symbol = 'BTCUSDT'
    cli.current_time = int(time.time() * 1000)
    cli.period = 30 * 24 * 60 * 60 * 1000
    cli.period_min = 60 * 1000
    cli.sort_key = '成交'
    cli.sort_reverse = True
    #市场 / 模拟交易 / 比赛排行
    put_radio(
        'switch_tab', 
        options=['市场', '模拟交易', '比赛排行'],
        inline=True,
        value='模拟交易',
    )
    pin.search = ''
    global_redraw(cli)

#全局重绘
def global_redraw(cli):
    while True:
        redraw_content(cli)

#内容重绘
@use_scope('content', clear=True)
def redraw_content(cli):
    while True:
        if pin.switch_tab == '市场':
            print('redraw market')
            if cli.switch_tab != pin.switch_tab: #切换tab，完全重绘
                print('redraw market all')
                temp_switch_tab = pin.switch_tab
                redraw_market(cli)
                print('redraw market all done')
                cli.switch_tab = temp_switch_tab
            else: #没切换tab，局部重绘
                print('redraw market part')
                #切换市场或者切换k线周期或者切换时间窗口，重绘k线图
                if cli.symbol != pin.symbol or \
                    cli.selectInterval != pin.selectInterval or \
                    cli.selectPeriod != pin.selectPeriod:
                    temp_symbol = pin.symbol
                    temp_selectInterval = pin.selectInterval
                    temp_selectPeriod = pin.selectPeriod
                    print('redraw market kline',pin.selectInterval, pin.selectPeriod)
                    redraw_market_kline(cli)
                    cli.symbol = temp_symbol
                    cli.selectInterval = temp_selectInterval
                    cli.selectPeriod = temp_selectPeriod
                #改变搜索框或者切换交易货币或者切换时间窗口或者改变排序字段，重绘市场列表
                if cli.search != pin.search or \
                    cli.selectBase != pin.selectBase or \
                    cli.selectPeriod != pin.selectPeriod:
                    temp_search = pin.search
                    temp_selectBase = pin.selectBase
                    temp_selectPeriod = pin.selectPeriod
                    print('redraw market table')
                    redraw_market_table(cli)
                    cli.selectPeriod = temp_selectPeriod
                    cli.search = temp_search
                    cli.selectBase = temp_selectBase
        elif pin.switch_tab == '模拟交易':
            print('redraw login')
            if cli.switch_tab != pin.switch_tab:
                print('redraw login all')
                temp_switch_tab = pin.switch_tab
                redraw.redraw_login(cli)
                cli.switch_tab = temp_switch_tab
            else:
                pass
        elif pin.switch_tab == '比赛排行':
            print('redraw rank')
            if cli.switch_tab != pin.switch_tab:
                print('redraw rank all')
                temp_switch_tab = pin.switch_tab
                redraw_rank(cli)
                cli.switch_tab = temp_switch_tab
            else:
                pass
        print('global_redraw waiting change...')
        #change detection
        changed = pin_changed(cli)
        if not changed:
            print('no change detected, waiting change...')
            changed = pin_wait_change(
                [
                    'switch_tab', 'search', 'symbol',
                    'selectBase', 'selectInterval', 'selectPeriod',
                    'buy_price_perc', 'buy_base_amount', 'buy_amount_perc', 'buy_quote_amount', 'buy_stop_loss_type', 'buy_stop_loss_perc',
                    'sell_price_perc', 'sell_base_amount', 'sell_amount_perc', 'sell_quote_amount', 'sell_stop_loss_type', 'sell_stop_loss_perc',
                    'long_price_perc', 'long_base_amount', 'long_leverage', 'long_quote_amount', 'long_stop_loss_type', 'long_stop_loss_perc',
                    'short_price_perc', 'short_base_amount', 'short_leverage', 'short_quote_amount', 'short_stop_loss_type', 'short_stop_loss_perc',
                    'grid_first_price_perc', 'grid_interval_perc', 'grid_order_num', 'grid_order_amount', 'grid_order_amount_type', 'grid_leverage', 'grid_stop_loss_perc',
                ]
            )
        print('change detected')
        if cli.switch_tab != pin.switch_tab:
            print('change detected: switch_tab')
            break

def pin_changed(cli):
    changed = {}
    if cli.switch_tab != pin.switch_tab:
        changed['switch_tab'] = pin.switch_tab
        return changed
    if pin.switch_tab == '市场':
        if cli.search != pin.search:
            changed['search'] = pin.search
            #changed.add('search')
        if cli.selectBase != pin.selectBase:
            changed['selectBase'] = pin.selectBase
            #changed.add('selectBase')
        if cli.selectInterval != pin.selectInterval:
            changed['selectInterval'] = pin.selectInterval
            #changed.add('selectInterval')
        if cli.selectPeriod != pin.selectPeriod:
            changed['selectPeriod'] = pin.selectPeriod
            #changed.add('selectPeriod')
        if cli.symbol != pin.symbol:
            changed['symbol'] = pin.symbol
            #changed.add('symbol')
        if cli.buy_amount_perc != pin.buy_amount_perc:
            changed['buy_amount_perc'] = pin.buy_amount_perc
            #changed.add('buy_amount_perc')
    return changed



def sort_button(cli,label):
    return put_button(
        label, 
        onclick=lambda cli=cli,label=label: 
        set_sort(cli,label),
        color = 'success' if cli.sort_key in label else 'secondary',
        small = True
        )

def update_header(cli):
    cli.header = ['市场', '价格', '幅', '成交']
    suffix = down_triangle if cli.sort_reverse else up_triangle
    for i in range(len(cli.header)):
        if cli.header[i] == cli.sort_key:
            cli.header[i] += suffix
            break
    cli.header_row = [sort_button(cli, label) for label in cli.header]

@use_scope('sponsor', clear=True)
def redraw_sponsor(cli: client):
    #输出赞助人（并输出感谢的话）：
    #淘淘
    #熊*添
    #刘*超
    #小点点
    #秦汉
    #张*勇
    #赵磊
    #冯*俊
    #徐坚
    #于*万
    #居中显示
    put_text('By AI纪元')
    put_text('感谢以下赞助人的支持！')
    put_text('淘淘')
    put_text('熊*添')
    put_text('刘*超')
    put_text('小点点')
    put_text('秦汉')
    put_text('张*勇')
    put_text('赵磊')
    put_text('冯*俊')
    put_text('徐坚')
    put_text('于*万')
    put_text('如果您也想成为赞助人，请联系：tbziy@foxmail.com')
    #超链接：
    put_link('项目地址','https://github.com/boristown/TradeContestServer')

def second_button(label):
    return {
        'label': label,
        'value': label,
        'color': 'secondary'
    }

def success_button(label):
    return {
        'label': label,
        'value': label,
        'color': 'success'
    }



@use_scope('market_table', clear=True)
def redraw_market_table(cli: client):
    selinterval = pin.selectInterval
    selperiod = pin.selectPeriod
    cli.interval=selinterval.replace('分钟','m').replace('小时','h').replace('天','d')
    cli.current_time = int(time.time() * 1000)
    cli.period_s = selperiod.replace('最近','').replace('小时', 'h').replace('天', 'd').replace('月', 'M').replace('年', 'y')
    print("redraw market table update header begin")
    update_header(cli)
    print("redraw market table update header end")
    mdata = [cli.header_row]
    mbody = commons.get_market_data(cli,pin.selectBase == "USDT",cli.period_s)
    print("redraw market table get market data end",cli.sort_key,cli.sort_reverse)
    if cli.sort_key == '市场':
        mbody.sort(key=lambda x: x[0], reverse=cli.sort_reverse)
    elif cli.sort_key == '价格':
        mbody.sort(key=lambda x: x[1], reverse=cli.sort_reverse)
    elif cli.sort_key == '幅':
        mbody.sort(key=lambda x: x[3], reverse=cli.sort_reverse)
    elif cli.sort_key == '成交':
        mbody.sort(key=lambda x: x[2], reverse=cli.sort_reverse)
    for row in mbody:
        sym = row[0]
        search_upper = pin.search.upper()
        if search_upper and search_upper not in sym: continue
        row[0] = put_button(
            row[0],
            onclick=lambda cli=cli,
            s=sym: set_symbol(cli,s),
            color='success' if cli.symbol == sym else 'secondary',
            small=True
            )
        mdata.append([row[0],row[1],row[3],'%.4g' % row[2]])
    put_table(mdata)