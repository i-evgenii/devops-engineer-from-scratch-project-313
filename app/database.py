import os
from functools import wraps

from sqlmodel import Session, create_engine


def with_session(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with Session(engine) as session:
            return func(session, *args, **kwargs)

    return wrapper


database_url = os.getenv("DATABASE_URL", "sqlite:///database.db").replace(
    "postgres://", "postgresql://", 1
)
engine = create_engine(database_url)
