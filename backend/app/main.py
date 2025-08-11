from contextlib import asynccontextmanager

from api import router
from db.database import create_tables
from fastapi import FastAPI


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

app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "AsyncLang Chat API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
