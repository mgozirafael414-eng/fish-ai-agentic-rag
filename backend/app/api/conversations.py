from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth import current_user
from app.db import (
    add_message,
    create_conversation,
    delete_conversation,
    get_conversation,
    get_conversations,
)

router = APIRouter(prefix="/api/conversations", tags=["Conversations"])


class ConversationCreate(BaseModel):
    title: str = "New chat"


class MessageCreate(BaseModel):
    role: str
    content: str
    metadata: dict | None = None


@router.get("")
def list_user_conversations(user=Depends(current_user)):
    return {"success": True, "conversations": get_conversations(user["id"])}


@router.post("")
def create_user_conversation(request: ConversationCreate, user=Depends(current_user)):
    return {"success": True, "conversation": create_conversation(user["id"], request.title)}


@router.get("/{conversation_id}")
def get_user_conversation(conversation_id: int, user=Depends(current_user)):
    conversation = get_conversation(user["id"], conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return {"success": True, "conversation": conversation}


@router.post("/{conversation_id}/messages")
def create_user_message(
    conversation_id: int,
    request: MessageCreate,
    user=Depends(current_user),
):
    if request.role not in {"user", "assistant"}:
        raise HTTPException(status_code=400, detail="Invalid message role.")
    try:
        message = add_message(
            user["id"], conversation_id, request.role, request.content, request.metadata
        )
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return {"success": True, "message": message}


@router.delete("/{conversation_id}")
def remove_user_conversation(conversation_id: int, user=Depends(current_user)):
    if not delete_conversation(user["id"], conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return {"success": True, "conversation_id": conversation_id}
