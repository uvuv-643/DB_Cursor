from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .connections.routes import router as connections_router
from .prompts.routes import router as prompts_router

app = FastAPI()

# CORS for frontend app using cookies
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://uvuv643.ru",
        "https://www.uvuv643.ru",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include routers
app.include_router(connections_router)
app.include_router(prompts_router)
