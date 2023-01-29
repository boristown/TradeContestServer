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

def trade_confirm_click(cli):
    account = cli.user_account
    lev_amt = commons.get_leverage_amount(account)
    tot_balance = commons.get_total_balance(account)
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

def set_symbol(cli,name):
    cli.symbol = name
    pin.symbol = cli.symbol
    redraw.redraw_market_kline(cli)
    redraw.redraw_market_table(cli)
    return cli.symbol

def set_sort(cli,label):
    label = label.replace(up_triangle, '').replace(down_triangle, '')
    if cli.sort_key == label:
        cli.sort_reverse = not cli.sort_reverse
    else:
        cli.sort_key = label
        cli.sort_reverse = False
    redraw.redraw_market_table(cli)
    
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
