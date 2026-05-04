'''
Starts a Twitter Clone Webpage.
'''

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import sqlite3
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory='templates')
app.mount("/static", StaticFiles(directory="static"), name="static")

# Internal Server Error: 
# always means a python error inside of the function that corresponds to
# the route or "page" you were connecting to in Firefox

def check_credentials():
    '''
    returns True if user logged in.
    '''
    ## FIXME: IMPLEMENT THIS
    return False


@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    # extract username from database
    con = sqlite3.connect('twitter_clone.db')
    cur = con.cursor()

    sql = """
    SELECT users.username, users.age, messages.message, messages.created_at
    FROM messages
    JOIN users ON messages.sender_id = users.id
    ORDER BY messages.created_at DESC;
    """

    cur.execute(sql)
    rows = cur.fetchall()
    messages = []

    for row in rows:
        messages.append({
            "username": row[0],
            "age": row[1],
            "message": row[2],
            "created_at": row[3]
        })

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "is_logged_in": check_credentials,
            "messages": messages
        }
    )
    con.close()

@app.get('/login', response_class=HTMLResponse)
async def login(request: Request): # can't write doctests for async functions
    is_logged_in = True
    return templates.TemplateResponse(
        request=request,
        name='login.html',
        context={
            'is_logged_in': check_credentials,
        }
    )

@app.get('/logout', response_class=HTMLResponse)
async def logout(request: Request):
    is_logged_in = False
    return templates.TemplateResponse(
        request=request,
        name='logout.html',
        context={
            'is_logged_in': check_credentials,
        }
    )

@app.get('/create_message', response_class=HTMLResponse)
async def create_message(request: Request):
    is_logged_in = True
    return templates.TemplateResponse(
        request=request,
        name='create_message.html',
        context={
            'is_logged_in': check_credentials,
        }
    )

@app.get('/create_user', response_class=HTMLResponse)
async def create_user(request: Request):
    is_logged_in = False
    return templates.TemplateResponse(
        request=request,
        name='create_user.html',
        context={
            'is_logged_in': check_credentials,
        }
    )

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)
