import jwt
import asyncio
import bcrypt

from fastapi import status, Depends
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/gateway/login")

class AuthConstructor:
    def __init__(self, app):
        self.app = app

    async def get_current_user(self, token: str = Depends(oauth2_scheme)):
        try:
            payload = jwt.decode(token, self.app.config.YOU_HAVE_BEEN_WARNED, algorithms="HS256")

            user = await self.app.db.dictionary(
                "SELECT * FROM users WHERE U_UUID = $1", payload.get("UUID")
            )

            return user

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or Expired Token",
                headers={"WWW-Authenticate": "Bearer"}
            )

    async def hash_password(self, password: str) -> bytes:
        """Hashes a password asynchronously using bcrypt."""
        # bcrypt.gensalt() and bcrypt.hashpw() are synchronous operations.
        # We run them in a separate thread to avoid blocking the event loop.
        hashed_password = await asyncio.to_thread(
            lambda: bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        )
        return hashed_password

    async def verify_password(self, password: str, hashed_password: bytes) -> bool:
        """Verifies a password asynchronously against a stored hash."""
        # bcrypt.checkpw() is a synchronous operation.
        # We run it in a separate thread to avoid blocking the event loop.
        is_valid = await asyncio.to_thread(
            lambda: bcrypt.checkpw(password.encode('utf-8'), hashed_password)
        )
        return is_valid

    async def authenticate_user(self, email: str, password: str):
        uuid, user_name, pass_key = await self.app.db.record(
            "SELECT U_UUID, USR_NAME, PASS_KEY FROM users WHERE EMAIL = $1", email
        )

        if user_name and await self.verify_password(password, pass_key.encode('utf-8')):
            return uuid, user_name

        return False

    async def generate_token(self, email: str, password: str):
        uuid, user_name = await self.authenticate_user(email, password)

        if not user_name:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or Expired Token",
                headers={"WWW-Authenticate": "Bearer"}
            )

        token_data = {
            "UUID": uuid,
            "USR_NAME": user_name
        }

        authentication_token = jwt.encode(token_data, self.app.config.YOU_HAVE_BEEN_WARNED, algorithm="HS256")
        return authentication_token

    async def verify_token(self, token: str):
        try:
            payload = jwt.decode(token, self.app.config.YOU_HAVE_BEEN_WARNED, algorithms="HS256")

            user_name, is_verified = await self.app.db.record(
                "SELECT USR_NAME, IS_VERIFIED FROM users WHERE U_UUID = $1", payload.get("UUID")
            )

            return payload.get("UUID"), user_name, is_verified

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or Expired Token",
                headers={"WWW-Authenticate": "Bearer"}
            )