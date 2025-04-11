import enum
from datetime import datetime, timezone

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
    DeclarativeBase,
)
from sqlalchemy import (
    String,
    ForeignKey,
    DateTime,
    func,
    Enum,
    Boolean,
)


class Base(DeclarativeBase):
    pass


class Role(str, enum.Enum):
    admin = "admin"
    user = "user"


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.user)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)

    rooms: Mapped[list["Room"]] = relationship(
        "Room", secondary="room_users", back_populates="users"
    )


class Room(Base):
    __tablename__ = "rooms"
    id: Mapped[int] = mapped_column(primary_key=True)
    user1_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user2_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    users: Mapped[list["User"]] = relationship(
        "User", secondary="room_users", back_populates="rooms"
    )
    messages: Mapped["Message"] = relationship("Message", back_populates="room")


class Message(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    received_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    message: Mapped[str] = mapped_column(nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    read: Mapped[bool] = mapped_column(Boolean, default=False)

    room: Mapped["Room"] = relationship("Room", back_populates="messages")
    sender: Mapped["User"] = relationship("User", foreign_keys=[sender_id])
    received: Mapped["User"] = relationship("User", foreign_keys=[received_id])


class RoomUser(Base):
    __tablename__ = "room_users"
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)

    room: Mapped["Room"] = relationship("Room")
    user: Mapped["User"] = relationship("User")
