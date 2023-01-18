
global CENTER, COLUMN, ROW, Pack, BOTTOM, TOP, LEFT, RIGHT
global defaultdict

import toga
from toga.style.pack import CENTER, COLUMN, ROW, Pack, BOTTOM, TOP, LEFT, RIGHT

from collections import defaultdict
# import time
# import threading
# import asyncio

global user_token
global up_triangle
global down_triangle
global current_version

user_token = None
up_triangle = '▲'
down_triangle = '▼'

#version: yyyymmddx
current_version = '202301150'

global HCenterElem
global ColumnBox
global BlackLabel
global FlexInput
global FlexButton
global FixedButton
global FlexNumber
global LayoutBox

def HCenterElem(element):
    return toga.Box(
        children=[
            element
        ],
        style=Pack(
            direction=ROW,
            alignment=CENTER,
            padding=5
        )
    )


def ColumnBox(children):
    return toga.Box(
        children=[HCenterElem(c) for c in children],
        style=Pack(
            direction=COLUMN,
            alignment=CENTER,
            padding=10
        )
    )

def BlackLabel(text):
    return toga.Label(
        text,
        #style=Pack(padding=(0, 5),color="black",alignment=CENTER,flex=1)
        style=Pack(padding=(0, 5),color="black",alignment=CENTER)
    )

def FlexInput(placeholder,on_change=None):
    return toga.TextInput(placeholder=placeholder,
        style=Pack(padding=(0, 5), flex=1),
        on_change=on_change
    )

def FlexButton(text,handler):
    return toga.Button(
        text,
        on_press=handler,
        style=Pack(padding=(0, 5),flex=1)
    )

def FixedButton(label, on_press, width):
    return toga.Button(
        label,
        on_press=on_press,
        style=Pack(padding=(0, 5),width=width)
    )

def FlexNumber():
    return toga.NumberInput(
        style=Pack(padding_left = 5, flex=1),
    )

def LayoutBox(ch):
    children = []
    for child in ch:
        if isinstance(child,list):
            children.append(
                toga.Box(
                children=child, 
                style=Pack(
                    flex=1,
                    direction=ROW,
                    alignment=LEFT,
                    padding=5
                )))
        else:
            children.append(child)
    return toga.Box(
        children=children,
        style=Pack(
            direction=COLUMN,
            alignment=TOP,
            padding=5,
            flex = 1
            )
    )

self.main_window = toga.MainWindow(title=self.formal_name)
self.tabledata = defaultdict(list)
self.realtabledata = defaultdict(list)

def market_page(self):
    self.search_input = FlexInput("输入币种名称执行搜索",self.on_search)
    self.search_button = FixedButton("搜索",self.on_search,100)
    header = ['市场', '价格', '交易额', '涨幅%']
    #self.tabledata = await self.get_market_data()
    #self.tabledata = []
    #self.realtabledata = self.tabledata[:]
    self.usdt_on = True
    self.symbol_base = 'USDT'
    self.usdt_toggle = FlexButton('USDT',self.on_usdt_toggle)
    self.btc_toggle = FlexButton('BTC',self.on_btc_toggle)
    #下拉：选项[USDT,BTC]
    self.dropdown_symbol_base = toga.Selection(
        items=['USDT','BTC'],
        on_select=self.on_dropdown_symbol_base_select,
        style=Pack(flex=1)
    )
    #下拉：选项[2小时，6小时，12小时，1天，3天，7天]
    self.dropdown_interval = toga.Selection(
        items=['2小时','6小时','12小时','1天','3天','7天'],
        on_select=self.on_dropdown_interval_select,
        style=Pack(flex=1)
    )
    #self.dropdown_interval.value = '1天'

    #2小时，6小时，12小时
    self.interval_2h_toggle = FlexButton('2小时',self.on_interval_2h_toggle)
    self.interval_6h_toggle = FlexButton('6小时',self.on_interval_6h_toggle)
    self.interval_12h_toggle = FlexButton('12小时',self.on_interval_12h_toggle)
    #1天，3天，7天
    self.interval_1d_toggle = FlexButton('1天',self.on_interval_1d_toggle)
    self.interval_3d_toggle = FlexButton('3天',self.on_interval_3d_toggle)
    self.interval_7d_toggle = FlexButton('7天',self.on_interval_7d_toggle)
    self.interval_1d_toggle.enabled = False
    self.interval = '1d'
    self.symbol_sort_button = FlexButton('市场',self.on_symbol_sort)
    self.price_sort_button = FlexButton('价格',self.on_price_sort)
    self.volume_sort_button = FlexButton('交易额',self.on_volume_sort)
    self.change_sort_button = FlexButton('涨幅%',self.on_change_sort)
    self.sort_field = 'volume'
    self.sort_desc = False
    self.usdt_toggle.enabled = False
    self.back_main_page_button = FlexButton('返回主页',self.on_main_page)
    self.start_trade_button = FlexButton('开始交易',self.on_trade)
    self.market_table = toga.Table(
        header, 
        data=self.realtabledata[self.symbol_base+self.interval], 
        style=Pack(padding=10, flex=1, alignment=CENTER),
        on_select=self.on_table_select,
        )
    self.refresh_button = FlexButton('刷新',self.refresh_table)
    self.update_sort_button()
    return self.market_page_static()

