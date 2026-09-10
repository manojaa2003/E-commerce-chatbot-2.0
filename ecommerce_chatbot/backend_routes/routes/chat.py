from ecommerce_chatbot.Orchestration.Orchestration import app as chatbot
from ..schema import ChatRequest, ChatResponse, MessageResponse
from langchain_core.messages import HumanMessage, AIMessage
from fastapi import APIRouter, Depends,HTTPException,status
from typing import List

from sqlalchemy.orm import Session

from .. import Oauth2, models
from ..database import get_db
from .. import schema

router = APIRouter(
    tags=["chat"]
)

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest,current_user: schema.TokenData = Depends(Oauth2.get_current_user),db: Session = Depends(get_db)):

    history = (
        db.query(models.Message)
        .filter(models.Message.user_id == current_user.id)
        .order_by(models.Message.created_at.desc())
        .limit(6)
        .all()
    )

    # We retrieved newest first, so reverse it
    history = history[::-1]

    lc_messages = []

    for msg in history:
        if msg.role == "human":
            lc_messages.append(
                HumanMessage(content=msg.content)
            )
        else:
            lc_messages.append(
                AIMessage(content=msg.content)
            )

    # Current user message
    lc_messages.append(
        HumanMessage(content=request.query)
    )

    result = chatbot.invoke({
        "messages": lc_messages
    })

    ai_response = result["messages"][-1].content

    # Save current user message
    db.add(
        models.Message(
            user_id=current_user.id,
            role="human",
            content=request.query
        )
    )

    # Save AI response
    db.add(
        models.Message(
            user_id=current_user.id,
            role="ai",
            content=ai_response
        )
    )

    db.commit()

    return ChatResponse(
        response=ai_response
    )

@router.get("/chat/history", response_model=List[MessageResponse])
async def get_history(current_user: schema.TokenData = Depends(Oauth2.get_current_user), db: Session = Depends(get_db)):

    messages = db.query(models.Message).filter(models.Message.user_id == current_user.id).order_by(models.Message.created_at).all()

    if not messages:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail=f"No conversation yet!")
    return messages

@router.delete("/chat/delete")
def Delete_chat(current_user: schema.TokenData = Depends(Oauth2.get_current_user),db : Session = Depends(get_db)):
    chat = db.query(models.Message).filter(models.Message.user_id == current_user.id ).all()

    if not chat :
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail=f"No conversation yet!")

    for message in chat:
        db.delete(message)
    db.commit()

    return {
        "message": f"conversation deleted successfully"
    }