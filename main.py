from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.staticfiles import StaticFiles
from mail import MailClient, LoginRequest
import uvicorn
import atexit
import datetime
from ApiHelpers import set_session_cookie, is_session_valid, jwt_encode


app = FastAPI()
mail = MailClient()


def exit_handler():
    print('Clean up')
    mail.logout()


atexit.register(exit_handler)


@app.get("/")
async def read_root():
    return RedirectResponse(url="/site", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/api/user/session")
async def current_user(request: Request):
    return is_session_valid(request)


@app.get("/api/mail/{folder}")
async def read_inbox(request: Request, folder: str = 'INBOX', q: str = None):
    try:
        is_session_valid(request)
        return mail.fetch(folder, q)
    except Exception:
        raise HTTPException(404)


@app.get("/api/mail/{folder}/{uid}")
async def read_inbox_item(request: Request, uid: int):
    is_session_valid(request)
    # this should be conditional
    # https://fastapi.tiangolo.com/advanced/custom-response/#:~:text=To%20return%20a%20response%20with%20HTML%20directly%20from,the%20parameter%20response_class%20of%20your%20path%20operation%20decorator.
    return HTMLResponse(content=mail.get_render(uid), status_code=200)


@app.get('/logout')
async def logout(response: Response):
    set_session_cookie(response=response, value='', hours=-1)
    return True


@app.post('/authenticate')
async def authenticate(response: Response, loginForm: LoginRequest):
    hours = 1
    expires = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) + \
        datetime.timedelta(hours=hours)
    payload = {
        'email': loginForm.email,
        'exp': expires
    }
    token = jwt_encode(payload)
    if mail.login(loginForm):
        set_session_cookie(response=response, value=token, hours=hours)
        return f'{token}'
    raise HTTPException(403, 'Invalid')


if __name__ == "__main__":
    app.mount("/site", StaticFiles(directory="site", html=True), name="site")
    uvicorn.run(app, host="0.0.0.0", port=8002)
