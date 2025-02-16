from fastapi import FastAPI
from fastapi import Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.api import kanban_router

templates = Jinja2Templates(directory="src/templates")


app = FastAPI()
app.mount("/static", StaticFiles(directory="src/static"), name="static")


app.include_router(kanban_router)


@app.get("/home/")
def home(request: Request):
    return templates.TemplateResponse("index.html", context={"request": request})


@app.get("/teststyles/")
def test_styles(request: Request):
    return templates.TemplateResponse("test_styles.html", context={"request": request})


@app.get("/kanban/")
def kanban(request: Request):
    return templates.TemplateResponse("kanban.html", context={"request": request})
