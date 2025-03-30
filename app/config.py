from decouple import config

FLASK_DEBUG = config("FLASK_DEBUG", cast=bool, default=False)
LOGFMT = config("LOGFMT", "text")
LOG_LEVEL = config("LOG_LEVEL", "info")

SERVICE_ENV = config("SERVICE_ENV")
SQLALCHEMY_DATABASE_URI = config("DATABASE_URI")
SQLALCHEMY_POOL_RECYCLE = config(
    "SQLALCHEMY_POOL_RECYCLE",
    default=600,
    cast=int,
)
SQLALCHEMY_POOL_SIZE = config(
    "SQLALCHEMY_POOL_SIZE",
    default=10,
    cast=int,
)
SQLALCHEMY_MAX_OVERFLOW = config(
    "SQLALCHEMY_MAX_OVERFLOW",
    default=20,
    cast=int,
)
SQLALCHEMY_POOL_PRE_PING = config("SQLALCHEMY_POOL_PRE_PING", cast=bool, default=False)
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_recycle": SQLALCHEMY_POOL_RECYCLE,
    "pool_size": SQLALCHEMY_POOL_SIZE,
    "max_overflow": SQLALCHEMY_MAX_OVERFLOW,
    "pool_pre_ping": SQLALCHEMY_POOL_PRE_PING,
}
SQLALCHEMY_TRACK_MODIFICATIONS = config(
    "SQLALCHEMY_TRACK_MODIFICATIONS",
    default=False,
    cast=bool,
)
