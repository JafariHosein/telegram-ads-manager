import enum

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

from config import Config
from database.base import Base


class Database:
    _engine = create_engine(
        f'postgresql+psycopg2://{Config.database_username}:{Config.database_password}'
        f'@{Config.database_host}:{Config.database_port}/{Config.database_name}'
    )

    _SessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=False)

    Base.metadata.create_all(bind=_engine)

    @classmethod
    @contextmanager
    def get_session(cls):
        session = cls._SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


class UpdateType(enum.Enum):
    INCREMENT = "increment"
    DECREMENT = "decrement"
    NORMAL = "normal"
