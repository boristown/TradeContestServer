from fastapi import FastAPI
import  requests
import base64
from binanceAPI import *
from fastapi.responses import HTMLResponse,PlainTextResponse
import json
import klines
import os
import re

app = FastAPI()

@app.get("/")
async def root():
    resp = requests.get("https://wwww.binance.com/fapi/v1/ticker/price")
    return resp.text

@app.get("/agent/")
async def agent(url):
    #访问url，获取返回值，并返回
    resp = requests.get(url)
    return resp.text

@app.get("/B/")
async def B(x):
    #x是base64编码的字符串，需要解码后，拼接到url后面，访问url，获取返回值，并返回
    x = base64.b64decode(x).decode()
    url = "https://www.binance.com/" + x
    print(url)
    resp = requests.get(url)
    #print(resp.text)
    return resp.text

#get ticker
@app.get("/ticker_u/{interval}")
async def ticker_u(interval):
    top_symbols = json.dumps(SYM_USDT[:100]).replace(" ", "")
    url = 'api/v3/ticker?symbols=' + top_symbols + '&windowSize='+interval
    #print(url)
    url = "https://www.binance.com/" + url
    resp = requests.get(url)
    return json.loads(resp.text)

@app.get("/ticker_b/{interval}")
async def ticker_b(interval):
    top_symbols = json.dumps(SYM_BTC[:100]).replace(" ", "")
    url = 'api/v3/ticker?symbols=' + top_symbols + '&windowSize='+interval
    #print(url)
    url = "https://www.binance.com/" + url
    resp = requests.get(url)
    return json.loads(resp.text)

@app.get("/kline/{symbol}", response_class=HTMLResponse)
async def Kline(symbol, interval='1h', start_time=None, end_time=None, indicators=[]):
    symbol = symbol.upper()
    fname = klines.draw_klines(symbol,interval,start_time,end_time,indicators)
    #返回本地html文件:html/id.html
    with open(fname, 'r', encoding='utf-8') as f:
        return f.read()

#检查最新的软件版本
#软件路径：download/Ayyyymmddx.apk
#版本号为：yyyymmddx
#例如：download/A202101010.apk
#版本号为：202101010
@app.get("/version/")
async def version():
    #获取当前目录下的所有文件
    files = os.listdir('download')
    #print(files)
    #获取最新的版本号
    version = 0
    for f in files:
        if f[0] == 'A':
            v = int(re.findall(r'\d+', f)[0])
            if v > version:
                version = v
    return str(version)

#为了certbot认证，支持访问该路径：
#.well-known/acme-challenge/{str}
@app.get("/.well-known/acme-challenge/{str}",response_class=PlainTextResponse)
async def acme(s):
    with open('.well-known/acme-challenge/'+s, 'r', encoding='utf-8') as f:
        s = f.read()
        print(s)
        return s


# 运行指令：
'''
uvicorn main:app --reload
uvicorn main:app --host 0.0.0.0 --port 2023 --reload
'''
