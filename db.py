import json

#用户及活动订单数据
class users:
    def __init__(self):
        self.path = 'db/user.json'
    
    def read(self):
        with open(self.path, 'r') as f:
            user = json.load(f)
        return user
    
    def write(self, user):
        with open(self.path, 'w') as f:
            json.dump(user, f)

#用户交易历史记录
class history:
    def __init__(self, user_key):
        self.path = 'db/history/' + user_key + '.json'
    
    def create(self):
        with open(self.path, 'w') as f:
            json.dump([], f)
    
    def read(self):
        with open(self.path, 'r') as f:
            history = json.load(f)
        return history
    
    def write(self, history):
        with open(self.path, 'w') as f:
            json.dump(history, f)

#市场价格清单
class ticker:
    def __init__(self, base, interval):
        if base == 'b':
            self.path = 'db/ticker_b/' + interval + '.json'
        elif base == 'u':
            self.path = 'db/ticker_u/' + interval + '.json'
    
    def read(self):
        with open(self.path, 'r') as f:
            ticker = json.load(f)
        return ticker
    
    def write(self, ticker):
        with open(self.path, 'w') as f:
            json.dump(ticker, f)