from backend.utils.db import postgresql

from fastapi import APIRouter, Depends, status

class ChurnPredictor:
    def __init__(self, app):
        self.app = app
        self.router = APIRouter(
            prefix="/api/v1/churnPredictor",
            tags=["churn predictor on v1"]
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
        @self.router.post("/subscribeWith/")
        async def subscribe_churn_predictor_module(bs_id: str, db: self.app.models.pydantic_churnPredictorIn, user: Depends(self.app.auth.get_current_user)):
            uuid_of_db = self.app.generate_id()
            db_info = db.dict(exclude_unset=True)
            COMPATIBLE_DATABASES = ["PostgreSQL", "OracleDB", "MySQL", "Microsoft SQL Server", "MongoDB", "MariaDB", "IBM DB2", "ElasticSearch", "Redis"]

            if db_info["database_provider"] not in COMPATIBLE_DATABASES:
                return {
                    "message": "that database is not implemented yet. contact our support"
                }

            if db_info["database_provider"] in ("MongoDB", "Microsoft SQL Server", "ElasticSearch"):
                ...

            else:

                handler = postgresql.PostgreSQL(
                    db=db_info["database_name"],
                    host=db_info["database_host"],
                    user=db_info["database_user"],
                    password=db_info["database_password"],
                    port=int(db_info["database_port"])
                )
                await handler.connect()
                print("connected")
                s = await handler.record("SELECT version()")
                print(s)
                #await handler.execute("DROP TABLE IF EXISTS public.app CASCADE")
                await handler.close()
                print("disconnected")

                await self.app.db.execute(
                    "INSERT INTO postgresql (PGSQL_UUID, DB_TYPE, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT, DB_HOST, BUSINESS_UUID, BS_OWNER_UUID) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)",
                    uuid_of_db,
                    "postgresql",
                    db_info["database_name"],
                    db_info["database_user"],
                    db_info["database_password"],
                    int(db_info["database_port"]),
                    db_info["database_host"],
                    bs_id,
                    user.get("uuid")
                )

            return {
                "database_type": db_info, "bs_uuid": bs_id
            }

    def add_put_routes(self):
        ...

    def add_delete_routes(self):
        ...