def login_page(self):
    #用toga创建一个登录页面
    #布局如下：
    #手机号Label：国家区号选择下拉框（默认中国+86）+手机号输入框
    #验证码Label：验证码输入框+获取验证码按钮（回调函数：self.on_valnum）
    #登录/注册按钮（回调函数：self.on_login）
    #用toga.box布局
    #水平拉伸元素，垂直居中元素
    
    #手机号Label
    self.phone_label = BlackLabel('手机号：')
    #国家区号选择下拉框
    self.country_code = toga.Selection(
        items=['中国+86', '美国+1', '英国+44', '日本+81', '韩国+82', '法国+33', '德国+49', '意大利+39', '西班牙+34', '俄罗斯+7', '加拿大+1', '澳大利亚+61', '新西兰+64', '印度+91', '巴西+55', '阿根廷+54', '墨西哥+52', '南非+27', '马来西亚+60', '泰国+66', '菲律宾+63', '印尼+62', '越南+84', '新加坡+65', '马尔代夫+960', '伊朗+98', '土耳其+90', '以色列+972', '阿联酋+971', '沙特阿拉伯+966', '卡塔尔+974', '科威特+965', '巴林+973', '阿曼+968', '约旦+962', '黎巴嫩+961', '伊拉克+964', '叙利亚+963', '巴勒斯坦+970', '也门+967', '科特迪瓦+225', '尼日利亚+234', '埃及+20', '南苏丹+211', '利比亚+218', '苏丹+249', '摩洛哥+212', '阿尔及利亚+213', '突尼斯+216', '埃塞俄比亚+251', '肯尼亚+254', '乌干达+256', '坦桑尼亚+255', '塞舌尔+248', '毛里求斯+230', '马达加斯加+261', '留尼汪+262', '津巴布韦+263', '莫桑比克+258'],
        on_select=self.on_select,
        style=Pack(width=150),
    )

    #手机号输入框
    self.phone_input = FlexNumber()

    #验证码Label
    self.valnum_label = BlackLabel('验证码：')

    #验证码输入框
    self.valnum_input = FlexNumber()

    #获取验证码按钮
    self.valnum_button = FixedButton('获取验证码',self.on_valnum,150)

    #登录/注册按钮
    self.login_button = FlexButton('登录/注册',self.on_login)

    #登录页面布局
    login_box = LayoutBox(
        [
            [self.phone_label],
            [self.country_code, self.phone_input],
            [self.valnum_label],
            [self.valnum_input, self.valnum_button],
            [self.login_button]
        ]
    )
    return login_box

