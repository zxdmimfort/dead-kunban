from typing import Dict, Any

from fastapi import FastAPI, Request, APIRouter, Response

api_router = APIRouter()

from src.models import Kanban
from fastapi import FastAPI, Request, Response
from starlette.staticfiles import StaticFiles
from src.models import Kanban


@api_router.post('/kanban_push')
def kanban_push(kanban: Kanban):
    print(kanban)
    return Response(status_code=404, headers={})


from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

import json


@api_router.get('/kanban_pull')
def kanban_pull(request: Request):
    with open("../kanban.json", 'r', encoding='utf-8') as file:
        obj = json.load(file)
    return JSONResponse(content=obj)


@api_router.post('/kanban_push')
def kanban_push():
    print()
    print(1 + 2)
    return Response(status_code=200)
    # kanban = schema.load(data=loads, partial=True)
    # print(kanban)
    # with open('kanban.json', 'w', encoding='utf-8') as file:
    #     json.dump(kanban, file, ensure_ascii=False, indent=4)
    # return JSONResponse(content=obj)
