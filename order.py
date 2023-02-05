class order:
    def __init__(self, order_type, ts, symbol, side, price, qty):
        self.order_type = order_type
        self.ts = ts
        self.symbol = symbol
        self.side = side
        self.price = price
        self.qty = qty