def on_select(self, widget):
    print("选中的国家区号：", widget.value)

def on_valnum(self, widget):
    print("获取验证码")

def on_login(self, widget):
    print("登录/注册")
    self.main_window.content = self.main_page()

def main_page(self):
    #用toga创建一个主页面
    #显示：
    #第三轮模拟交易竞赛
    #2023年1月2日~2023年1月8日”
    #余额：1000000 USDT
    #当前排名：第3名
    #之后是按钮：
    #查看排行榜
    #查看我的交易
    #查看我的订单
    #查看我的持仓
    #用toga.box从上往下布局
    
    #第三轮模拟交易竞赛（水平居中）
    self.round_label = BlackLabel('第三轮模拟交易竞赛')
    #2023年1月2日~2023年1月8日”
    self.date_label = BlackLabel('2023年1月2日~2023年1月8日')
    #余额：1000000 USDT
    self.balance_label = BlackLabel('余额：1000000 USDT')
    #当前排名：第3名
    self.rank_label = BlackLabel('当前排名：第3名')
    #查看排行榜
    self.rank_button = FlexButton('查看排行榜',self.on_rank)
    #浏览市场
    self.view_markets = FlexButton('浏览市场',self.on_market)
    #开始交易
    self.start_trade = FlexButton('开始交易',self.on_trade)
    #查看我的交易
    self.trade_log_button = FlexButton('交易日志',self.on_trade_log)
    #查看我的订单
    self.order_button = FlexButton('我的订单',self.on_order)
    #查看我的持仓
    self.position_button = FlexButton('查看我的持仓',self.on_position)
    #退出登录
    self.logout_button = FlexButton('退出登录',self.on_logout)
    #布局
    main_box = ColumnBox([self.round_label,self.date_label,self.balance_label,self.rank_label,self.view_markets,self.start_trade,self.trade_log_button,self.order_button,self.position_button,self.rank_button,self.logout_button])
    return main_box

def on_logout(self, widget):
    print("退出登录")
    self.main_window.content = self.login_page()

async def on_market(self, widget):
    # self.loading_market = True
    # self.main_window.content = LayoutBox([
    #     [BlackLabel("载入中……")],
    #     [FlexButton('返回主页',self.on_main_page)]
    #     ])
    #self.view_markets.text = "浏览市场(载入中……)"
    self.tabledata = defaultdict(list)
    self.realtabledata = defaultdict(list)
    await self.show_market_page()
    #self.view_markets.text = "浏览市场"
    await self.refresh_table(widget)

async def show_market_page(self):
    content = self.market_page()
    #if self.loading_market:
    self.main_window.content = content
    self.main_window.content.refresh()

#实现异步方法get_market_data
async def get_market_data(self):
    #获取数据
    #if not self.loading_market: return
    self.usdt_on = self.symbol_base == "USDT"
    data1d = await get_binance_ticker(self.usdt_on,self.interval)
    #if not self.loading_market: return
    #await asyncio.sleep(0.8)
    #if not self.loading_market: return
    #data7d = await get_binance_ticker("7d")
    #if not self.loading_market: return
    symbolinfo = defaultdict(dict)
    for d1d in data1d:
        symbol = d1d["symbol"]
        symbolinfo[symbol]["price"] = d1d["lastPrice"]
        symbolinfo[symbol]["Change1d"] = d1d["priceChangePercent"]
        symbolinfo[symbol]["Volume1d"] = d1d["quoteVolume"]
    # for d7d in data7d:
    #     symbol = d7d["symbol"]
    #     symbolinfo[symbol]["Change7d"] = d7d["priceChangePercent"]
    #     symbolinfo[symbol]["Volume7d"] = d7d["quoteVolume"]
    data = []
    #top100_symbols = get_SYM_USDT() if self.usdt_on else get_SYM_BTC()
    for symbol in symbolinfo:
        info = symbolinfo[symbol]
        data.append([symbol,float(info["price"]),float(info["Volume1d"]),float(info["Change1d"])])
    #data.sort(key=lambda x:x[2],reverse=True)
    data = [[d[0],d[1],d[2],d[3]] for d in data]
    return data

