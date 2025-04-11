from pydantic import BaseModel, EmailStr, Field


class RoomSchema(BaseModel):
    user1_id: int
    user2_id: int


class MessageSchema(BaseModel):
    room_id: int
    sender_id: int
    received_id: int
    message: str
    read: bool = False


class MessageResponse(BaseModel):
    room_id: int
    sender_id: int
    received_id: int
    message: str


class RoomUserSchema(BaseModel):
    room_id: int
    user_id: int
