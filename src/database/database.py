import asyncio
import os
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from injector import Module, provider, singleton
from sqlalchemy.ext.asyncio import AsyncEngine, async_scoped_session, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

load_dotenv()


class DatabaseConnection:
    @singleton
    def __init__(self, connection_url: str, migration_url: str, option: dict = {}):
        self.connection_url = connection_url
        self.migration_url = migration_url
        self.option = option
        self.engine = self.get_async_engine()
        self.session = self.get_session(self.engine)

    @asynccontextmanager
    async def get_db(self):
        async with self.session() as session:
            yield session

    async def close_engine(self):
        if self.engine:
            await self.engine.dispose()
            await self.session.close()
            self.engine = None
            self.session = None

    def get_url(self) -> str:
        return self.connection_url

    def get_migration_url(self) -> str:
        return self.migration_url

    def get_async_engine(self) -> AsyncEngine:
        return create_async_engine(self.connection_url, **self.option)

    def get_session(self, engine: AsyncEngine) -> AsyncSession:
        async_session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=True,
        )
        # セッションのスコープ設定
        return async_scoped_session(async_session_factory, scopefunc=asyncio.current_task)


# DB設定クラスのインターフェース
class ConfigInterface(ABC):
    @abstractmethod
    def db_url(self) -> str:
        pass

    @abstractmethod
    def migration_url(self) -> str:
        pass

    @abstractmethod
    def get_option(self) -> dict:
        pass


class AppConfig(Module, ConfigInterface):
    @singleton
    @provider
    def provide_database_connection(self) -> DatabaseConnection:
        return DatabaseConnection(self.db_url(), self.migration_url(), self.get_option())

    def db_url(self) -> str:
        dialect = os.getenv("DB_DIALECT")
        driver = os.getenv("DB_DRIVER")
        username = os.getenv("DB_USER")
        password = os.getenv("DB_PASS")
        host = os.getenv("DB_HOST")
        port = os.getenv("DB_PORT")
        db_name = os.getenv("DB_NAME")
        return f"{dialect}+{driver}://{username}:{password}@{host}:{port}/{db_name}?charset=utf8"

    def migration_url(self) -> str:
        dialect = os.getenv("DB_DIALECT")
        username = os.getenv("DB_USER")
        password = os.getenv("DB_PASS")
        host = os.getenv("DB_HOST")
        port = os.getenv("DB_PORT")
        db_name = os.getenv("DB_NAME")
        return f"{dialect}+pymysql://{username}:{password}@{host}:{port}/{db_name}?charset=utf8"

    def get_option(self):
        logging = bool(os.getenv("SQL_LOGGING"))
        pool_size = int(os.getenv("DB_POOL_SIZE"))
        pool_connection_timeout = int(os.getenv("POOL_CONN_TIMEOUT"))
        max_overflow = int(os.getenv("DB_MAX_OVERFLOW"))
        pool_recycle = int(os.getenv("POOL_RECYCLE"))
        return {
            "echo": logging,
            "echo_pool": logging,
            "pool_size": pool_size,
            "pool_timeout": pool_connection_timeout,
            "max_overflow": max_overflow,
            "pool_recycle": pool_recycle,
            "pool_pre_ping": True,
        }