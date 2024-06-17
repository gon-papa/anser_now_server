
from injector import inject

from src.repository.user_repository import UserRepository


class UserService:
    @inject
    def __init__(
        self,
        repository: UserRepository,
    ):
        self.repository = repository

    async def get_user(self):
        return await self.repository.get_user()