from fastapi import FastAPI, Request, APIRouter, Response


from starlette.staticfiles import StaticFiles

api_router = APIRouter()

@api_router.post('/kanban_push')
def kanban_push(request: Request):
    return Response(status_code=404, headers={})


@api_router.get('/kanban_pull')
def kanban_pull(request: Request):
    return Response(status_code=404, headers={})

