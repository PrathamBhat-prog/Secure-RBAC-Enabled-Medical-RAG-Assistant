from fastapi import APIRouter, Depends, Form, HTTPException

from auth.routes import authenticate
from chat.chat_query import answer_query


router = APIRouter()


@router.post("/chat")
async def chat(user=Depends(authenticate), message: str = Form(...)):
    if not (message or "").strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    return await answer_query(message, user["role"])
