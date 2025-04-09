import bcrypt
import jwt

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

from datetime import datetime, timedelta, timezone
from typing import Optional

from src.entity.models import User
from src.conf.connfig import config
from src.database.db import get_db
from src.repository import users as repository_users

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


class Auth:
    SECRET_KEY = config.SECRET_KEY
    ALGORITHM = config.ALGORITHM

    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )

    def _create_token(self, data: dict, expires_delta: timedelta, scope: str) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update(
            {
                "iat": datetime.now(timezone.utc),
                "sub": data.get("sub"),
                "exp": expire,
                "scope": scope,
            }
        )
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        return self._create_token(
            data, expires_delta or timedelta(minutes=15), "access_token"
        )

    def create_refresh_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        return self._create_token(
            data, expires_delta or timedelta(days=7), "refresh_token"
        )

    def create_email_token(self, data: dict) -> str:
        return self._create_token(data, timedelta(days=1), "email_token")

    def get_email_from_token(self, token: str):
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload.get("sub")
        except jwt.PyJWTError as err:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid token for email verification",
            )

    async def decode_refresh_token(self, refresh_token: str) -> str:
        try:
            payload = jwt.decode(
                refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM]
            )
            if payload["scope"] != "refresh_token":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid scope"
                )
            return payload["sub"]
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

    async def get_current_user(
        self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
    ) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload.get("scope") != "access_token":
                raise credentials_exception
            email = payload.get("sub")
            if not email:
                raise credentials_exception
        except jwt.PyJWTError:
            raise credentials_exception

        user = await repository_users.get_user_by_email(email, db)
        if not user:
            raise credentials_exception
        return user


auth_service = Auth()
