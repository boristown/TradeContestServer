from fastapi import FastAPI
import  requests
import base64
from binanceAPI import *
import json

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
@app.get("/ticker/{interval}")
async def ticker(interval):
    top_symbols = json.dumps(top100_symbols[:100]).replace(" ", "")
    url = 'api/v3/ticker?symbols=' + top_symbols + '&windowSize='+interval
    #print(url)
    url = "https://www.binance.com/" + url
    resp = requests.get(url)
    return json.loads(resp.text)

@app.get("/symbols/")
async def symbols():
    return top100_symbols[:100]

# 运行指令：
'''
uvicorn main:app --reload
uvicorn main:app --host 0.0.0.0 --port 2023 --reload
'''
