from pywebio import *
from pywebio.input import *
from pywebio.output import *
from pywebio.pin import *
from client import client
import json
import time
import random
import redraw
import commons
import UI
import binanceAPI

def login(cli: client, btn):
    if btn == '登陆':
        key = pin.key
        print("key:",key)
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
                redraw.redraw_login(cli)
            else:
                with use_scope('login_info', clear=True):
                    put_error('密钥不存在，请重新输入')

    elif btn == '注册':
        #输出一个32为随机在字符串
        key = commons.ramdom_str(32)
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
        redraw.redraw_login(cli)

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
        redraw.redraw_login(cli)

def pin_changed(cli):
    changed = {}
    if cli.switch_tab != pin.switch_tab:
        changed['switch_tab'] = pin.switch_tab
        return pin_wait(changed)
    if pin.switch_tab == '市场':
        UI.chain_changed(cli,changed,[
            'search',
            'selectBase', 'selectInterval', 'selectPeriod',
            'buy_price_perc', 'buy_base_amount', 'buy_amount_perc', 'buy_quote_amount', 'buy_stop_loss_type', 'buy_stop_loss_perc',
            'sell_price_perc', 'sell_base_amount', 'sell_amount_perc', 'sell_quote_amount', 'sell_stop_loss_type', 'sell_stop_loss_perc',
            'long_price_perc', 'long_base_amount', 'long_leverage', 'long_quote_amount', 'long_stop_loss_type', 'long_stop_loss_perc',
            'short_price_perc', 'short_base_amount', 'short_leverage', 'short_quote_amount', 'short_stop_loss_type', 'short_stop_loss_perc',
            'grid_first_price_perc', 'grid_interval_perc', 'grid_order_num', 'grid_order_amount', 'grid_order_amount_type', 'grid_leverage', 'grid_stop_loss_perc',
        ]
        )
    return pin_wait(changed)

def pin_wait(changed):
    print("pin wait begin")
    if not changed:
        print('no change detected, waiting change...')
        changed = pin_wait_change(
            [
                'switch_tab', 'search',
                'selectBase', 'selectInterval', 'selectPeriod',
                'buy_price_perc', 'buy_base_amount', 'buy_amount_perc', 'buy_quote_amount', 'buy_stop_loss_type', 'buy_stop_loss_perc',
                'sell_price_perc', 'sell_base_amount', 'sell_amount_perc', 'sell_quote_amount', 'sell_stop_loss_type', 'sell_stop_loss_perc',
                'long_price_perc', 'long_base_amount', 'long_leverage', 'long_quote_amount', 'long_stop_loss_type', 'long_stop_loss_perc',
                'short_price_perc', 'short_base_amount', 'short_leverage', 'short_quote_amount', 'short_stop_loss_type', 'short_stop_loss_perc',
                'grid_first_price_perc', 'grid_interval_perc', 'grid_order_num', 'grid_order_amount', 'grid_order_amount_type', 'grid_leverage', 'grid_stop_loss_perc',
            ]
        )
    print('change detected')
    return changed

def execute_buy(cli):
    ts10 = commons.get_ts10()
    #获取当前交易对
    symbol = cli.symbol
    quote, base = commons.split_quote_base(symbol)
    #交易对价格
    pin.symbol_price = commons.get_price_symbol(symbol, ts10)
    #手续费
    fee = float(pin.buy_fee)
    #交易数量
    base_amount = float(cli.buy_base_amount)
    #买入量
    buy_amount = (base_amount  - fee) / pin.symbol_price
    #修改账户余额
    user_account = cli.user_account
    user_account[base] -= base_amount
    user_account[quote] += buy_amount
    #写入文件
    with open('db/user.json', 'r') as f:
        users = json.load(f)
    users[cli.user_key]['account'] = user_account
    with open('db/user.json', 'w') as f:
        json.dump(users, f)
    #输出信息：成功买入buy_amount quote，价格 pin.symbol_price base,花费base_amount base，手续费fee base，当前账户余额为user_account
    msg = f'成功买入{buy_amount} {quote}，价格{pin.symbol_price} {base}，花费{base_amount} {base}，手续费{fee} {base}，当前账户余额为{user_account}'
    redraw.redraw_trade_options_msg(cli, msg, False)

