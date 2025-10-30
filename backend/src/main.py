from fastapi import FastAPI

from .connections.routes import router as connections_router
from .prompts.routes import router as prompts_router

app = FastAPI()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include routers
app.include_router(connections_router)
app.include_router(prompts_router)
