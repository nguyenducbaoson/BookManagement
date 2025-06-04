from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from configurations import users_collection
from app.schemas import all_data
from app.models import StandardResponse, Token, User, UserOut, UserCreate
from app.auth.auth_handler import authenticate_user, create_access_token, get_password_hash
from app.auth.auth_bearer import get_current_user
from datetime import timedelta
from fastapi.responses import JSONResponse
from app.constants.message_keys import MessageKeys
from app.utils.response import make_response

app = FastAPI()
router = APIRouter()

@router.post("/token", response_model=StandardResponse)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=make_response(
            success=False,
            message_key=MessageKeys.INVALID_CREDENTIALS,
            data=None,
            errors=None
        )
    )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

    return make_response(
        success=True,
        message_key=MessageKeys.LOGIN_SUCCESS,
        data={"access_token": access_token, "token_type": "bearer"}
    )

@router.get("/user/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/user/me/items", response_model=User)
async def read_own_items(current_user: User = Depends(get_current_user)):
    return [{"item_id": 1, "owner": current_user.username}]

@router.post("/register", response_model=UserOut)
async def register_user(user: UserCreate):
    hashed_pw = get_password_hash(user.password)
    user_dict = user.dict()
    user_dict["hashed_password"] = hashed_pw
    del user_dict["password"]
    
    if users_collection.find_one({"username": user.username}):
        raise HTTPException(
            status_code=400,
            detail=MessageKeys.USERNAME_EXISTS
        )
    users_collection.insert_one(user_dict)
    return make_response(
        success=True,
        message_key=MessageKeys.REGISTER_SUCCESS,
        data=UserOut(**user_dict).dict()
    )