from tortoise import fields, Model
from datetime import datetime, timezone
from tortoise.contrib.pydantic import pydantic_model_creator


class User(Model):
    uuid = fields.BigIntField(primary_key=True, index=True)
    user_name = fields.CharField(max_length=60, null=False)
    full_name = fields.CharField(max_length=100, null=False)
    email = fields.CharField(max_length=300, null=False, unique=True)
    pass_key = fields.CharField(max_length=20, null=False, unique=False)
    is_verified = fields.BooleanField(default=False)
    phone_number = fields.CharField(max_length=30, null=False, unique=True)
    joined_at = fields.DatetimeField(default=datetime.now(timezone.utc))


class Business(Model):
    uuid = fields.BigIntField(primary_key=True, index=True)
    name = fields.CharField(max_length=120, null=False, unique=True)
    categories = fields.CharField(max_length=255, null=True)
    city = fields.CharField(max_length=60, null=False, default="Unspecified")
    address = fields.CharField(max_length=600, null=False, default="Unspecified")
    email = fields.CharField(max_length=255, null=True)
    website = fields.CharField(max_length=255, null=True)
    description = fields.TextField(null=True)
    phone_number = fields.CharField(max_length=30, null=False, unique=True)
    #logo = fields.CharField(max_length=120, null=False, default="logo.jpg")
    created_at = fields.DatetimeField(default=datetime.now(timezone.utc))
    owner = fields.ForeignKeyField("models.User", related_name="business")

class ChurnPredictor(Model):
    uuid = fields.BigIntField(primary_key=True, index=True)
    database_provider = fields.CharField(max_length=60, null=True)
    database_user = fields.CharField(max_length=120, null=True)
    database_name = fields.CharField(max_length=120, null=True)
    database_host = fields.CharField(max_length=255, null=True)
    database_port = fields.CharField(max_length=6, null=True)
    database_password = fields.CharField(max_length=255, unique=True, null=True)

    #database_driver = fields.CharField(max_length=12, null=True)
    #database_cluster_name = fields.CharField(max_length=120, null=True)


pydantic_user = pydantic_model_creator(User, name="User", exclude=("is_verified",))
pydantic_userIn = pydantic_model_creator(User, name="UserIn", exclude_readonly=True, exclude=("is_verified", "joined_at",))
pydantic_userOut = pydantic_model_creator(User, name="UserOut", exclude=("pass_key",))

pydantic_business = pydantic_model_creator(Business, name="Business")
pydantic_businessIn = pydantic_model_creator(Business, name="BusinessIn", exclude_readonly=True, exclude=("created_at",))

pydantic_churnPredictor = pydantic_model_creator(ChurnPredictor, name="ChurnPredictor")
pydantic_churnPredictorIn = pydantic_model_creator(ChurnPredictor, name="ChurnPredictorIn", exclude_readonly=True)