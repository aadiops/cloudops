from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from datetime import datetime, timezone
import os
import time

app = FastAPI(title="CloudOps", version="1.0.0", description="CloudOps portfolio application")

REQUEST_COUNT = Counter("cloudops_requests_total", "Total requests received")
REQUEST_LATENCY = Histogram("cloudops_request_latency_seconds", "Request latency in seconds")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

START_TIME = time.time()

@app.middleware("http")
async def metrics_middleware(request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    REQUEST_COUNT.inc()
    REQUEST_LATENCY.observe(time.perf_counter() - start_time)
    return response

@app.get("/")
async def root():
    return {
        "service": "cloudops",
        "status": "ok",
        "message": "CloudOps – Automated Cloud Infrastructure & Deployment Platform",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "environment": os.getenv("APP_ENV", "local"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

@app.get("/health")
async def health():
    uptime_seconds = round(time.time() - START_TIME, 2)
    return {
        "status": "healthy",
        "service": "cloudops",
        "uptime_seconds": uptime_seconds,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

@app.get("/ready")
async def ready():
    return {
        "status": "ready",
        "checks": {
            "application": "ok",
            "dependencies": "ok",
            "environment": os.getenv("APP_ENV", "local"),
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
