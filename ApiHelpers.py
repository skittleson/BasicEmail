import jwt
from fastapi import HTTPException, Request, Response, status
import datetime
from dotenv import load_dotenv
import os

# openssl rand -hex 32
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
print(SECRET_KEY)

# https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/


@staticmethod
def is_session_valid(request: Request) -> bool:
    token = request.cookies.get('session')
    if token is None:
        if 'authorization' in request.headers.keys():
            token = request.headers['Authorization']
    try:
        # Decode the JWT token
        decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return True
    except jwt.ExpiredSignatureError:
        # Handle token expiration
        print('Token has expired')
        raise HTTPException(410, detail='token expired')
    except jwt.DecodeError:
        # Handle invalid token
        print('Invalid token')
    # return False
    raise HTTPException(403)


@staticmethod
def jwt_encode(payload):
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


@staticmethod
def set_session_cookie(response: Response, value: str, hours: int):
    expires = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) + \
        datetime.timedelta(hours=hours)
    response.set_cookie(
        key='session', value=value, httponly=True, samesite="strict", expires=expires)
