import uvicorn
from fastapi import FastAPI
from .db import DATABASE_URL
from .api import v1

app = FastAPI(title="Revenue Leakage Analytics Platform", version="0.1.0")

app.include_router(v1.router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