def on_search(self, widget):
    print("搜索")
    txt = self.search_input.value.upper()
    #self.realtabledata[self.symbol_base+self.interval] = self.tabledata[self.symbol_base+self.interval][:]
    self.realtabledata[self.symbol_base+self.interval] = [itm for itm in self.tabledata[self.symbol_base+self.interval] if txt in itm[0]]
    self.market_table.data = self.strmap(self.realtabledata[self.symbol_base+self.interval])
    self.on_sort(widget)

def on_table_select(self, widget, row):
    self.symbol = row.市场
    self.price = row.价格
    self.volume = row.交易额
    self.change = row.涨幅
    print('选择了：',self.symbol,self.price,self.volume,self.change)
    self.start_trade_button.enabled = True
    self.show_symbol_chart(self.symbol)

def show_symbol_chart(self,symbol):
    print('显示图表：',symbol)
    #self.main_window.content = self.chart_page()
    #self.main_window.content = self.chart_page(symbol)
    self.main_window.content = self.symbol_chart_page(symbol)

def symbol_chart_page(self,symbol):
    self.Klinewebview = toga.WebView(
        on_webview_load=self.on_webview_loaded, style=Pack(flex=1, padding=10, alignment=CENTER, width=600, height=800),
    )
    #K线图测试url（中国的）
    #self.Klinewebview.url = 'https://gu.qq.com/sh000001/zs'
    self.sel_interval = '1小时'
    self.sel_period = '最近1天'
    self.sel_symbol = symbol
    self.Klinewebview.url = html_kline(self.sel_symbol,self.sel_interval,self.sel_period)
    print('K线图url：',self.Klinewebview.url)
    self.interval_selection = toga.Selection(
                items=['1小时','3分钟','5分钟','15分钟','30分钟','2小时','6小时','1天','3天','7天','14天'],
                on_select=self.on_select_interval,
                style=Pack(flex=1),
            )
    #self.interval_selection.value = self.sel_interval
    self.window_selection = toga.Selection(
                items=['最近1天','最近1小时','最近2小时','最近6小时','最近12小时','最近3天','最近7天','最近1个月','最近3个月','最近6个月','最近1年'],
                on_select=self.on_select_period,
                style=Pack(flex=1),
            )
    return self.symbol_chart_page_static()

def symbol_chart_page_static(self):
    return LayoutBox([
        [FlexButton('模拟交易',self.on_trade),FlexButton('市场主页面',self.on_market)],
        [
            self.interval_selection,
            self.window_selection
        ], #下拉列表
        #[BlackLabel('---这是'+symbol+'的K线图---')],
        self.Klinewebview,
        #FlexButton('返回',self.on_market),
        ]
    )

def on_select_interval(self, widget):
    print(widget.value)
    self.sel_interval = widget.value
    self.Klinewebview.url = html_kline(self.sel_symbol,self.sel_interval,self.sel_period)
    self.main_window.content = self.symbol_chart_page_static()
    
def on_select_period(self, widget):
    self.sel_period = widget.value
    self.Klinewebview.url = html_kline(self.sel_symbol,self.sel_interval,self.sel_period)
    self.main_window.content = self.symbol_chart_page_static()

def on_webview_loaded(self, widget):
    self.url_input.value = self.webview.url

def init_interval_toggle(self):
    self.interval_2h_toggle.enabled = True
    self.interval_6h_toggle.enabled = True
    self.interval_12h_toggle.enabled = True
    self.interval_1d_toggle.enabled = True
    self.interval_3d_toggle.enabled = True
    self.interval_7d_toggle.enabled = True

