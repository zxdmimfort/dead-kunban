from typing import Dict, Any, List

from fastapi import FastAPI, Request, APIRouter, Response, Body

api_router = APIRouter()

from src.models import Kanban, KanbanCard
from fastapi import FastAPI, Request, Response
from starlette.staticfiles import StaticFiles
from src.models import Kanban
from fastapi.responses import JSONResponse

import json


@api_router.get('/kanban_pull')
def kanban_pull(request: Request):
    with open("../kanban.json", 'r', encoding='utf-8') as file:
        obj = json.load(file)
    return JSONResponse(content=obj)


@api_router.post('/kanban_push')
def kanban_push(kanban: Kanban):
    # with open('../kanban.json', 'w', encoding='utf-8') as file:
    #     json.dump(strkanban, file, ensure_ascii=False, indent=4)
    with open('../kanban.json', 'w', encoding='utf-8') as file:
        file.write(kanban.json())
    return Response(status_code=200)