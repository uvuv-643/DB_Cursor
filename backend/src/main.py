from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def hello_world():
    return {"message": "Hello World! From github actions."}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

