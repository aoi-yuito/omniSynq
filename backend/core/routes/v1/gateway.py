from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse

from fastapi import Request, APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

class Gateway:
    def __init__(self, app):
        self.app = app
        self.router = APIRouter(
            prefix="/api/v1/gateway",
            tags=["gateway on v1"]
        )

        self.add_routes()

    def add_routes(self):
        self.add_get_routes()
        self.add_post_routes()
        self.add_put_routes()
        self.add_delete_routes()

    def add_get_routes(self):
        @self.router.get("/verify/{token}", response_class=HTMLResponse)
        async def user_verification(request: Request, token: str):
            uuid, user_name, is_verified = await self.app.auth.verify_token(token)

            if not is_verified:
                await self.app.db.execute("UPDATE users SET IS_VERIFIED = $1 WHERE U_UUID = $2", True, uuid)

                return self.app.jinja2template.TemplateResponse(
                    "verification.html", {
                        "request": request,
                        "user_name": user_name
                    }
                )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or Expired Token",
                headers={"WWW-Authenticate": "Bearer"}
            )

    def add_post_routes(self):
        @self.router.post("/registration")
        async def sign_up(user: self.app.models.pydantic_userIn):
            uuid_of_user = self.app.generate_id()
            user_info = user.dict(exclude_unset=True)

            hashed = await self.app.auth.hash_password(user_info["pass_key"])
            #print(f"Hashed password: {hashed.decode('utf-8')}")

            #is_correct = await self.auth.verify_password(password, hashed)
            #print(f"Password verification successful: {is_correct}")

            #wrong_password = "wrongpassword"
            #is_correct_wrong = await self.auth.verify_password(wrong_password, hashed)
            #print(f"Wrong password verification successful: {is_correct_wrong}")

            await self.app.db.execute(
                "INSERT INTO users (U_UUID, USR_NAME, EMAIL, PASS_KEY, PHONE) VALUES ($1, $2, $3, $4, $5)",
                uuid_of_user,
                user_info["user_name"],
                user_info["email"],
                hashed.decode("utf-8"),
                user_info["phone_number"]
            )

            user_info["uuid"] = uuid_of_user
            #user_info["pass_key"] = hashed.decode("utf-8")
            await self.app.email.send_mail([user_info["email"]], user_info)

            return {
                "status": status.HTTP_200_OK, "object": user_info
            }

        @self.router.post("/login")
        async def user_login(request_form: OAuth2PasswordRequestForm = Depends()):
            token = await self.app.auth.generate_token(request_form.username, request_form.password)

            return {
                "access_token": token, "token_type": "Bearer"
            }

    def add_put_routes(self):
        ...

    def add_delete_routes(self):
        ...