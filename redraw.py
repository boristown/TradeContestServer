from pywebio import *
from pywebio.input import *
from pywebio.output import *
from pywebio.pin import *
from client import client
import on_event
import time
import commons
import klines
import UI
import binanceAPI
import db
import pywebio_battery

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
    print('cli.symbol',cli.symbol)
    sym2 = binanceAPI.SYM_DICT[cli.symbol][0]
    put_row([
        put_input('symbol', value=sym2, readonly=True),
    ])
    cli.search = pin.search
    cli.selectBase = pin.selectBase
    cli.selectInterval = pin.selectInterval
    cli.selectPeriod = pin.selectPeriod

#内容重绘
@use_scope('content', clear=True)
def redraw_content(cli):
    pywebio_battery.set_cookie(
        'pin.switch_tab', 
        commons.tab_pos[pin.switch_tab]
        )
    while True:
        pywebio_battery.set_cookie(
            'pin.switch_tab', 
            commons.tab_pos[pin.switch_tab]
            )
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
                if cli.selectInterval != pin.selectInterval or \
                    cli.selectPeriod != pin.selectPeriod:
                    temp_selectInterval = pin.selectInterval
                    temp_selectPeriod = pin.selectPeriod
                    print('redraw market kline',pin.selectInterval, pin.selectPeriod)
                    redraw_market_kline(cli)
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
                print("trade_type", cli.trade_type)
                if cli.trade_type == '买入':
                    on_event.update_buy_options(cli)
                elif cli.trade_type == '卖出':
                    on_event.update_sell_options(cli)
                elif cli.trade_type == '做多':
                    on_event.update_long_options(cli)
                elif cli.trade_type == '做空':
                    on_event.update_short_options(cli)
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
        changed = on_event.pin_changed(cli)
        if cli.switch_tab != pin.switch_tab:
            print('change detected: switch_tab')
            break

@use_scope('login', clear=True)
def redraw_login(cli: client):
    put_scope('login_input')
    put_scope('login_welcome')
    put_scope('login_button')
    put_scope('login_info')
    #当前时间戳（10秒）
    ts10 = int(time.time() / 10)
    #输入密钥点击登陆
    #如果没有密钥，点击注册
    #点击注册后，输出一个32为随机在字符串
    #提示用户：该密钥是您的唯一登陆凭证，请妥善保管，如果遗失，将无法找回
    #请将该密钥复制到上方输入框中，点击登陆
    if cli.user_key == '': #未登录

        with use_scope('login_input', clear=True):
            put_input('key', placeholder='输入密钥')
            
        if cli.reg_key == '':
            with use_scope('login_button', clear=True):
                put_buttons(['登陆', '注册'], onclick=lambda btn: on_event.login(cli, btn))
            #put_scope('login_info')
        else:
            with use_scope('login_button', clear=True):
                put_buttons(['登陆'], onclick=lambda btn: on_event.login(cli, btn))
            with use_scope('login_info', clear=True):
                put_success('该密钥是您的唯一登陆凭证，请妥善保管，如果遗失，将无法找回')
                put_success('请将该密钥复制到上方输入框中，点击登陆')
                put_input('user_key', value=cli.reg_key, readonly=True)
    else:
        #请输入用户名
        if cli.user_name == '':
            put_input('user_name', placeholder='输入用户名')
            put_buttons(['确认用户名'], onclick=lambda btn: on_event.conf_name(cli, btn))
            #put_scope('login_info')
        else:
            redraw_login_welcome(cli)
            with use_scope('login_button', clear=True):
                put_buttons(['登出'], onclick=lambda btn: on_event.logout(cli))

