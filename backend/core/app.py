import time
import uvicorn
from pytz import utc
from fastapi import FastAPI

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from tortoise.contrib.fastapi import register_tortoise

from .routes.v1 import Gateway, FileUpload, User
from backend import Config, models, utils
from backend.db import Database

class ApiServer:
    def __init__(self, directory):
        # Step 1: Instantiate the FastAPI object
        self.app = FastAPI(
            title="Kureghor API",
            version="1.0.0"
        )
        self.directory = directory
        self.app.mount(
            "/static",
            StaticFiles(
                directory=str(
                    self.directory / "static"
                )
            ),
            name="static"
        )

        self.config = Config
        self.models = models
        self.jinja2template = Jinja2Templates(
            directory=str(self.directory / "templates")
        )
        self.auth = utils.AuthConstructor(self)
        self.email = utils.EmailConstructor(self)
        self._profile_upload = str(self.directory / "static/images/profiles")
        self._bs_logo_upload = str(self.directory / "static/images/bs_logos")
        #self._product_upload = str(self.directory / "static/images/products")
        self._dynamic = "./backend/data/dynamic"
        self._static = "./backend/data/static"

        self.scheduler = AsyncIOScheduler()
        self.scheduler.configure(timezone=utc)
        self.db = Database(self)

        # Add routes (can be done with decorators on class methods)
        self.include_routers()
        self.add_routes()

    @staticmethod
    def generate_id():
        return hex(int(time.time() * 1e7))[2:]

    def include_routers(self):
        gateway_router = Gateway(self).router
        self.app.include_router(gateway_router)

        user_router = User(self).router
        self.app.include_router(user_router)

        upload_router = FileUpload(self).router
        self.app.include_router(upload_router)

    def add_routes(self):
        @self.app.on_event("startup")
        async def startup():
            print("Connecting to Database...")
            await self.db.connect()
            print("Connected to database.")

            self.scheduler.start()
            print(f"Scheduler started ({len(self.scheduler.get_jobs()):,} job(s)).")

        @self.app.on_event("shutdown")
        async def shutdown():
            print("Closing database...")
            await self.db.close()
            print("Closed database connection.")

        @self.app.get("/")
        async def read_root():
            return {"Hello": "World", "api_version": self.app.version}

        @self.app.get("/api/items/{item_id}")
        async def read_item(item_id: int):
            x = await self.db.field(f'SELECT {item_id};')
            return {"item_id": item_id, "db_calls": self.db._calls, "db_response": x}

    def run(self, host="0.0.0.0", port=8000, reload=False):
        """
        Step 3: Run the FastAPI app using uvicorn programmatically.
        When using reload=True, uvicorn needs the app object in the
        "module:attribute" format (e.g., "main:server.app").
        """

        if reload:
            register_tortoise(
                self.app,
                db_url="sqlite://database.sqlite3",
                modules={"models": ["backend.models.models"]},
                generate_schemas=True,
                add_exception_handlers=True

            )

            uvicorn.run(
                "backend.core.app:server.app",  # Reference the global instance
                host=host,
                port=port,
                reload=reload
            )
        else:
            register_tortoise(
                self.app,
                db_url="sqlite://database.sqlite3",
                modules={"models": ["backend.models.models"]},
                generate_schemas=True,
                add_exception_handlers=True
            )

            # For production or without reload, you can pass the app instance directly
            uvicorn.run(self.app, host=host, port=port)