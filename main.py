import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from dotenv import load_dotenv

load_dotenv()

from routes.auth_routes import router as auth_router
from routes.property_routes import router as property_router

app = FastAPI(title="Real Estate API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom exception handlers to match Node.js response structure: {"message": "..."}
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    error_msg = "Validation error"
    if errors:
        loc_list = errors[0].get("loc", [])
        # Ignore 'body' in loc list if present to keep it user friendly
        if len(loc_list) > 1 and loc_list[0] == "body":
            loc_list = loc_list[1:]
        loc = ".".join(str(x) for x in loc_list)
        msg = errors[0].get("msg", "invalid value")
        error_msg = f"{loc}: {msg}"
    return JSONResponse(
        status_code=400,
        content={"message": error_msg},
    )

# Include Routers
app.include_router(auth_router, prefix="/api/auth")
app.include_router(property_router, prefix="/api/properties")

# Test Route
@app.get("/")
def home():
    return PlainTextResponse("Real Estate API is running...")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
