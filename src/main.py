from fastapi import FastAPI
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

@app.get("/")
def read_root():
    return {"message": "Clash Subscription Merger is running"}