def execute_sell(cli):
    ts10 = commons.get_ts10()
    #获取当前交易对
    symbol = cli.symbol
    quote, base = commons.split_quote_base(symbol)
    #交易对价格
    pin.symbol_price = commons.get_price_symbol(symbol, ts10)
    #手续费
    fee = float(pin.sell_fee)
    #交易数量
    quote_amount = float(cli.sell_quote_amount)
    #卖出量
    sell_amount = (quote_amount - fee) * pin.symbol_price
    #修改账户余额
    user_account = cli.user_account
    user_account[base] += sell_amount
    user_account[quote] -= quote_amount
    #写入文件
    with open('db/user.json', 'r') as f:
        users = json.load(f)
    users[cli.user_key]['account'] = user_account
    with open('db/user.json', 'w') as f:
        json.dump(users, f)
    #输出信息：成功卖出sell_amount base，价格 pin.symbol_price base,收入quote_amount quote，手续费fee quote，当前账户余额为user_account
    msg = f'成功卖出{sell_amount} {base}，价格{pin.symbol_price} {base}，收入{quote_amount} {quote}，手续费{fee} {quote}，当前账户余额为{user_account}'
    redraw.redraw_trade_options_msg(cli, msg, False)

def trade_confirm_click(cli):
    account = cli.user_account
    lev_amt = commons.get_leverage_amount(account)
    tot_balance = commons.get_total_balance(account)
    # 点击确认按钮后，根据当前交易类型，判断输入是否合法，如果合法则发送交易请求，否则提示错误信息。
    if cli.trade_type == '买入':
        if not cli.buy_base_amount \
            and not cli.buy_amount_perc \
            and not cli.buy_quote_amount:
            redraw.redraw_trade_options_msg(cli, '交易数量不能为空！', True)
        else:
            execute_buy(cli)
    elif cli.trade_type == '卖出':
        if not pin.sell_quote_amount \
            and not pin.sell_amount_perc \
            and not pin.sell_base_amount:
            redraw.redraw_trade_options_msg(cli, '交易数量不能为空！', True)
        else:
            execute_sell(cli)
    elif cli.trade_type == '做多':
        if not pin.long_base_amount \
            and not pin.long_leverage \
            and not pin.long_quote_amount:
            redraw.redraw_trade_options_msg(cli, '交易数量不能为空！', True)
        else:
            redraw.redraw_trade_options_msg(cli, '成功做多。', False)
    elif cli.trade_type == '做空':
        if not pin.short_quote_amount \
            and not pin.short_leverage \
            and not pin.short_base_amount:
            redraw.redraw_trade_options_msg(cli, '交易数量不能为空！', True)
        else:
            redraw.redraw_trade_options_msg(cli, '成功做空。', False)
    elif cli.trade_type == '网格交易':
        if not pin.grid_first_price_perc \
            and not pin.grid_interval_perc:
            redraw.redraw_trade_options_msg(cli, '请填写首单位置或每单间隔！', True)
        elif not pin.grid_order_num:
            redraw.redraw_trade_options_msg(cli, '请填写单侧订单数量！', True)
        elif not pin.grid_order_amount \
            and not pin.grid_leverage:
            redraw.redraw_trade_options_msg(cli, '请填写每单数量或整体杠杆率！', True)
        else:
            redraw.redraw_trade_options_msg(cli, '成功网格交易。', False)

def set_symbol(cli,name):
    cli.symbol = name
    pin.symbol = binanceAPI.SYM_DICT[cli.symbol][0]
    redraw.redraw_market_kline(cli)
    redraw.redraw_market_table(cli)
    return cli.symbol

def set_sort(cli,label):
    label = label.replace(commons.up_triangle, '').replace(commons.down_triangle, '')
    if cli.sort_key == label:
        cli.sort_reverse = not cli.sort_reverse
    else:
        cli.sort_key = label
        cli.sort_reverse = False
    redraw.redraw_market_table(cli)

