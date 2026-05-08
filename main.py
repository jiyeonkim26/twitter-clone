'''
Starts a Twitter Clone Webpage.
'''

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
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

def check_credentials(request: Request):
    '''
    returns username if user is logged in.
    if not logged in, return None.
    '''
    # Check values typed into the login form / URL
    query_username = request.query_params.get('username')
    query_password = request.query_params.get('password')
    print('query_username=', query_username)
    print('query_password=', query_password)

    # Check values saved in browser cookies
    cookie_username = request.cookies.get('username')
    cookie_password = request.cookies.get('password')
    print('cookie_username=', cookie_username)
    print('cookie_password=', cookie_password)

    # Prefer the login form values if they exist
    if query_username is not None and query_password is not None:
        username = query_username
        password = query_password
    else:
        username = cookie_username
        password = cookie_password

    # If there is no username/password from either place, user is not logged in
    if username is None or password is None:
        print("no username/password found")
        return None

    # Check username/password against database
    con = sqlite3.connect('twitter_clone.db')
    cur = con.cursor()

    sql = """
    SELECT username
    FROM users
    WHERE username = ? AND password = ?;
    """

    cur.execute(sql, [username, password])
    row = cur.fetchone()

    con.close()

    # If no matching user was found
    if row is None:
        print("username/password did not match database")
        return None

    # If a matching user was found
    username = row[0]
    print(f"logged in as {username}")
    return username

def username_exists(username):
    """
    Returns True if username is already in the database.
    Returns False otherwise.
    """
    # Check username against database
    con = sqlite3.connect('twitter_clone.db')
    cur = con.cursor()

    sql = """
    SELECT id
    FROM users
    WHERE username = ?;
    """

    cur.execute(sql, [username])
    row = cur.fetchone()

    con.close()

    # If no matching username is found, return False (else True)
    if row is None:
        return False
    else:
        return True

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
            "is_logged_in": check_credentials(request),
            "username": check_credentials(request),
            "messages": messages
        }
    )
    con.close()

@app.get('/logout', response_class=HTMLResponse)
async def logout(request: Request):
    response = templates.TemplateResponse(
        request=request,
        name='logout.html',
    )
    response.delete_cookie(key='username')
    response.delete_cookie(key='password')
    return response

@app.get('/login', response_class=HTMLResponse)
async def login(request: Request): # can't write doctests for async functions
    query_username = request.query_params.get('username')
    query_password = request.query_params.get('password')

    # Page was opened normally, before the form was submitted
    if query_username is None and query_password is None:
        return templates.TemplateResponse(
            request=request,
            name='login.html',
            context={
                'is_logged_in': False,
                'username': None,
                'error': None,
            }
        )

    # Form was submitted, but username or password was blank
    if not query_username or not query_password:
        return templates.TemplateResponse(
            request=request,
            name='login.html',
            context={
                'is_logged_in': False,
                'username': None,
                'error': 'Please enter both a username and password.',
            }
        )

    # Use check_credentials to check the database
    username = check_credentials(request)

    # If username is None, the database did not find a match
    if username is None:
        return templates.TemplateResponse(
            request=request,
            name='login.html',
            context={
                'is_logged_in': False,
                'username': None,
                'error': 'Invalid username or password.',
            }
        )

    # If username is not None, login succeeded
    response = RedirectResponse(url='/', status_code=302)
    response.set_cookie(key='username', value=request.query_params.get('username'))
    response.set_cookie(key='password', value=request.query_params.get('password'))
    return response

@app.get('/create_user', response_class=HTMLResponse)
async def create_user(request: Request):
    username = request.query_params.get('username')
    password = request.query_params.get('password')
    confirm_password = request.query_params.get('confirm_password')
    age = request.query_params.get('age')

    error = None

    # If incomplete fields, non-matching passwords, and pre-existing usernames
    if username is not None:
        if username == "" or password == "" or confirm_password == "" or age == "":
            error = "Please fill out all fields."
        elif password != confirm_password:
            error = "Passwords do not match."
        elif username_exists(username):
            error = "That username is already taken. Please choose another one."

        # Connects to database and inserts fields if no error
        else:
            con = sqlite3.connect('twitter_clone.db')
            cur = con.cursor()

            sql = """
            INSERT INTO users (username, password, age)
            VALUES (?, ?, ?);
            """

            cur.execute(sql, [username, password, age])
            con.commit()
            con.close()

            # Takes user to login page after creating account
            return templates.TemplateResponse(
                request=request,
                name='login.html',
                context={
                    'error': "Account created! Please log in.",
                    'is_logged_in': False
                }
            )

    return templates.TemplateResponse(
        request=request,
        name='create_user.html',
        context={
            'error': error,
            'is_logged_in': False
        }
    )

@app.get('/create_message', response_class=HTMLResponse)
async def create_message(request: Request):
    username = check_credentials(request)
    message = request.query_params.get('message')

    error = None
    success = None

    # If user is not logged in, send them to login page
    if username is None:
        return templates.TemplateResponse(
            request=request,
            name='login.html',
            context={
                'error': 'Please log in before creating a message.',
                'is_logged_in': False
            }
        )

    # If the user submitted the form
    if message is not None:
        if message == "":
            error = "Message cannot be blank."
        else:
            con = sqlite3.connect('twitter_clone.db')
            cur = con.cursor()

            # Find the id of the logged-in user
            sql = """
            SELECT id
            FROM users
            WHERE username = ?;
            """

            cur.execute(sql, [username])
            row = cur.fetchone()

            if row is None:
                error = "Could not find logged-in user in database."
            else:
                sender_id = row[0]

                # Insert the new message into database, record current time in localtime
                sql = """
                INSERT INTO messages (sender_id, message, created_at)
                VALUES (?, ?, datetime('now', 'localtime'));
                """

                cur.execute(sql, [sender_id, message])
                con.commit()

                success = "Message created!"

            con.close()

    return templates.TemplateResponse(
        request=request,
        name='create_message.html',
        context={
            'is_logged_in': username,
            'username': username,
            'error': error,
            'success': success
        }
    )

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)
