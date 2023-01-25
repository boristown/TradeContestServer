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
        self.ticker_cache = {}
        self.kline_cache = {}
        self.switch_tab = ''
        self.sort_field = '成交'
        self.sort_reverse = True
        self.selectBase = ''
        self.selectInterval = ''
        self.selectPeriod = ''
        self.search = ''

def pywebio_run():
    client_id = ramdom_str(32)
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
        value='市场',
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
                print('redraw market all done',pin.selectInterval, pin.selectPeriod)
                cli.switch_tab = temp_switch_tab            
                cli.symbol = pin.symbol
                cli.selectInterval = pin.selectInterval
                cli.selectPeriod = pin.selectPeriod
                cli.search = pin.search
                cli.selectBase = pin.selectBase
                cli.selectPeriod = pin.selectPeriod
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
                redraw_login(cli)
                cli.switch_tab = temp_switch_tab
            else:
                pass
        print('global_redraw waiting change...')
        #change detection
        if cli.switch_tab == pin.switch_tab \
            and cli.search == pin.search \
            and cli.selectBase == pin.selectBase \
            and cli.selectInterval == pin.selectInterval \
            and cli.selectPeriod == pin.selectPeriod \
            and cli.symbol == pin.symbol:
            changed = pin_wait_change(
                [
                    'switch_tab', 'search', 'symbol',
                    'selectBase', 'selectInterval', 'selectPeriod'
                ]
            )
        print('change detected:' + str(changed))
        if cli.switch_tab != pin.switch_tab:
            print('change detected: switch_tab')
            break

@use_scope('market_header', clear=True)
def redraw_market_header(cli):
    put_input('search', placeholder ='输入市场名:')
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

def set_symbol(cli,name):
    cli.symbol = name
    pin.symbol = cli.symbol
    redraw_market_kline(cli)
    return cli.symbol

def set_sort(cli,label):
    label = label.replace(up_triangle, '').replace(down_triangle, '')
    if cli.sort_key == label:
        cli.sort_reverse = not cli.sort_reverse
    else:
        cli.sort_key = label
        cli.sort_reverse = False
    redraw_market_table(cli)

def sort_button(cli,label):
    return put_button(
        label, 
        onclick=lambda cli=cli,label=label: 
        set_sort(cli,label)
        )

def update_header(cli):
    cli.header = ['市场', '价格', '幅', '成交']
    suffix = down_triangle if cli.sort_reverse else up_triangle
    for i in range(len(cli.header)):
        if cli.header[i] == cli.sort_key:
            cli.header[i] += suffix
            break
    cli.header_row = [sort_button(cli, label) for label in cli.header]

@use_scope('login', clear=True)
def redraw_login(cli: client):
    #输入密钥点击登陆
    #如果没有密钥，点击注册
    #点击注册后，输出一个32为随机在字符串
    #提示用户：该密钥是您的唯一登陆凭证，请妥善保管，如果遗失，将无法找回
    #请将该密钥复制到上方输入框中，点击登陆
    put_input('key', placeholder='输入密钥')
    put_buttons(['登陆', '注册'], onclick=lambda btn: login(cli, btn))
    put_scope('login_info')

def login(cli: client, btn):
    if btn == '登陆':
        key = pin.key
        if key == '':
            with use_scope('login_info', clear=True):
                put_error('请输入密钥')
        else:
            cli = client(key, '', '', 0, 0, 0)
            cli.interval = '1d'
            cli.symbol = 'BTCUSDT'
            cli.current_time = int(time.time() * 1000)
            cli.period = 30 * 24 * 60 * 60 * 1000
            cli.period_min = 60 * 1000
            cli.sort_key = '成交'
            cli.sort_reverse = True
            #redraw(cli)
    elif btn == '注册':
        key = ramdom_str(32)
        with use_scope('login_info', clear=True):
            put_text('该密钥是您的唯一登陆凭证，请妥善保管，如果遗失，将无法找回')
            put_text('请将该密钥复制到上方输入框中，点击登陆')
            put_input('user_key', value=key, readonly=True)

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

@use_scope('market_kline', clear=True)
def redraw_market_kline(cli: client):
    selinterval = pin.selectInterval
    selperiod = pin.selectPeriod
    cli.interval = selinterval.replace('分钟','m').replace('小时','h').replace('天','d')
    cli.current_time = int(time.time() * 1000)
    cli.period = selperiod.replace('最近','').replace('小时', 'h').replace('天', 'd').replace('月', 'M').replace('年', 'y')
    cli.period = cli.period.replace('y', ' * 365 * 24 * 60 * 60 * 1000')
    cli.period = cli.period.replace('M', ' * 30 * 24 * 60 * 60 * 1000')
    cli.period = cli.period.replace('d', ' * 24 * 60 * 60 * 1000')
    cli.period = cli.period.replace('h', ' * 60 * 60 * 1000')
    cli.period = cli.period.replace('m', ' * 60 * 1000')
    cli.period = eval(cli.period)
    key = (cli.symbol, cli.interval, cli.period)
    if key in cli.kline_cache:
        html = cli.kline_cache[key]
    else:
        html = draw_klines(cli.symbol, cli.interval, cli.current_time - cli.period, cli.current_time, [], 1)
        cli.kline_cache[key] = html
    put_html(html)

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
    mbody = get_market_data(cli,pin.selectBase == "USDT",cli.period_s)
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
        row[0] = put_button(row[0],onclick=lambda cli=cli,s=sym: set_symbol(cli,s))
        mdata.append([row[0],row[1],row[3],'%.4g' % row[2]])
    put_table(mdata)

@use_scope('market', clear=True)
def redraw_market(cli: client):
    redraw_market_header(cli)
    redraw_market_kline(cli)
    redraw_market_table(cli)
    redraw_sponsor(cli)
        
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
    cli.ticker_cache[key] = deepcopy(data)
    return data

def ramdom_str(length):
    str = ''
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    for i in range(length):
        str += chars[random.randint(0, len(chars) - 1)]
    return str