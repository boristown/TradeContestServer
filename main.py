from fastapi import FastAPI
import  requests
import base64
from binanceAPI import *
from fastapi.responses import HTMLResponse,PlainTextResponse,FileResponse,RedirectResponse
import json
import klines
import os
import re
import time
from collections import defaultdict
from pywebio.platform.fastapi import webio_routes
import pywebio_app as myapp
import pywebio.session
import my_websockets
import order

app = FastAPI()

# @app.get("/")
# async def root():
#     url = "http://aitrad.in:80/"
#     response = RedirectResponse(url)
#     return response

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


#距离上次获取相同参数的数据的时间间隔，超过cache_time（毫秒），才重新获取数据
cache_time = 1000 * 60

cache_ticker_u = {}
cache_ticker_u_time = defaultdict(int)
cache_ticker_b = {}
cache_ticker_b_time = defaultdict(int)

#get ticker
@app.get("/ticker_u/{interval}")
async def ticker_u(interval):
    t = int(time.time() * 1000)
    if t - cache_ticker_u_time[interval] <= cache_time:
        return cache_ticker_u[interval]
    top_symbols = json.dumps(SYM_USDT[:100]).replace(" ", "").replace("/", "")
    url = 'api/v3/ticker?symbols=' + top_symbols + '&windowSize='+interval
    #print(url)
    url = "https://www.binance.com/" + url
    resp = requests.get(url)
    cache_ticker_u[interval] = json.loads(resp.text)
    cache_ticker_u_time[interval] = t
    return cache_ticker_u[interval]

@app.get("/ticker_b/{interval}")
async def ticker_b(interval):
    t = int(time.time() * 1000)
    if t - cache_ticker_b_time[interval] <= cache_time:
        return cache_ticker_b[interval]
    top_symbols = json.dumps(SYM_BTC[:100]).replace(" ", "").replace("/", "")
    url = 'api/v3/ticker?symbols=' + top_symbols + '&windowSize='+interval
    #print(url)
    url = "https://www.binance.com/" + url
    resp = requests.get(url)
    cache_ticker_b[interval] = json.loads(resp.text)
    cache_ticker_b_time[interval] = t
    return cache_ticker_b[interval]

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

#下载最新的软件
#软件路径：download/Ayyyymmddx.apk
#注意返回的是文件流，不是默认的json
@app.get("/android")
async def android():
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
    #返回最新版本的文件流
    filename_client = 'TradingContest_'+str(version)+'.apk'
    filename_server = 'A'+str(version)+'.apk'
    filepath = 'download/' + filename_server
    return FileResponse(path=filepath,filename=filename_client)

#下载指定版本的软件
@app.get("/download/{version}")
async def download(version):
    #返回指定版本的文件流
    filename = 'A'+str(version)+'.apk'
    filepath = 'download/' + filename
    return FileResponse(path=filepath,filename=filename)

#返回程序启动时动态执行的代码
@app.get("/start_up_code/",response_class=PlainTextResponse)
async def start_up_code():
    filename = 'dynamic/start_up_code.py'
    with open(filename, 'r', encoding='utf-8') as f:
        s = f.read()
        return s

#为了certbot认证，支持访问该路径：
#.well-known/acme-challenge/{str}
@app.get("/.well-known/acme-challenge/{str}",response_class=PlainTextResponse)
async def acme(s):
    with open('.well-known/acme-challenge/'+s, 'r', encoding='utf-8') as f:
        s = f.read()
        print(s)
        return s

#链接到index.html
@app.get("/", response_class=HTMLResponse)
async def index():
    with open('pages/index.html', 'r', encoding='utf-8') as f:
        return f.read()

#定义全局活动订单对象，维护open状态的订单
#第一维度：symbol
#第二维度：user_id
#第三维度：order_id
global_orders = defaultdict(lambda:defaultdict(list))

#初始化全局活动订单对象
order.init_orders(global_orders)

def pywebio_task():
    pywebio.session.run_js('WebIO._state.CurrentSession.on_session_close(()=>{setTimeout(()=>location.reload(), 4000})')
    myapp.pywebio_run()
    
# `pywebio_task` is PyWebIO task function
#取消PyWebIO入口
# app.mount("/home", FastAPI(routes=webio_routes(pywebio_task),debug=True))


#开启websocket监听
#my_websockets.start_listening(global_orders)

# 运行指令：
'''
uvicorn main:app --reload
uvicorn main:app --host 0.0.0.0 --port 2023 --reload
'''
