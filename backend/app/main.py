"""FastAPI entrypoint. Run with: uvicorn app.main:app --reload"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .routes import router

app = FastAPI(title="who-is API")

# Local dev only — the Astro dev server's origin. Tighten before any real deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4321", "http://127.0.0.1:4321"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    """Routes/stub raise HTTPException with `detail` already shaped like docs/API_CONTRACT.md's
    `{error, message}` — return it as the body directly instead of FastAPI's default
    `{"detail": ...}` wrapping."""
    if isinstance(exc.detail, dict) and "error" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"error": "not_found", "message": str(exc.detail)})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
    first = exc.errors()[0]
    field_path = ".".join(str(p) for p in first["loc"] if p != "body")
    message = f"{field_path}: {first['msg']}" if field_path else first["msg"]
    return JSONResponse(status_code=422, content={"error": "validation_error", "message": message})


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
