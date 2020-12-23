import os

from gino import Gino
from marshmallow import Schema, fields
from laviewset import SerializerMixin


DB_ARGS = dict(
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", 5432),
    user=os.getenv("DB_USER", "laviewset"),
    password=os.getenv("DB_PASS", ""),
    database=os.getenv("DB_NAME", "postgres"),
)
PG_URL = "postgresql://{user}:{password}@{host}" \
         ":{port}/{database}".format(**DB_ARGS)

db = Gino()


class User(db.Model):

    __tablename__ = "test_users"

    id = db.Column(db.BigInteger(), primary_key=True)
    nickname = db.Column("name", db.Unicode(), default=lambda: "test user")


class UserSchema(Schema, SerializerMixin):

    id = fields.Int(required=True)
    nickname = fields.Str(required=True)

    async def is_valid(self, cleaned_data, *args, **kwargs) -> None:
        user = await User.select('id').where(
            User.nickname == cleaned_data["nickname"]
        ).gino.first()
        if user is not None:
            self.not_valid(
                msg=f"User with nickname \"{cleaned_data['nickname']}\" "
                    f"already exists."
            )
