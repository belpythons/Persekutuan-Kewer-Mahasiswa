from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from database import check_db_connection
from services.warmup import warmup_service
from api.routes_forecast import router as forecast_router
from api.routes_anomaly import router as anomaly_router
from api.routes_capacity import router as capacity_router
from api.routes_dashboard import router as dashboard_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI Lifespan Context Manager:
    Startup Event: Pre-load ML models (XGBoost & PyTorch) ke RAM dan jalankan dummy inference warm-up.
    Shutdown Event: Cleanup resources.
    """
    # Startup: Model Warm-up
    warmup_service.perform_warmup()
    yield
    # Shutdown: Cleanup
    pass

app = FastAPI(
    title=settings.APP_NAME,
    description="Microservice AI untuk Forecasting Fuel Ratio, Deteksi Anomali Unit (PyTorch Autoencoder), dan Combined Capacity Determination.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(forecast_router)
app.include_router(anomaly_router)
app.include_router(capacity_router)
app.include_router(dashboard_router)

@app.get("/", status_code=status.HTTP_200_OK)
def root():
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs"
    }

@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """
    Health Check Endpoint: Memeriksa kesehatan service dan status koneksi ke Database
    """
    db_status = check_db_connection()
    is_healthy = db_status.get("status") == "connected"
    
    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "environment": settings.APP_ENV,
        "database": db_status
    }

@app.get("/ready", status_code=status.HTTP_200_OK)
def readiness_check():
    """
    Readiness Probe: Memastikan model ML sudah pre-loaded di RAM dan siap menerima trafik inferensi (< 2.0s latency)
    """
    return {
        "status": "ready" if warmup_service.is_warmed_up else "warming",
        "warmup_details": warmup_service.warmup_details
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
