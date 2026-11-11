from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes import ask, health

BASE_DIR = Path(__file__).parent
UI_DIST = BASE_DIR.parent / "ui" / "dist"

app = FastAPI(title="Shopfloor Copilot")
app.include_router(health.router, prefix="/api")
app.include_router(ask.router, prefix="/api")
app.mount("/pdfs", StaticFiles(directory=BASE_DIR / "data"), name="pdfs")