def update_buy_options(cli: client):
    ts10 = commons.get_ts10()
    if not cli.user_key: return
    user_account = cli.user_account
    symbol = cli.symbol
    print('cli.symbol',symbol)
    quote,base = commons.split_quote_base(symbol)
    base_asset = user_account.get(base,0)
    pin.symbol_price = commons.get_price_symbol(symbol, ts10)
    #总手续费
    tot_fee = base_asset * commons.fees_ratio
    #实际可用基准货币资产余额
    aval_base_asset = base_asset - tot_fee
    #最大能买入的数量
    quote_can_buy = aval_base_asset / pin.symbol_price
    print('quote_can_buy',quote_can_buy)
    #改变买入数量占总资产百分比，重绘买入数量
    if cli.buy_amount_perc != pin.buy_amount_perc \
        or cli.buy_base_amount != pin.buy_base_amount \
        or cli.buy_quote_amount != pin.buy_quote_amount:
        #分情况讨论
        #1. 百分比修改，无论数量是否修改，都按照百分比计算
        if cli.buy_amount_perc != pin.buy_amount_perc:
            #空置为0
            if not pin.buy_amount_perc:
                pin.buy_amount_perc = 0
            #调整到0~100之间
            pin.buy_amount_perc = max(0, min(100, pin.buy_amount_perc))
            cli.buy_amount_perc = pin.buy_amount_perc
            #按照百分比计算base_amount数量
            cli.buy_base_amount = base_asset * pin.buy_amount_perc / 100 
            #手续费
            pin.buy_fee = cli.buy_base_amount * commons.fees_ratio
            #实际买入的基准货币金额
            real_base_amount = cli.buy_base_amount - pin.buy_fee
            #计算quote_amount数量
            cli.buy_quote_amount = real_base_amount / pin.symbol_price 
            #调整到正确的范围
            cli.buy_base_amount = max(0, min(base_asset, cli.buy_base_amount))
            cli.buy_quote_amount = max(0, min(quote_can_buy, cli.buy_quote_amount))
        #2. 百分比未修改，quote_amount数量修改，按照quote_amount数量计算百分比和base_amount数量
        elif cli.buy_quote_amount != pin.buy_quote_amount:
            #空置为0
            if not pin.buy_quote_amount:
                pin.buy_quote_amount = 0
            #调整到0~最大能买入的数量之间
            pin.buy_quote_amount = max(0, min(quote_can_buy, pin.buy_quote_amount))
            cli.buy_quote_amount = pin.buy_quote_amount
            #按照quote_amount数量计算base_amount数量
            cli.buy_base_amount = pin.buy_quote_amount * pin.symbol_price
            #含手续费的base_amount数量
            real_base_amount = cli.buy_base_amount / (1 - commons.fees_ratio)
            #手续费
            pin.buy_fee = real_base_amount - cli.buy_base_amount
            cli.buy_base_amount = real_base_amount
            #计算百分比
            cli.buy_amount_perc = cli.buy_base_amount / base_asset * 100
            #调整到正确范围
            cli.buy_base_amount = max(0, min(base_asset, cli.buy_base_amount))
            cli.buy_amount_perc = max(0, min(100, cli.buy_amount_perc))
        #3. 百分比未修改，quote_amount数量也未修改，base_amount数量修改，按照base_amount数量计算百分比和quote_amount数量
        elif cli.buy_base_amount != pin.buy_base_amount:
            #空置为0
            if not pin.buy_base_amount:
                pin.buy_base_amount = 0
            #调整到0~最大能买入的数量之间
            pin.buy_base_amount = max(0, min(base_asset, pin.buy_base_amount))
            cli.buy_base_amount = pin.buy_base_amount
            #计算买入的百分比
            cli.buy_amount_perc = cli.buy_base_amount / base_asset * 100
            #手续费
            pin.buy_fee = cli.buy_base_amount * commons.fees_ratio
            #实际买入的基准货币金额
            real_base_amount = cli.buy_base_amount - pin.buy_fee
            #计算quote_amount数量
            cli.buy_quote_amount = real_base_amount / pin.symbol_price
            #调整到正确范围
            cli.buy_quote_amount = max(0, min(quote_can_buy, cli.buy_quote_amount))
            cli.buy_amount_perc = max(0, min(100, cli.buy_amount_perc))
        #4. 更新界面pin值
        pin.buy_amount_perc = cli.buy_amount_perc
        pin.buy_base_amount = cli.buy_base_amount
        pin.buy_quote_amount = cli.buy_quote_amount

