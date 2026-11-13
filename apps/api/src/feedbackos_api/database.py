from collections.abc import Iterator
from contextlib import contextmanager
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from feedbackos_api.config import get_settings


class Database:
    def __init__(self, url: str) -> None:
        self.engine = create_engine(url, pool_pre_ping=True, hide_parameters=True)
        self.session_factory = sessionmaker(self.engine, expire_on_commit=False)

    @contextmanager
    def transaction(self) -> Iterator[Session]:
        """调用方在响应前退出此边界；成功提交，任意异常回滚并关闭会话。"""
        with self.session_factory.begin() as session:
            yield session

    def dispose(self) -> None:
        self.engine.dispose()


@lru_cache
def get_database() -> Database:
    settings = get_settings()
    assert settings.database_url is not None
    return Database(settings.database_url.get_secret_value())
