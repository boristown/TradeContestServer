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
        self.reg_key = ''
        self.user_key = ''
        self.user_name = ''
        self.user_elo = 1500
        self.trade_type = None
        #买入
        self.buy_price_perc = None
        self.buy_base_amount = None
        self.buy_amount_perc = None
        self.buy_quote_amount = None
        self.buy_stop_loss_type = None
        self.buy_stop_loss_perc = None
        #卖出
        self.sell_price_perc = None
        self.sell_quote_amount = None
        self.sell_amount_perc = None
        self.sell_base_amount = None
        self.sell_stop_loss_type = None
        self.sell_stop_loss_perc = None
        #做多
        self.long_price_perc = None
        self.long_base_amount = None
        self.long_leverage = None
        self.long_quote_amount = None
        self.long_stop_loss_type = None
        self.long_stop_loss_perc = None
        #做空
        self.short_price_perc = None
        self.short_quote_amount = None
        self.short_leverage = None
        self.short_base_amount = None
        self.short_stop_loss_type = None
        self.short_stop_loss_perc = None
        #网格交易
        self.grid_first_price_perc = None
        self.grid_interval_perc = None
        self.grid_order_num = None
        self.grid_order_amount = None
        self.grid_order_amount_type = None
        self.grid_leverage = None
        self.grid_stop_loss_perc = None

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
                redraw_login(cli)
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
                    'buy_amount_perc'
                ]
            )
        print('change detected')
        if cli.switch_tab != pin.switch_tab:
            print('change detected: switch_tab')
            break

@use_scope('rank', clear=True)
def redraw_rank(cli):
    #比赛实时排行
    # 第0轮模拟交易竞赛
    # 我的排名：第1名
    # 我的余额：1000000
    # 我的收益：0%
    #
    # 排名 用户名   余额    ELO分 分数变化
    # 1    基准账户 1000000 1500  +0
    # 2    ak-bot  1000000 1500  +0
    if cli.user_key:
        put_text('第0轮模拟交易竞赛')
        put_text('我的排名：第2名')
        put_text('我的余额：1000000')
        put_text('我的收益：0%')

    data = [
        ['排名', '用户名', '余额', 'ELO分', '分数变化'],
        ['1', '基准账户', '1000000', '1500', '+0'],
        ['2', 'ak-bot', '1000000', '1500', '+0']
    ]
    put_table(data)

def pin_changed(cli):
    changed = set()
    if cli.switch_tab != pin.switch_tab:
        changed.add('switch_tab')
        return changed
    if pin.switch_tab == '市场':
        if cli.search != pin.search:
            changed.add('search')
        if cli.selectBase != pin.selectBase:
            changed.add('selectBase')
        if cli.selectInterval != pin.selectInterval:
            changed.add('selectInterval')
        if cli.selectPeriod != pin.selectPeriod:
            changed.add('selectPeriod')
        if cli.symbol != pin.symbol:
            changed.add('symbol')
        #buy_amount_perc
        print('buy_amount_perc:', cli.buy_amount_perc, pin.buy_amount_perc)
        if cli.buy_amount_perc and pin.buy_amount_perc and cli.buy_amount_perc != pin.buy_amount_perc:
            changed.add('buy_amount_perc')
    return changed

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
    cli.search = pin.search
    cli.selectBase = pin.selectBase
    cli.selectInterval = pin.selectInterval
    cli.selectPeriod = pin.selectPeriod
    cli.symbol = pin.symbol

def set_symbol(cli,name):
    cli.symbol = name
    pin.symbol = cli.symbol
    redraw_market_kline(cli)
    redraw_market_table(cli)
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