def update_sell_options(cli):
    #参考方法：update_buy_options实现该方法
    ts10 = commons.get_ts10()
    if not cli.user_key: return
    user_account = cli.user_account
    symbol = cli.symbol
    print('cli.symbol',symbol)
    quote,base = commons.split_quote_base(symbol)
    print('quote,base',quote,base)
    quote_asset = user_account.get(quote, 0)
    pin.symbol_price = commons.get_price_symbol(symbol, ts10)
    #总手续费
    tot_fee = quote_asset * commons.fees_ratio
    #实际卖出的quote数量
    real_quote_asset = quote_asset - tot_fee
    #最大能卖出的金额
    base_can_sell = real_quote_asset * pin.symbol_price
    print('base_can_sell',base_can_sell)
    #改变卖出数量占总资产百分比，重绘卖出界面
    #1. 百分比修改，按照百分比计算base_amount数量和quote_amount数量
    if cli.sell_amount_perc != pin.sell_amount_perc:
        #空置为0
        if not pin.sell_amount_perc:
            pin.sell_amount_perc = 0
        #调整到0~100之间
        pin.sell_amount_perc = max(0, min(100, pin.sell_amount_perc))
        cli.sell_amount_perc = pin.sell_amount_perc
        #计算卖出的资产数量
        cli.sell_quote_amount = quote_asset * cli.sell_amount_perc / 100
        #手续费
        pin.sell_fee = cli.sell_quote_amount * commons.fees_ratio
        #实际卖出的quote数量
        real_quote_asset = cli.sell_quote_amount - pin.sell_fee
        #计算base_amount数量
        cli.sell_base_amount = real_quote_asset * pin.symbol_price
        #调整到正确范围
        cli.sell_quote_amount = max(0, min(quote_asset, cli.sell_quote_amount))
        cli.sell_base_amount = max(0, min(base_can_sell, cli.sell_base_amount))
    #2. 百分比未修改，base_amount数量修改，按照base_amount数量计算百分比和quote_amount数量
    elif cli.sell_base_amount != pin.sell_base_amount:
        #空置为0
        if not pin.sell_base_amount:
            pin.sell_base_amount = 0
        #调整到0~最大能卖出的数量之间
        pin.sell_base_amount = max(0, min(base_can_sell, pin.sell_base_amount))
        cli.sell_base_amount = pin.sell_base_amount
        #计算卖出的quote数量
        cli.sell_quote_amount = cli.sell_base_amount / pin.symbol_price
        #含手续费的quote数量
        real_quote_asset = cli.sell_quote_amount / (1 - commons.fees_ratio)
        #手续费
        pin.sell_fee = real_quote_asset - cli.sell_quote_amount
        cli.sell_quote_amount = real_quote_asset
        #计算百分比
        cli.sell_amount_perc = cli.sell_quote_amount / quote_asset * 100
        #调整到正确范围
        cli.sell_quote_amount = max(0, min(quote_asset, cli.sell_quote_amount))
        cli.sell_amount_perc = max(0, min(100, cli.sell_amount_perc))
    #3. 百分比未修改，quote_amount数量修改，按照quote_amount数量计算百分比和base_amount数量
    elif cli.sell_quote_amount != pin.sell_quote_amount:
        #空置为0
        if not pin.sell_quote_amount:
            pin.sell_quote_amount = 0
        #调整到0~最大能卖出的数量之间
        pin.sell_quote_amount = max(0, min(quote_asset, pin.sell_quote_amount))
        cli.sell_quote_amount = pin.sell_quote_amount
        #计算卖出百分比
        cli.sell_amount_perc = cli.sell_quote_amount / quote_asset * 100
        #手续费
        pin.sell_fee = cli.sell_quote_amount * commons.fees_ratio
        #实际卖出的quote数量
        real_quote_asset = cli.sell_quote_amount - pin.sell_fee
        #计算base_amount数量
        cli.sell_base_amount = real_quote_asset * pin.symbol_price
        #调整到正确范围
        cli.sell_base_amount = max(0, min(base_can_sell, cli.sell_base_amount))
        cli.sell_amount_perc = max(0, min(100, cli.sell_amount_perc))
    #4. 三个都未修改，不做处理
    else:
        pass
    #重绘卖出界面
    pin.sell_amount_perc = cli.sell_amount_perc
    pin.sell_base_amount = cli.sell_base_amount
    pin.sell_quote_amount = cli.sell_quote_amount

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
