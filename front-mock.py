from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.responses import HTMLResponse

templates = Jinja2Templates(directory="templates")

@app.get('/auth/register', response_class=HTMLResponse, include_in_schema=False)
async def show_register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get('/auth/token', response_class=HTMLResponse, include_in_schema=False)
async def show_login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})