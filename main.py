from fastapi import FastAPI
import  requests

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/agent/")
async def agent(url):
    #访问url，获取返回值，并返回
    resp = requests.get(url)
    return resp.text

# 运行指令：
'''
uvicorn main:app --reload
uvicorn main:app --host 0.0.0.0 --port 2023 --reload
'''
