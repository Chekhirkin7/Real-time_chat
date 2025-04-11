from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import Room, Message
from src.schemas.chat import RoomSchema, MessageSchema
from src.repository.users import get_user_by_username


async def create_room(body: RoomSchema, db: AsyncSession = Depends(get_db)):
    new_room = Room(**body.model_dump())
    db.add(new_room)
    await db.commit()
    await db.refresh(new_room)
    return new_room


async def get_room_by_usernames(
    username1: str, username2: str, db: AsyncSession = Depends(get_db)
):
    user1 = await get_user_by_username(username1, db)
    user2 = await get_user_by_username(username2, db)
    user_id_1 = user1.id
    user_id_2 = user2.id
    stmt = select(Room).filter_by(user1_id=user_id_1, user2_id=user_id_2)
    room = await db.execute(stmt)
    room = room.scalar_one_or_none()
    return room


async def create_message(body: MessageSchema, db: AsyncSession = Depends(get_db)):
    new_message = Message(**body)
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)
    return new_message


async def get_messages_for_room(room_id: int, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Message)
        .filter(Message.room_id == room_id)
        .order_by(Message.timestamp.asc())
    )
    result = await db.execute(stmt)
    messages = result.scalars().all()
    return messages


async def get_room_by_id(room_id: int, db: AsyncSession):
    stmt = select(Room).where(Room.id == room_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