@use_scope('login', clear=True)
def redraw_login(cli: client):
    #当前时间戳（10秒）
    ts10 = int(time.time() / 10)
    #输入密钥点击登陆
    #如果没有密钥，点击注册
    #点击注册后，输出一个32为随机在字符串
    #提示用户：该密钥是您的唯一登陆凭证，请妥善保管，如果遗失，将无法找回
    #请将该密钥复制到上方输入框中，点击登陆
    if cli.user_key == '': #未登录
        put_input('key', placeholder='输入密钥')
        if cli.reg_key == '':
            put_buttons(['登陆', '注册'], onclick=lambda btn: login(cli, btn))
            put_scope('login_info')
        else:
            put_buttons(['登陆'], onclick=lambda btn: login(cli, btn))
            with use_scope('login_info', clear=True):
                put_success('该密钥是您的唯一登陆凭证，请妥善保管，如果遗失，将无法找回')
                put_success('请将该密钥复制到上方输入框中，点击登陆')
                put_input('user_key', value=cli.reg_key, readonly=True)
    else:
        #请输入用户名
        if cli.user_name == '':
            put_input('user_name', placeholder='输入用户名')
            put_buttons(['确认用户名'], onclick=lambda btn: conf_name(cli, btn))
            put_scope('login_info')
        else:
            #欢迎：用户名
            with use_scope('login_welcome', clear=True):
                put_text('欢迎：' + cli.user_name)
                res = '账户信息：\n'
                res += 'ELO分：' + str(cli.user_elo) + '\n'
                #格式：{'BTC':0,'USDT':1000}
                price = get_price_btc(ts10)
                user_account = cli.user_account
                #格式：{'BTC':10000,'USDT':1}
                #res = get_contest_text() + '\n'
                #res = '用户：' + cli.user_name + '\n'
                res += 'BTC：' + str(user_account['BTC']) + '\n'
                res += 'USDT：' + str(user_account['USDT']) + '\n'
                res += '估值：' + str(user_account['BTC']*price + user_account['USDT']) + '\n'
                res += '杠杆率：' + str(get_leverage(user_account))
                #btc_price = get_price_btc(ts10)
                put_text(res)
            put_buttons(['登出'], onclick=lambda btn: login(cli, btn))
            put_scope('login_info')

def get_total_balance(user_account):
    #总资产
    #本金 = USDT余额 + BTC数量*当前价格
    ts10 = int(time.time() / 10)
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
    ts10 = int(time.time() / 10)
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

@lru_cache
def get_price_btc(ts10):
    # 获取当前BTCUSDT价格
    url = 'https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT'
    r = requests.get(url)
    price = float(r.json()['price'])
    return price

@lru_cache
def get_price_eth(ts10):
    # 获取当前ETHUSDT价格
    url = 'https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT'
    r = requests.get(url)
    price = float(r.json()['price'])
    return price

@lru_cache
def get_price_symbol(symbol, ts10):
    # 获取当前symbol价格
    url = 'https://api.binance.com/api/v3/ticker/price?symbol=' + symbol
    r = requests.get(url)
    price = float(r.json()['price'])
    return price

def conf_name(cli, btn):
    if btn == '确认用户名':
        name = pin.user_name
        if name == '':
            with use_scope('login_info', clear=True):
                put_error('请输入用户名')
        else:
            #验证用户名是否存在
            #如果存在，提示用户：用户名已存在，请重新输入
            #如果不存在，更新用户名
            with open('db/user.json', 'r') as f:
                users = json.load(f)
            for key in users:
                if users[key]['name'] == name:
                    with use_scope('login_info', clear=True):
                        put_error('用户名已存在，请重新输入')
                    return
            users[cli.user_key]['name'] = name
            cli.user_name = name
            with open('db/user.json', 'w') as f:
                json.dump(users, f)
        redraw_login(cli)

