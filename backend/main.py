from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.routes import thread_router
from src.infrastructure.database import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield


app = FastAPI(
    title="AsyncLang Chat API",
    description="LLM Chat Application Backend",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(thread_router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "AsyncLang Chat API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
