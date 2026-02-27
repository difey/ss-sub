from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from contextlib import asynccontextmanager
from src.routers import subscription, rules
from src.services.scheduler import start_scheduler, stop_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    start_scheduler()
    yield
    # Shutdown
    stop_scheduler()

app = FastAPI(title="Clash Subscription Merger", lifespan=lifespan)

app.include_router(subscription.router)
app.include_router(rules.router)

os.makedirs("static", exist_ok=True)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