def login(cli: client, btn):
    if btn == '登陆':
        key = pin.key
        if key == '':
            with use_scope('login_info', clear=True):
                put_error('请输入密钥')
        else:
            #验证key是否存在
            #如果存在，更新last_login_time
            #如果不存在，提示用户：密钥不存在，请重新输入
            with open('db/user.json', 'r') as f:
                users = json.load(f)
            if key in users:
                users[key]['last_login_time'] = int(time.time() * 1000)
                with open('db/user.json', 'w') as f:
                    json.dump(users, f)
                cli.reg_key = ''
                cli.user_key = key
                cli.user_name = users[key]['name']
                cli.user_account = users[key]['account']
                cli.user_elo = users[key]['ELO']
                cli.user_orders = users[key]['orders']
                redraw_login(cli)
            else:
                with use_scope('login_info', clear=True):
                    put_error('密钥不存在，请重新输入')

    elif btn == '注册':
        #输出一个32为随机在字符串
        key = ramdom_str(32)
        #存储key到服务端 db/user.json
        #存储格式：{key: '', name: '', reg_time: '',  last_login_time: ''}
        with open('db/user.json', 'r') as f:
            users = json.load(f)
        users[key] = {
            'name': '', 
            'ELO': 1500.0,
            'reg_time': int(time.time() * 1000), 
            'last_login_time': int(time.time() * 1000),
            'account': {
                "USDT":1000000.0,
                "BTC":0.0,
                },
            'orders': [],
            }
        with open('db/user.json', 'w') as f:
            json.dump(users, f)
        cli.reg_key = key
        redraw_login(cli)

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

    if cli.user_key != '':
        redraw_trade_options(cli)
        put_scope('trade_options_msg')

@use_scope('trade_options_msg', clear=True)
def redraw_trade_options_msg(cli: client, msg, is_error):
    if is_error:
        print('error', msg)
        put_error(msg)
    else:
        print('success', msg)
        put_success(msg)

