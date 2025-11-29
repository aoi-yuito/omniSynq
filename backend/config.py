rom os import getenv
from typing import Final

from dotenv import load_dotenv

load_dotenv()


class Config:
    PG_DB: Final = getenv("PG_DB", "")
    PG_HOST: Final = getenv("PG_HOST", "")
    PG_USER: Final = getenv("PG_USER", "")
    PG_PASS: Final = getenv("PG_PASS", "")
    PG_PORT: Final = getenv("PG_PORT", "")

    MAIL_ADDRESS: Final = getenv("MAIL_ADDRESS", "")
    MAIL_PASSWORD: Final = getenv("MAIL_PASSWORD", "")
    YOU_HAVE_BEEN_WARNED: Final = getenv("YOU_HAVE_BEEN_WARNED", "")