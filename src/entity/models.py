import enum
from datetime import date

from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy import String, Integer, ForeignKey, DateTime, func, Enum, Boolean


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
    created_at: Mapped[date] = mapped_column(DateTime, server_default=func.now())
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
