from fastapi import APIRouter, Depends, status

class User:
    def __init__(self, app):
        self.app = app
        self.router = APIRouter(
            prefix="/api/v1/user",
            tags=["user on v1"]
        )

        self.add_routes()

    def add_routes(self):
        self.add_get_routes()
        self.add_post_routes()
        self.add_put_routes()
        self.add_delete_routes()

    def add_get_routes(self):
        ...

    def add_post_routes(self):
        @self.router.post("/me")
        async def get_myself(user = Depends(self.app.auth.get_current_user)):
            return {
                "status": status.HTTP_200_OK, "object": user
            }

    def add_put_routes(self):
        @self.router.put("/update/me")
        async def update_user_info(updated_user: self.app.models.pydantic_userIn, user = Depends(self.app.auth.get_current_user)):
            user_info = updated_user.dict(exclude_unset=True)

            await self.app.db.execute(
                "UPDATE users SET USR_NAME = $1, PHONE = $2 WHERE U_UUID = $3",
                user_info["username"],
                user_info["phone"],
                user.get("uuid")
            )

            return {
                "status": status.HTTP_200_OK, "object": user_info
            }

    def add_delete_routes(self):
        @self.router.delete("/delete/me")
        async def delete_user(user = Depends(self.app.auth.get_current_user)):
            deleted_user = await self.app.db.execute("DELETE FROM users WHERE U_UUID = $1", user.get("uuid"))

            #if not deleted_user:
            #    return {
            #        "status": 404, "details": "user not found"
            #    }

            return {
                "status": status.HTTP_200_OK
            }