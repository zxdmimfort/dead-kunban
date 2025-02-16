import json

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse

from src.models import Kanban

kanban_router = APIRouter()


@kanban_router.get("/kanban_pull")
def kanban_pull(request: Request):
    with open("kanban.json", "r", encoding="utf-8") as file:
        obj = json.load(file)
    return JSONResponse(content=obj)


@kanban_router.post("/kanban_push")
def kanban_push(kanban: Kanban):
    with open("kanban.json", "w", encoding="utf-8") as file:
        file.write(kanban.model_dump_json())
    return Response(status_code=200)
