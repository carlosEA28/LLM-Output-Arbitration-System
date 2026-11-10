from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.api.routes.arbitration import router as arbitration_router
from src.api.routes.health import router as health_router

app = FastAPI()


@app.exception_handler(RequestValidationError)
def invalid_request(_request: Request, _error: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": "Invalid request"})


app.include_router(health_router)
app.include_router(arbitration_router)
