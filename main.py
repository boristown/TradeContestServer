from fastapi import FastAPI
import  requests

app = FastAPI()

@app.get("/")
async def root():
    resp = requests.get("https://wwww.binance.com/fapi/v1/ticker/price")
    return resp.text

@app.get("/agent/")
async def agent(url):
    #访问url，获取返回值，并返回
    print("req:",url)
    resp = requests.get(url)
    print("res:",resp.text)
    return resp.text

@app.get("/B/")
async def B(x):
    url = "https://wwww.binance.com/" + x
    resp = requests.get(url)
    return resp.text

# 运行指令：
'''
uvicorn main:app --reload
uvicorn main:app --host 0.0.0.0 --port 2023 --reload
'''
