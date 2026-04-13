import os

from sqlmodel import create_engine

database_url = os.getenv("DATABASE_URL", "sqlite:///database.db").replace(
    "postgres://", "postgresql://", 1
)
engine = create_engine(database_url)