async def on_interval_1d_toggle(self, widget):
    if self.interval == '1d': return
    self.interval = '1d'
    self.init_interval_toggle()
    self.interval_1d_toggle.enabled = False
    self.market_table.data = self.strmap(self.realtabledata[self.symbol_base+self.interval])
    await self.refresh_table(widget)

async def on_interval_3d_toggle(self, widget):
    if self.interval == '3d': return
    self.interval = '3d'
    self.init_interval_toggle()
    self.interval_3d_toggle.enabled = False
    self.market_table.data = self.strmap(self.realtabledata[self.symbol_base+self.interval])
    await self.refresh_table(widget)

#7d
async def on_interval_7d_toggle(self, widget):
    if self.interval == '7d': return
    self.interval = '7d'
    self.init_interval_toggle()
    self.interval_7d_toggle.enabled = False
    self.market_table.data = self.strmap(self.realtabledata[self.symbol_base+self.interval])
    await self.refresh_table(widget)

#2h
async def on_interval_2h_toggle(self, widget):
    if self.interval == '2h': return
    self.interval = '2h'
    self.init_interval_toggle()
    self.interval_2h_toggle.enabled = False
    self.market_table.data = self.strmap(self.realtabledata[self.symbol_base+self.interval])
    await self.refresh_table(widget)

#6h
async def on_interval_6h_toggle(self, widget):
    if self.interval == '6h': return
    self.interval = '6h'
    self.init_interval_toggle()
    self.interval_6h_toggle.enabled = False
    self.market_table.data = self.strmap(self.realtabledata[self.symbol_base+self.interval])
    await self.refresh_table(widget)

#12h
async def on_interval_12h_toggle(self, widget):
    if self.interval == '12h': return
    self.interval = '12h'
    self.init_interval_toggle()
    self.interval_12h_toggle.enabled = False
    self.market_table.data = self.strmap(self.realtabledata[self.symbol_base+self.interval])
    await self.refresh_table(widget)

def on_symbol_sort(self, widget):
    if self.sort_field == 'symbol':
        self.sort_desc = not self.sort_desc
    else:
        self.sort_field = 'symbol'
        self.sort_desc = False
    self.on_sort()

def on_price_sort(self, widget):
    if self.sort_field == 'price':
        self.sort_desc = not self.sort_desc
    else:
        self.sort_field = 'price'
        self.sort_desc = False
    self.on_sort()

def on_volume_sort(self, widget):
    if self.sort_field == 'volume':
        self.sort_desc = not self.sort_desc
    else:
        self.sort_field = 'volume'
        self.sort_desc = False
    self.on_sort()

def on_change_sort(self, widget):
    if self.sort_field == 'change':
        self.sort_desc = not self.sort_desc
    else:
        self.sort_field = 'change'
        self.sort_desc = False
    self.update_sort_button()
    self.change_sort_button.label = '涨幅%' + (down_triangle if self.sort_desc else up_triangle)
    self.on_sort()

def update_sort_button(self):
    print("更新排序按钮")
    self.symbol_sort_button.label = '市场'
    self.price_sort_button.label = '价格'
    self.volume_sort_button.label = '交易额'
    self.change_sort_button.label = '涨幅%'
    suffix = down_triangle if self.sort_desc else up_triangle
    if self.sort_field == 'symbol':
        self.symbol_sort_button.label += suffix
    elif self.sort_field == 'price':
        self.price_sort_button.label += suffix
    elif self.sort_field == 'volume':
        self.volume_sort_button.label += suffix
    elif self.sort_field == 'change':
        self.change_sort_button.label += suffix

def on_sort(self):
    print("排序")
    idx = 0
    if self.sort_field == 'symbol':
        idx = 0
    elif self.sort_field == 'price':
        idx = 1
    elif self.sort_field == 'volume':
        idx = 2
    elif self.sort_field == 'change':
        idx = 3
    self.realtabledata[self.symbol_base+self.interval] = sorted(self.realtabledata[self.symbol_base+self.interval],key=lambda x:x[idx],reverse=self.sort_desc)
    self.market_table.data = self.strmap(self.realtabledata[self.symbol_base+self.interval])
    self.update_sort_button()

