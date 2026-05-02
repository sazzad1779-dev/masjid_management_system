from typing import Generator
from sqlmodel import create_engine, Session

SQLALCHEMY_DATABASE_URL = "sqlite:///./masjid.db"
# Use a basic sqlite DB for development. Adjust check_same_thread for SQLite
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

def init_db():
    from sqlmodel import SQLModel
    # Import all models here so SQLModel knows about them
    from src.models.masjid import Masjid
    from src.models.user import User
    from src.models.income import Income
    SQLModel.metadata.create_all(engine)
