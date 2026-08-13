"""FastAPI entrypoint. Run with: uvicorn app.main:app --reload"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .profile.route import router as profile_router
from .search.route import router as search_router

app = FastAPI(title="who-is API")

# Local dev only — the Astro dev server's origin, plus Cloudflare quick tunnels (random
# *.trycloudflare.com subdomain each run, so a regex instead of a fixed origin) for sharing a
# local run over a public URL. Tighten before any real deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4321", "http://127.0.0.1:4321"],
    allow_origin_regex=r"https://.*\.trycloudflare\.com",
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search_router)
app.include_router(profile_router)


@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    """Domain services raise HTTPException with `detail` already shaped like .docs/API_CONTRACT.md's
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
