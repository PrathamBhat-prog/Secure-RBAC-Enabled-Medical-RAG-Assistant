from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from psycopg2 import IntegrityError

from .hash_utils import hash_password, verify_password
from .models import SignupRequest
from config.db import create_user, find_user_by_username


router = APIRouter()
security = HTTPBasic()


def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    user = find_user_by_username(credentials.username)
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"username": user["username"], "role": user["role"]}


@router.post("/signup")
def signup(req: SignupRequest):
    if find_user_by_username(req.username):
        raise HTTPException(status_code=400, detail="User already exists")
    try:
        create_user(req.username, hash_password(req.password), req.role)
        return {"message": "User created successfully"}
    except IntegrityError:
        raise HTTPException(status_code=400, detail="User already exists")
    except Exception as e:
        print(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/login")
def login(user=Depends(authenticate)):
    return {"message": f"Welcome {user['username']}", "role": user["role"]}
