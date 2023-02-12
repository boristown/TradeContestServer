
def make_order(ts, symbol, side, type, price, amount, currency,target_amount, target_currency, fee, status):
    return {
            'ts': ts,
            'symbol': symbol,
            'side': side,
            'type': type,
            'price': price,
            'amount': amount,
            'currency': currency,
            'target_amount': target_amount,
            'target_currency': target_currency,
            'fee': fee,
            'status': status,
            }

#初始化全局活动订单对象
def init_orders(global_orders):
    pass