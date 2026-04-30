'''
Starts a hello world observer.
'''
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import sqlite3
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory='templates')

# Internal Server Error: 
# always means a python error inside of the function that corresponds to
# the route or "page" you were connecting to in Firefox
@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    is_logged_in = True

    # extract username from database
    con = sqlite3.connect('twitter_clone.db')
    cur = con.cursor()
    sql = """
    SELECT username FROM users WHERE id=1;
    """
    cur.execute(sql)
    for row in cur.fetchall():
        username=row[0]
    
    # create response
    return templates.TemplateResponse(
        request=request,
        name='index.html',
        context={
            'is_logged_in': is_logged_in,
            'username': username,
        }
    )
    return '<i>hello</i> <b>world</b>'

@app.get('/login', response_class=HTMLResponse)
async def login(request: Request): # can't write doctests for async functions
    is_logged_in = True
    return templates.TemplateResponse(
        request=request,
        name='login.html',
        context={
            'is_logged_in': is_logged_in,
        }
    )

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)