async def on_usdt_toggle(self, widget):
    if self.usdt_on: return
    self.usdt_on = True
    self.usdt_toggle.enabled = False
    self.btc_toggle.enabled = True
    self.symbol_base = 'USDT'
    self.market_table.data = self.strmap(self.realtabledata[self.symbol_base+self.interval])
    await self.refresh_table(None)

async def on_btc_toggle(self, widget):
    if not self.usdt_on: return
    self.usdt_on = False
    self.usdt_toggle.enabled = True
    self.btc_toggle.enabled = False
    self.symbol_base = 'BTC'
    self.market_table.data = self.strmap(self.realtabledata[self.symbol_base+self.interval])
    await self.refresh_table(None)

def market_page_static(self):
    return LayoutBox(
        [
            #[self.refresh_button,self.start_trade_button,self.back_main_page_button],
            [self.refresh_button,self.start_trade_button],
            [self.dropdown_symbol_base,self.dropdown_interval],
            [self.search_input],
            [self.symbol_sort_button,self.price_sort_button,self.volume_sort_button,self.change_sort_button],
            [self.market_table]
        ]
    )

def strmap(self, data):
    return [[str(x) for x in row] for row in data]

async def check_last_version(self):
    print("检查版本")
    last_version = await get_last_version()
    if last_version == None: return #获取失败
    if last_version != current_version:
        #弹出对话框“发现新版本”，并且显示最新版本号,询问是否下载最新版本，点击确定调用download_last_version()下载新版
        self.main_window.info_dialog(self.formal_name, '发现新版本: ' + last_version + '\n是否下载最新版本？', self.download_last_version)

async def download_last_version(self, widget=None, dialog=None):
    print("下载新版本")
    #弹出对话框“正在下载新版本”，并且显示下载进度，下载完成后自动关闭弹窗
    self.main_window.info_dialog(self.formal_name, '正在下载新版本...', self.exit)
    self.apkfile = await download_last_version()
    if self.apkfile == None: return #下载失败
    #弹出对话框“下载完成”，询问是否安装新版本，点击确定调用install_last_version()安装新版
    self.main_window.info_dialog(self.formal_name, '下载完成，是否安装新版本？', self.install_last_version)
    #self.exit()

async def install_last_version(self, widget=None, dialog=None):
    print("安装新版本")
    #弹出对话框“正在安装新版本”，并且显示安装进度，安装完成后自动关闭弹窗
    self.main_window.info_dialog(self.formal_name, '正在安装新版本...', self.exit)
    await self.install_apkfile(self.apkfile)
    #self.exit()

async def install_apkfile(self, apkfile):
    print("安装apk文件")
    #安装apk文件
    self.exit()

async def refresh_table(self, widget):
    print("刷新")
    self.refresh_button.enabled = False
    self.refresh_button.text = "刷新中..."
    #self.loading_market = True
    self.tabledata[self.symbol_base+self.interval] = await self.get_market_data()
    self.realtabledata[self.symbol_base+self.interval] = self.tabledata[self.symbol_base+self.interval][:]
    self.market_table.data = self.strmap(self.realtabledata[self.symbol_base+self.interval])
    self.refresh_button.text = "刷新"
    self.refresh_button.enabled = True
    #self.loading_market = False
    self.main_window.content = self.market_page_static()
    self.on_sort()
    #await self.check_last_version()

def on_main_page(self, widget):
    #self.loading_market = False
    print("返回主页")
    self.main_window.content = self.main_page()

def on_trade_log(self, widget):
    print("查看交易日志")
    self.main_window.content = self.trade_log_page()

def on_rank(self, widget):
    print("查看排行榜")
    self.main_window.content = self.rank_page()

def rank_page(self):
    pass

def on_trade(self, widget):
    print("查看我的交易")
    self.main_window.content = self.trade_page()

