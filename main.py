from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/")
def home():
    return {"status": "ok"}

@app.post("/woocommerce/order")
async def receive_order(request: Request):
    data = await request.json()
    print(data)

    return {"ok": True}
