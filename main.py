from typing import Union
from fastapi import FastAPI, Request,status
from fastapi.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from mail import MailClient
import uvicorn
import atexit


app = FastAPI()
mail = MailClient()



def exit_handler():
    print('Clean up')
    mail.logout()


atexit.register(exit_handler)


@app.get("/")
async def read_root(request: Request):
    return RedirectResponse(url="/site", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/inbox/")
async def read_inbox():
    return mail.inbox()


@app.get("/mail/inbox/{uid}")
async def read_inbox_item(uid: int):
    return mail.item(uid)


if __name__ == "__main__":

    mail.login('',
               '', '')
    app.mount("/site", StaticFiles(directory="site", html=True), name="site")
    uvicorn.run(app, host="0.0.0.0", port=8002)
