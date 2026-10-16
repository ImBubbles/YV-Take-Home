from fastapi import FastAPI
from fastapi import HTTPException
from context import yv_context
from datetime import date

app = FastAPI()

@app.get("/")
def root():
  return {"message": "Hello, world!"}

@app.get("/votd")
def get_votd(day: int = date.today().timetuple().tm_yday, version: int = 12):
  if day < 1 or day > 366:
    raise HTTPException(
      status_code=400,
      detail={
        "code": "INVALID_DAY",
        "message": "day must be an integer between 1 and 366"
      }
    )
  if not yv_context.yv_is_eligible_version(version):
    raise HTTPException(
      status_code=400,
      detail={
        "code": "INVALID_DAY",
        "message": "day must be an integer between 1 and 366"
      }
    )
  return yv_context.yv_get_votd(day, version)