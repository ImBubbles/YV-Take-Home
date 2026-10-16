from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from context import yv_context
from datetime import date

app = FastAPI()

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
  detail = exc.detail
  if not isinstance(detail, dict) or "code" not in detail or "message" not in detail:
    detail = {"code": "REQUEST_FAILED", "message": "The request could not be completed"}
  return JSONResponse(status_code=exc.status_code, content={"error": detail})

@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
  invalid_day = any(error["loc"] == ("query", "day") for error in exc.errors())
  if invalid_day:
    error = {
      "code": "INVALID_DAY",
      "message": "day must be an integer between 1 and 366"
    }
  else:
    error = {"code": "INVALID_PARAMETER", "message": "query parameters must be valid integers"}
  return JSONResponse(status_code=400, content={"error": error})

@app.get("/")
def root():
  return {"message": "Hello, world!"}

@app.get("/votd")
def get_votd(day: int | None = None, version: int = 12):
  day_number = date.today().timetuple().tm_yday if day is None else day
  if day_number < 1 or day_number > 366:
    return JSONResponse(
      status_code=400,
      content={"error": {
        "code": "INVALID_DAY",
        "message": "day must be an integer between 1 and 366"
      }}
    )
  if not yv_context.yv_is_eligible_version(version):
    return JSONResponse(
      status_code=400,
      content={"error": {"code": "INVALID_VERSION", "message": "version is not available"}}
    )
  return yv_context.yv_get_votd(day_number, version)