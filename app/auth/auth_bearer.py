from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from app.constants.message_keys import MessageKeys
from app.models import UserInDB, TokenData, StandardResponse
from fastapi import HTTPException, Depends, status
from jose import JWTError, jwt
from app.auth.auth_handler import get_user
from app.utils.response import make_response
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
TOKEN = "token"

auth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

async def get_current_user(token: str = Depends(auth2_scheme)):
    credentials_exception = JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=make_response(
            success=False,
            message_key=MessageKeys.NOT_AUTHENTICATED,
            data=None,
            errors=None
        )
    )     
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        token_data = TokenData(username=username)
        user = get_user(username=token_data.username)
        if user is None:
            raise credentials_exception
        return user

    except JWTError:
        raise credentials_exception

async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    if current_user.disabled:
        raise JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=make_response(
            success=False,
            message_key=MessageKeys.NOT_AUTHENTICATED,
            data=None,
            errors=None
        )
    )
    return current_user

async def get_current_active_superuser(current_user: UserInDB = Depends(get_current_active_user)):
    if not current_user.is_superuser:
        raise JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=make_response(
                success=False,
                message_key=MessageKeys.NOT_AUTHENTICATED,
                data=None,
                errors=None
            )
        )
    return current_user