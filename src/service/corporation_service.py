from injector import inject

from src.core.logging import log
from src.repository.corporation_repository import CorporationRepository




class CorporationService:
    @inject
    def __init__(
        self,
        repository: CorporationRepository,
    ):
        self.repository = repository

    async def check_uuid(self, uuid: str) -> bool:
        corporation = await self.repository.get_corporation_by_uuid(uuid=uuid)
        return corporation