import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles
from fastapi import Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="./templates")

from src.api import api_router

routes = [
    Mount("/static", app=StaticFiles(directory="static"), name="static"),
]
app = FastAPI(routes=routes)


app.include_router(api_router)

@app.get("/home/")
def home(request: Request):
    return templates.TemplateResponse("index.html", context={"request": request})


@app.get('/teststyles/')
def test_styles(request: Request):
    return templates.TemplateResponse('test_styles.html', context={"request": request})


@app.get('/kanban/')
def kanban(request: Request):
    return templates.TemplateResponse('kanban.html', context={"request": request})


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
    )