@use_scope('trade_options', clear=True)
def redraw_trade_options(cli: client):
    print("account")
    account = cli.user_account
    #显示一行小字，内容是：*交易手续费0.1%。
    put_text('*交易手续费0.1%。')
    #买入、卖出、做多、做空、网格交易，趋势追踪
    put_buttons([
        second_button('买入') if cli.trade_type != '买入' else success_button('买入'),
        second_button('卖出') if cli.trade_type != '卖出' else success_button('卖出'),
        second_button('做多') if cli.trade_type != '做多' else success_button('做多'),
        second_button('做空') if cli.trade_type != '做空' else success_button('做空'),
        second_button('网格交易') if cli.trade_type != '网格交易' else success_button('网格交易'),
        ], onclick=lambda btn,cli=cli:trade_btn_click(btn,cli), small=True)
    symbol = cli.symbol
    if symbol[-4:] == 'USDT':
        base = symbol[-4:]
        quote = symbol[:-4]
    else:
        base = symbol[-3:]
        quote = symbol[:-3]
    if cli.trade_type == '买入':
        put_row(
            [
                put_text('低于市场价'),
                put_input('buy_price_perc',type=FLOAT,placeholder='-99999~100'),
                put_text('%'),
            ],
            size = f"30% auto 30%",
        ),
        put_row(
            [
                put_text('使用'),
                put_input('buy_base_amount',type=FLOAT,placeholder='0~'+str(account.get('USDT',0))),
                put_text(base),
            ],
            size = f"30% auto 30%",
        )
        put_row(
            [
                put_text('消耗'),
                put_input('buy_amount_perc',type=FLOAT,placeholder='0~100'),
                put_text('%'),
            ],
            size = f"30% auto 30%",
        )
        put_row(
            [
                put_text('买入'),
                put_input('buy_quote_amount',type=FLOAT,placeholder='0~9999999'),
                put_text(quote),
            ],
            size = f"30% auto 30%",
        )
        put_row(
            [
                put_text('相对于'),
                put_select('buy_stop_loss_type', ['成交时','最大盈利']),
                None
            ],
            size = f"30% auto 30%",
        )
        put_row(
            [
                put_text('亏损占比资产'),
                put_input('buy_stop_loss_perc',type=FLOAT,placeholder='0~99'),
                put_text('%时止损'),
            ],
            size = f"30% auto 30%",
        )
        print('trade_confirm_button')
        put_button('确认', onclick=lambda clsi=cli:trade_confirm_click(cli), small=True)
    elif cli.trade_type == '卖出':
        put_row(
            [
                put_text('高于市场价'),
                put_input('sell_price_perc',type=FLOAT,placeholder='-100~99999'),
                put_text('%'),
            ],
            size = f"30% auto 30%",
        )
        put_row(
            [
                put_text('卖出'),
                put_input('sell_quote_amount',type=FLOAT,placeholder='0~9999999'),
                put_text(quote),
            ],
            size = f"30% auto 30%",
        )
        put_row(
            [
                put_text('消耗'),
                put_input('sell_amount_perc',type=FLOAT,placeholder='0~100'),
                put_text('%'),
            ],
            size = f"30% auto 30%",
        )
        put_row(
            [
                put_text('价值'),
                put_input('sell_base_amount',type=FLOAT,placeholder='0~9999999'),
                put_text(base),
            ],
            size = f"30% auto 30%",
        )
        put_row(
            [
                put_text('相对于'),
                put_select('sell_stop_loss_type', ['成交时','最大盈利']),
                None
            ],
            size = f"30% auto 30%",
        )
        put_row(
            [
                put_text('亏损占比资产'),
                put_input('sell_stop_loss_perc',type=FLOAT,placeholder='0~99'),
                put_text('%时止损'),
            ],
            size = f"30% auto 30%",
        )
        put_button('确认', onclick=lambda cli=cli:trade_confirm_click(cli), small=True)
    elif cli.trade_type == '做多':
        put_row(
            [
                put_text('低于市场价'),
                put_input('long_price_perc',type=FLOAT,placeholder='-99999~100'),
                put_text('%'),
            ],
            size = f"30% auto 30%",
        )
        put_row(
            [
                put_text('使用'),
                put_input('long_base_amount',type=FLOAT,placeholder='0~9999999'),
                put_text(base),
            ],
            size = f"30% auto 30%",
        )
        put_row(
            [
                put_text('杠杆率'),
                put_input('long_leverage',type=FLOAT,placeholder='0~100'),
                put_text('%'),
            ],
            size = f"30% auto 30%",
        )
        put_row(
            [
                put_text('做多'),
                put_input('long_quote_amount',type=FLOAT,placeholder='0~9999999'),
                put_text(quote),
            ],
            size = f"30% auto 30%",
        )
        put_row(
            [
                put_text('相对于'),
                put_select('long_stop_loss_type', ['成交时','最大盈利']),
                None
            ],
            size = f"30% auto 30%",
        )
        put_row(
            [
                put_text('亏损占比资产'),
                put_input('long_stop_loss_perc',type=FLOAT,placeholder='0~99'),
                put_text('%时止损'),
            ],
            size = f"30% auto 30%",
        )
        put_button('确认', onclick=lambda cli=cli:trade_confirm_click(cli), small=True)
    elif cli.trade_type == '做空':
        put_row(
            [
                put_text('高于市场价'),
                put_input('short_price_perc',type=FLOAT,placeholder='-100~99999'),
                put_text('%'),
            ],
            size = f"30% auto 30%",
        )
        put_row(
            [
                put_text('做空'),
                put_input('short_quote_amount',type=FLOAT,placeholder='0~9999999'),
                put_text(quote),
            ],
            size = f"30% auto 30%",
        )
        put_row(
            [
                put_text('杠杆率'),
                put_input('short_leverage',type=FLOAT,placeholder='0~100'),
                put_text('%'),
            ],
            size = f"30% auto 30%",
        )
        put_row(
            [
                put_text('价值'),
                put_input('short_base_amount',type=FLOAT,placeholder='0~9999999'),
                put_text(base),
            ],
            size = f"30% auto 30%",
        )
        put_row(
            [
                put_text('相对于'),
                put_select('short_stop_loss_type', ['成交时','最大盈利']),
                None
            ],
            size = f"30% auto 30%",
        )
        put_row(
            [
                put_text('亏损占比资产'),
                put_input('short_stop_loss_perc',type=FLOAT,placeholder='0~99'),
                put_text('%时止损'),
            ],
            size = f"30% auto 30%",
        )
        put_button('确认', onclick=lambda cli=cli:trade_confirm_click(cli), small=True)
    elif cli.trade_type == '网格交易':
        #网格交易：首单位置___%，每单间隔___%，单侧订单数量___（下拉：[quote]/[base]），每单数量___，整体杠杆率___%，亏损占比总资产___%时止损。确认按钮。
        put_row(
            [
                put_text('首单位置'),
                put_input('grid_first_price_perc',type=FLOAT,placeholder='0~50'),
                put_text('%'),
            ],
            size = f"30% auto 30%",
        )
        put_row(
            [
                put_text('每单间隔'),
                put_input('grid_interval_perc',type=FLOAT,placeholder='0~50'),
                put_text('%'),
            ],
            size = f"30% auto 30%",
        )
        put_row(
            [
                put_text('单侧订单数量'),
                put_input('grid_order_num',type=NUMBER,placeholder='1~999'),
                put_text('个'),
            ],
            size = f"30% auto 30%",
        )
        put_row(
            [
                put_text('每单数量'),
                put_input('grid_order_amount',type=FLOAT,placeholder='0~9999999'),
                put_select('grid_order_amount_type', [quote,base]),
            ],
            size = f"30% auto 30%",
        )
        put_row(
            [
                put_text('整体杠杆率'),
                put_input('grid_leverage',type=FLOAT,placeholder='0~100'),
                put_text('%'),
            ],
            size = f"30% auto 30%",
        )
        put_row(
            [
                put_text('亏损占比资产'),
                put_input('grid_stop_loss_perc',type=FLOAT,placeholder='0~99'),
                put_text('%时止损'),
            ],
            size = f"30% auto 30%",
        )
        put_button('确认', onclick=lambda cli=cli:trade_confirm_click(cli), small=True)

