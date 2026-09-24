# ==========================================
# CHAT API
# FishAI Agentic RAG
# ==========================================

from pathlib import Path
from uuid import uuid4
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel

from app.ai_service import generate_ai_response
from app.router_agent import route_query

from app.agents.dispatcher import dispatch_agent
from app.agents.fish_agent import fish_knowledge_agent
from app.agents.rag_agent import rag_agent
from app.agents.time_agent import time_agent
from app.agents.fish_identification_agent import fish_identification_agent
from app.auth import current_user
from app.db import add_message, create_conversation, get_conversation


# ==========================================
# CREATE ROUTER
# ==========================================

router = APIRouter(
    prefix="/api",
    tags=["Chat"]
)


# ==========================================
# CHAT MESSAGE MODEL
# ==========================================

class ChatMessage(BaseModel):
    role: str
    content: str


# ==========================================
# CHAT REQUEST MODEL
# ==========================================

class ChatRequest(BaseModel):
    message: str
    conversation: List[ChatMessage] = []
    conversation_id: Optional[int] = None


# ==========================================
# CHAT RESPONSE MODEL
# ==========================================

class ChatResponse(BaseModel):
    success: bool
    response: str
    route: str
    agent: str
    conversation_id: Optional[int] = None


# ==========================================
# NORMAL CHAT ENDPOINT
# ==========================================

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, user=Depends(current_user)):

    # ------------------------------------------
    # GET USER MESSAGE
    # ------------------------------------------

    user_message = request.message.strip()

    if not user_message:

        return ChatResponse(
            success=False,
            response="Please enter a message.",
            route="NONE",
            agent="NONE"
        )

    try:

        if request.conversation_id:
            stored_conversation = get_conversation(user["id"], request.conversation_id)
            if not stored_conversation:
                raise HTTPException(status_code=404, detail="Conversation not found.")
            conversation_id = request.conversation_id
            conversation = [
                {"role": item["role"], "content": item["content"]}
                for item in stored_conversation["messages"]
            ]
        else:
            conversation_record = create_conversation(
                user["id"],
                user_message[:60],
            )
            conversation_id = conversation_record["id"]
            conversation = []

        add_message(user["id"], conversation_id, "user", user_message)

        # ==========================================
        # QUERY ROUTER
        # ==========================================

        selected_route = route_query(user_message)

        print(
            f"[ROUTER] Question: {user_message}"
        )

        print(
            f"[ROUTER] Selected route: {selected_route}"
        )


        # ==========================================
        # AGENT DISPATCHER
        # ==========================================

        selected_agent = dispatch_agent(
            selected_route
        )

        print(
            f"[DISPATCHER] Selected agent: {selected_agent}"
        )


        # ==========================================
        # CONVERSATION HISTORY
        # ==========================================

        # ==========================================
        # FISH INFORMATION AGENT
        # ==========================================

        if selected_route == "FISH_INFORMATION":

            ai_response = await fish_knowledge_agent(
                user_message=user_message,
                conversation=conversation
            )


        # ==========================================
        # DOCUMENT RAG AGENT
        # ==========================================

        elif selected_route == "DOCUMENT_QUERY":

            ai_response = await rag_agent(
                user_message=user_message,
                conversation=conversation
            )


        # ==========================================
        # TIME AGENT
        # ==========================================

        elif selected_route == "TIME_QUERY":

            ai_response = await time_agent(
                user_message=user_message,
                conversation=conversation
            )


        # ==========================================
        # FISH IDENTIFICATION AGENT
        # ==========================================

        elif selected_route == "IMAGE_ANALYSIS":

            ai_response = await fish_identification_agent(
                user_message=user_message,
                conversation=conversation
            )


        # ==========================================
        # GENERAL / TECHNOLOGY / CONVERSATION
        # ==========================================

        else:

            ai_response = await generate_ai_response(
                user_message=user_message,
                conversation=conversation
            )


        # ==========================================
        # RETURN RESPONSE
        # ==========================================

        add_message(user["id"], conversation_id, "assistant", ai_response)

        return ChatResponse(
            success=True,
            response=ai_response,
            route=selected_route,
            agent=selected_agent,
            conversation_id=conversation_id,
        )


    # ==========================================
    # ERROR HANDLING
    # ==========================================

    except HTTPException:
        raise

    except Exception as error:

        print(
            "AI ERROR:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to generate AI response."
        )


# ==========================================
# FISH IMAGE UPLOAD
# ==========================================

UPLOAD_DIR = Path(
    "uploads/fish_images"
)

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ==========================================
# IMAGE IDENTIFICATION ENDPOINT
# ==========================================

@router.post("/chat/image")
async def identify_fish_image(
    image: UploadFile = File(...)
):

    # ==========================================
    # ALLOWED IMAGE TYPES
    # ==========================================

    allowed_types = {
        "image/jpeg",
        "image/png",
        "image/webp"
    }


    # ==========================================
    # VALIDATE IMAGE TYPE
    # ==========================================

    if image.content_type not in allowed_types:

        raise HTTPException(
            status_code=400,
            detail=(
                "Only JPG, PNG and WEBP "
                "images are supported."
            )
        )


    # ==========================================
    # GET FILE EXTENSION
    # ==========================================

    extension = Path(
        image.filename or ""
    ).suffix.lower()


    if not extension:

        extension = ".jpg"


    # ==========================================
    # GENERATE UNIQUE FILE NAME
    # ==========================================

    filename = (
        f"{uuid4()}{extension}"
    )


    file_path = (
        UPLOAD_DIR / filename
    )


    # ==========================================
    # SAVE IMAGE
    # ==========================================

    try:

        with open(
            file_path,
            "wb"
        ) as buffer:

            while True:

                chunk = await image.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                buffer.write(chunk)


    except Exception as error:

        print(
            "IMAGE UPLOAD ERROR:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to upload image."
        )


    # ==========================================
    # SEND IMAGE TO FISH IDENTIFICATION AGENT
    # ==========================================

    try:

        ai_response = await fish_identification_agent(
            image_path=str(file_path),
            user_message=(
                "Identify this fish from "
                "the uploaded image."
            ),
            conversation=[]
        )


    except Exception as error:

        print(
            "FISH IDENTIFICATION ERROR:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to analyze fish image."
            )
        )


    # ==========================================
    # RETURN RESULT
    # ==========================================

    return {

        "success": True,

        "message": (
            "Fish image uploaded successfully."
        ),

        "filename": filename,

        "image_path": str(file_path),

        "response": ai_response
    }
