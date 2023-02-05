
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