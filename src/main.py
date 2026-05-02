from fastapi import FastAPI
from src.db.session import init_db
from src.api.v1.api import api_router

app = FastAPI(title="Masjid Management System", version="0.1.0")

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(api_router, prefix="/api/v1")
