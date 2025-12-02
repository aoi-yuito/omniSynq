from fastapi import APIRouter, Depends, status

class Business:
    def __init__(self, app):
        self.app = app
        self.router = APIRouter(
            prefix="/api/v1/business",
            tags=["business on v1"]
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
        @self.router.post("/registration")
        async def business_sign_up(business: self.app.models.pydantic_businessIn, user = Depends(self.app.auth.get_current_user)):
            uuid_of_business = self.app.generate_id()
            business_info = business.dict(exclude_unset=True)

            await self.app.db.execute(
                "INSERT INTO business (BS_UUID, BS_NAME, CITY, BS_PHONE, BS_OWNER_ID) VALUES ($1, $2, $3, $4, $5)",
                uuid_of_business,
                business_info["name"],
                business_info["city"],
                business_info["phone_number"],
                user.get("uuid")
            )

            business_info["uuid"] = uuid_of_business

            return {
                "status": status.HTTP_200_OK, "object": business_info
            }

    def add_put_routes(self):
        ...

    def add_delete_routes(self):
        ...