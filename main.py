from fastapi import FastAPI
import  requests

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/agent/")
def agent(url):
    #访问url，获取返回值，并返回
    print("req:",url)
    resp = requests.get(url)
    print("res:",resp.text)
    return resp.text

# 运行指令：
'''
uvicorn main:app --reload
uvicorn main:app --host 0.0.0.0 --port 2023 --reload
'''