@use_scope('login_welcome', clear=True)
def redraw_login_welcome(cli: client):
    put_markdown('# ' + cli.user_name)
    put_markdown('## 账户信息：')
    user_account = cli.user_account
    for curr in user_account:
        put_markdown("### " + curr + '：' + str(user_account[curr]))
    #put_text(res)
    put_markdown('### 估值：' + str(commons.get_total_balance(user_account)) + ' USDT')
    put_markdown('### 杠杆率：' + str(commons.get_leverage(user_account)))
    pie_chart_html = commons.get_pie_chart_html(user_account)
    put_html(pie_chart_html)
    users = db.users().read()
    user = users[cli.user_key]
    print("user", user)
    orders = user['orders']
    print("orders", orders)
    if len(orders) > 0:
        #我的订单
        put_markdown('## 我的订单：')
        put_table(commons.get_orders_table(orders))
    #交易历史记录
    put_markdown('## 交易历史记录')
    history = db.history(cli.user_key)
    history_list = history.read()
    if history_list == None:
        history_list = []
    history_list.append(
        [
        #交易类型
        #交易时间（ms）
        #交易对
        #交易数量(quote)
        #交易quote
        #交易数量(base)
        #交易base
        #手续费
        #手续费单位
        #交易价格
        #交易后账户余额
        '交易类型',
        '交易时间戳',
        '交易对',
        '交易数量(quote)',
        '交易quote',
        '交易数量(base)',
        '交易base',
        '手续费',
        '手续费单位',
        '交易价格',
        '交易后账户余额',
        '账户估值(USDT)'
        ]
    )
    history_list.reverse()
    put_table(history_list)

@use_scope('market', clear=True)
def redraw_market(cli: client):
    if pin.switch_tab == '市场': redraw_market_header(cli)
    if pin.switch_tab == '市场': redraw_market_kline(cli)
    if pin.switch_tab == '市场': redraw_market_table(cli)
    #if pin.switch_tab == '市场': redraw_sponsor(cli)

@use_scope('sponsor', clear=True)
def redraw_sponsor(cli: client):
    print("redraw_sponsor")
    put_markdown('## 感谢以下赞助人的支持:')
    put_markdown('### 淘淘')
    put_markdown('### 熊*添')
    put_markdown('### 刘*超')
    put_markdown('### 小点点')
    put_markdown('### 秦汉')
    put_markdown('### 张*勇')
    put_markdown('### 赵磊')
    put_markdown('### 冯*俊')
    put_markdown('### 徐坚')    
    put_markdown('### 于*万')
    put_markdown('#### 如果您也想成为赞助人，请联系：tbziy@foxmail.com')
    #超链接：
    put_markdown('[![github](https://www.iconpacks.net/icons/3/free-github-logo-icon-6531.png)](https://github.com/boristown/TradeContestServer)')
    #put_markdown('#### [项目地址](https://github.com/boristown/TradeContestServer)')
    put_markdown('#### by AI纪元')

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

def sort_button(cli,label):
    return put_button(
        label, 
        onclick=lambda cli=cli,label=label: 
        on_event.set_sort(cli,label),
        color = 'success' if cli.sort_key in label else 'secondary',
        small = True
        )

def update_header(cli):
    cli.header = ['市场', '价格', '幅', '成交']
    suffix = commons.down_triangle if cli.sort_reverse else commons.up_triangle
    for i in range(len(cli.header)):
        if cli.header[i] == cli.sort_key:
            cli.header[i] += suffix
            break
    cli.header_row = [sort_button(cli, label) for label in cli.header]

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
        sym2 = binanceAPI.SYM_DICT[sym][0]
        search_upper = pin.search.upper()
        if search_upper and search_upper not in sym and search_upper not in sym2: continue
        row[0] = put_button(
            sym2,
            onclick=lambda cli=cli,
            s=sym: on_event.set_symbol(cli,s),
            color='success' if cli.symbol == sym else 'secondary',
            small=True
            )
        mdata.append([row[0],row[1],row[3],'%.4g' % row[2]])
    put_table(mdata)

@use_scope('rank', clear=True)
def redraw_rank(cli):
    rank_list, my_rank, my_days = commons.get_rank_list(cli)

    if cli.user_key:
        put_markdown('## ' + cli.user_name)
        put_markdown('### 余额：' + str(round(commons.get_total_balance(cli.user_account),2)) + " USDT")
        put_markdown('### 排名：第' + str(my_rank) + '名')
        put_markdown('### 交易次数：' + str(cli.trade_cnt) + '次')
        put_markdown('### 注册天数：' + str(my_days) + '天')

    data = [
        ['排名', '用户名', '余额', '交易次数', '注册天数'],
    ]

    for i in range(len(rank_list)):
        row = rank_list[i]
        data.append([row[4], row[0], row[1], row[2], row[3]])
    put_table(data)
    redraw_sponsor(cli)

