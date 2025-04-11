from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.repository.chat import (
    create_message,
    get_messages_for_room,
    get_room_by_id,
    create_room,
    get_room_by_usernames,
)
from src.repository.users import get_user_by_username
from src.services.auth import auth_service
from src.schemas.chat import RoomSchema
import json

router = APIRouter(prefix="/chat", tags=["chat"])

active_connections: dict[int, list[WebSocket]] = {}


@router.post("/create-room", response_model=RoomSchema)
async def create_chat_room(body: RoomSchema, db: AsyncSession = Depends(get_db)):
    room = await create_room(body, db)
    return room


@router.get("/get-room")
async def get_room(username1: str, username2: str, db: AsyncSession = Depends(get_db)):
    room = await get_room_by_usernames(username1, username2, db)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@router.get("/messages/{room_id}")
async def get_messages(room_id: int, db: AsyncSession = Depends(get_db)):
    messages = await get_messages_for_room(room_id, db)
    return messages


@router.websocket("/ws/{room_id}/{username}")
async def websocket_chat(
    websocket: WebSocket,
    room_id: int,
    username: str,
    db: AsyncSession = Depends(get_db),
):
    await websocket.accept()

    user = await get_user_by_username(username, db)
    if not user:
        await websocket.close(code=1008)
        return

    room = await get_room_by_id(room_id, db)
    if not room:
        await websocket.close(code=1008)
        return

    if room_id not in active_connections:
        active_connections[room_id] = []
    active_connections[room_id].append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            msg_schema = {
                "room_id": room_id,
                "sender_id": user.id,
                "message": message_data["message"],
            }
            new_msg = await create_message(msg_schema, db)

            for conn in active_connections[room_id]:
                await conn.send_json(
                    {
                        "message": new_msg.message,
                    }
                )

    except WebSocketDisconnect:
        active_connections[room_id].remove(websocket)
        if not active_connections[room_id]:
            del active_connections[room_id]
