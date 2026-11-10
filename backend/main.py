from fastapi import FastAPI
from routes import health, ask

app = FastAPI()

API_PREFIX = "/api"

app.include_router(health.router, prefix=API_PREFIX)
app.include_router(ask.router, prefix=API_PREFIX)