def trade_page(self):
    return LayoutBox(
        [
            [FlexButton('查看我的订单',self.on_order),FlexButton('查看我的持仓',self.on_position)],
            #返回主页
            [FlexButton('返回主页',self.on_main_page)]
        ]
    )

def on_order(self, widget):
    print("查看我的订单")
    self.main_window.content = self.order_page()

def order_page(self):
    pass

def on_position(self, widget):
    print("查看我的持仓")
    self.main_window.content = self.position_page()

def position_page(self):
    pass
 
async def on_dropdown_symbol_base_select(self, widget):
    self.symbol_base = widget.value
    #self.interval = self.dropdown_interval.selected_option.replace('天','d').replace('小时','h')
    self.market_table.data = self.strmap(self.realtabledata[self.symbol_base+self.interval])
    await self.refresh_table(widget)

async def on_dropdown_interval_select(self, widget):
    #self.symbol_base = self.dropdown_symbol_base.selected_option
    self.interval = widget.value
    self.interval = self.interval.replace('天','d').replace('小时','h')
    self.market_table.data = self.strmap(self.realtabledata[self.symbol_base+self.interval])
    await self.refresh_table(widget)

TradingContest.market_page = market_page
TradingContest.login_page = login_page
TradingContest.on_select = on_select
TradingContest.on_valnum = on_valnum
TradingContest.on_login = on_login
TradingContest.main_page = main_page
TradingContest.on_logout = on_logout
TradingContest.on_market = on_market
TradingContest.show_market_page = show_market_page
TradingContest.get_market_data = get_market_data
TradingContest.on_search = on_search
TradingContest.on_table_select = on_table_select
TradingContest.show_symbol_chart = show_symbol_chart
TradingContest.symbol_chart_page = symbol_chart_page
TradingContest.symbol_chart_page_static = symbol_chart_page_static
TradingContest.on_select_interval = on_select_interval
TradingContest.on_select_period = on_select_period
TradingContest.on_webview_loaded = on_webview_loaded
TradingContest.init_interval_toggle = init_interval_toggle
TradingContest.on_interval_1d_toggle = on_interval_1d_toggle
TradingContest.on_interval_3d_toggle = on_interval_3d_toggle
TradingContest.on_interval_7d_toggle = on_interval_7d_toggle
TradingContest.on_interval_2h_toggle = on_interval_2h_toggle
TradingContest.on_interval_6h_toggle = on_interval_6h_toggle
TradingContest.on_interval_12h_toggle = on_interval_12h_toggle
TradingContest.on_symbol_sort = on_symbol_sort
TradingContest.on_price_sort = on_price_sort
TradingContest.on_volume_sort = on_volume_sort
TradingContest.on_change_sort = on_change_sort
TradingContest.update_sort_button = update_sort_button
TradingContest.on_sort = on_sort
TradingContest.on_usdt_toggle = on_usdt_toggle
TradingContest.on_btc_toggle = on_btc_toggle
TradingContest.market_page_static = market_page_static
TradingContest.strmap = strmap
TradingContest.check_last_version = check_last_version
TradingContest.download_last_version = download_last_version
TradingContest.install_last_version = install_last_version
TradingContest.install_apkfile = install_apkfile
TradingContest.refresh_table = refresh_table
TradingContest.on_main_page = on_main_page
TradingContest.on_trade_log = on_trade_log
TradingContest.on_rank = on_rank
TradingContest.rank_page = rank_page
TradingContest.on_trade = on_trade
TradingContest.trade_page = trade_page
TradingContest.on_order = on_order
TradingContest.order_page = order_page
TradingContest.on_position = on_position
TradingContest.position_page = position_page
TradingContest.on_dropdown_symbol_base_select = on_dropdown_symbol_base_select
TradingContest.on_dropdown_interval_select = on_dropdown_interval_select

content = self.market_page()
self.main_window.content = content
self.main_window.show()
