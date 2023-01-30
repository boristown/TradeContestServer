import commons

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
        #初始化
        self.interval = '1d'
        self.symbol = 'BTCUSDT'
        self.current_time = commons.get_tsms()
        self.period = 30 * 24 * 60 * 60 * 1000
        self.period_min = 60 * 1000
        self.sort_key = '成交'
        self.sort_reverse = True