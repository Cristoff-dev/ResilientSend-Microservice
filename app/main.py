# app/main.py
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routes import router as notification_router

# Configure standard logging for the microservice observability
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI application with detailed Swagger UI metadata
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A fault-tolerant notification microservice with automatic failover, rate limiting, and idempotency.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS (Cross-Origin Resource Sharing)
# Essential for allowing frontend applications or external SaaS platforms to consume this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Security note: In production, replace "*" with specific client domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the notification routing module
app.include_router(notification_router)

@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint utilized by container orchestrators (e.g., Kubernetes, Docker Swarm) 
    and load balancers (e.g., AWS ALB, Render) to verify service uptime.
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": "production"
    }