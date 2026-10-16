from fastapi import FastAPI
from context import yv_context
from datetime import date

app = FastAPI()

@app.get("/")
def root():
  return {"message": "Hello, world!"}

@app.get("/votd")
def get_votd(day: int = date.today().timetuple().tm_yday, version: int = 12):
  if day < 1 or day > 366:
    return {"message:": "Invalid day entered"}
  if not yv_context.yv_is_eligible_version(version):
    return {"message:": "Invalid version entered"}
  return yv_context.yv_get_passages(version, yv_context.yv_get_votd(day))