@use_scope('trade_options', clear=True)
def trade_btn_click(btn,cli):
    # 将当前symbol拆成base和quote, base是symbol末尾的BTC或者USDT，quote是symbol前面的部分。
    # 例如：BTCUSDT -> BTC, USDT，ETHBTC -> ETH, BTC
    # 买入、卖出、做多、做空、网格,点击后在按钮下方出现一个输入界面，第二行开始是如下输入界面。
    # 点击其它交易按钮时切换输入界面，再次点击时隐藏输入界面
    #买入：低于市场价___%，使用___[base]，消耗___%，买入___[quote]，相对于____(下拉：成交时/最大盈利）亏损占比总资产___%时止损。确认按钮。
    #卖出：高于市场价___%，卖出___[quote]，消耗___%，价值___[base]，相对于____(下拉：成交时/最大盈利）亏损占比总资产___%时止损。确认按钮。
    #做多：低于市场价___%，使用___[base]，杠杆率___%，做多___[quote]，相对于____(下拉：成交时/最大盈利）亏损占比总资产___%时止损。确认按钮。
    #做空：高于市场价___%，做空___[quote]，杠杆率___%，价值___[base]，相对于____(下拉：成交时/最大盈利）亏损占比总资产___%时止损。确认按钮。
    #网格交易：首单位置___%，每单间隔___%，单侧订单数量___（下拉：[quote]/[base]），每单数量___，整体杠杆率___%，亏损占比总资产___%时止损。确认按钮。
    if btn == '买入':
        if cli.trade_type == '买入':
            cli.trade_type = None
        else:
            cli.trade_type = '买入'
    elif btn == '卖出':
        if cli.trade_type == '卖出':
            cli.trade_type = ''
        else:
            cli.trade_type = '卖出'
    elif btn == '做多':
        if cli.trade_type == '做多':
            cli.trade_type = None
        else:
            cli.trade_type = '做多'
    elif btn == '做空':
        if cli.trade_type == '做空':
            cli.trade_type = None
        else:
            cli.trade_type = '做空'
    elif btn == '网格交易':
        if cli.trade_type == '网格交易':
            cli.trade_type = None
        else:
            cli.trade_type = '网格交易'
    redraw_trade_options(cli)

