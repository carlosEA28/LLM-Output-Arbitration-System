from fastapi import FastAPI

from src.api.routes.arbitration import router as arbitration_router
from src.api.routes.health import router as health_router

app = FastAPI()
app.include_router(health_router)
app.include_router(arbitration_router)
