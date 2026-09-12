from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from buy_or_wait.config import Settings
from buy_or_wait.db.models import Base


def get_engine(settings: Settings | None = None):
    settings = settings or Settings()
    return create_engine(settings.database_url, pool_pre_ping=True)


def init_db(settings: Settings | None = None) -> None:
    Base.metadata.create_all(get_engine(settings))


def get_session(settings: Settings | None = None) -> Session:
    factory = sessionmaker(bind=get_engine(settings))
    return factory()
