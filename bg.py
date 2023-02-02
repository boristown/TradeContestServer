import requests
import json
import time
import db
import binanceAPI

#这是一个后台作业

#循环调用:
# https://aitrad.in/ticker_u/{interval}
# https://aitrad.in/ticker_b/{interval}
#其中{interval}是：
# 1m,2m....59m - for minutes
# 1h, 2h....23h - for hours
# 1d...7d - for days
# 每次调用，间隔1秒
#将获取到的数据存入:
# /db/ticker_u/{interval}.json
# /db/ticker_b/{interval}.json

m = [str(i)+'m' for i in range(1, 60)]
h = [str(i)+'h' for i in range(1, 24)]
d = [str(i)+'d' for i in range(1, 8)]

def run_task():
    for interval in m + h + d:
        #url = 'https://aitrad.in/ticker_u/' + interval
        top_symbols = json.dumps(binanceAPI.SYM_USDT[:100]).replace(" ", "").replace("/", "")
        url = 'api/v3/ticker?symbols=' + top_symbols + '&windowSize='+interval
        url = "https://www.binance.com/" + url
        resp = requests.get(url).json()
        db.ticker('u', interval).write(resp)
        print('u_', interval, resp)
        top_symbols = json.dumps(binanceAPI.SYM_BTC[:100]).replace(" ", "").replace("/", "")
        url = 'api/v3/ticker?symbols=' + top_symbols + '&windowSize='+interval
        url = "https://www.binance.com/" + url
        resp = requests.get(url).json()
        db.ticker('b', interval).write(resp)
        print('b_', interval, resp)
        time.sleep(10)

if __name__ == "__main__":
    while True:
        run_task()