from typing import Annotated
from typing import List, Dict

from fastapi import FastAPI, Body, Request
from starlette.middleware.cors import CORSMiddleware
from web.routes import aeka_plan_executor_api
app = FastAPI()
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]
app.add_middleware(CORSMiddleware,
                   allow_origins=['*'],
                   allow_methods=["*"],
                   allow_headers=["*"])

app.include_router(aeka_plan_executor_api.router)


@app.get("/vulcan/hello")
def hello():
    return "hello"


@app.post("/vulcan/body_test")
def btest(goals_list: Annotated[Dict, Body()],
          pv: Annotated[int, Body()],
          tl: List[str] = Body()):
    return {"Body found": goals_list, "pv": pv, "tl": tl}

#
# if __name__ == "__main__":
#     from uvicorn import run
#       run("fast-app:app", host="127.0.0.1", port=5000, reload=False, log_level="info")
