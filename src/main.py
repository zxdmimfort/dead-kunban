from fastapi import FastAPI
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles
from fastapi import Request
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="src/templates")


from src.api import api_router

routes = [
    Mount("/static", app=StaticFiles(directory="src/static"), name="static"),
]
app = FastAPI(routes=routes)
app.include_router(api_router)



@app.get("/home")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get('/teststyles/')
def test_styles(request: Request):
    return templates.TemplateResponse('test_styles.html', context={"request": request})