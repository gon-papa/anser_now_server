from typing import Any, Type, TypeVar
from injector import Injector, inject
from src.database.database import AppConfig

T = TypeVar('T')

class DependencyInjector:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DependencyInjector, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.di = Injector([AppConfig()])

    async def update_injector(self, _class: Type[Any]):
        self.di = Injector([_class])

    @inject
    def get_class(self, _class: Type[T]) -> T:
        return self.di.get(_class)

di_injector = DependencyInjector()