@use_scope('market_kline', clear=True)
def redraw_market_kline(cli: client):
    print("def redraw_market_kline")
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
    print("cli.period",cli.period)
    cli.period = eval(cli.period)
    key = (cli.symbol, cli.interval, cli.period)
    if key in cli.kline_cache:
        html = cli.kline_cache[key]
    else:
        print("get kline data begin")
        html = klines.draw_klines(cli.symbol, cli.interval, cli.current_time - cli.period, cli.current_time, [], 1)
        cli.kline_cache[key] = html
    print(html)
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
    ts10 = commons.get_ts10()
    print("account")
    account = cli.user_account
    #显示一行小字，内容是：*交易手续费0.1%。
    #put_text('*交易手续费0.1%。')
    #买入、卖出、做多、做空、网格交易，趋势追踪
    symbol = cli.symbol
    quote,base = commons.split_quote_base(symbol)
    symbol_price = commons.get_price_symbol(symbol, ts10)
    UI.trade_options_row(
        put_text('1 '+quote+' ='), 
        put_input('symbol_price',type=FLOAT,readonly=True,value=symbol_price),
        put_text(" "+base)
        )
    put_buttons([
        second_button('买入') if cli.trade_type != '买入' else success_button('买入'),
        second_button('卖出') if cli.trade_type != '卖出' else success_button('卖出'),
        second_button('做多') if cli.trade_type != '做多' else success_button('做多'),
        second_button('做空') if cli.trade_type != '做空' else success_button('做空'),
        second_button('网格交易') if cli.trade_type != '网格交易' else success_button('网格交易'),
        ], onclick=lambda btn,cli=cli:trade_btn_click(btn,cli), small=True)
    if cli.trade_type == '买入':
        UI.trade_options_row(
            put_text('低于市场价'),UI.float_input('buy_price_perc'),put_text(" "+'%'))
        UI.trade_options_row(
            put_text('使用'),UI.float_input('buy_base_amount'),put_text(" "+base))
        UI.trade_options_row(
            put_text('消耗'),UI.float_input('buy_amount_perc'),put_text(" "+'%'),)
        UI.trade_options_row(
            put_text('买入'),UI.float_input('buy_quote_amount'),put_text(" "+quote),)
        UI.trade_options_row(
            put_text('相对于'),
            put_select('buy_stop_loss_type', ['成交时','最大盈利']),None)
        UI.trade_options_row(
            put_text('亏损占比资产'), UI.float_input('buy_stop_loss_perc'),put_text(" "+'%时止损'),)
        UI.trade_options_row(
            put_text('手续费(0.1%)'), UI.float_input('buy_fee',True), put_text(" "+base))
        UI.trade_options_row(
            put_text('交易价格'), 
            put_input('buy_price',type=FLOAT,readonly=True,value=symbol_price),
            put_text(" "+base))
        UI.trade_conf_button(cli)
    elif cli.trade_type == '卖出':
        UI.trade_options_row(
            put_text('高于市场价'),UI.float_input('sell_price_perc'),put_text(" "+'%'))
        UI.trade_options_row(
            put_text('卖出'),UI.float_input('sell_quote_amount'),put_text(" "+quote))
        UI.trade_options_row(
            put_text('消耗'),UI.float_input('sell_amount_perc'),put_text(" "+'%'))
        UI.trade_options_row(
            put_text('价值'),UI.float_input('sell_base_amount'),put_text(" "+base))
        UI.trade_options_row(
            put_text('相对于'),put_select('sell_stop_loss_type', ['成交时','最大盈利']),None)
        UI.trade_options_row(
            put_text('亏损占比资产'),UI.float_input('sell_stop_loss_perc'),put_text(" "+'%时止损'))
        UI.trade_options_row(
            put_text('手续费(0.1%)'), UI.float_input('sell_fee',True),put_text(" "+base))
        UI.trade_options_row(
            put_text('交易价格'), 
            put_input('sell_price',type=FLOAT,readonly=True,value=symbol_price),
            put_text(" "+base))
        UI.trade_conf_button(cli)
    elif cli.trade_type == '做多':
        UI.trade_options_row(
            put_text('低于市场价'),UI.float_input('long_price_perc'),put_text(' %'))
        UI.trade_options_row(
            put_text('使用'),UI.float_input('long_base_amount'),put_text(" "+base))
        UI.trade_options_row(
            put_text('杠杆率'),UI.float_input('long_leverage'),put_text(' 倍'))
        UI.trade_options_row(
            put_text('做多'),UI.float_input('long_quote_amount'),put_text(" "+quote))
        UI.trade_options_row(
            put_text('相对于'),
            put_select('long_stop_loss_type', ['成交时','最大盈利']),None)
        UI.trade_options_row(
            put_text('亏损占比资产'),UI.float_input('long_stop_loss_perc'),put_text(' %时止损'))
        UI.trade_options_row(
            put_text('手续费(0.1%)'),UI.float_input('long_fee',True),put_text(" "+base))
        UI.trade_options_row(
            put_text('交易价格'), 
            put_input('long_price',type=FLOAT,readonly=True,value=symbol_price),
            put_text(" "+base))
        UI.trade_conf_button(cli)
    elif cli.trade_type == '做空':
        UI.trade_options_row(
            put_text('高于市场价'),UI.float_input('short_price_perc'),put_text(' %'))
        UI.trade_options_row(
            put_text('做空'),UI.float_input('short_quote_amount'),put_text(" "+quote))
        UI.trade_options_row(
            put_text('杠杆率'),UI.float_input('short_leverage'),put_text(' 倍'))
        UI.trade_options_row(
            put_text('价值'),UI.float_input('short_base_amount'),put_text(" "+base))
        UI.trade_options_row(
            put_text('相对于'),
            put_select('short_stop_loss_type', ['成交时','最大盈利']),None)
        UI.trade_options_row(
            put_text('亏损占比资产'),UI.float_input('short_stop_loss_perc'),put_text(' %时止损'))
        UI.trade_options_row(
            put_text('手续费(0.1%)'),UI.float_input('short_fee',True),put_text(" "+quote))
        UI.trade_options_row(
            put_text('交易价格'), 
            put_input('short_price',type=FLOAT,readonly=True,value=symbol_price),
            put_text(" "+base))
        UI.trade_conf_button(cli)
    elif cli.trade_type == '网格交易':
        #网格交易：首单位置___%，每单间隔___%，单侧订单数量___（下拉：[quote]/[base]），每单数量___，整体杠杆率___%，亏损占比总资产___%时止损。确认按钮。
        UI.trade_options_row(
            put_text('首单位置'),
            put_input('grid_first_price_perc',type=FLOAT,placeholder='0~50'),
            put_text('%'),
        )
        UI.trade_options_row(
            put_text('每单间隔'),
            put_input('grid_interval_perc',type=FLOAT,placeholder='0~50'),
            put_text('%'),
        )
        UI.trade_options_row(
            put_text('单侧订单数量'),
            put_input('grid_order_num',type=NUMBER,placeholder='1~999'),
            put_text('个'),
        )
        UI.trade_options_row(
            put_text('每单数量'),
            put_input('grid_order_amount',type=FLOAT,placeholder='0~9999999'),
            put_select('grid_order_amount_type', [quote,base]),
        )
        UI.trade_options_row(
            put_text('整体杠杆率'),
            put_input('grid_leverage',type=FLOAT,placeholder='0~100'),
            put_text('%'),
        )
        UI.trade_options_row(
            put_text('亏损占比资产'),
            put_input('grid_stop_loss_perc',type=FLOAT,placeholder='0~99'),
            put_text('%时止损'),
        )
        UI.trade_conf_button(cli)

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
