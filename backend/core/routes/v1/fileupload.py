import secrets
import aiofiles

from PIL import Image
from fastapi import APIRouter, File, UploadFile, Depends, status

class FileUpload:
    def __init__(self, app):
        self.app = app
        self.router = APIRouter(
            prefix="/api/v1/uploadfile",
            tags=["uploadfile on v1"]
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
        @self.router.post("/user/me/profile")
        async def profile_upload(file: UploadFile = File(...),  user = Depends(self.app.auth.get_current_user)):
            file_name = file.filename
            extension = file_name.split(".")[1]

            if extension not in ["jpg", "png"]:
                return {
                    "status": "error",
                    "details": "File extension is not allowed"
                }

            token = secrets.token_hex(10) + "." + extension
            #print(token)
            generated_file = self.app._profile_upload + "/" + token
            #print(generated_file)
            file_content = await file.read()

            async with aiofiles.open(generated_file, "wb") as script:
                await script.write(file_content)

            image = Image.open(generated_file)
            image = image.resize(size=(200, 200))
            image.save(generated_file)

            await self.app.db.execute(
                "UPDATE users SET AVATAR = $1 WHERE U_UUID = $2", token, user.get("uuid")
            )

            file_url = "https://filthy-cauldron-6q6pxgq4wg2rppr-8000.app.github.dev/https://filthy-cauldron-6q6pxgq4wg2rppr-8000.app.github.dev/static/images/profiles/" + token

            return {
                "status": status.HTTP_200_OK, "file_url": file_url
            }

        @self.router.post("/business/logo/{uuid}", response_model=None)
        async def business_logo_upload(uuid: str, file: UploadFile = File(...), user = Depends(self.app.auth.get_current_user)):
            file_name = file.filename
            extension = file_name.split(".")[1]

            if extension not in ["jpg", "png"]:
                return {
                    "status": "error",
                    "details": "File extension is not allowed"
                }

            token = secrets.token_hex(10) + "." + extension
            #print(token)
            generated_file = self.app._bs_logo_upload + "/" + token
            #print(generated_file)
            file_content = await file.read()

            async with aiofiles.open(generated_file, "wb") as script:
                await script.write(file_content)

            image = Image.open(generated_file)
            image = image.resize(size=(200, 200))
            image.save(generated_file)

            await self.app.db.execute(
                "UPDATE business SET BS_LOGO = $1 WHERE BS_UUID = $2", token, uuid
            )

            file_url = "https://filthy-cauldron-6q6pxgq4wg2rppr-8000.app.github.dev/https://filthy-cauldron-6q6pxgq4wg2rppr-8000.app.github.dev/static/images/bs_logos/" + token

            return {
                "status": status.HTTP_200_OK, "file_url": file_url
            }

    def add_put_routes(self):
        ...

    def add_delete_routes(self):
        ...