def trade_confirm_click(cli):
    account = cli.user_account
    lev_amt = get_leverage_amount(account)
    tot_balance = get_total_balance(account)
    # 点击确认按钮后，根据当前交易类型，判断输入是否合法，如果合法则发送交易请求，否则提示错误信息。
    if cli.trade_type == '买入':
        if not pin.buy_base_amount \
            and not pin.buy_amount_perc \
            and not pin.buy_quote_amount:
            redraw_trade_options_msg(cli, '交易数量不能为空！', True)
        else:
            redraw_trade_options_msg(cli, '成功买入。', False)
    elif cli.trade_type == '卖出':
        if not pin.sell_quote_amount \
            and not pin.sell_amount_perc \
            and not pin.sell_base_amount:
            redraw_trade_options_msg(cli, '交易数量不能为空！', True)
        else:
            redraw_trade_options_msg(cli, '成功卖出。', False)
    elif cli.trade_type == '做多':
        if not pin.long_base_amount \
            and not pin.long_leverage \
            and not pin.long_quote_amount:
            redraw_trade_options_msg(cli, '交易数量不能为空！', True)
        else:
            redraw_trade_options_msg(cli, '成功做多。', False)
    elif cli.trade_type == '做空':
        if not pin.short_quote_amount \
            and not pin.short_leverage \
            and not pin.short_base_amount:
            redraw_trade_options_msg(cli, '交易数量不能为空！', True)
        else:
            redraw_trade_options_msg(cli, '成功做空。', False)
    elif cli.trade_type == '网格交易':
        if not pin.grid_first_price_perc \
            and not pin.grid_interval_perc:
            redraw_trade_options_msg(cli, '请填写首单位置或每单间隔！', True)
        elif not pin.grid_order_num:
            redraw_trade_options_msg(cli, '请填写单侧订单数量！', True)
        elif not pin.grid_order_amount \
            and not pin.grid_leverage:
            redraw_trade_options_msg(cli, '请填写每单数量或整体杠杆率！', True)
        else:
            redraw_trade_options_msg(cli, '成功网格交易。', False)

def trade_price_change(x,cli):
    #价格输入框内容改变事件
    #获取输入框内容
    #调用交易接口
    #显示交易结果
    pass

def trade_amount_change(x,cli):
    #数量输入框内容改变事件
    #获取输入框内容
    #调用交易接口
    #显示交易结果
    pass

def trade_cost_change(x,cli):
    #金额输入框内容改变事件
    #获取输入框内容
    #调用交易接口
    #显示交易结果
    pass

def trade_leverage_change(x,cli):
    #杠杆率输入框内容改变事件
    #获取输入框内容
    #调用交易接口
    #显示交易结果
    pass

def trade_stop_mode_change(x,cli):
    #止损方式下拉框内容改变事件
    #获取输入框内容
    #调用交易接口
    #显示交易结果
    pass

def trade_stop_ratio_change(x,cli):
    #止损比例输入框内容改变事件
    #获取输入框内容
    #调用交易接口
    #显示交易结果
    pass

def trade_stop_mode_change(x,cli):
    #止损方式下拉框内容改变事件
    #获取输入框内容
    #调用交易接口
    #显示交易结果
    pass

def trade_stop_price_change(x,cli):
    #止损价格输入框内容改变事件
    #获取输入框内容
    #调用交易接口
    #显示交易结果
    pass

def trade_interval_change(x,cli):
    #间隔输入框内容改变事件
    #获取输入框内容
    #调用交易接口
    #显示交易结果
    pass

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
        row[0] = put_button(
            row[0],
            onclick=lambda cli=cli,
            s=sym: set_symbol(cli,s),
            color='success' if cli.symbol == sym else 'secondary',
            small=True
            )
        mdata.append([row[0],row[1],row[3],'%.4g' % row[2]])
    put_table(mdata)

@use_scope('market', clear=True)
def redraw_market(cli: client):
    if pin.switch_tab == '市场': redraw_market_header(cli)
    if pin.switch_tab == '市场': redraw_market_kline(cli)
    if pin.switch_tab == '市场': redraw_market_table(cli)
    if pin.switch_tab == '市场': redraw_sponsor(cli)
    
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