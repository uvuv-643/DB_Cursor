from fastapi import FastAPI
from .connection.connection_routes import router as connection_router
app = FastAPI()
app.include_router(connection_router)

@app.get("/")
async def hello_world():
    return {"message": "Hello World! From github actions."}
 

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

